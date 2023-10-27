import {
  aws_apigateway as apigateway,
  aws_dynamodb as dynamodb,
  aws_ec2 as ec2,
  aws_iam as iam,
  aws_lambda as lambda,
  aws_logs,
  aws_lambda_event_sources as events,
  aws_secretsmanager as secretsmanager,
  aws_ssm as ssm,
  Duration,
  RemovalPolicy,
  Stack,
} from "aws-cdk-lib";
import { Construct } from "constructs";
import { CustomLambdaFunctionProps } from "../utils";

export class StacIngestor extends Construct {
  table: dynamodb.Table;
  public handlerRole: iam.Role;

  constructor(scope: Construct, id: string, props: StacIngestorProps) {
    super(scope, id);

    this.table = this.buildTable();

    const env: Record<string, string> = {
      DYNAMODB_TABLE: this.table.tableName,
      ROOT_PATH: `/${props.stage}`,
      NO_PYDANTIC_SSM_SETTINGS: "1",
      STAC_URL: props.stacUrl,
      DATA_ACCESS_ROLE: props.dataAccessRole.roleArn,
      ...props.apiEnv,
    };

    this.handlerRole = new iam.Role(this, "execution-role", {
      description:
        "Role used by STAC Ingestor. Manually defined so that we can choose a name that is supported by the data access roles trust policy",
      assumedBy: new iam.ServicePrincipal("lambda.amazonaws.com"),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName(
          "service-role/AWSLambdaBasicExecutionRole",
        ),
        iam.ManagedPolicy.fromAwsManagedPolicyName(
          "service-role/AWSLambdaVPCAccessExecutionRole",
        ),
      ],
    });
    
    const handler = this.buildApiLambda({
      table: this.table,
      env,
      dataAccessRole: props.dataAccessRole,
      stage: props.stage,
      dbSecret: props.stacDbSecret,
      dbVpc: props.vpc,
      dbSecurityGroup: props.stacDbSecurityGroup,
      subnetSelection: props.subnetSelection,
      lambdaFunctionOptions: props.apiLambdaFunctionOptions,
    });

    this.buildApiEndpoint({
      handler,
      stage: props.stage,
      endpointConfiguration: props.apiEndpointConfiguration,
      policy: props.apiPolicy,
      ingestorDomainNameOptions: props.ingestorDomainNameOptions,
    });

    this.buildIngestor({
      table: this.table,
      env: env,
      dbSecret: props.stacDbSecret,
      dbVpc: props.vpc,
      dbSecurityGroup: props.stacDbSecurityGroup,
      subnetSelection: props.subnetSelection,
      lambdaFunctionOptions: props.ingestorLambdaFunctionOptions
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
    dataAccessRole: iam.IRole;
    stage: string;
    dbSecret: secretsmanager.ISecret;
    dbVpc: undefined | ec2.IVpc;
    dbSecurityGroup: ec2.ISecurityGroup;
    subnetSelection: undefined | ec2.SubnetSelection
    lambdaFunctionOptions?: CustomLambdaFunctionProps;
  }): lambda.Function {
        
    const handler = new lambda.Function(this, "api-handler", {
      // defaults for configurable properties
      runtime: lambda.Runtime.PYTHON_3_9,
      handler: "src.handler.handler",
      memorySize: 2048,
      logRetention: aws_logs.RetentionDays.ONE_WEEK,
      timeout: Duration.seconds(30),
      code:lambda.Code.fromDockerBuild(__dirname, {
        file: "runtime/Dockerfile",
        buildArgs: { PYTHON_VERSION: '3.9' },
      }),
      // overwrites defaults with user-provided configurable properties
      ...props.lambdaFunctionOptions,
      // Non configurable properties that are going to be overwritten even if provided by the user
      vpc: props.dbVpc,
      vpcSubnets: props.subnetSelection,
      allowPublicSubnet: true,
      environment: { DB_SECRET_ARN: props.dbSecret.secretArn, ...props.env },
      role: this.handlerRole
    });

    // Allow handler to read DB secret
    props.dbSecret.grantRead(handler);

    // Allow handler to connect to DB

    if (props.dbVpc){
      props.dbSecurityGroup.addIngressRule(
        handler.connections.securityGroups[0],
        ec2.Port.tcp(5432),
        "Allow connections from STAC Ingestor"
      );
    }

    props.table.grantReadWriteData(handler);

    return handler;
  }

