import {
  Stack,
  aws_ec2 as ec2,
  aws_rds as rds,
  aws_lambda as lambda,
  aws_secretsmanager as secretsmanager,
  CfnOutput,
  Duration,
  aws_logs,
} from "aws-cdk-lib";
import { IDomainName, HttpApi } from "@aws-cdk/aws-apigatewayv2-alpha";
import { HttpLambdaIntegration } from "@aws-cdk/aws-apigatewayv2-integrations-alpha";
import { Construct } from "constructs";
import { CustomLambdaFunctionOptions } from "../utils";

export class PgStacApiLambda extends Construct {
  readonly url: string;
  public stacApiLambdaFunction: lambda.Function;

  constructor(scope: Construct, id: string, props: PgStacApiLambdaProps) {
    super(scope, id);
    
    this.stacApiLambdaFunction = new lambda.Function(this, "lambda", {
      ...props.lambdaFunctionOptions ?? {
        runtime: lambda.Runtime.PYTHON_3_10,
        handler: "src.handler.handler",
        memorySize: 8192,
        logRetention: aws_logs.RetentionDays.ONE_WEEK,
        timeout: Duration.seconds(30)
      },
      code: props.lambdaAssetCode ?? lambda.Code.fromDockerBuild(__dirname, {
        file: "runtime/Dockerfile",
        buildArgs: { PYTHON_VERSION: '3.10' },
      }),
      vpc: props.vpc,
      vpcSubnets: props.subnetSelection,
      allowPublicSubnet: true,
      environment: {
        PGSTAC_SECRET_ARN: props.dbSecret.secretArn,
        DB_MIN_CONN_SIZE: "0",
        DB_MAX_CONN_SIZE: "1",
        ...props.apiEnv,
      },
    });

    props.dbSecret.grantRead(this.stacApiLambdaFunction);
    this.stacApiLambdaFunction.connections.allowTo(props.db, ec2.Port.tcp(5432));

    const stacApi = new HttpApi(this, `${Stack.of(this).stackName}-stac-api`, {
      defaultDomainMapping: props.stacApiDomainName ? { 
        domainName: props.stacApiDomainName
      } : undefined,
      defaultIntegration: new HttpLambdaIntegration("integration", this.stacApiLambdaFunction),
    });

    this.url = stacApi.url!;

    new CfnOutput(this, "stac-api-output", {
      exportName: `${Stack.of(this).stackName}-url`,
      value: this.url,
    });
  }
}

export interface PgStacApiLambdaProps {
  /**
   * VPC into which the lambda should be deployed.
   */
  readonly vpc: ec2.IVpc;

  /**
   * RDS Instance with installed pgSTAC.
   */
  readonly db: rds.IDatabaseInstance;

  /**
   * Subnet into which the lambda should be deployed.
   */
  readonly subnetSelection: ec2.SubnetSelection;

  /**
   * Secret containing connection information for pgSTAC database.
   */
  readonly dbSecret: secretsmanager.ISecret;

  /**
   * Customized environment variables to send to fastapi-pgstac runtime.
   */
  readonly apiEnv?: Record<string, string>;

  /**
   * Custom Domain Name Options for STAC API,
   */
   readonly stacApiDomainName?: IDomainName;

  /**
     * Optional settings for the lambda function.
     *
     * @default - defined in the construct.
     */
  readonly lambdaFunctionOptions?: CustomLambdaFunctionOptions;

  /**
   * Optional lambda asset code
   * @default - default runtime defined in this repository.
   */
  readonly lambdaAssetCode?: lambda.AssetCode;
}

