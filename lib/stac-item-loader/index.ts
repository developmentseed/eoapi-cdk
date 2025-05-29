import {
  aws_lambda as lambda,
  aws_sqs as sqs,
  aws_sns as sns,
  aws_sns_subscriptions as snsSubscriptions,
  aws_lambda_event_sources as lambdaEventSources,
  aws_logs as logs,
  Duration,
  CfnOutput,
} from "aws-cdk-lib";
import { Construct } from "constructs";
import { PgStacDatabase } from "../database";
import * as path from "path";

/**
 * Configuration properties for the StacItemLoader construct.
 *
 * The StacItemLoader is part of a two-phase serverless STAC ingestion pipeline
 * that loads STAC items into a pgstac database. This construct creates
 * the infrastructure for receiving STAC items from multiple sources:
 * 1. SNS messages containing STAC metadata (direct ingestion)
 * 2. S3 event notifications for STAC items uploaded to S3 buckets
 *
 * Items from both sources are batched and inserted into PostgreSQL with the pgstac extension.
 *
 * @example
 * const loader = new StacItemLoader(this, 'ItemLoader', {
 *   pgstacDb: database,
 *   batchSize: 1000,
 *   maxBatchingWindowMinutes: 1,
 *   lambdaTimeoutSeconds: 45
 * });
 */
export interface StacItemLoaderProps {
  /**
   * The PgSTAC database instance to load items into.
   *
   * This database must have the pgstac extension installed and be properly
   * configured with collections before items can be loaded. The loader will
   * use AWS Secrets Manager to securely access database credentials.
   */
  readonly pgstacDb: PgStacDatabase;

  /**
   * The lambda runtime to use for the item loading function.
   *
   * The function is implemented in Python and uses pypgstac for database
   * operations. Ensure the runtime version is compatible with the pgstac
   * version specified in the database configuration.
   *
   * @default lambda.Runtime.PYTHON_3_11
   */
  readonly lambdaRuntime?: lambda.Runtime;

  /**
   * The timeout for the item load lambda in seconds.
   *
   * This should accommodate the time needed to process up to `batchSize`
   * items and perform database insertions. The SQS visibility timeout
   * will be set to this value plus 10 seconds.
   *
   * @default 45
   */
  readonly lambdaTimeoutSeconds?: number;

  /**
   * Memory size for the lambda function in MB.
   *
   * Higher memory allocation may improve performance when processing
   * large batches of STAC items, especially for memory-intensive
   * database operations.
   *
   * @default 1024
   */
  readonly memorySize?: number;

  /**
   * SQS batch size for lambda event source.
   *
   * This determines the maximum number of STAC items that will be
   * processed together in a single lambda invocation. Larger batch
   * sizes improve database insertion efficiency but require more
   * memory and longer processing time.
   *
   * @default 1000
   */
  readonly batchSize?: number;

  /**
   * Maximum batching window in minutes.
   *
   * Even if the batch size isn't reached, the lambda will be triggered
   * after this time period to ensure timely processing of items.
   * This prevents items from waiting indefinitely in low-volume scenarios.
   *
   * @default 1
   */
  readonly maxBatchingWindowMinutes?: number;

  /**
   * Additional environment variables for the lambda function.
   *
   * These will be merged with the default environment variables including
   * PGSTAC_SECRET_ARN. Use this for custom configuration or debugging flags.
   */
  readonly environment?: { [key: string]: string };
}

/**
 * AWS CDK Construct for STAC Item Loading Infrastructure
 *
 * The StacItemLoader creates a serverless, event-driven system for loading
 * STAC (SpatioTemporal Asset Catalog) items into a PostgreSQL database with
 * the pgstac extension. This construct supports multiple ingestion pathways
 * for flexible STAC item loading.
 *
 * ## Architecture Overview
 *
 * This construct creates the following AWS resources:
 * - **SNS Topic**: Entry point for STAC items and S3 event notifications
 * - **SQS Queue**: Buffers and batches messages before processing (60-second visibility timeout)
 * - **Dead Letter Queue**: Captures failed loading attempts after 5 retries
 * - **Lambda Function**: Python function that processes batches and inserts items into pgstac
 *
 * ## Data Flow
 *
 * The loader supports two primary data ingestion patterns:
 *
 * ### Direct STAC Item Publishing
 * 1. STAC items (JSON) are published directly to the SNS topic
 * 2. The SQS queue collects items and batches them (up to 1000 items or 1 minute window)
 * 3. The Lambda function receives batches, validates items, and inserts into pgstac
 *
 * ### S3 Event-Driven Loading
 * 1. STAC items are uploaded to S3 buckets as JSON/GeoJSON files
 * 2. S3 event notifications are sent to the SNS topic when items are uploaded
 * 3. The Lambda function receives S3 events, fetches items from S3, and loads into pgstac
 *
 * Failed messages are sent to the dead letter queue for inspection and retry
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
 * - The pgstac database has collections loaded (items require existing collection IDs)
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
 * // Create item loader
 * const loader = new StacItemLoader(this, 'ItemLoader', {
 *   pgstacDb: database,
 *   batchSize: 1000,          // Process up to 1000 items per batch
 *   maxBatchingWindowMinutes: 1, // Wait max 1 minute to fill batch
 *   lambdaTimeoutSeconds: 45     // Allow 45 seconds for database operations
 * });
 *
 * // The topic ARN can be used by other services to publish items
 * new CfnOutput(this, 'LoaderTopicArn', {
 *   value: loader.topic.topicArn
 * });
 * ```
 *
 * ## Direct Item Publishing
 *
 * External services can publish STAC items directly to the topic:
 *
 * ```bash
 * aws sns publish --topic-arn $ITEM_LOAD_TOPIC --message '{
 *   "type": "Feature",
 *   "stac_version": "1.0.0",
 *   "id": "example-item",
 *   "properties": {"datetime": "2021-01-01T00:00:00Z"},
 *   "geometry": {"type": "Polygon", "coordinates": [...]},
 *   "collection": "example-collection"
 * }'
 * ```
 *
 * ## S3 Event Configuration
 *
 * To enable S3 event-driven loading, configure S3 bucket notifications to send
 * events to the SNS topic when STAC items (.json or .geojson files) are uploaded:
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
 * When STAC items are uploaded to the configured S3 bucket, the loader will:
 * 1. Receive S3 event notifications via SNS
 * 2. Fetch the STAC item JSON from S3
 * 3. Validate and load the item into the pgstac database
 *
 * ## Monitoring and Troubleshooting
 *
 * - Monitor Lambda logs: `/aws/lambda/{FunctionName}`
 * - Check dead letter queue for failed items
 * - Use batch item failure reporting for partial batch processing
 * - CloudWatch metrics available for queue depth and Lambda performance
 *
 * @see {@link https://github.com/stactools-packages} for stactools packages
 * @see {@link https://github.com/stac-utils/pgstac} for pgstac documentation
 */
