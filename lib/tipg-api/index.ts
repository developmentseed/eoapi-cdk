import {
    Stack,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_lambda as lambda,
    aws_secretsmanager as secretsmanager,
    CfnOutput,
    Duration,
  } from "aws-cdk-lib";
  import {
    PythonFunction,
    PythonFunctionProps,
  } from "@aws-cdk/aws-lambda-python-alpha";
  import { IDomainName, HttpApi } from "@aws-cdk/aws-apigatewayv2-alpha";
  import { HttpLambdaIntegration } from "@aws-cdk/aws-apigatewayv2-integrations-alpha";
  import { Construct } from "constructs";

  export class TiPgApiLambda extends Construct {
    readonly url: string;
    public tiPgLambdaFunction: PythonFunction;

    constructor(scope: Construct, id: string, props: TiPgApiLambdaProps) {
      super(scope, id);

      const apiCode = props.apiCode || {
        entry: `${__dirname}/runtime`,
        index: "src/handler.py",
        handler: "handler",
      };

      this.tiPgLambdaFunction = new PythonFunction(this, "tipg-api", {
        ...apiCode,
        runtime: lambda.Runtime.PYTHON_3_10,
        architecture: lambda.Architecture.X86_64,
        environment: {
          PGSTAC_SECRET_ARN: props.dbSecret.secretArn,
          DB_MIN_CONN_SIZE: "1",
          DB_MAX_CONN_SIZE: "1",
          ...props.apiEnv,
        },
        vpc: props.vpc,
        vpcSubnets: props.subnetSelection,
        allowPublicSubnet: true,
        memorySize: 1024,
        timeout: Duration.seconds(30),
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
     * Custom code to run for the application.
     *
     * @default - simplified version of tipg.
     */
    readonly apiCode?: TiPgApiEntrypoint;

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
  }

  export interface TiPgApiEntrypoint {
    /**
     * Path to the source of the function or the location for dependencies.
     */
    readonly entry: PythonFunctionProps["entry"];
    /**
     * The path (relative to entry) to the index file containing the exported handler.
     */
    readonly index: PythonFunctionProps["index"];
    /**
     * The name of the exported handler in the index file.
     */
    readonly handler: PythonFunctionProps["handler"];
  }
