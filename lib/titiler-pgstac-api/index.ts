import {
  aws_apigatewayv2 as apigatewayv2,
  aws_iam as iam,
  aws_ec2 as ec2,
  aws_rds as rds,
  aws_lambda as lambda,
  aws_secretsmanager as secretsmanager,
  Duration,
  aws_logs,
} from "aws-cdk-lib";
import { Construct } from "constructs";
import { CustomLambdaFunctionProps } from "../utils";
import { LambdaApiGateway } from "../lambda-api-gateway";
import * as path from "path";

// default settings that can be overridden by the user-provided environment.
let defaultTitilerPgstacEnv: Record<string, string> = {
  CPL_VSIL_CURL_ALLOWED_EXTENSIONS: ".tif,.TIF,.tiff",
  GDAL_CACHEMAX: "200",
  GDAL_DISABLE_READDIR_ON_OPEN: "EMPTY_DIR",
  GDAL_INGESTED_BYTES_AT_OPEN: "32768",
  GDAL_HTTP_MERGE_CONSECUTIVE_RANGES: "YES",
  GDAL_HTTP_MULTIPLEX: "YES",
  GDAL_HTTP_VERSION: "2",
  PYTHONWARNINGS: "ignore",
  VSI_CACHE: "TRUE",
  VSI_CACHE_SIZE: "5000000",
  DB_MIN_CONN_SIZE: "1",
  DB_MAX_CONN_SIZE: "1",
};

export class TitilerPgstacApiLambdaRuntime extends Construct {
  public readonly titilerPgstacLambdaFunction: lambda.Function;

  constructor(
    scope: Construct,
    id: string,
    props: TitilerPgstacApiLambdaRuntimeProps
  ) {
    super(scope, id);

    this.titilerPgstacLambdaFunction = new lambda.Function(this, "lambda", {
      // defaults
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: "handler.handler",
      memorySize: 3008,
      logRetention: aws_logs.RetentionDays.ONE_WEEK,
      timeout: Duration.seconds(30),
      code: lambda.Code.fromDockerBuild(path.join(__dirname, ".."), {
        file: "titiler-pgstac-api/runtime/Dockerfile",
        buildArgs: { PYTHON_VERSION: "3.11" },
      }),
      vpc: props.vpc,
      vpcSubnets: props.subnetSelection,
      allowPublicSubnet: true,
      environment: {
        ...defaultTitilerPgstacEnv,
        ...props.apiEnv, // if user provided environment variables, merge them with the defaults.
        PGSTAC_SECRET_ARN: props.dbSecret.secretArn,
      },
      // overwrites defaults with user-provided configurable properties
      ...props.lambdaFunctionOptions,
    });

    // grant access to buckets using addToRolePolicy
    if (props.buckets) {
      props.buckets.forEach((bucket) => {
        this.titilerPgstacLambdaFunction.addToRolePolicy(
          new iam.PolicyStatement({
            actions: ["s3:GetObject"],
            resources: [`arn:aws:s3:::${bucket}/*`],
          })
        );
      });
    }

    props.dbSecret.grantRead(this.titilerPgstacLambdaFunction);

    if (props.vpc) {
      this.titilerPgstacLambdaFunction.connections.allowTo(
        props.db,
        ec2.Port.tcp(5432),
        "allow connections from titiler"
      );
    }
  }
}

export interface TitilerPgstacApiLambdaRuntimeProps {
  /**
   * VPC into which the lambda should be deployed.
   */
  readonly vpc?: ec2.IVpc;

  /**
   * RDS Instance with installed pgSTAC or pgbouncer server.
   */
  readonly db: rds.IDatabaseInstance | ec2.IInstance;

  /**
   * Subnet into which the lambda should be deployed.
   */
  readonly subnetSelection?: ec2.SubnetSelection;

  /**
   * Secret containing connection information for pgSTAC database.
   */
  readonly dbSecret: secretsmanager.ISecret;

  /**
   * Customized environment variables to send to titiler-pgstac runtime. These will be merged with `defaultTitilerPgstacEnv`.
   * The database secret arn is automatically added to the environment variables at deployment.
   */
  readonly apiEnv?: Record<string, string>;

  /**
   * list of buckets the lambda will be granted access to.
   */
  readonly buckets?: string[];

  /**
   * Can be used to override the default lambda function properties.
   *
   * @default - defined in the construct.
   */
  readonly lambdaFunctionOptions?: CustomLambdaFunctionProps;
}

export class TitilerPgstacApiLambda extends Construct {
  readonly url: string;
  public titilerPgstacLambdaFunction: lambda.Function;

  constructor(
    scope: Construct,
    id: string,
    props: TitilerPgstacApiLambdaProps
  ) {
    super(scope, id);

    const runtime = new TitilerPgstacApiLambdaRuntime(this, "runtime", {
      vpc: props.vpc,
      subnetSelection: props.subnetSelection,
      db: props.db,
      dbSecret: props.dbSecret,
      apiEnv: props.apiEnv,
      buckets: props.buckets,
      lambdaFunctionOptions: props.lambdaFunctionOptions,
    });
    this.titilerPgstacLambdaFunction = runtime.titilerPgstacLambdaFunction;

    const api = new LambdaApiGateway(this, "titlier-pgstac-api", {
      lambdaFunction: runtime.titilerPgstacLambdaFunction,
      domainName: props.titilerPgstacApiDomainName,
      outputName: "titiler-pgstac-url",
    });

    this.url = api.url;
  }
}

export interface TitilerPgstacApiLambdaProps
  extends TitilerPgstacApiLambdaRuntimeProps {
  /**
   * Custom Domain Name Options for Titiler Pgstac API,
   *
   * @default - undefined.
   */
  readonly titilerPgstacApiDomainName?: apigatewayv2.IDomainName;
}
