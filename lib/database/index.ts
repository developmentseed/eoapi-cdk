import {
  Stack,
  aws_rds as rds,
  aws_ec2 as ec2,
  aws_secretsmanager as secretsmanager,
  aws_lambda,
  CustomResource,
  RemovalPolicy,
  Duration,
  aws_logs,
} from "aws-cdk-lib";
import { Construct } from "constructs";
import { CustomLambdaFunctionProps } from "../utils";
import { PgBouncer } from "./PgBouncer";

const instanceSizes: Record<string, number> = require("./instance-memory.json");
const DEFAULT_PGSTAC_VERSION = "0.8.5";

let defaultPgSTACCustomOptions: { [key: string]: any } = {
  context: "FALSE",
  mosaic_index: "TRUE",
};

function hasVpc(
  instance: rds.DatabaseInstance | rds.IDatabaseInstance
): instance is rds.DatabaseInstance {
  return (instance as rds.DatabaseInstance).vpc !== undefined;
}

/**
 * An RDS instance with pgSTAC installed. This is a wrapper around the
 * `rds.DatabaseInstance` higher-level construct making use
 * of the BootstrapPgStac construct.
 */
export class PgStacDatabase extends Construct {
  db: rds.DatabaseInstance;
  pgstacSecret: secretsmanager.ISecret;
  private _pgBouncerServer?: PgBouncer;

  public readonly connectionTarget: rds.IDatabaseInstance | ec2.Instance;
  public readonly securityGroup?: ec2.SecurityGroup;
  public readonly secretBootstrapper?: CustomResource;

  constructor(scope: Construct, id: string, props: PgStacDatabaseProps) {
    super(scope, id);

    const defaultParameters = this.getParameters(
      props.instanceType?.toString() || "m5.large",
      props.parameters
    );
    const parameterGroup = new rds.ParameterGroup(this, "parameterGroup", {
      engine: props.engine,
      parameters: {
        max_connections: defaultParameters.maxConnections,
        shared_buffers: defaultParameters.sharedBuffers,
        effective_cache_size: defaultParameters.effectiveCacheSize,
        work_mem: defaultParameters.workMem,
        maintenance_work_mem: defaultParameters.maintenanceWorkMem,
        max_locks_per_transaction: defaultParameters.maxLocksPerTransaction,
        temp_buffers: defaultParameters.tempBuffers,
        seq_page_cost: defaultParameters.seqPageCost,
        random_page_cost: defaultParameters.randomPageCost,
        ...props.parameters,
      },
    });

    this.db = new rds.DatabaseInstance(this, "db", {
      instanceIdentifier: Stack.of(this).stackName,
      parameterGroup,
      ...props,
    });

    const handler = new aws_lambda.Function(this, "lambda", {
      // defaults
      runtime: aws_lambda.Runtime.PYTHON_3_11,
      handler: "handler.handler",
      memorySize: 128,
      logRetention: aws_logs.RetentionDays.ONE_WEEK,
      timeout: Duration.minutes(2),
      code: aws_lambda.Code.fromDockerBuild(__dirname, {
        file: "bootstrapper_runtime/Dockerfile",
        buildArgs: {
          PYTHON_VERSION: "3.11",
        },
      }),
      vpc: hasVpc(this.db) ? this.db.vpc : props.vpc,
      allowPublicSubnet: true,
      // overwrites defaults with user-provided configurable properties,
      ...props.bootstrapperLambdaFunctionOptions,
    });

    this.pgstacSecret = new secretsmanager.Secret(this, "bootstrappersecret", {
      secretName: [
        props.secretsPrefix || "pgstac",
        id,
        this.node.addr.slice(-8),
      ].join("/"),
      generateSecretString: {
        secretStringTemplate: JSON.stringify({
          dbname: props.pgstacDbName || "pgstac",
          engine: "postgres",
          port: 5432,
          host: this.db.instanceEndpoint.hostname,
          username: props.pgstacUsername || "pgstac_user",
        }),
        generateStringKey: "password",
        excludePunctuation: true,
      },
      description: `PgSTAC database bootstrapped by ${
        Stack.of(this).stackName
      }`,
    });

    // Allow lambda to...
    // read new user secret
    this.pgstacSecret.grantRead(handler);
    // read database secret
    this.db.secret!.grantRead(handler);
    // connect to database
    this.db.connections.allowFrom(handler, ec2.Port.tcp(5432));

    let customResourceProperties: { [key: string]: any } =
      props.customResourceProperties
        ? { ...defaultPgSTACCustomOptions, ...props.customResourceProperties }
        : defaultPgSTACCustomOptions;

    // update properties
    customResourceProperties["conn_secret_arn"] = this.db.secret!.secretArn;
    customResourceProperties["new_user_secret_arn"] =
      this.pgstacSecret.secretArn;

    // if props.lambdaFunctionOptions doesn't have 'code' defined, update pgstac_version (needed for default runtime)
    if (!props.bootstrapperLambdaFunctionOptions?.code) {
      customResourceProperties["pgstac_version"] =
        props.pgstacVersion || DEFAULT_PGSTAC_VERSION;
    }

    // add timestamp to properties to ensure the Lambda gets re-executed on each deploy
    customResourceProperties["timestamp"] = new Date().toISOString();

    const bootstrapper = new CustomResource(this, "bootstrapper", {
      serviceToken: handler.functionArn,
      properties: customResourceProperties,
      removalPolicy: RemovalPolicy.RETAIN, // This retains the custom resource (which doesn't really exist), not the database
    });

    // PgBouncer: connection poolercustomresource trigger on redeploy
    const addPgbouncer = props.addPgbouncer ?? true;
    if (addPgbouncer) {
      this._pgBouncerServer = new PgBouncer(this, "pgbouncer", {
        instanceName: `${Stack.of(this).stackName}-pgbouncer`,
        instanceType: ec2.InstanceType.of(
          ec2.InstanceClass.T3,
          ec2.InstanceSize.MICRO
        ),
        vpc: props.vpc,
        database: {
          connections: this.db.connections,
          secret: this.pgstacSecret,
        },
        dbMaxConnections: parseInt(defaultParameters.maxConnections),
        usePublicSubnet:
          !props.vpcSubnets ||
          props.vpcSubnets.subnetType === ec2.SubnetType.PUBLIC,
        pgBouncerConfig: {
          poolMode: "transaction",
          maxClientConn: 1000,
          defaultPoolSize: 20,
          minPoolSize: 10,
          reservePoolSize: 5,
          reservePoolTimeout: 5,
        },
      });

      this._pgBouncerServer.node.addDependency(bootstrapper);

      this.pgstacSecret = this._pgBouncerServer.pgbouncerSecret;
      this.connectionTarget = this._pgBouncerServer.instance;
      this.securityGroup = this._pgBouncerServer.securityGroup;
      this.secretBootstrapper = this._pgBouncerServer.secretUpdateComplete;
    } else {
      this.connectionTarget = this.db;
    }
  }

