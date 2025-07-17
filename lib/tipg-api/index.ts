import {
  aws_apigatewayv2 as apigatewayv2,
  aws_ec2 as ec2,
  aws_lambda as lambda,
  aws_logs as logs,
  aws_rds as rds,
  aws_secretsmanager as secretsmanager,
  Duration,
} from "aws-cdk-lib";
import { Construct } from "constructs";
import { CustomLambdaFunctionProps, LambdaApiGateway } from "../utils";
import * as path from "path";

export class TiPgApiLambdaRuntime extends Construct {
  public readonly tiPgLambdaFunction: lambda.Function;

  constructor(scope: Construct, id: string, props: TiPgApiLambdaRuntimeProps) {
    super(scope, id);

    this.tiPgLambdaFunction = new lambda.Function(this, "lambda", {
      // defaults
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: "handler.handler",
      memorySize: 1024,
      logRetention: logs.RetentionDays.ONE_WEEK,
      timeout: Duration.seconds(30),
      code: lambda.Code.fromDockerBuild(path.join(__dirname, ".."), {
        file: "tipg-api/runtime/Dockerfile",
        buildArgs: { PYTHON_VERSION: "3.11" },
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
      // overwrites defaults with user-provided configurable properties
      ...props.lambdaFunctionOptions,
    });

    props.dbSecret.grantRead(this.tiPgLambdaFunction);

    if (props.vpc) {
      this.tiPgLambdaFunction.connections.allowTo(
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
   * Can be used to override the default lambda function properties.
   *
   * @default - defined in the construct.
   */
  readonly lambdaFunctionOptions?: CustomLambdaFunctionProps;
}

export class TiPgApiLambda extends Construct {
  readonly url: string;
  public tiPgLambdaFunction: lambda.Function;

  constructor(scope: Construct, id: string, props: TiPgApiLambdaProps) {
    super(scope, id);

    const runtime = new TiPgApiLambdaRuntime(this, "runtime", {
      vpc: props.vpc,
      subnetSelection: props.subnetSelection,
      db: props.db,
      dbSecret: props.dbSecret,
      apiEnv: props.apiEnv,
      lambdaFunctionOptions: props.lambdaFunctionOptions,
    });
    this.tiPgLambdaFunction = runtime.tiPgLambdaFunction;

    const api = new LambdaApiGateway(this, "api", {
      lambdaFunction: runtime.tiPgLambdaFunction,
      domainName: props.tipgApiDomainName,
      outputName: "tip-url",
    });

    this.url = api.url;
  }
}

export interface TiPgApiLambdaProps extends TiPgApiLambdaRuntimeProps {
  /**
   * Custom Domain Name for tipg API. If defined, will create the
   * domain name and integrate it with the tipg API.
   *
   * @default - undefined
   */
  readonly tipgApiDomainName?: apigatewayv2.IDomainName;
}
