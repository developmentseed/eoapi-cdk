import {
  aws_ec2 as ec2,
  aws_iam as iam,
  aws_lambda as lambda,
  aws_secretsmanager as secretsmanager,
  CustomResource,
  Stack,
} from "aws-cdk-lib";
import { Construct } from "constructs";

import * as fs from "fs";
import * as path from "path";

// used to populate pgbouncer config:
// see https://www.pgbouncer.org/config.html for details
export interface PgBouncerConfigProps {
  poolMode?: "transaction" | "session" | "statement";
  maxClientConn?: number;
  defaultPoolSize?: number;
  minPoolSize?: number;
  reservePoolSize?: number;
  reservePoolTimeout?: number;
  maxDbConnections?: number;
  maxUserConnections?: number;
}

export interface PgBouncerProps {
  /**
   * Name for the pgbouncer instance
   */
  instanceName: string;

  /**
   * VPC to deploy PgBouncer into
   */
  vpc: ec2.IVpc;

  /**
   * The RDS instance to connect to
   */
  database: {
    connections: ec2.Connections;
    secret: secretsmanager.ISecret;
  };

  /**
   * Maximum connections setting for the database.
   * PgBouncer will use 10 fewer than this value.
   */
  dbMaxConnections: number;

  /**
   * Whether to deploy in public subnet
   * @default false
   */
  usePublicSubnet?: boolean;

  /**
   * Instance type for PgBouncer
   * @default t3.micro
   */
  instanceType?: ec2.InstanceType;

  /**
   * PgBouncer configuration options
   */
  pgBouncerConfig?: PgBouncerConfigProps;
}

export class PgBouncer extends Construct {
  public readonly instance: ec2.Instance;
  public readonly pgbouncerSecret: secretsmanager.Secret;

  // The max_connections parameter in PgBouncer determines the maximum number of
  // connections to open on the actual database instance. We want that number to
  // be slightly smaller than the actual max_connections value on the RDS instance
  // so we perform this calculation.

  private getDefaultConfig(
    dbMaxConnections: number
  ): Required<PgBouncerConfigProps> {
    // maxDbConnections (and maxUserConnections) are the only settings that need
    // to be responsive to the database size/max_connections setting
    return {
      poolMode: "transaction",
      maxClientConn: 1000,
      defaultPoolSize: 5,
      minPoolSize: 0,
      reservePoolSize: 5,
      reservePoolTimeout: 5,
      maxDbConnections: dbMaxConnections - 10,
      maxUserConnections: dbMaxConnections - 10,
    };
  }

  constructor(scope: Construct, id: string, props: PgBouncerProps) {
    super(scope, id);

    // Set defaults for optional props
    const defaultInstanceType = ec2.InstanceType.of(
      ec2.InstanceClass.T3,
      ec2.InstanceSize.MICRO
    );

    const instanceType = props.instanceType ?? defaultInstanceType;
    const defaultConfig = this.getDefaultConfig(props.dbMaxConnections);

    // Merge provided config with defaults
    const pgBouncerConfig: Required<PgBouncerConfigProps> = {
      ...defaultConfig,
      ...props.pgBouncerConfig,
    };

    // Create role for PgBouncer instance to enable writing to CloudWatch
    const role = new iam.Role(this, "InstanceRole", {
      description:
        "pgbouncer instance role with Systems Manager + CloudWatch permissions",
      assumedBy: new iam.ServicePrincipal("ec2.amazonaws.com"),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName(
          "AmazonSSMManagedInstanceCore"
        ),
        iam.ManagedPolicy.fromAwsManagedPolicyName(
          "CloudWatchAgentServerPolicy"
        ),
      ],
    });

    // Add policy to allow reading RDS credentials from Secrets Manager
    role.addToPolicy(
      new iam.PolicyStatement({
        actions: ["secretsmanager:GetSecretValue"],
        resources: [props.database.secret.secretArn],
      })
    );

