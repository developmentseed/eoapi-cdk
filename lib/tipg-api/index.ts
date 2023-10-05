import {
    Stack,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_lambda as lambda,
    aws_logs as logs,
    aws_secretsmanager as secretsmanager,
    CfnOutput,
    Duration,
  } from "aws-cdk-lib";
  import { IDomainName, HttpApi } from "@aws-cdk/aws-apigatewayv2-alpha";
  import { HttpLambdaIntegration } from "@aws-cdk/aws-apigatewayv2-integrations-alpha";
  import { Construct } from "constructs";
  import { CustomLambdaFunctionOptions } from "../utils";

  export class TiPgApiLambda extends Construct {
    readonly url: string;
    public tiPgLambdaFunction: lambda.Function;

    constructor(scope: Construct, id: string, props: TiPgApiLambdaProps) {
      super(scope, id);

      this.tiPgLambdaFunction = new lambda.Function(this, "lambda", {
        ...props.lambdaFunctionOptions ?? {
          runtime: lambda.Runtime.PYTHON_3_10,
          handler: "handler.handler",
          memorySize: 1024,
          logRetention: logs.RetentionDays.ONE_WEEK,
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
          DB_MIN_CONN_SIZE: "1",
          DB_MAX_CONN_SIZE: "1",
          ...props.apiEnv,
        },
      });

      props.dbSecret.grantRead(this.tiPgLambdaFunction);
      this.tiPgLambdaFunction.connections.allowTo(props.db, ec2.Port.tcp(5432), "allow connections from tipg");

      const tipgApi = new HttpApi(this, `${Stack.of(this).stackName}-tipg-api`, {
        defaultDomainMapping: props.tipgApiDomainName ? { 
          domainName: props.tipgApiDomainName
        } : undefined,
        defaultIntegration: new HttpLambdaIntegration("integration", this.tiPgLambdaFunction),
      });

      this.url = tipgApi.url!;

      new CfnOutput(this, "tipg-api-output", {
        exportName: `${Stack.of(this).stackName}-tip-url`,
        value: this.url,
      });
    }
  }

  export interface TiPgApiLambdaProps {

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
     * Customized environment variables to send to titiler-pgstac runtime.
     */
    readonly apiEnv?: Record<string, string>;
  
    /**
     * Custom Domain Name for tipg API. If defined, will create the 
     * domain name and integrate it with the tipg API. 
     * 
     * @default - undefined
     */
    readonly tipgApiDomainName?: IDomainName;


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
