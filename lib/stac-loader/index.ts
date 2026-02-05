import {
  CfnOutput,
  Duration,
  aws_ec2 as ec2,
  aws_lambda as lambda,
  aws_lambda_event_sources as lambdaEventSources,
  aws_logs as logs,
  aws_sns as sns,
  aws_sns_subscriptions as snsSubscriptions,
  aws_sqs as sqs,
  Stack,
} from "aws-cdk-lib";
import { Construct } from "constructs";
import * as path from "path";
import { PgStacDatabase } from "../database";
import { CustomLambdaFunctionProps, resolveLambdaCode } from "../utils";

/**
 * Configuration properties for the StacLoader construct.
 *
 * The StacLoader is part of a two-phase serverless STAC ingestion pipeline
 * that loads STAC collections and items into a pgstac database. This construct creates
 * the infrastructure for receiving STAC objects from multiple sources:
 * 1. SNS messages containing STAC metadata (direct ingestion)
 * 2. S3 event notifications for STAC objects uploaded to S3 buckets
 *
 * Objects from both sources are batched and inserted into PostgreSQL with the pgstac extension.
 *
 * @example
 * const loader = new StacLoader(this, 'StacLoader', {
 *   pgstacDb: database,
 *   batchSize: 1000,
 *   maxBatchingWindowMinutes: 1,
 *   lambdaTimeoutSeconds: 300
 * });
 */
export interface StacLoaderProps {
  /**
   * The PgSTAC database instance to load data into.
   *
   * This database must have the pgstac extension installed and be properly
   * configured with collections before objects can be loaded. The loader will
   * use AWS Secrets Manager to securely access database credentials.
   */
  readonly pgstacDb: PgStacDatabase;

  /**
   * VPC into which the lambda should be deployed.
   */
  readonly vpc?: ec2.IVpc;

  /**
   * Subnet into which the lambda should be deployed.
   */
  readonly subnetSelection?: ec2.SubnetSelection;

  /**
   * The lambda runtime to use for the item loading function.
   *
   * The function is implemented in Python and uses pypgstac for database
   * operations. Ensure the runtime version is compatible with the pgstac
   * version specified in the database configuration.
   *
   * @default lambda.Runtime.PYTHON_3_12
   */
  readonly lambdaRuntime?: lambda.Runtime;

  /**
   * The timeout for the item load lambda in seconds.
   *
   * This should accommodate the time needed to process up to `batchSize`
   * objects and perform database insertions. The SQS visibility timeout
   * will be set to this value plus 10 seconds.
   *
   * @default 300
   */
  readonly lambdaTimeoutSeconds?: number;

  /**
   * Memory size for the lambda function in MB.
   *
   * Higher memory allocation may improve performance when processing
   * large batches of STAC objects, especially for memory-intensive
   * database operations.
   *
   * @default 1024
   */
  readonly memorySize?: number;

  /**
   * SQS batch size for lambda event source.
   *
   * This determines the maximum number of STAC objects that will be
   * processed together in a single lambda invocation. Larger batch
   * sizes improve database insertion efficiency but require more
   * memory and longer processing time.
   *
   * **Batching Behavior**: SQS will wait to accumulate up to this many
   * messages before triggering the Lambda, OR until the maxBatchingWindow
   * timeout is reached, whichever comes first. This creates an efficient
   * balance between throughput and latency.
   *
   * @default 500
   */
  readonly batchSize?: number;

  /**
   * Maximum batching window in minutes.
   *
   * Even if the batch size isn't reached, the lambda will be triggered
   * after this time period to ensure timely processing of objects.
   * This prevents objects from waiting indefinitely in low-volume scenarios.
   *
   * **Important**: This timeout works in conjunction with batchSize - SQS
   * will trigger the Lambda when EITHER the batch size is reached OR this
   * time window expires, ensuring objects are processed in a timely manner
   * regardless of volume.
   *
   * @default 1
   */
  readonly maxBatchingWindowMinutes?: number;

