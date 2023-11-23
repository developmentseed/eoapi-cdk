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
  import { CustomLambdaFunctionProps } from "../utils";

  const DEFAULT_TIPG_VERSION = "0.3.1";

  export class TiPgApiLambda extends Construct {
    readonly url: string;
    public tiPgLambdaFunction: lambda.Function;

    constructor(scope: Construct, id: string, props: TiPgApiLambdaProps) {
      super(scope, id);

      this.tiPgLambdaFunction = new lambda.Function(this, "lambda", {
        // defaults for configurable properties
        runtime: lambda.Runtime.PYTHON_3_11,
        handler: "handler.handler",
        memorySize: 1024,
        logRetention: logs.RetentionDays.ONE_WEEK,
        timeout: Duration.seconds(30),
        code: lambda.Code.fromDockerBuild(__dirname, {
        file: "runtime/Dockerfile",
          buildArgs: { PYTHON_VERSION: '3.11', TIPG_VERSION: props.tipgVersion || DEFAULT_TIPG_VERSION },
        }),
        // overwrites defaults with user-provided configurable properties
        ...props.lambdaFunctionOptions,
        // Non configurable properties that are going to be overwritten even if provided by the user
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
      if (props.vpc){
        this.tiPgLambdaFunction.connections.allowTo(props.db, ec2.Port.tcp(5432), "allow connections from tipg");
      }
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
    readonly vpc?: ec2.IVpc;

    /**
     * RDS Instance with installed pgSTAC.
     */
    readonly db: rds.IDatabaseInstance;

    /**
     * Subnet into which the lambda should be deployed.
     */
    readonly subnetSelection?: ec2.SubnetSelection;

    /**
     * Secret containing connection information for pgSTAC database.
     */
    readonly dbSecret: secretsmanager.ISecret;

    /**
     * Version of tipg to install in the Lambda Docker image 
     * 
     * @default 0.3.1
     */
    readonly tipgVersion?: string;

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
     * Optional settings for the lambda function. Can be anything that can be configured on the lambda function, but some will be overwritten by values defined here. 
     *
     * @default - defined in the construct.
     */
    readonly lambdaFunctionOptions?: CustomLambdaFunctionProps;
  }
