import {
  aws_apigatewayv2 as apigatewayv2,
  CfnOutput,
  Duration,
  aws_ec2 as ec2,
  aws_lambda as lambda,
  aws_logs as logs,
  aws_rds as rds,
  aws_secretsmanager as secretsmanager,
  Stack,
} from "aws-cdk-lib";
import { Construct } from "constructs";
import * as path from "path";
import { LambdaApiGateway } from "../lambda-api-gateway";
import { CustomLambdaFunctionProps, resolveLambdaCode } from "../utils";

export class TiPgApiLambdaRuntime extends Construct {
  public readonly lambdaFunction: lambda.Function;

  constructor(scope: Construct, id: string, props: TiPgApiLambdaRuntimeProps) {
    super(scope, id);

    const { code: userCode, ...otherLambdaOptions } =
      props.lambdaFunctionOptions || {};

    this.lambdaFunction = new lambda.Function(this, "lambda", {
      // defaults
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: "handler.handler",
      memorySize: 1024,
      logRetention: logs.RetentionDays.ONE_WEEK,
      timeout: Duration.seconds(30),
      code: resolveLambdaCode(userCode, path.join(__dirname, ".."), {
        file: "tipg-api/runtime/Dockerfile",
        buildArgs: { PYTHON_VERSION: "3.12" },
      }),
      vpc: props.vpc,
      vpcSubnets: props.subnetSelection,
      allowPublicSubnet: true,
      environment: {
        PGSTAC_SECRET_ARN: props.dbSecret.secretArn,
        DB_MIN_CONN_SIZE: "1",
        DB_MAX_CONN_SIZE: "1",
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
        "allow connections from tipg"
      );
    }
  }
}

export interface TiPgApiLambdaRuntimeProps {
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
   * Customized environment variables to send to titiler-pgstac runtime.
   */
  readonly apiEnv?: Record<string, string>;

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

export class TiPgApiLambda extends Construct {
  /**
   * URL for the TiPg API.
   */
  readonly url: string;

  /**
   * Lambda function for the TiPg API.
   */
  readonly lambdaFunction: lambda.Function;

  /**
   * @deprecated - use lambdaFunction instead
   */
  public tiPgLambdaFunction: lambda.Function;

  constructor(scope: Construct, id: string, props: TiPgApiLambdaProps) {
    super(scope, id);

    const runtime = new TiPgApiLambdaRuntime(this, "runtime", {
      vpc: props.vpc,
      subnetSelection: props.subnetSelection,
      db: props.db,
      dbSecret: props.dbSecret,
      apiEnv: props.apiEnv,
      enableSnapStart: props.enableSnapStart,
      lambdaFunctionOptions: props.lambdaFunctionOptions,
    });
    this.tiPgLambdaFunction = this.lambdaFunction = runtime.lambdaFunction;

    const { api } = new LambdaApiGateway(this, "api", {
      lambdaFunction: props.enableSnapStart!
        ? runtime.lambdaFunction.currentVersion
        : runtime.lambdaFunction,
      domainName: props.domainName ?? props.tipgApiDomainName,
    });

    this.url = api.url!;

    new CfnOutput(this, "tipg-api-output", {
      exportName: `${Stack.of(this).stackName}-tip-url`,
      value: this.url,
    });
  }
}

export interface TiPgApiLambdaProps extends TiPgApiLambdaRuntimeProps {
  /**
   * Domain Name for the TiPg API. If defined, will create the domain name and integrate it with the TiPg API.
   *
   * @default - undefined
   */
  readonly domainName?: apigatewayv2.IDomainName;

  /**
   * Custom Domain Name for tipg API. If defined, will create the
   * domain name and integrate it with the tipg API.
   *
   * @deprecated Use 'domainName' instead.
   * @default - undefined
   */
  readonly tipgApiDomainName?: apigatewayv2.IDomainName;
}
