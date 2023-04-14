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

function hasVpc(
  instance: aws_rds.DatabaseInstance | aws_rds.IDatabaseInstance
): instance is aws_rds.DatabaseInstance {
  return (instance as aws_rds.DatabaseInstance).vpc !== undefined;
}

const DEFAULT_PGSTAC_VERSION = "0.6.13";

/**
 * Bootstraps a database instance, installing pgSTAC onto the database.
 */
export class BootstrapPgStac extends Construct {
  secret: aws_secretsmanager.ISecret;

  constructor(scope: Construct, id: string, props: BootstrapPgStacProps) {
    super(scope, id);

    const { pgstacVersion = DEFAULT_PGSTAC_VERSION } = props;
    const handler = new aws_lambda.Function(this, "lambda", {
      handler: "handler.handler",
      runtime: aws_lambda.Runtime.PYTHON_3_8,
      code: aws_lambda.Code.fromDockerBuild(__dirname, {
        file: "runtime/Dockerfile",
        buildArgs: { PGSTAC_VERSION: pgstacVersion },
      }),
      timeout: Duration.minutes(2),
      vpc: hasVpc(props.database) ? props.database.vpc : props.vpc,
      logRetention: aws_logs.RetentionDays.ONE_WEEK,
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
        // By setting pgstac_version in the properties assures
        // that Create/Update events will be passed to the service token
        pgstac_version: pgstacVersion,
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
   * pgSTAC version to be installed.
   *
   * @default 0.6.8
   */
  readonly pgstacVersion?: string;

  /**
   * Prefix to assign to the generated `secrets_manager.Secret`
   *
   * @default pgstac
   */
  readonly secretsPrefix?: string;
}