  /**
   * Maximum concurrent executions for the StacLoader Lambda function
   *
   * This limit will be applied to the Lambda function and will control how
   * many concurrent batches will be released from the SQS queue.
   *
   * @default 2
   */
  readonly maxConcurrency?: number;

  /**
   * Additional environment variables for the lambda function.
   *
   * These will be merged with the default environment variables including
   * PGSTAC_SECRET_ARN. Use this for custom configuration or debugging flags.
   *
   * If you want to enable the option to upload a boilerplate collection record
   * in the event that the collection record does not yet exist for an item that
   * is set to be loaded, set the variable `"CREATE_COLLECTIONS_IF_MISSING": "TRUE"`.
   */
  readonly environment?: { [key: string]: string };

  /**
   * Can be used to override the default lambda function properties.
   *
   * @default - defined in the construct.
   */
  readonly lambdaFunctionOptions?: CustomLambdaFunctionProps;
}

/**
 * AWS CDK Construct for STAC Object Loading Infrastructure
 *
 * The StacLoader creates a serverless, event-driven system for loading
 * STAC (SpatioTemporal Asset Catalog) objects into a PostgreSQL database with
 * the pgstac extension. This construct supports multiple ingestion pathways
 * for flexible STAC object loading.
 *
 * ## Architecture Overview
 *
 * This construct creates the following AWS resources:
 * - **SNS Topic**: Entry point for STAC objects and S3 event notifications
 * - **SQS Queue**: Buffers and batches messages before processing (60-second visibility timeout)
 * - **Dead Letter Queue**: Captures failed loading attempts after 5 retries
 * - **Lambda Function**: Python function that processes batches and inserts objects into pgstac
 *
 * ## Data Flow
 *
 * The loader supports two primary data ingestion patterns:
 *
 * ### Direct STAC Object Publishing
 * 1. STAC objects (JSON) are published directly to the SNS topic in message bodies
 * 2. The SQS queue collects messages and batches them (up to {batchSize} objects or 1 minute window)
 * 3. The Lambda function receives batches, validates objects, and inserts into pgstac
 *
 * ### S3 Event-Driven Loading
 * 1. An S3 bucket is configured to send notifications to the SNS topic when json files are created
 * 2. STAC objects are uploaded to S3 buckets as JSON/GeoJSON files
 * 3. S3 event notifications are sent to the SNS topic when objects are uploaded
 * 4. The Lambda function receives S3 events in the SQS message batch, fetches objects from S3, and loads into pgstac
 *
 * ## Batching Behavior
 *
 * The SQS-to-Lambda integration uses intelligent batching to optimize performance:
 *
 * - **Batch Size**: Lambda waits to receive up to `batchSize` messages (default: 500)
 * - **Batching Window**: If fewer than `batchSize` messages are available, Lambda
 *   triggers after `maxBatchingWindow` minutes (default: 1 minute)
 * - **Trigger Condition**: Lambda executes when EITHER condition is met first
 * - **Concurrency**: Limited to `maxConcurrency` concurrent executions to prevent database overload
 * - **Partial Failures**: Uses `reportBatchItemFailures` to retry only failed objects
 *
 * This approach balances throughput (larger batches = fewer database connections)
 * with latency (time-based triggers prevent indefinite waiting).
 *
 * ## Message Ordering and Deduplication
 *
 * **Standard Queues**: This construct uses standard (non-FIFO) SNS topics and SQS queues,
 * which means messages are **not guaranteed to arrive in order**. Multiple messages
 * with the same STAC item or collection ID may arrive in any sequence.
 *
 * **Timestamp-Based Deduplication**: Within each batch, the loader uses SNS timestamps
 * to ensure only the newest version of each item/collection is ingested:
 *
 * - When multiple messages have the same item/collection ID in a batch, the loader
 *   compares their SNS Timestamps (automatically set when messages are published)
 * - Only the message with the **newest timestamp** is kept for database insertion
 * - Older versions are discarded and logged at the debug level
 * - This guarantees that within a batch, the chronologically latest update wins
 *
 * **Important Limitations**:
 * - Deduplication only occurs **within a single batch** - messages in different batches
 *   are not compared across batches
 * - The database upsert operation will update existing records, so later batches can
 *   still overwrite earlier batches regardless of timestamps
 * - For guaranteed ordering across all messages, consider implementing version tracking
 *   in your STAC metadata and database constraints
 *
 * ## Error Handling and Dead Letter Queue
 *
 * Failed messages are sent to the dead letter queue after 5 processing attempts.
 * **Important**: This construct provides NO automated handling of dead letter queue
 * messages - monitoring, inspection, and reprocessing of failed objects is the
 * responsibility of the implementing application.
 *
 * Consider implementing:
 * - CloudWatch alarms on dead letter queue depth
 * - Manual or automated reprocessing workflows
 * - Logging and alerting for failed objects
 * - Regular cleanup of old dead letter messages (14-day retention)
 *
 * ## Operational Characteristics
 *
 * - **Scalability**: Lambda scales automatically based on queue depth
 * - **Reliability**: Dead letter queue captures failures for debugging
 * - **Efficiency**: Batching optimizes database operations for high throughput
 * - **Security**: Database credentials accessed via AWS Secrets Manager
 * - **Observability**: CloudWatch logs retained for one week
 *
 * ## Prerequisites
 *
 * Before using this construct, ensure:
 * - The pgstac database has collections loaded (objects require existing collection IDs)
 * - Database credentials are stored in AWS Secrets Manager
 * - The pgstac extension is properly installed and configured
 *
 * ## Usage Example
 *
 * ```typescript
 * // Create database first
 * const database = new PgStacDatabase(this, 'Database', {
 *   pgstacVersion: '0.9.5'
 * });
 *
 * // Create Object loader
 * const loader = new StacLoader(this, 'StacLoader', {
 *   pgstacDb: database,
 *   batchSize: 1000,          // Process up to 1000 objects per batch
 *   maxBatchingWindowMinutes: 1, // Wait max 1 minute to fill batch
 *   lambdaTimeoutSeconds: 300     // Allow up to 300 seconds for database operations
 * });
 *
 * // The topic ARN can be used by other services to publish objects
 * new CfnOutput(this, 'LoaderTopicArn', {
 *   value: loader.topic.topicArn
 * });
 * ```
 *
 * ## Direct Object Publishing
 *
 * External services can publish STAC objects directly to the topic:
 *
 * ```bash
 * aws sns publish --topic-arn $STAC_LOAD_TOPIC --message  '{
 *   "id": "example-collection",
 *   "type": "Collection",
 *   "title": "Example Collection",
 *   "description": "An example collection",
 *   "license": "proprietary",
 *   "extent": {
 *       "spatial": {"bbox": [[-180, -90, 180, 90]]},
 *       "temporal": {"interval": [[null, null]]}
 *   },
 *   "stac_version": "1.1.0",
 *   "links": []
 * }'
 *
 * aws sns publish --topic-arn $STAC_LOAD_TOPIC --message '{
 *   "type": "Feature",
 *   "stac_version": "1.0.0",
 *   "id": "example-item",
 *   "properties": {"datetime": "2021-01-01T00:00:00Z"},
 *   "geometry": {"type": "Polygon", "coordinates": [...]},
 *   "collection": "example-collection"
 * }'
 *
 *
 * ```
 *
 * ## S3 Event Configuration
 *
 * To enable S3 event-driven loading, configure S3 bucket notifications to send
 * events to the SNS topic when STAC objects (.json or .geojson files) are uploaded:
 *
 * ```typescript
 * // Configure S3 bucket to send notifications to the loader topic
 * bucket.addEventNotification(
 *   s3.EventType.OBJECT_CREATED,
 *   new s3n.SnsDestination(loader.topic),
 *   { suffix: '.json' }
 * );
 *
 * bucket.addEventNotification(
 *   s3.EventType.OBJECT_CREATED,
 *   new s3n.SnsDestination(loader.topic),
 *   { suffix: '.geojson' }
 * );
 * ```
 *
 * When STAC objects are uploaded to the configured S3 bucket, the loader will:
 * 1. Receive S3 event notifications via SNS
 * 2. Fetch the STAC JSON from S3
 * 3. Validate and load the objects into the pgstac database
 *
 * ## Monitoring and Troubleshooting
 *
 * - Monitor Lambda logs: `/aws/lambda/{FunctionName}`
 * - **Dead Letter Queue**: Check for failed objects - **no automated handling provided**
 * - Use batch objects failure reporting for partial batch processing
 * - CloudWatch metrics available for queue depth and Lambda performance
 *
 * ### Dead Letter Queue Management
 *
 * Applications must implement their own dead letter queue monitoring:
 *
 * ```typescript
 * // Example: CloudWatch alarm for dead letter queue depth
 * new cloudwatch.Alarm(this, 'DeadLetterAlarm', {
 *   metric: loader.deadLetterQueue.metricApproximateNumberOfVisibleMessages(),
 *   threshold: 1,
 *   evaluationPeriods: 1
 * });
 *
 * // Example: Lambda to reprocess dead letter messages
 * const reprocessFunction = new lambda.Function(this, 'Reprocess', {
 *   // Implementation to fetch and republish failed messages
 * });
 * ```
 *
 */
