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
import { CustomLambdaFunctionOptions } from "../utils";

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
      ...props.lambdaFunctionOptions ?? {
        runtime: aws_lambda.Runtime.PYTHON_3_8,
        handler: "handler.handler",
        memorySize: 128,
        logRetention: aws_logs.RetentionDays.ONE_WEEK,
        timeout: Duration.minutes(2)
      },
      code: props.lambdaAssetCode ?? aws_lambda.Code.fromDockerBuild(__dirname, {
        file: "runtime/Dockerfile",
      }),
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

    // this.connections = props.database.connections;
    new CustomResource(this, "bootstrapper", {
      serviceToken: handler.functionArn,
      properties: {
        conn_secret_arn: props.dbSecret.secretArn,
        new_user_secret_arn: this.secret.secretArn,
      },
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
   * Optional settings for the lambda function.
   *
   * @default - defined in the construct.
   */
  readonly lambdaFunctionOptions?: CustomLambdaFunctionOptions;

  /**
   * Optional lambda asset code
   * @default default runtime defined in this repository
   */
  readonly lambdaAssetCode?: aws_lambda.AssetCode;
}
