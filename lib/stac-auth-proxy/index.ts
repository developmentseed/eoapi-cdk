import * as cdk from "aws-cdk-lib";
import * as ec2 from "aws-cdk-lib/aws-ec2";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as apigatewayv2 from "aws-cdk-lib/aws-apigatewayv2";
import { Construct } from "constructs";
import { LambdaApiGateway } from "../lambda-api-gateway";
import { CustomLambdaFunctionProps } from "../utils";
import * as path from "path";

export class StacAuthProxyLambdaRuntime extends Construct {
  public readonly lambdaFunction: lambda.Function;

  constructor(
    scope: Construct,
    id: string,
    props: StacAuthProxyLambdaRuntimeProps
  ) {
    super(scope, id);

    this.lambdaFunction = new lambda.Function(this, "lambda", {
      runtime: lambda.Runtime.PYTHON_3_13,
      handler: "handler.handler",
      memorySize: 8192,
      logRetention: cdk.aws_logs.RetentionDays.ONE_WEEK,
      timeout: cdk.Duration.seconds(30),
      code: lambda.Code.fromDockerBuild(path.join(__dirname, ".."), {
        file: "stac-auth-proxy/runtime/Dockerfile",
        buildArgs: { PYTHON_VERSION: "3.13" },
      }),
      vpc: props.vpc,
      vpcSubnets: props.subnetSelection,
      allowPublicSubnet: true,
      environment: {
        // stac-auth-proxy config
        UPSTREAM_URL: props.upstreamUrl,
        OIDC_DISCOVERY_URL: props.oidcDiscoveryUrl,

        // swagger-ui config
        OPENAPI_SPEC_ENDPOINT: "/api",
        SWAGGER_UI_ENDPOINT: "/api.html",
        SWAGGER_UI_INIT_OAUTH:
          props.stacApiClientId &&
          cdk.Stack.of(this).toJsonString({
            clientId: props.stacApiClientId,
            usePkceWithAuthorizationCodeGrant: true,
          }),

        // customized settings
        ...props.apiEnv,
      },
      // overwrites defaults with user-provided configurable properties
      ...props.lambdaFunctionOptions,
    });
  }
}

export interface StacAuthProxyLambdaRuntimeProps {
  /**
   * URL to upstream STAC API.
   */
  readonly upstreamUrl: string;

  /**
   * URL to OIDC Discovery Endpoint.
   */
  readonly oidcDiscoveryUrl: string;

  /**
   * OAuth Client ID for Swagger UI.
   */
  readonly stacApiClientId?: string;

  /**
   * VPC into which the lambda should be deployed.
   */
  readonly vpc?: ec2.IVpc;

  /**
   * Subnet into which the lambda should be deployed.
   */
  readonly subnetSelection?: ec2.SubnetSelection;

  /**
   * Customized environment variables to send to stac-auth-proxy runtime.
   * https://github.com/developmentseed/stac-auth-proxy/?tab=readme-ov-file#configuration
   */
  readonly apiEnv?: Record<string, string>;

  /**
   * Can be used to override the default lambda function properties.
   *
   * @default - defined in the construct.
   */
  readonly lambdaFunctionOptions?: CustomLambdaFunctionProps;
}

export class StacAuthProxyLambda extends Construct {
  /**
   * URL for the STAC API.
   */
  readonly url: string;

  /**
   * Lambda function for the STAC API.
   */
  readonly lambdaFunction: lambda.Function;

  constructor(scope: Construct, id: string, props: StacAuthProxyLambdaProps) {
    super(scope, id);

    const runtime = new StacAuthProxyLambdaRuntime(this, "runtime", {
      vpc: props.vpc,
      subnetSelection: props.subnetSelection,
      apiEnv: props.apiEnv,
      upstreamUrl: props.upstreamUrl,
      oidcDiscoveryUrl: props.oidcDiscoveryUrl,
      lambdaFunctionOptions: props.lambdaFunctionOptions,
    });
    this.lambdaFunction = runtime.lambdaFunction;

    const { api } = new LambdaApiGateway(this, "stac-auth-proxy", {
      lambdaFunction: runtime.lambdaFunction,
      domainName: props.domainName,
    });

    this.url = api.url!;

    new cdk.CfnOutput(this, "stac-auth-proxy-output", {
      exportName: `${cdk.Stack.of(this).stackName}-stac-auth-proxy-url`,
      value: this.url,
    });
  }
}

export interface StacAuthProxyLambdaProps
  extends StacAuthProxyLambdaRuntimeProps {
  /**
   * Domain Name for the STAC API. If defined, will create the domain name and integrate it with the STAC API.
   *
   * @default - undefined
   */
  readonly domainName?: apigatewayv2.IDomainName;
}