export class StacItemLoader extends Construct {
  /**
   * The SNS topic that receives STAC items and S3 event notifications for loading.
   *
   * This topic serves as the entry point for two types of events:
   * 1. Direct STAC item JSON documents published by external services
   * 2. S3 event notifications when STAC items are uploaded to configured buckets
   *
   * The topic fans out to the SQS queue for batched processing.
   */
  public readonly topic: sns.Topic;

  /**
   * The SQS queue that buffers messages before processing.
   *
   * This queue collects both direct STAC items from SNS and S3 event
   * notifications, batching them for efficient database operations.
   * Configured with a visibility timeout that accommodates Lambda
   * processing time plus buffer.
   */
  public readonly queue: sqs.Queue;

  /**
   * Dead letter queue for failed item loading attempts.
   *
   * Messages that fail processing after 5 attempts are sent here
   * for inspection and potential replay. Retains messages for 14 days
   * to allow for debugging and manual intervention.
   */
  public readonly deadLetterQueue: sqs.Queue;

  /**
   * The Lambda function that loads STAC items into the pgstac database.
   *
   * This Python function receives batches of messages from SQS and processes
   * them based on their type:
   * - Direct STAC items: Validates and loads directly into pgstac
   * - S3 events: Fetches STAC items from S3, validates, and loads into pgstac
   *
   * The function connects to PostgreSQL using credentials from Secrets Manager
   * and uses pypgstac for efficient database operations.
   */
  public readonly lambdaFunction: lambda.Function;

  constructor(scope: Construct, id: string, props: StacItemLoaderProps) {
    super(scope, id);

    const timeoutSeconds = props.lambdaTimeoutSeconds ?? 45;
    const lambdaRuntime = props.lambdaRuntime ?? lambda.Runtime.PYTHON_3_11;

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
      displayName: `${id}-StacItemLoaderTopic`,
    });

    // Subscribe the queue to the topic
    this.topic.addSubscription(
      new snsSubscriptions.SqsSubscription(this.queue)
    );

    // Create the lambda function
    this.lambdaFunction = new lambda.Function(this, "Function", {
      runtime: lambdaRuntime,
      handler: "stac_item_loader.handler.handler",
      code: lambda.Code.fromDockerBuild(path.join(__dirname, ".."), {
        file: "stac-item-loader/runtime/Dockerfile",
        platform: "linux/amd64",
        buildArgs: {
          PYTHON_VERSION: lambdaRuntime.toString().replace("python", ""),
          PGSTAC_VERSION: props.pgstacDb.pgstacVersion,
        },
      }),
      memorySize: props.memorySize ?? 1024,
      timeout: Duration.seconds(timeoutSeconds),
      logRetention: logs.RetentionDays.ONE_WEEK,
      environment: {
        PGSTAC_SECRET_ARN: props.pgstacDb.pgstacSecret.secretArn,
        ...props.environment,
      },
    });

    // Grant permissions to read the database secret
    props.pgstacDb.pgstacSecret.grantRead(this.lambdaFunction);

    // Add SQS event source to the lambda
    this.lambdaFunction.addEventSource(
      new lambdaEventSources.SqsEventSource(this.queue, {
        batchSize: props.batchSize ?? 1000,
        maxBatchingWindow: Duration.minutes(
          props.maxBatchingWindowMinutes ?? 1
        ),
        reportBatchItemFailures: true,
      })
    );

    // Create outputs
    new CfnOutput(this, "TopicArn", {
      value: this.topic.topicArn,
      description: "ARN of the StacItemLoader SNS Topic",
      exportName: "stac-item-loader-topic-arn",
    });

    new CfnOutput(this, "QueueUrl", {
      value: this.queue.queueUrl,
      description: "URL of the StacItemLoader SQS Queue",
      exportName: "stac-item-loader-queue-url",
    });

    new CfnOutput(this, "DeadLetterQueueUrl", {
      value: this.deadLetterQueue.queueUrl,
      description: "URL of the StacItemLoader Dead Letter Queue",
      exportName: "stac-item-loader-deadletter-queue-url",
    });

    new CfnOutput(this, "FunctionName", {
      value: this.lambdaFunction.functionName,
      description: "Name of the StacItemLoader Lambda Function",
      exportName: "stac-item-loader-function-name",
    });
  }
}
