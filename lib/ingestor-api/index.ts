import {
  aws_apigateway as apigateway,
  aws_dynamodb as dynamodb,
  aws_ec2 as ec2,
  aws_iam as iam,
  aws_lambda as lambda,
  aws_lambda_event_sources as events,
  aws_secretsmanager as secretsmanager,
  aws_ssm as ssm,
  Duration,
  RemovalPolicy,
  Stack,
} from "aws-cdk-lib";
import { PythonFunction } from "@aws-cdk/aws-lambda-python-alpha";
import { Construct } from "constructs";

export class StacIngestor extends Construct {
  table: dynamodb.Table;

  constructor(scope: Construct, id: string, props: StacIngestorProps) {
    super(scope, id);

    this.table = this.buildTable();

    const env: Record<string, string> = {
      DYNAMODB_TABLE: this.table.tableName,
      ROOT_PATH: `/${props.stage}`,
      NO_PYDANTIC_SSM_SETTINGS: "1",
      STAC_URL: props.stacUrl,
      DATA_ACCESS_ROLE: props.dataAccessRoleArn,
      ...props.apiEnv,
    };

    const handler = this.buildApiLambda({
      table: this.table,
      env,
      apiHandlerRoleArn: props.stacIngestorRoleArn,
      stage: props.stage,
      dbSecret: props.stacDbSecret,
      dbVpc: props.vpc,
      dbSecurityGroup: props.stacDbSecurityGroup,
      subnetSelection: props.subnetSelection,
    });

    this.buildApiEndpoint({
      handler,
      stage: props.stage,
      endpointConfiguration: props.apiEndpointConfiguration,
      policy: props.apiPolicy,
    });

    this.buildIngestor({
      table: this.table,
      env: env,
      dbSecret: props.stacDbSecret,
      dbVpc: props.vpc,
      dbSecurityGroup: props.stacDbSecurityGroup,
      subnetSelection: props.subnetSelection,
    });

    this.registerSsmParameter({
      name: "dynamodb_table",
      value: this.table.tableName,
      description: "Name of table used to store ingestions",
    });
  }

