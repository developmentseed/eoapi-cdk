import {
  Stack,
  CfnOutput,
  aws_apigatewayv2 as apigatewayv2,
  aws_apigatewayv2_integrations as apigatewayv2_integrations,
  aws_lambda as lambda,
} from "aws-cdk-lib";
import { Construct } from "constructs";

export interface LambdaApiGatewayProps {
  /**
   * Lambda function to integrate with the API Gateway.
   */
  readonly lambdaFunction: lambda.Function;

  /**
   * Custom Domain Name for the API. If defined, will create the
   * domain name and integrate it with the API.
   *
   * @default - undefined
   */
  readonly domainName?: apigatewayv2.IDomainName;

  /**
   * Name for the CfnOutput export.
   */
  readonly outputName: string;

  /**
   * Name of the API Gateway.
   */
  readonly apiName?: string;
}

export class LambdaApiGateway extends Construct {
  readonly url: string;

  constructor(scope: Construct, id: string, props: LambdaApiGatewayProps) {
    super(scope, id);

    const defaultDomainMapping = props.domainName
      ? { domainName: props.domainName }
      : undefined;

    const defaultIntegration =
      new apigatewayv2_integrations.HttpLambdaIntegration(
        "integration",
        props.lambdaFunction,
        props.domainName
          ? {
              parameterMapping:
                new apigatewayv2.ParameterMapping().overwriteHeader(
                  "host",
                  apigatewayv2.MappingValue.custom(props.domainName.name)
                ),
            }
          : undefined
      );

    const api = new apigatewayv2.HttpApi(this, "api", {
      apiName: props.apiName || `${Stack.of(this).stackName}-${id}`,
      defaultDomainMapping,
      defaultIntegration: defaultIntegration,
    });

    this.url = api.url!;

    new CfnOutput(this, "output", {
      exportName: `${Stack.of(this).stackName}-${props.outputName}`,
      value: this.url,
    });
  }
}
