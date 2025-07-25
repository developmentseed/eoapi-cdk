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
  readonly lambdaFunction: lambda.IFunction;

  /**
   * Lambda integration options for the API Gateway.
   */
  readonly lambdaIntegrationOptions?: apigateway.LambdaIntegrationOptions;

  /**
   * VPC to create the API Gateway in.
   */
  readonly vpc: ec2.IVpc;

  /**
   * Whether to create a VPC endpoint for the API Gateway.
   *
   * @default - true
   */
  readonly createVpcEndpoint?: boolean;

  /**
   * The subnets in which to create a VPC endpoint network interface. At most one per availability zone.

   */
  readonly vpcEndpointSubnetSelection?: ec2.SubnetSelection;

  /**
   * Name for the API Gateway.
   *
   * @default - `${scope.node.id}-private-api`
   */
  readonly restApiName?: string;

  /**
   * Description for the API Gateway.
   *
   * @default - "Private REST API Gateway"
   */
  readonly description?: string;

  /**
   * Deploy options for the API Gateway.
   */
  readonly deployOptions?: apigateway.StageOptions;

  /**
   * Policy for the API Gateway.
   *
   * @default - Policy that allows any principal with the same VPC to invoke the API.
   */
  readonly policy?: iam.PolicyDocument;
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
      restApiName,
      description,
      lambdaFunction,
      vpc,
      vpcEndpointSubnetSelection,
      createVpcEndpoint = true,
      deployOptions,
      policy,
      lambdaIntegrationOptions,
    } = props;

    if (createVpcEndpoint) {
      // Create VPC Endpoint for API Gateway
      this.vpcEndpoint = new ec2.InterfaceVpcEndpoint(this, "vpc-endpoint", {
        vpc,
        service: ec2.InterfaceVpcEndpointAwsService.APIGATEWAY,
        subnets: vpcEndpointSubnetSelection,
      });
    }

    const defaultIntegration = new apigateway.LambdaIntegration(
      lambdaFunction,
      lambdaIntegrationOptions
    );

    // Create Private REST API Gateway
    this.api = new apigateway.RestApi(this, "rest-api", {
      restApiName: restApiName ?? `${scope.node.id}-private-api`,
      description: description ?? "Private REST API Gateway",
      endpointTypes: [apigateway.EndpointType.PRIVATE],
      policy:
        policy ??
        new iam.PolicyDocument({
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
