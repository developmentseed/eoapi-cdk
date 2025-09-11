import {
  aws_ec2 as ec2,
  aws_iam as iam,
  aws_lambda as lambda,
  aws_secretsmanager as secretsmanager,
  CustomResource,
  Duration,
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
   * PgBouncer configuration options
   */
  pgBouncerConfig?: PgBouncerConfigProps;

  /**
   * EC2 instance options
   */
  instanceProps?: Partial<ec2.InstanceProps>;
}

export class PgBouncer extends Construct {
  public readonly instance: ec2.Instance;
  public readonly pgbouncerSecret: secretsmanager.Secret;
  public readonly securityGroup: ec2.SecurityGroup;
  public readonly secretUpdateComplete: CustomResource;
  public readonly healthCheck: CustomResource;

  // The max_connections parameter in PgBouncer determines the maximum number of
  // connections to open on the actual database instance. We want that number to
  // be slightly smaller than the actual max_connections value on the RDS instance
  // so we perform this calculation.

  private getDefaultPgbouncerConfig(
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

    const defaultPgbouncerConfig = this.getDefaultPgbouncerConfig(
      props.dbMaxConnections
    );

    // Merge provided config with defaults
    const pgBouncerConfig: Required<PgBouncerConfigProps> = {
      ...defaultPgbouncerConfig,
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

    // Create a security group and allow connections from the Lambda IP ranges for this region
    this.securityGroup = new ec2.SecurityGroup(this, "PgBouncerSecurityGroup", {
      vpc: props.vpc,
      description: "Security group for PgBouncer instance",
      allowAllOutbound: true,
    });

    // Create PgBouncer instance
    const defaultInstanceConfig: Omit<ec2.InstanceProps, "vpc"> = {
      instanceName: "pgbouncer",
      instanceType: ec2.InstanceType.of(
        ec2.InstanceClass.T3,
        ec2.InstanceSize.MICRO
      ),
      vpcSubnets: {
        subnetType: props.usePublicSubnet
          ? ec2.SubnetType.PUBLIC
          : ec2.SubnetType.PRIVATE_WITH_EGRESS,
      },
      machineImage: ec2.MachineImage.fromSsmParameter(
        "/aws/service/canonical/ubuntu/server/noble/stable/current/amd64/hvm/ebs-gp3/ami-id",
        { os: ec2.OperatingSystemType.LINUX }
      ),
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
      role,
      securityGroup: this.securityGroup,
      userData: this.loadUserDataScript(pgBouncerConfig, props.database),
      userDataCausesReplacement: true,
      associatePublicIpAddress: props.usePublicSubnet,
    };

    this.instance = new ec2.Instance(this, "Instance", {
      ...defaultInstanceConfig,
      ...props.instanceProps,
      vpc: props.vpc,
    });

    // Allow PgBouncer to connect to RDS
    props.database.connections.allowFrom(
      this.instance,
      ec2.Port.tcp(5432),
      "Allow PgBouncer to connect to RDS"
    );

    // Create a new secret for pgbouncer connection credentials
    this.pgbouncerSecret = new secretsmanager.Secret(this, "PgBouncerSecret", {
      description: "Connection information for PgBouncer instance",
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

    this.secretUpdateComplete = new CustomResource(
      this,
      "pgbouncerSecretBootstrapper",
      {
        serviceToken: secretUpdaterFn.functionArn,
        properties: {
          instanceIp: props.usePublicSubnet
            ? this.instance.instancePublicIp
            : this.instance.instancePrivateIp,
        },
      }
    );

    // Add health check custom resource
    const healthCheckFunction = new lambda.Function(
      this,
      "HealthCheckFunction",
      {
        runtime: lambda.Runtime.NODEJS_20_X,
        handler: "index.handler",
        timeout: Duration.minutes(10),
        code: lambda.Code.fromAsset(
          path.join(__dirname, "lambda/pgbouncer-health-check")
        ),
        description: "PgBouncer health check function",
      }
    );

    // Grant SSM permissions for health check
    healthCheckFunction.addToRolePolicy(
      new iam.PolicyStatement({
        actions: [
          "ssm:SendCommand",
          "ssm:GetCommandInvocation",
          "ssm:DescribeInstanceInformation",
          "ssm:ListCommandInvocations",
        ],
        resources: ["*"],
      })
    );

    this.healthCheck = new CustomResource(this, "PgBouncerHealthCheck", {
      serviceToken: healthCheckFunction.functionArn,
      properties: {
        InstanceId: this.instance.instanceId,
        // Add timestamp to force re-execution on stack updates
        Timestamp: new Date().toISOString(),
      },
    });

    // Ensure health check runs after instance is created but before secret update
    this.healthCheck.node.addDependency(this.instance);
    this.secretUpdateComplete.node.addDependency(this.healthCheck);
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
