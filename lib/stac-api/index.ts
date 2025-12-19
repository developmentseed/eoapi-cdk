import {
  aws_apigatewayv2 as apigatewayv2,
  aws_logs,
  CfnOutput,
  Duration,
  aws_ec2 as ec2,
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

export const EXTENSIONS = {
  QUERY: "query",
  SORT: "sort",
  FIELDS: "fields",
  FILTER: "filter",
  FREE_TEXT: "free_text",
  PAGINATION: "pagination",
  COLLECTION_SEARCH: "collection_search",
  TRANSACTION: "transaction",
  BULK_TRANSACTION: "bulk_transactions",
} as const;

type ExtensionType = (typeof EXTENSIONS)[keyof typeof EXTENSIONS];

/**
 * Validates if a given string is a valid STAC extension
 */
function isValidExtension(value: string): value is ExtensionType {
  return Object.values(EXTENSIONS).includes(value as any);
}

export class PgStacApiLambdaRuntime extends Construct {
  public readonly lambdaFunction: lambda.Function;

  constructor(
    scope: Construct,
    id: string,
    props: PgStacApiLambdaRuntimeProps,
  ) {
    super(scope, id);

    const defaultExtensions: ExtensionType[] = [
      EXTENSIONS.QUERY,
      EXTENSIONS.SORT,
      EXTENSIONS.FIELDS,
      EXTENSIONS.FILTER,
      EXTENSIONS.FREE_TEXT,
      EXTENSIONS.PAGINATION,
      EXTENSIONS.COLLECTION_SEARCH,
    ];

    if (props.enabledExtensions) {
      for (const ext of props.enabledExtensions) {
        if (!isValidExtension(ext)) {
          throw new Error(
            `Invalid extension: "${ext}". Must be one of: ${Object.values(
              EXTENSIONS,
            ).join(", ")}`,
          );
        }
      }
    }

    const enabledExtensions = props.enabledExtensions || defaultExtensions;

    const { code: userCode, ...otherLambdaOptions } =
      props.lambdaFunctionOptions || {};

    this.lambdaFunction = new lambda.Function(this, "lambda", {
      // defaults
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: "stac_api.handler.handler",
      memorySize: 8192,
      logRetention: aws_logs.RetentionDays.ONE_WEEK,
      timeout: Duration.seconds(30),
      code: resolveLambdaCode(userCode, path.join(__dirname, ".."), {
        file: "stac-api/runtime/Dockerfile",
        buildArgs: { PYTHON_VERSION: "3.12" },
      }),
      vpc: props.vpc,
      vpcSubnets: props.subnetSelection,
      allowPublicSubnet: true,
      environment: {
        PGSTAC_SECRET_ARN: props.dbSecret.secretArn,
        DB_MIN_CONN_SIZE: "0",
        DB_MAX_CONN_SIZE: "1",
        ENABLED_EXTENSIONS: enabledExtensions.join(","),
        ...props.apiEnv,
      },
      snapStart: props.enableSnapStart
        ? lambda.SnapStartConf.ON_PUBLISHED_VERSIONS
        : undefined,
      // overwrites defaults with user-provided configurable properties (excluding code)
      ...otherLambdaOptions,
    });

    props.dbSecret.grantRead(this.lambdaFunction);

    if (props.vpc) {
      this.lambdaFunction.connections.allowTo(
        props.db,
        ec2.Port.tcp(5432),
        "allow connections from stac-fastapi-pgstac",
      );
    }
  }
}

export interface PgStacApiLambdaRuntimeProps {
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
   * Customized environment variables to send to fastapi-pgstac runtime.
   */
  readonly apiEnv?: Record<string, string>;

  /**
   * List of STAC API extensions to enable.
   *
   * @default - query, sort, fields, filter, free_text, pagination, collection_search
   */
  readonly enabledExtensions?: ExtensionType[];

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

export class PgStacApiLambda extends Construct {
  /**
   * URL for the STAC API.
   */
  readonly url: string;

  /**
   * Lambda function for the STAC API.
   */
  readonly lambdaFunction: lambda.Function;

  /**
   * @deprecated - use lambdaFunction instead
   */
  public stacApiLambdaFunction: lambda.Function;

  constructor(scope: Construct, id: string, props: PgStacApiLambdaProps) {
    super(scope, id);

    const runtime = new PgStacApiLambdaRuntime(this, "runtime", {
      vpc: props.vpc,
      subnetSelection: props.subnetSelection,
      db: props.db,
      dbSecret: props.dbSecret,
      enabledExtensions: props.enabledExtensions,
      apiEnv: props.apiEnv,
      enableSnapStart: props.enableSnapStart,
      lambdaFunctionOptions: props.lambdaFunctionOptions,
    });
    this.stacApiLambdaFunction = this.lambdaFunction = runtime.lambdaFunction;

    // Determine which lambda to use for API Gateway
    let apiLambda: lambda.Function | lambda.Version;
    if (props.enableSnapStart) {
      // Extract dependencies from database if it's a PgStacDatabase with PgBouncer
      const dbDependencies = extractDatabaseDependencies(props.db);

      // Create version with dependencies to ensure snapshot creation waits
      apiLambda = createLambdaVersionWithDependencies(
        runtime.lambdaFunction,
        dbDependencies,
      );
    } else {
      apiLambda = runtime.lambdaFunction;
    }

    const { api } = new LambdaApiGateway(this, "stac-api", {
      lambdaFunction: apiLambda,
      domainName: props.domainName ?? props.stacApiDomainName,
    });

    this.url = api.url!;

    new CfnOutput(this, "stac-api-output", {
      exportName: `${Stack.of(this).stackName}-url`,
      value: this.url,
    });
  }
}

export interface PgStacApiLambdaProps extends PgStacApiLambdaRuntimeProps {
  /**
   * Domain Name for the STAC API. If defined, will create the domain name and integrate it with the STAC API.
   *
   * @default - undefined
   */
  readonly domainName?: apigatewayv2.IDomainName;

  /**
   * Custom Domain Name Options for STAC API.
   *
   * @deprecated Use 'domainName' instead.
   * @default - undefined.
   */
  readonly stacApiDomainName?: apigatewayv2.IDomainName;
}