    // Create PgBouncer instance
    this.instance = new ec2.Instance(this, "Instance", {
      vpc: props.vpc,
      vpcSubnets: {
        subnetType: props.usePublicSubnet
          ? ec2.SubnetType.PUBLIC
          : ec2.SubnetType.PRIVATE_WITH_EGRESS,
      },
      instanceType,
      instanceName: props.instanceName,
      machineImage: ec2.MachineImage.fromSsmParameter(
        "/aws/service/canonical/ubuntu/server/jammy/stable/current/amd64/hvm/ebs-gp2/ami-id",
        { os: ec2.OperatingSystemType.LINUX }
      ),
      role,
      blockDevices: [
        {
          deviceName: "/dev/xvda",
          volume: ec2.BlockDeviceVolume.ebs(20, {
            volumeType: ec2.EbsDeviceVolumeType.GP3,
            encrypted: true,
            deleteOnTermination: true,
          }),
        },
      ],
      userData: this.loadUserDataScript(pgBouncerConfig, props.database),
      userDataCausesReplacement: true,
    });

    // Allow PgBouncer to connect to RDS
    props.database.connections.allowFrom(
      this.instance,
      ec2.Port.tcp(5432),
      "Allow PgBouncer to connect to RDS"
    );

    // Create a new secret for pgbouncer connection credentials
    this.pgbouncerSecret = new secretsmanager.Secret(this, "PgBouncerSecret", {
      description: `Connection information for PgBouncer instance ${props.instanceName}`,
      generateSecretString: {
        generateStringKey: "dummy",
        secretStringTemplate: "{}",
      },
    });

    // Grant the role permission to read the new secret
    this.pgbouncerSecret.grantRead(role);

    // Update pgbouncerSecret to contain pgstacSecret values but with new value for host
    const secretUpdaterFn = new lambda.Function(this, "SecretUpdaterFunction", {
      runtime: lambda.Runtime.NODEJS_20_X,
      handler: "index.handler",
      code: lambda.Code.fromAsset(
        path.join(__dirname, "lambda/pgbouncer-secret-updater")
      ),
      environment: {
        SOURCE_SECRET_ARN: props.database.secret.secretArn,
        TARGET_SECRET_ARN: this.pgbouncerSecret.secretArn,
      },
    });

    props.database.secret.grantRead(secretUpdaterFn);
    this.pgbouncerSecret.grantWrite(secretUpdaterFn);

    new CustomResource(this, "pgbouncerSecretBootstrapper", {
      serviceToken: secretUpdaterFn.functionArn,
      properties: {
        instanceIp: this.instance.instancePrivateIp,
      },
    });
  }

  private loadUserDataScript(
    pgBouncerConfig: Required<NonNullable<PgBouncerProps["pgBouncerConfig"]>>,
    database: { secret: secretsmanager.ISecret }
  ): ec2.UserData {
    const userDataScript = ec2.UserData.forLinux();

    // Set environment variables with configuration parameters
    userDataScript.addCommands(
      'export SECRET_ARN="' + database.secret.secretArn + '"',
      'export REGION="' + Stack.of(this).region + '"',
      'export POOL_MODE="' + pgBouncerConfig.poolMode + '"',
      'export MAX_CLIENT_CONN="' + pgBouncerConfig.maxClientConn + '"',
      'export DEFAULT_POOL_SIZE="' + pgBouncerConfig.defaultPoolSize + '"',
      'export MIN_POOL_SIZE="' + pgBouncerConfig.minPoolSize + '"',
      'export RESERVE_POOL_SIZE="' + pgBouncerConfig.reservePoolSize + '"',
      'export RESERVE_POOL_TIMEOUT="' +
        pgBouncerConfig.reservePoolTimeout +
        '"',
      'export MAX_DB_CONNECTIONS="' + pgBouncerConfig.maxDbConnections + '"',
      'export MAX_USER_CONNECTIONS="' + pgBouncerConfig.maxUserConnections + '"'
    );

    // Load the startup script
    const scriptPath = path.join(__dirname, "./pgbouncer-setup.sh");
    let script = fs.readFileSync(scriptPath, "utf8");

    userDataScript.addCommands(script);

    return userDataScript;
  }
}