export class StacLoader extends Construct {
  /**
   * The SNS topic that receives STAC objects and S3 event notifications for loading.
   *
   * This topic serves as the entry point for two types of events:
   * 1. Direct STAC JSON documents published by external services
   * 2. S3 event notifications when STAC objects are uploaded to configured buckets
   *
   * The topic fans out to the SQS queue for batched processing.
   */
  public readonly topic: sns.Topic;

  /**
   * The SQS queue that buffers messages before processing.
   *
   * This queue collects both direct STAC objects from SNS and S3 event
   * notifications, batching them for efficient database operations.
   * Configured with a visibility timeout that accommodates Lambda
   * processing time plus buffer.
   */
  public readonly queue: sqs.Queue;

  /**
   * Dead letter queue for failed objects loading attempts.
   *
   * Messages that fail processing after 5 attempts are sent here
   * for inspection and potential replay. Retains messages for 14 days
   * to allow for debugging and manual intervention.
   *
   * **User Responsibility**: This construct provides NO automated monitoring,
   * alerting, or reprocessing of dead letter queue messages. Applications
   * using this construct must implement their own:
   * - Dead letter queue depth monitoring and alerting
   * - Failed message inspection and debugging workflows
   * - Manual or automated reprocessing mechanisms
   * - Cleanup procedures for old failed messages
   */
  public readonly deadLetterQueue: sqs.Queue;

