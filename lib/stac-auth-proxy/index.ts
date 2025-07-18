import * as cdk from "aws-cdk-lib";
import * as certificatemanager from "aws-cdk-lib/aws-certificatemanager";
import * as ec2 from "aws-cdk-lib/aws-ec2";
import * as ecs from "aws-cdk-lib/aws-ecs";
import * as ecs_patterns from "aws-cdk-lib/aws-ecs-patterns";
import * as elbv2 from "aws-cdk-lib/aws-elasticloadbalancingv2";
import { Construct } from "constructs";

export interface StacAuthProxyProps {
  vpc: ec2.IVpc;
  upstreamUrl: string;
  oidcDiscoveryUrl: string;
  stacApiClientId: string;
  subnetSelection: ec2.SubnetSelection;
  certificateArn?: string;
}

export class StacAuthProxy extends Construct {
  public readonly service: ecs_patterns.ApplicationLoadBalancedFargateService;

  constructor(scope: Construct, id: string, props: StacAuthProxyProps) {
    super(scope, id);

    const taskOptions: ecs_patterns.ApplicationLoadBalancedTaskImageOptions = {
      image: ecs.ContainerImage.fromRegistry(
        "ghcr.io/developmentseed/stac-auth-proxy:0.5.0"
      ),
      containerPort: 8000,
      environment: {
        // stac-auth-proxy config
        UPSTREAM_URL: props.upstreamUrl,
        OIDC_DISCOVERY_URL: props.oidcDiscoveryUrl,
        DEFAULT_PUBLIC: "false",
        OPENAPI_SPEC_ENDPOINT: "/api",
        // swagger-ui config
        SWAGGER_UI_ENDPOINT: "/api.html",
        SWAGGER_UI_INIT_OAUTH: JSON.stringify({
          clientId: props.stacApiClientId,
          usePkceWithAuthorizationCodeGrant: true,
        }),
      },
    };

    const albCertificate = props.certificateArn
      ? certificatemanager.Certificate.fromCertificateArn(
          this,
          "cert",
          props.certificateArn
        )
      : undefined;

    this.service = new ecs_patterns.ApplicationLoadBalancedFargateService(
      this,
      "service",
      {
        vpc: props.vpc,
        desiredCount: 1,
        taskImageOptions: taskOptions,
        minHealthyPercent: 100,
        taskSubnets: props.subnetSelection,
        assignPublicIp: true,
        healthCheckGracePeriod: cdk.Duration.seconds(60),
        protocol: elbv2.ApplicationProtocol.HTTPS,
        targetProtocol: elbv2.ApplicationProtocol.HTTP,
        circuitBreaker: { rollback: true },
        certificate: albCertificate,
        redirectHTTP: true,
      }
    );

    this.service.targetGroup.configureHealthCheck({
      path: "/healthz",
    });
  }
}
