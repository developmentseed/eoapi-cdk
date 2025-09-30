import {
  Stack,
  aws_apigatewayv2 as apigatewayv2,
  aws_apigatewayv2_integrations as apigatewayv2_integrations,
  aws_lambda as lambda,
} from "aws-cdk-lib";
import { Construct } from "constructs";

export interface LambdaApiGatewayProps {
  /**
   * Lambda function to integrate with the API Gateway.
   */
  readonly lambdaFunction: lambda.Function | lambda.Version;

  /**
   * Custom Domain Name for the API. If defined, will create the
   * domain name and integrate it with the API.
   *
   * @default - undefined
   */
  readonly domainName?: apigatewayv2.IDomainName;

  /**
   * Name of the API Gateway.
   */
  readonly apiName?: string;
}

export class LambdaApiGateway extends Construct {
  readonly api: apigatewayv2.HttpApi;

  constructor(scope: Construct, id: string, props: LambdaApiGatewayProps) {
    super(scope, id);

    const {
      apiName = `${Stack.of(this).stackName}-${id}`,
      domainName,
      lambdaFunction,
    } = props;

    const defaultDomainMapping = domainName ? { domainName } : undefined;

    const defaultIntegration =
      new apigatewayv2_integrations.HttpLambdaIntegration(
        "integration",
        lambdaFunction,
        domainName
          ? {
              parameterMapping:
                new apigatewayv2.ParameterMapping().overwriteHeader(
                  "host",
                  apigatewayv2.MappingValue.custom(domainName.name)
                ),
            }
          : undefined
      );

    this.api = new apigatewayv2.HttpApi(this, "api", {
      apiName,
      defaultDomainMapping,
      defaultIntegration: defaultIntegration,
    });
  }
}