  /**
   * The Lambda function that loads STAC objects into the pgstac database.
   *
   * This Python function receives batches of messages from SQS and processes
   * them based on their type:
   * - Direct STAC objects: Validates and loads directly into pgstac
   * - S3 events: Fetches STAC JSON from S3, validates, and loads into pgstac
   *
   * The function connects to PostgreSQL using credentials from Secrets Manager
   * and uses pypgstac for efficient database operations.
   */
  public readonly lambdaFunction: lambda.Function;

  constructor(scope: Construct, id: string, props: StacLoaderProps) {
    super(scope, id);

    const timeoutSeconds = props.lambdaTimeoutSeconds ?? 300;
    const lambdaRuntime = props.lambdaRuntime ?? lambda.Runtime.PYTHON_3_12;
    const maxConcurrency = props.maxConcurrency ?? 2;

    // Create dead letter queue
    this.deadLetterQueue = new sqs.Queue(this, "DeadLetterQueue", {
      retentionPeriod: Duration.days(14),
    });

    // Create main queue
    this.queue = new sqs.Queue(this, "Queue", {
      visibilityTimeout: Duration.seconds(timeoutSeconds + 10),
      encryption: sqs.QueueEncryption.SQS_MANAGED,
      deadLetterQueue: {
        maxReceiveCount: 5,
        queue: this.deadLetterQueue,
      },
    });

    // Create SNS topic
    this.topic = new sns.Topic(this, "Topic", {
      displayName: `${id}-StacLoaderTopic`,
    });

    // Subscribe the queue to the topic
    this.topic.addSubscription(
      new snsSubscriptions.SqsSubscription(this.queue)
    );

    // Create the lambda function
    const { code: userCode, ...otherLambdaOptions } =
      props.lambdaFunctionOptions || {};

    this.lambdaFunction = new lambda.Function(this, "Function", {
      runtime: lambdaRuntime,
      handler: "stac_loader.handler.handler",
      vpc: props.vpc,
      vpcSubnets: props.subnetSelection,
      code: resolveLambdaCode(userCode, path.join(__dirname, ".."), {
        file: "stac-loader/runtime/Dockerfile",
        platform: "linux/amd64",
        buildArgs: {
          PYTHON_VERSION: lambdaRuntime.toString().replace("python", ""),
          PGSTAC_VERSION: props.pgstacDb.pgstacVersion,
        },
      }),
      memorySize: props.memorySize ?? 1024,
      timeout: Duration.seconds(timeoutSeconds),
      reservedConcurrentExecutions: maxConcurrency,
      logRetention: logs.RetentionDays.ONE_WEEK,
      environment: {
        PGSTAC_SECRET_ARN: props.pgstacDb.pgstacSecret.secretArn,
        ...props.environment,
      },
      // overwrites defaults with user-provided configurable properties
      ...otherLambdaOptions,
    });

    // Grant permissions to read the database secret
    props.pgstacDb.pgstacSecret.grantRead(this.lambdaFunction);

    // Add SQS event source to the lambda
    this.lambdaFunction.addEventSource(
      new lambdaEventSources.SqsEventSource(this.queue, {
        batchSize: props.batchSize ?? 500,
        maxBatchingWindow: Duration.minutes(
          props.maxBatchingWindowMinutes ?? 1
        ),
        maxConcurrency: maxConcurrency,
        reportBatchItemFailures: true,
      })
    );

    // Create outputs
    const exportPrefix = Stack.of(this).stackName;
    new CfnOutput(this, "TopicArn", {
      value: this.topic.topicArn,
      description: "ARN of the StacLoader SNS Topic",
      exportName: `${exportPrefix}-stac-loader-topic-arn`,
    });

    new CfnOutput(this, "QueueUrl", {
      value: this.queue.queueUrl,
      description: "URL of the StacLoader SQS Queue",
      exportName: `${exportPrefix}-stac-loader-queue-url`,
    });

    new CfnOutput(this, "DeadLetterQueueUrl", {
      value: this.deadLetterQueue.queueUrl,
      description: "URL of the StacLoader Dead Letter Queue",
      exportName: `${exportPrefix}-stac-loader-deadletter-queue-url`,
    });

    new CfnOutput(this, "FunctionName", {
      value: this.lambdaFunction.functionName,
      description: "Name of the StacLoader Lambda Function",
      exportName: `${exportPrefix}-stac-loader-function-name`,
    });
  }
}

/**
 * @deprecated Use StacLoader instead. StacItemLoader will be removed in a future version.
 */
export class StacItemLoader extends StacLoader {
  constructor(scope: Construct, id: string, props: StacLoaderProps) {
    console.warn(
      `StacItemLoader is deprecated. Please use StacLoader instead. ` +
        `StacItemLoader will be removed in a future version.`
    );

    super(scope, id, props);
  }
}

// Also create a deprecated interface alias if you had a separate interface
/**
 * @deprecated Use StacLoaderProps instead. StacItemLoaderProps will be removed in a future version.
 */
export interface StacItemLoaderProps extends StacLoaderProps {}