  private buildTable(): dynamodb.Table {
    const table = new dynamodb.Table(this, "ingestions-table", {
      partitionKey: { name: "created_by", type: dynamodb.AttributeType.STRING },
      sortKey: { name: "id", type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: RemovalPolicy.DESTROY,
      stream: dynamodb.StreamViewType.NEW_IMAGE,
    });

    table.addGlobalSecondaryIndex({
      indexName: "status",
      partitionKey: { name: "status", type: dynamodb.AttributeType.STRING },
      sortKey: { name: "created_at", type: dynamodb.AttributeType.STRING },
    });

    return table;
  }

  private buildApiLambda(props: {
    table: dynamodb.ITable;
    env: Record<string, string>;
    apiHandlerRoleArn: string;
    stage: string;
    dbSecret: secretsmanager.ISecret;
    dbVpc: ec2.IVpc;
    dbSecurityGroup: ec2.ISecurityGroup;
    subnetSelection: ec2.SubnetSelection;
  }): PythonFunction {
    const handler_role = iam.Role.fromRoleArn(this, "execution-role", props.apiHandlerRoleArn);

    const handler = new PythonFunction(this, "api-handler", {
      entry: `${__dirname}/runtime`,
      index: "src/handler.py",
      runtime: lambda.Runtime.PYTHON_3_9,
      timeout: Duration.seconds(30),
      environment: { DB_SECRET_ARN: props.dbSecret.secretArn, ...props.env },
      vpc: props.dbVpc,
      vpcSubnets: props.subnetSelection,
      allowPublicSubnet: true,
      role: handler_role,
      memorySize: 2048,
    });

    // Allow handler to read DB secret
    props.dbSecret.grantRead(handler);

    // Allow handler to connect to DB
    props.dbSecurityGroup.addIngressRule(
      handler.connections.securityGroups[0],
      ec2.Port.tcp(5432),
      "Allow connections from STAC Ingestor"
    );

    props.table.grantReadWriteData(handler);

    return handler;
  }

  private buildIngestor(props: {
    table: dynamodb.ITable;
    env: Record<string, string>;
    dbSecret: secretsmanager.ISecret;
    dbVpc: ec2.IVpc;
    dbSecurityGroup: ec2.ISecurityGroup;
    subnetSelection: ec2.SubnetSelection;
  }): PythonFunction {
    const handler = new PythonFunction(this, "stac-ingestor", {
      entry: `${__dirname}/runtime`,
      index: "src/ingestor.py",
      runtime: lambda.Runtime.PYTHON_3_9,
      timeout: Duration.seconds(180),
      environment: { DB_SECRET_ARN: props.dbSecret.secretArn, ...props.env },
      vpc: props.dbVpc,
      vpcSubnets: props.subnetSelection,
      allowPublicSubnet: true,
      memorySize: 2048,
    });

    // Allow handler to read DB secret
    props.dbSecret.grantRead(handler);

    // Allow handler to connect to DB
    props.dbSecurityGroup.addIngressRule(
      handler.connections.securityGroups[0],
      ec2.Port.tcp(5432),
      "Allow connections from STAC Ingestor"
    );

    // Allow handler to write results back to DBƒ
    props.table.grantWriteData(handler);

    // Trigger handler from writes to DynamoDB table
    handler.addEventSource(
      new events.DynamoEventSource(props.table, {
        // Read when batches reach size...
        batchSize: 1000,
        // ... or when window is reached.
        maxBatchingWindow: Duration.seconds(10),
        // Read oldest data first.
        startingPosition: lambda.StartingPosition.TRIM_HORIZON,
        retryAttempts: 1,
      })
    );

    return handler;
  }

  private buildApiEndpoint(props: {
    handler: lambda.IFunction;
    stage: string;
    policy?: iam.PolicyDocument;
    endpointConfiguration?: apigateway.EndpointConfiguration;
  }): apigateway.LambdaRestApi {
    return new apigateway.LambdaRestApi(
      this,
      `${Stack.of(this).stackName}-ingestor-api`,
      {
        handler: props.handler,
        proxy: true,

        cloudWatchRole: true,
        deployOptions: { stageName: props.stage },
        endpointExportName: `ingestor-api-${props.stage}`,

        endpointConfiguration: props.endpointConfiguration,
        policy: props.policy,
      }
    );
  }

  private registerSsmParameter(props: {
    name: string;
    value: string;
    description: string;
  }): ssm.IStringParameter {
    const parameterNamespace = Stack.of(this).stackName;
    return new ssm.StringParameter(
      this,
      `${props.name.replace("_", "-")}-parameter`,
      {
        description: props.description,
        parameterName: `/${parameterNamespace}/${props.name}`,
        stringValue: props.value,
      }
    );
  }
}

export interface StacIngestorProps {
  /**
   * ARN of AWS Role used to validate access to S3 data. 
   */
  readonly dataAccessRoleArn: string;

  /**
   * ARN of AWS Role to be used by the ingestor API lambda. Must have permissions to
   * assume the role represented by `dataAccessRoleArn` along with `service-role/AWSLambdaBasicExecutionRole` 
   * and `service-role/AWSLambdaVPCAccessExecutionRole` managed policies.
   */
  readonly stacIngestorRoleArn: string;

  /**
   * URL of STAC API
   */
  readonly stacUrl: string;

  /**
   * Stage of deployment (e.g. `dev`, `prod`)
   */
  readonly stage: string;

  /**
   * Secret containing pgSTAC DB connection information
   */
  readonly stacDbSecret: secretsmanager.ISecret;

  /**
   * VPC running pgSTAC DB
   */
  readonly vpc: ec2.IVpc;

  /**
   * Security Group used by pgSTAC DB
   */
  readonly stacDbSecurityGroup: ec2.ISecurityGroup;

  /**
   * Boolean indicating whether or not pgSTAC DB is in a public subnet
   */
  readonly subnetSelection: ec2.SubnetSelection;

  /**
   * Environment variables to be sent to Lambda.
   */
  readonly apiEnv?: Record<string, string>;

  /**
   * API Endpoint Configuration, useful for creating private APIs.
   */
  readonly apiEndpointConfiguration?: apigateway.EndpointConfiguration;

  /**
   * API Policy Document, useful for creating private APIs.
   */
  readonly apiPolicy?: iam.PolicyDocument;
}
