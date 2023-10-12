import {
  aws_ec2,
  aws_rds,
  aws_lambda,
  aws_logs,
  aws_secretsmanager,
  CustomResource,
  Duration,
  Stack,
  RemovalPolicy,
} from "aws-cdk-lib";
import { Construct } from "constructs";
import { CustomLambdaFunctionProps } from "../utils";

const DEFAULT_PGSTAC_VERSION = "0.6.13";

function hasVpc(
  instance: aws_rds.DatabaseInstance | aws_rds.IDatabaseInstance
): instance is aws_rds.DatabaseInstance {
  return (instance as aws_rds.DatabaseInstance).vpc !== undefined;
}

/**
 * Bootstraps a database instance, installing pgSTAC onto the database.
 */
export class BootstrapPgStac extends Construct {
  secret: aws_secretsmanager.ISecret;

  constructor(scope: Construct, id: string, props: BootstrapPgStacProps) {
    super(scope, id);

    const handler = new aws_lambda.Function(this, "lambda", {
      // defaults for configurable properties
      runtime: aws_lambda.Runtime.PYTHON_3_8,
      handler: "handler.handler",
      memorySize: 128,
      logRetention: aws_logs.RetentionDays.ONE_WEEK,
      timeout: Duration.minutes(2),
      code: aws_lambda.Code.fromDockerBuild(__dirname, {
        file: "runtime/Dockerfile",
        buildArgs: {PGSTAC_VERSION: DEFAULT_PGSTAC_VERSION, PYTHON_VERSION: "3.8"}
      }),
      // overwrites defaults with user-provided configurable properties
      ...props.lambdaFunctionOptions,
      // Non configurable properties that are going to be overwritten even if provided by the user
      vpc: hasVpc(props.database) ? props.database.vpc : props.vpc,
    });

    this.secret = new aws_secretsmanager.Secret(this, "secret", {
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
          host: props.database.instanceEndpoint.hostname,
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
    this.secret.grantRead(handler);
    // read database secret
    props.dbSecret.grantRead(handler);
    // connect to database
    props.database.connections.allowFrom(handler, aws_ec2.Port.tcp(5432));

    let customResourceProperties : { [key: string]: any} = {};

    // if customResourceProperties are provided, fill in the values. 
    if (props.customResourceProperties) {
      Object.assign(customResourceProperties, props.customResourceProperties);
    }

    // update properties
    customResourceProperties["conn_secret_arn"] = props.dbSecret.secretArn;
    customResourceProperties["new_user_secret_arn"] = this.secret.secretArn;

    // if props.lambdaFunctionOptions doesn't have 'code' defined, update pgstac_version (needed for default runtime)
    if (!props.lambdaFunctionOptions?.code) {
      customResourceProperties["pgstac_version"] = DEFAULT_PGSTAC_VERSION;
    }
    // this.connections = props.database.connections;
    new CustomResource(this, "bootstrapper", {
      serviceToken: handler.functionArn,
      properties: customResourceProperties,
      removalPolicy: RemovalPolicy.RETAIN, // This retains the custom resource (which doesn't really exist), not the database
    });
  }
}

export interface BootstrapPgStacProps {
  /**
   * VPC in which the database resides.
   *
   * Note - Must be explicitely set if the `database` only conforms to the
   * `aws_rds.IDatabaseInstace` interface (ie it is a reference to a database instance
   * rather than a database instance.)
   *
   * @default - `vpc` property of the `database` instance provided.
   */
  readonly vpc?: aws_ec2.IVpc;

  /**
   * Database onto which pgSTAC should be installed.
   */
  readonly database: aws_rds.DatabaseInstance | aws_rds.IDatabaseInstance;

  /**
   * Secret containing valid connection details for the database instance. Secret must
   * conform to the format of CDK's `DatabaseInstance` (i.e. a JSON object containing a
   * `username`, `password`, `host`, `port`, and optionally a `dbname`). If a `dbname`
   * property is not specified within the secret, the bootstrapper will attempt to
   * connect to a database with the name of `"postgres"`.
   */
  readonly dbSecret: aws_secretsmanager.ISecret;

  /**
   * Name of database that is to be created and onto which pgSTAC will be installed.
   *
   * @default pgstac
   */
  readonly pgstacDbName?: string;

  /**
   * Name of user that will be generated for connecting to the pgSTAC database.
   *
   * @default pgstac_user
   */
  readonly pgstacUsername?: string;

  /**
   * Prefix to assign to the generated `secrets_manager.Secret`
   *
   * @default pgstac
   */
  readonly secretsPrefix?: string;

  /**
   * Optional settings for the lambda function. Can be anything that can be configured on the lambda function, but some will be overwritten by values defined here. 
   *
   * @default - defined in the construct.
   */
  readonly lambdaFunctionOptions?: CustomLambdaFunctionProps;

  /**
   * Lambda function Custom Resource properties. A custom resource property is going to be created
   * to trigger the boostrapping lambda function. This parameter allows the user to specify additional properties
   * on top of the defaults ones. 
   *
   */
  readonly customResourceProperties?: {
    [key: string]: any;
}

}
