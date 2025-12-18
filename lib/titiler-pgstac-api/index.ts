import {
  aws_apigatewayv2 as apigatewayv2,
  aws_logs,
  CfnOutput,
  Duration,
  aws_ec2 as ec2,
  aws_iam as iam,
  aws_lambda as lambda,
  aws_rds as rds,
  aws_secretsmanager as secretsmanager,
  Stack,
} from "aws-cdk-lib";
import { Construct } from "constructs";
import * as path from "path";
import { LambdaApiGateway } from "../lambda-api-gateway";
import {
  CustomLambdaFunctionProps,
  resolveLambdaCode,
  extractDatabaseDependencies,
  createLambdaVersionWithDependencies,
} from "../utils";

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
  public readonly lambdaFunction: lambda.Function;

  constructor(
    scope: Construct,
    id: string,
    props: TitilerPgstacApiLambdaRuntimeProps,
  ) {
    super(scope, id);

    const { code: userCode, ...otherLambdaOptions } =
      props.lambdaFunctionOptions || {};

    this.lambdaFunction = new lambda.Function(this, "lambda", {
      // defaults
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: "titiler_pgstac_api.handler.handler",
      memorySize: 3008,
      logRetention: aws_logs.RetentionDays.ONE_WEEK,
      timeout: Duration.seconds(30),
      code: resolveLambdaCode(userCode, path.join(__dirname, ".."), {
        file: "titiler-pgstac-api/runtime/Dockerfile",
        buildArgs: { PYTHON_VERSION: "3.12" },
      }),
      vpc: props.vpc,
      vpcSubnets: props.subnetSelection,
      allowPublicSubnet: true,
      environment: {
        ...defaultTitilerPgstacEnv,
        ...props.apiEnv, // if user provided environment variables, merge them with the defaults.
        PGSTAC_SECRET_ARN: props.dbSecret.secretArn,
      },
      snapStart: props.enableSnapStart
        ? lambda.SnapStartConf.ON_PUBLISHED_VERSIONS
        : undefined,
      // overwrites defaults with user-provided configurable properties (excluding code)
      ...otherLambdaOptions,
    });

    // grant access to buckets using addToRolePolicy
    if (props.buckets) {
      props.buckets.forEach((bucket) => {
        this.lambdaFunction.addToRolePolicy(
          new iam.PolicyStatement({
            actions: ["s3:GetObject"],
            resources: [`arn:aws:s3:::${bucket}/*`],
          }),
        );
      });
    }

    props.dbSecret.grantRead(this.lambdaFunction);

    if (props.vpc) {
      this.lambdaFunction.connections.allowTo(
        props.db,
        ec2.Port.tcp(5432),
        "allow connections from titiler",
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
   * Enable SnapStart to reduce cold start latency.
   *
   * SnapStart creates a snapshot of the initialized Lambda function, allowing new instances
   * to start from this pre-initialized state instead of starting from scratch.
   *
   * Benefits:
   * - Significantly reduces cold start times (typically 10x faster)
   * - Improves API response time for infrequent requests
   *
   * Considerations:
   * - Additional cost: charges for snapshot storage and restore operations
   * - Requires Lambda versioning (automatically configured by this construct)
   * - Database connections are recreated on restore using snapshot lifecycle hooks
   *
   * @see https://docs.aws.amazon.com/lambda/latest/dg/snapstart.html
   * @default false
   */
  readonly enableSnapStart?: boolean;

  /**
   * Can be used to override the default lambda function properties.
   *
   * @default - defined in the construct.
   */
  readonly lambdaFunctionOptions?: CustomLambdaFunctionProps;
}

export class TitilerPgstacApiLambda extends Construct {
  /**
   * URL for the Titiler Pgstac API.
   */
  readonly url: string;

  /**
   * Lambda function for the Titiler Pgstac API.
   */
  readonly lambdaFunction: lambda.Function;

  /**
   * @deprecated - use lambdaFunction instead
   */
  public titilerPgstacLambdaFunction: lambda.Function;

  constructor(
    scope: Construct,
    id: string,
    props: TitilerPgstacApiLambdaProps,
  ) {
    super(scope, id);

    const runtime = new TitilerPgstacApiLambdaRuntime(this, "runtime", {
      vpc: props.vpc,
      subnetSelection: props.subnetSelection,
      db: props.db,
      dbSecret: props.dbSecret,
      apiEnv: props.apiEnv,
      buckets: props.buckets,
      enableSnapStart: props.enableSnapStart,
      lambdaFunctionOptions: props.lambdaFunctionOptions,
    });
    this.titilerPgstacLambdaFunction = this.lambdaFunction =
      runtime.lambdaFunction;

    // Determine which lambda to use for API Gateway
    let apiLambda: lambda.Function | lambda.Version;
    if (props.enableSnapStart) {
      // Extract dependencies from database if it's a PgStacDatabase with PgBouncer
      const dbDependencies = extractDatabaseDependencies(props.db);

      // Create version with dependencies to ensure snapshot creation waits
      apiLambda = createLambdaVersionWithDependencies(
        this,
        "lambda-version",
        runtime.lambdaFunction,
        dbDependencies
      );
    } else {
      apiLambda = runtime.lambdaFunction;
    }

    const { api } = new LambdaApiGateway(this, "titlier-pgstac-api", {
      lambdaFunction: apiLambda,
      domainName: props.domainName ?? props.titilerPgstacApiDomainName,
    });

    this.url = api.url!;

    new CfnOutput(this, "titiler-pgstac-api-output", {
      exportName: `${Stack.of(this).stackName}-titiler-pgstac-url`,
      value: this.url,
    });
  }
}

export interface TitilerPgstacApiLambdaProps
  extends TitilerPgstacApiLambdaRuntimeProps {
  /**
   * Domain Name for the Titiler Pgstac API. If defined, will create the domain name and integrate it with the Titiler Pgstac API.
   *
   * @default - undefined.
   */
  readonly domainName?: apigatewayv2.IDomainName;

  /**
   * Custom Domain Name Options for Titiler Pgstac API,
   *
   * @deprecated Use 'domainName' instead.
   * @default - undefined.
   */
  readonly titilerPgstacApiDomainName?: apigatewayv2.IDomainName;
}