  private buildIngestor(props: {
    table: dynamodb.ITable;
    env: Record<string, string>;
    dbSecret: secretsmanager.ISecret;
    dbVpc: undefined | ec2.IVpc;
    dbSecurityGroup: ec2.ISecurityGroup;
    subnetSelection: undefined | ec2.SubnetSelection;
    lambdaFunctionOptions?: CustomLambdaFunctionProps;
  }): lambda.Function {

    
    const handler = new lambda.Function(this, "stac-ingestor",{
      // defaults for configurable properties
      runtime: lambda.Runtime.PYTHON_3_9,
      handler: "src.ingestor.handler",
      memorySize: 2048,
      logRetention: aws_logs.RetentionDays.ONE_WEEK,
      timeout: Duration.seconds(180),
      code: lambda.Code.fromDockerBuild(__dirname, {
        file: "runtime/Dockerfile",
        buildArgs: { PYTHON_VERSION: '3.9' },
      }),
      // overwrites defaults with user-provided configurable properties
      ...props.lambdaFunctionOptions,

      // Non configurable properties that are going to be overwritten even if provided by the user
      vpc: props.dbVpc,
      vpcSubnets: props.subnetSelection,
      allowPublicSubnet: true,
      environment: { DB_SECRET_ARN: props.dbSecret.secretArn, ...props.env },
      role: this.handlerRole
    });

    // Allow handler to read DB secret
    props.dbSecret.grantRead(handler);

    // Allow handler to connect to DB
    if (props.dbVpc){
      props.dbSecurityGroup.addIngressRule(
        handler.connections.securityGroups[0],
        ec2.Port.tcp(5432),
        "Allow connections from STAC Ingestor"
      );
    }

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
    ingestorDomainNameOptions?: apigateway.DomainNameOptions;
  }): apigateway.LambdaRestApi {

    return new apigateway.LambdaRestApi(
      this,
      `${Stack.of(this).stackName}-ingestor-api`,
      {
        handler: props.handler,
        proxy: true,

        cloudWatchRole: true,
        deployOptions: { stageName: props.stage },
        endpointExportName: `${Stack.of(this)}-ingestor-api`,

        endpointConfiguration: props.endpointConfiguration,
        policy: props.policy,

        domainName:  props.ingestorDomainNameOptions ? {
          domainName: props.ingestorDomainNameOptions.domainName,
          certificate: props.ingestorDomainNameOptions.certificate,
        } : undefined,
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
   * ARN of AWS Role used to validate access to S3 data
   */
  readonly dataAccessRole: iam.IRole;

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
  readonly vpc?: ec2.IVpc;

  /**
   * Security Group used by pgSTAC DB
   */
  readonly stacDbSecurityGroup: ec2.ISecurityGroup;

  /**
   * Subnet into which the lambda should be deployed if using a VPC
   */
  readonly subnetSelection?: ec2.SubnetSelection;

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

  /**
   * Custom Domain Name Options for Ingestor API
   */
   readonly ingestorDomainNameOptions?: apigateway.DomainNameOptions;

  /**
     * Optional settings for the lambda function. Can be anything that can be configured on the lambda function, but some will be overwritten by values defined here. 
     *
     * @default - default settings are defined in the construct.
     */
  readonly apiLambdaFunctionOptions?: CustomLambdaFunctionProps;

  /**
     * Optional settings for the lambda function. Can be anything that can be configured on the lambda function, but some will be overwritten by values defined here. 
     *
     * @default - default settings are defined in the construct.
     */
readonly ingestorLambdaFunctionOptions?: CustomLambdaFunctionProps;
  
}