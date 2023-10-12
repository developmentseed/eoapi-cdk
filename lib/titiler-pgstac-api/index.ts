import {
    Stack,
    aws_iam as iam,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_lambda as lambda,
    aws_secretsmanager as secretsmanager,
    CfnOutput,
    Duration,
    aws_logs
  } from "aws-cdk-lib";
  import { IDomainName, HttpApi } from "@aws-cdk/aws-apigatewayv2-alpha";
  import { HttpLambdaIntegration } from "@aws-cdk/aws-apigatewayv2-integrations-alpha";
  import { Construct } from "constructs";
import { CustomLambdaFunctionProps } from "../utils";
  

  // default settings that can be overridden by the user-provided environment. 
  let defaultTitilerPgstacEnv :{ [key: string]: any } = {
    "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": ".tif,.TIF,.tiff",
    "GDAL_CACHEMAX": "200", 
    "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
    "GDAL_INGESTED_BYTES_AT_OPEN": "32768",
    "GDAL_HTTP_MERGE_CONSECUTIVE_RANGES": "YES",
    "GDAL_HTTP_MULTIPLEX": "YES",
    "GDAL_HTTP_VERSION": "2",
    "PYTHONWARNINGS": "ignore",
    "VSI_CACHE": "TRUE",
    "VSI_CACHE_SIZE": "5000000", 
    "DB_MIN_CONN_SIZE": "1",
    "DB_MAX_CONN_SIZE": "1"
  }

  export class TitilerPgstacApiLambda extends Construct {
    readonly url: string;
    public titilerPgstacLambdaFunction: lambda.Function;
  
    constructor(scope: Construct, id: string, props: TitilerPgStacApiLambdaProps) {
      super(scope, id);
      
      this.titilerPgstacLambdaFunction = new lambda.Function(this, "lambda", {
        // defaults for configurable properties
        runtime: lambda.Runtime.PYTHON_3_10,
        handler: "handler.handler",
        memorySize: 3008,
        logRetention: aws_logs.RetentionDays.ONE_WEEK,
        timeout: Duration.seconds(30),
        code: lambda.Code.fromDockerBuild(__dirname, {
          file: "runtime/Dockerfile",
          buildArgs: { PYTHON_VERSION: '3.10' }
        }),
        // overwrites defaults with user-provided configurable properties
        ...props.lambdaFunctionOptions,
        // Non configurable properties that are going to be overwritten even if provided by the user
        vpc: props.vpc,
        vpcSubnets: props.subnetSelection,
        allowPublicSubnet: true,
        // if user provided environment variables, merge them with the defaults.
        environment: props.apiEnv ? { ...defaultTitilerPgstacEnv, ...props.apiEnv, "PGSTAC_SECRET_ARN": props.dbSecret.secretArn } : defaultTitilerPgstacEnv,
      });
      
      // grant access to buckets using addToRolePolicy
      if (props.buckets) {
        props.buckets.forEach(bucket => {
          this.titilerPgstacLambdaFunction.addToRolePolicy(new iam.PolicyStatement({
            actions: ["s3:GetObject"],
            resources: [`arn:aws:s3:::${bucket}/*`],
          }));
        });
      }
      
      props.dbSecret.grantRead(this.titilerPgstacLambdaFunction);
      this.titilerPgstacLambdaFunction.connections.allowTo(props.db, ec2.Port.tcp(5432), "allow connections from titiler");
  
      const stacApi = new HttpApi(this, `${Stack.of(this).stackName}-titiler-pgstac-api`, {
        defaultDomainMapping: props.titilerPgstacApiDomainName ? { 
          domainName: props.titilerPgstacApiDomainName 
        } : undefined,
        defaultIntegration: new HttpLambdaIntegration("integration", this.titilerPgstacLambdaFunction),
      });
  
      this.url = stacApi.url!;
  
      new CfnOutput(this, "titiler-pgstac-api-output", {
        exportName: `${Stack.of(this).stackName}-titiler-pgstac-url`,
        value: this.url,
      });
    }
  }
  
  export interface TitilerPgStacApiLambdaProps {

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
     * Customized environment variables to send to titiler-pgstac runtime. These will be merged with `defaultTitilerPgstacEnv`.
     * The database secret arn is automatically added to the environment variables at deployment. 
    /*/
    readonly apiEnv?: Record<string, string>;

    /**
     * list of buckets the lambda will be granted access to. 
     */
    readonly buckets?: string[];

    /**
     * Custom Domain Name Options for Titiler Pgstac API,
     * 
     * @default - undefined. 
     */
    readonly titilerPgstacApiDomainName?: IDomainName;

    /**
     * Optional settings for the lambda function. Can be anything that can be configured on the lambda function, but some will be overwritten by values defined here. 
     *
     * @default - defined in the construct.
     */
    readonly lambdaFunctionOptions?: CustomLambdaFunctionProps;

  }

