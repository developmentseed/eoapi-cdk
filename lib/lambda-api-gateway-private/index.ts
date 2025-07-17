import {
  aws_apigateway as apigateway,
  aws_ec2 as ec2,
  aws_iam as iam,
  aws_lambda as lambda,
} from "aws-cdk-lib";
import { Construct } from "constructs";

export interface PrivateLambdaApiGatewayProps {
  /**
   * Lambda function to integrate with the API Gateway.
   */
  lambdaFunction: lambda.IFunction;

  /**
   * Lambda integration options for the API Gateway.
   */
  lambdaIntegrationOptions?: apigateway.LambdaIntegrationOptions;

  /**
   * VPC to create the API Gateway in.
   */
  vpc: ec2.IVpc;

  /**
   * Subnet selection for the API Gateway.
   */
  subnetSelection: ec2.SubnetSelection;

  /**
   * Whether to create a VPC endpoint for the API Gateway.
   *
   * @default - true
   */
  createVpcEndpoint?: boolean;

  /**
   * Deploy options for the API Gateway.
   */
  deployOptions?: apigateway.StageOptions;
}

export class PrivateLambdaApiGateway extends Construct {
  public readonly api: apigateway.RestApi;
  public readonly vpcEndpoint?: ec2.InterfaceVpcEndpoint;

  constructor(
    scope: Construct,
    id: string,
    props: PrivateLambdaApiGatewayProps
  ) {
    super(scope, id);

    const {
      lambdaFunction,
      vpc,
      subnetSelection,
      createVpcEndpoint = true,
      deployOptions,
      lambdaIntegrationOptions,
    } = props;

    if (createVpcEndpoint) {
      // Create VPC Endpoint for API Gateway
      this.vpcEndpoint = new ec2.InterfaceVpcEndpoint(this, "vpc-endpoint", {
        vpc,
        service: ec2.InterfaceVpcEndpointAwsService.APIGATEWAY,
        subnets: subnetSelection,
      });
    }

    const defaultIntegration = new apigateway.LambdaIntegration(
      lambdaFunction,
      lambdaIntegrationOptions
    );

    // Create Private REST API Gateway
    this.api = new apigateway.RestApi(this, "rest-api", {
      restApiName: `${scope.node.id}-private-api`,
      description: "Private REST API Gateway for STAC API",
      endpointTypes: [apigateway.EndpointType.PRIVATE],
      policy: new iam.PolicyDocument({
        statements: [
          new iam.PolicyStatement({
            effect: iam.Effect.ALLOW,
            principals: [new iam.AnyPrincipal()],
            actions: ["execute-api:Invoke"],
            resources: ["execute-api:/*"],
            conditions: {
              StringEquals: { "aws:SourceVpc": vpc.vpcId },
            },
          }),
        ],
      }),
      deployOptions: deployOptions ?? {
        loggingLevel: apigateway.MethodLoggingLevel.INFO,
        dataTraceEnabled: true,
      },
      defaultIntegration,
      defaultMethodOptions: {
        authorizationType: apigateway.AuthorizationType.NONE,
      },
    });

    this.api.root.addMethod("ANY");
    this.api.root.addResource("{proxy+}").addMethod("ANY");
  }
}