  public getParameters(
    instanceType: string,
    parameters: PgStacDatabaseProps["parameters"]
  ): DatabaseParameters {
    // https://github.com/aws/aws-cli/issues/1279#issuecomment-909318236
    const memory_in_kb = instanceSizes[instanceType] * 1024;

    // It's only necessary to consider passed in parameters for any value that used to
    // derive subsequent values. Values that don't have dependencies will be overriden
    // when we unpack the passed-in user parameters
    const maxConnections = parameters?.maxConnections
      ? Number.parseInt(parameters.maxConnections)
      : // https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Limits.html#RDS_Limits.MaxConnections
        Math.min(Math.round((memory_in_kb * 1024) / 9531392), 5000);
    const sharedBuffers = parameters?.sharedBufers
      ? Number.parseInt(parameters.sharedBufers)
      : Math.round(0.25 * memory_in_kb);

    const effectiveCacheSize = Math.round(0.75 * memory_in_kb);
    const workMem = Math.floor(sharedBuffers / maxConnections);
    const maintenanceWorkMem = Math.round(0.25 * sharedBuffers);

    const tempBuffers = 128 * 1024;
    const seqPageCost = 1;
    const randomPageCost = 1.1;

    return {
      maxConnections: `${maxConnections}`,
      sharedBuffers: `${sharedBuffers / 8}`, // Represented in 8kb blocks
      effectiveCacheSize: `${effectiveCacheSize / 8}`, // Represented in 8kb blocks
      workMem: `${workMem}`,
      maintenanceWorkMem: `${maintenanceWorkMem}`,
      maxLocksPerTransaction: "1024",
      tempBuffers: `${tempBuffers / 8}`, // Represented in 8kb blocks
      seqPageCost: `${seqPageCost}`,
      randomPageCost: `${randomPageCost}`,
    };
  }
}

export interface PgStacDatabaseProps extends rds.DatabaseInstanceProps {
  /**
   * Name of database that is to be created and onto which pgSTAC will be installed.
   *
   * @default pgstac
   */
  readonly pgstacDbName?: string;

  /**
   * Version of pgstac to install on the database
   *
   * @default 0.8.5
   */
  readonly pgstacVersion?: string;

  /**
   * Prefix to assign to the generated `secrets_manager.Secret`
   *
   * @default pgstac
   */
  readonly secretsPrefix?: string;

  /**
   * Name of user that will be generated for connecting to the pgSTAC database.
   *
   * @default pgstac_user
   */
  readonly pgstacUsername?: string;

  /**
   * Add pgbouncer instance for managing traffic to the pgSTAC database
   *
   * @default true
   */
  readonly addPgbouncer?: boolean;

  /**
   * Lambda function Custom Resource properties. A custom resource property is going to be created
   * to trigger the boostrapping lambda function. This parameter allows the user to specify additional properties
   * on top of the defaults ones.
   *
   */
  readonly customResourceProperties?: {
    [key: string]: any;
  };

  /**
   * Can be used to override the default lambda function properties.
   *
   * @default - defined in the construct.
   */
  readonly bootstrapperLambdaFunctionOptions?: CustomLambdaFunctionProps;
}

export interface DatabaseParameters {
  /**
   * @default - LEAST({DBInstanceClassMemory/9531392}, 5000)
   */
  readonly maxConnections: string;

  /**
   * Note: This value is measured in 8KB blocks.
   *
   * @default '{DBInstanceClassMemory/32768}' 25% of instance memory, ie `{(DBInstanceClassMemory/(1024*8)) * 0.25}`
   */
  readonly sharedBuffers: string;

  /**
   * @default - 75% of instance memory
   */
  readonly effectiveCacheSize: string;

  /**
   * @default - shared buffers divided by max connections
   */
  readonly workMem: string;

  /**
   * @default - 25% of shared buffers
   */
  readonly maintenanceWorkMem: string;

  /**
   * @default 1024
   */
  readonly maxLocksPerTransaction: string;

  /**
   * @default 131172 (128 * 1024)
   */
  readonly tempBuffers: string;

  /**
   * @default 1
   */
  readonly seqPageCost: string;

  /**
   * @default 1.1
   */
  readonly randomPageCost: string;
}
