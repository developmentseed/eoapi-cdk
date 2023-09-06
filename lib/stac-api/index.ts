import {
  Stack,
  aws_ec2 as ec2,
  aws_rds as rds,
  aws_lambda as lambda,
  aws_secretsmanager as secretsmanager,
  CfnOutput,
  DockerImage,
} from "aws-cdk-lib";
import {
  PythonFunction,
  PythonFunctionProps,
} from "@aws-cdk/aws-lambda-python-alpha";
import { IDomainName, HttpApi } from "@aws-cdk/aws-apigatewayv2-alpha";
import { HttpLambdaIntegration } from "@aws-cdk/aws-apigatewayv2-integrations-alpha";
import { Construct } from "constructs";

export class PgStacApiLambda extends Construct {
  readonly url: string;
  public stacApiLambdaFunction: PythonFunction;

  constructor(scope: Construct, id: string, props: PgStacApiLambdaProps) {
    super(scope, id);

    const apiCode = props.apiCode || {
      entry: `${__dirname}/runtime`,
      index: "src/handler.py",
      handler: "handler",
    };

    this.stacApiLambdaFunction = new PythonFunction(this, "stac-api", {
      ...apiCode,
      /**
       * NOTE: Unable to use Py3.9, due to issues with hashes:
       *
       *    ERROR: Hashes are required in --require-hashes mode, but they are missing
       *    from some requirements. Here is a list of those requirements along with the
       *    hashes their downloaded archives actually had. Add lines like these to your
       *    requirements files to prevent tampering. (If you did not enable
       *    --require-hashes manually, note that it turns on automatically when any
       *    package has a hash.)
       *        anyio==3.6.1 --hash=sha256:cb29b9c70620506a9a8f87a309591713446953302d7d995344d0d7c6c0c9a7be
       * */
      runtime: lambda.Runtime.PYTHON_3_8,
      architecture: lambda.Architecture.X86_64,
      environment: {
        PGSTAC_SECRET_ARN: props.dbSecret.secretArn,
        DB_MIN_CONN_SIZE: "0",
        DB_MAX_CONN_SIZE: "1",
        ...props.apiEnv,
      },
      vpc: props.vpc,
      vpcSubnets: props.subnetSelection,
      allowPublicSubnet: true,
      memorySize: 8192,
      bundling: {
        image: DockerImage.fromBuild(__dirname)
      }
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
   * Custom code to run for fastapi-pgstac.
   *
   * @default - simplified version of fastapi-pgstac
   */
  readonly apiCode?: ApiEntrypoint;

  /**
   * Customized environment variables to send to fastapi-pgstac runtime.
   */
  readonly apiEnv?: Record<string, string>;

  /**
   * Custom Domain Name Options for STAC API,
   */
   readonly stacApiDomainName?: IDomainName;
}

export interface ApiEntrypoint {
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
