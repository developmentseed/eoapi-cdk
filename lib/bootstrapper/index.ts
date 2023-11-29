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
  
  const DEFAULT_PGSTAC_VERSION = "0.7.10";
  
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
  export class PgStacDatabaseBootstrapper extends Construct {
    pgstacSecret: secretsmanager.ISecret;
  
    constructor(scope: Construct, id: string, props: PgStacDatabaseBootstrapperProps) {
      super(scope, id);
  
      

      const handler = new aws_lambda.Function(this, "lambda", {
        // defaults for configurable properties
        runtime: aws_lambda.Runtime.PYTHON_3_11,
        handler: "handler.handler",
        memorySize: 128,
        logRetention: aws_logs.RetentionDays.ONE_WEEK,
        timeout: Duration.minutes(2),
        code: aws_lambda.Code.fromDockerBuild(__dirname, {
          file: "bootstrapper_runtime/Dockerfile",
          buildArgs: {PGSTAC_VERSION: DEFAULT_PGSTAC_VERSION, PYTHON_VERSION: "3.11"}
        }),
        // overwrites defaults with user-provided configurable properties
        ...props.bootstrapperLambdaFunctionOptions,
        // Non configurable properties that are going to be overwritten even if provided by the user
        vpc: hasVpc(props.db) ? props.db.vpc : props.vpc,
        allowPublicSubnet: true
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
            host: props.db.instanceEndpoint.hostname,
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
      props.db.secret!.grantRead(handler);
      // connect to database
      props.db.connections.allowFrom(handler, ec2.Port.tcp(5432));
  
      let customResourceProperties : { [key: string]: any} = {};
  
      // if customResourceProperties are provided, fill in the values. 
      if (props.customResourceProperties) {
        Object.assign(customResourceProperties, props.customResourceProperties);
      }
  
      // update properties
      customResourceProperties["conn_secret_arn"] = props.db.secret!.secretArn;
      customResourceProperties["new_user_secret_arn"] = this.pgstacSecret.secretArn;
  
      // if props.lambdaFunctionOptions doesn't have 'code' defined, update pgstac_version (needed for default runtime)
      if (!props.bootstrapperLambdaFunctionOptions?.code) {
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
  
  export interface PgStacDatabaseBootstrapperProps extends rds.DatabaseInstanceProps {

    /**
     * RDS instance to install pgSTAC on.
     */
    readonly db: rds.DatabaseInstance;
  

    /**
     * Name of database that is to be created and onto which pgSTAC will be installed.
     *
     * @default pgstac
     */
    readonly pgstacDbName?: string;

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
     * Lambda function Custom Resource properties. A custom resource property is going to be created
     * to trigger the boostrapping lambda function. This parameter allows the user to specify additional properties
     * on top of the defaults ones. 
     *
     */
    readonly customResourceProperties?: {
      [key: string]: any;
  }
  
    /**
     * Optional settings for the bootstrapper lambda function. Can be anything that can be configured on the lambda function, but some will be overwritten by values defined here. 
     *
     * @default - defined in the construct.
     */
    readonly bootstrapperLambdaFunctionOptions?: CustomLambdaFunctionProps;
  }