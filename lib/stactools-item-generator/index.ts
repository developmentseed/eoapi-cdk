import {
  aws_ec2 as ec2,
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
import { Platform } from "aws-cdk-lib/aws-ecr-assets";
import * as path from "path";
import { CustomLambdaFunctionProps } from "../utils";

/**
 * Configuration properties for the StactoolsItemGenerator construct.
 *
 * The StactoolsItemGenerator is part of a two-phase serverless STAC ingestion pipeline
 * that generates STAC items from source data. This construct creates the
 * infrastructure for the first phase of the pipeline - processing metadata
 * about assets and transforming them into standardized STAC items.
 *
 * @example
 * const generator = new StactoolsItemGenerator(this, 'ItemGenerator', {
 *   itemLoadTopicArn: loader.topic.topicArn,
 *   lambdaTimeoutSeconds: 120,
 *   maxConcurrency: 100,
 *   batchSize: 10
 * });
 */
export interface StactoolsItemGeneratorProps {
  /**
   * The lambda runtime to use for the item generation function.
   *
   * The function is containerized using Docker and can accommodate various
   * stactools packages. The runtime version should be compatible with the
   * packages you plan to use for STAC item generation.
   *
   * @default lambda.Runtime.PYTHON_3_11
   */
  readonly lambdaRuntime?: lambda.Runtime;

  /**
   * VPC into which the lambda should be deployed.
   */
  readonly vpc?: ec2.IVpc;

  /**
   * Subnet into which the lambda should be deployed.
   */
  readonly subnetSelection?: ec2.SubnetSelection;

  /**
   * The timeout for the item generation lambda in seconds.
   *
   * This should accommodate the time needed to:
   * - Install stactools packages using uvx
   * - Download and process source data
   * - Generate STAC metadata
   * - Publish results to SNS
   *
   * The SQS visibility timeout will be set to this value plus 10 seconds.
   *
   * @default 120
   */
  readonly lambdaTimeoutSeconds?: number;

  /**
   * Memory size for the lambda function in MB.
   *
   * Higher memory allocation may be needed for processing large geospatial
   * datasets or when stactools packages have high memory requirements.
   * More memory also provides proportionally more CPU power.
   *
   * @default 1024
   */
  readonly memorySize?: number;

  /**
   * Maximum number of concurrent executions.
   *
   * This controls how many item generation tasks can run simultaneously.
   * Higher concurrency enables faster processing of large batches but
   * may strain downstream systems or external data sources.
   *
   * @default 100
   */
  readonly maxConcurrency?: number;

  /**
   * SQS batch size for lambda event source.
   *
   * This determines how many generation requests are processed together
   * in a single lambda invocation. Unlike the loader, generation typically
   * processes items individually, so smaller batch sizes are common.
   *
   * @default 10
   */
  readonly batchSize?: number;

  /**
   * Additional environment variables for the lambda function.
   *
   * These will be merged with default environment variables including
   * ITEM_LOAD_TOPIC_ARN and LOG_LEVEL. Use this for custom configuration
   * or to pass credentials for external data sources.
   */
  readonly environment?: { [key: string]: string };

  /**
   * ARN of the SNS topic to publish generated items to.
   *
   * This is typically the topic from a StacLoader construct.
   * Generated STAC items will be published here for downstream
   * processing and database insertion.
   */
  readonly itemLoadTopicArn: string;

  /**
   * Can be used to override the default lambda function properties.
   *
   * @default - defined in the construct.
   */
  readonly lambdaFunctionOptions?: CustomLambdaFunctionProps;
}

/**
 * AWS CDK Construct for STAC Item Generation Infrastructure
 *
 * The StactoolsItemGenerator creates a serverless, event-driven system for generating
 * STAC (SpatioTemporal Asset Catalog) items from source data. This construct
 * implements the first phase of a two-stage ingestion pipeline that transforms
 * raw geospatial data into standardized STAC metadata.
 *
 * ## Architecture Overview
 *
 * This construct creates the following AWS resources:
 * - **SNS Topic**: Entry point for triggering item generation workflows
 * - **SQS Queue**: Buffers generation requests (120-second visibility timeout)
 * - **Dead Letter Queue**: Captures failed messages after 5 processing attempts
 * - **Lambda Function**: Containerized function that generates STAC items using stactools
 *
 * ## Data Flow
 *
 * 1. External systems publish ItemRequest messages to the SNS topic with metadata about assets
 * 2. The SQS queue buffers these messages and triggers the Lambda function
 * 3. The Lambda function:
 *    - Uses `uvx` to install the required stactools package
 *    - Executes the `create-item` CLI command with provided arguments
 *    - Publishes generated STAC items to the ItemLoad topic
 * 4. Failed processing attempts are sent to the dead letter queue
 *
 * ## Operational Characteristics
 *
 * - **Scalability**: Lambda scales automatically based on queue depth (up to maxConcurrency)
 * - **Flexibility**: Supports any stactools package through dynamic installation
 * - **Reliability**: Dead letter queue captures failed generation attempts
 * - **Isolation**: Each generation task runs in a fresh container environment
 * - **Observability**: CloudWatch logs retained for one week
 *
 * ## Message Schema
 *
 * The function expects messages matching the ItemRequest model:
 *
 * ```json
 * {
 *   "package_name": "stactools-glad-global-forest-change",
 *   "group_name": "gladglobalforestchange",
 *   "create_item_args": [
 *     "https://example.com/data.tif"
 *   ],
 *   "collection_id": "glad-global-forest-change-1.11"
 * }
 * ```
 *
 * ## Usage Example
 *
 * ```typescript
 * // Create item loader first (or get existing topic ARN)
 * const loader = new StacLoader(this, 'ItemLoader', {
 *   pgstacDb: database
 * });
 *
 * // Create item generator that feeds the loader
 * const generator = new StactoolsItemGenerator(this, 'ItemGenerator', {
 *   itemLoadTopicArn: loader.topic.topicArn,
 *   lambdaTimeoutSeconds: 120,    // Allow time for package installation
 *   maxConcurrency: 100,          // Control parallel processing
 *   batchSize: 10                 // Process 10 requests per invocation
 * });
 *
 * // Grant permission to publish to the loader topic
 * loader.topic.grantPublish(generator.lambdaFunction);
 * ```
 *
 * ## Publishing Generation Requests
 *
 * Send messages to the generator topic to trigger item creation:
 *
 * ```bash
 * aws sns publish --topic-arn $ITEM_GEN_TOPIC --message '{
 *   "package_name": "stactools-glad-global-forest-change",
 *   "group_name": "gladglobalforestchange",
 *   "create_item_args": [
 *     "https://storage.googleapis.com/earthenginepartners-hansen/GFC-2023-v1.11/Hansen_GFC-2023-v1.11_gain_40N_080W.tif"
 *   ],
 *   "collection_id": "glad-global-forest-change-1.11"
 * }'
 * ```
 *
 * ## Batch Processing Example
 *
 * For processing many assets, you can loop through URLs:
 *
 * ```bash
 * while IFS= read -r url; do
 *   aws sns publish --topic-arn "$ITEM_GEN_TOPIC" --message "{
 *     \"package_name\": \"stactools-glad-glclu2020\",
 *     \"group_name\": \"gladglclu2020\",
 *     \"create_item_args\": [\"$url\"]
 *   }"
 * done < urls.txt
 * ```
 *
 * ## Monitoring and Troubleshooting
 *
 * - Monitor Lambda logs: `/aws/lambda/{FunctionName}`
 * - Check dead letter queue for failed generation attempts
 * - Use CloudWatch metrics to track processing rates and errors
 * - Failed items can be replayed from the dead letter queue
 *
 * ## Supported Stactools Packages
 *
 * Any package available on PyPI that follows the stactools plugin pattern
 * can be used. Examples include:
 * - `stactools-glad-global-forest-change`
 * - `stactools-glad-glclu2020`
 * - `stactools-landsat`
 * - `stactools-sentinel2`
 *
 * @see {@link https://github.com/stactools-packages} for available stactools packages
 * @see {@link https://stactools.readthedocs.io/} for stactools documentation
 */
export class StactoolsItemGenerator extends Construct {
  /**
   * The SQS queue that buffers item generation requests.
   *
   * This queue receives messages from the SNS topic containing ItemRequest
   * payloads. It's configured with a visibility timeout that matches the
   * Lambda timeout plus buffer time to prevent duplicate processing.
   */
  public readonly queue: sqs.Queue;

  /**
   * Dead letter queue for failed item generation attempts.
   *
   * Messages that fail processing after 5 attempts are sent here for
   * inspection and potential replay. This helps with debugging stactools
   * package issues, network failures, or malformed requests.
   */
  public readonly deadLetterQueue: sqs.Queue;

  /**
   * The SNS topic that receives item generation requests.
   *
   * External systems publish ItemRequest messages to this topic to trigger
   * STAC item generation. The topic fans out to the SQS queue for processing.
   */
  public readonly topic: sns.Topic;

  /**
   * The containerized Lambda function that generates STAC items.
   *
   * This Docker-based function dynamically installs stactools packages
   * using uvx, processes source data, and publishes generated STAC items
   * to the configured ItemLoad SNS topic.
   */
  public readonly lambdaFunction: lambda.DockerImageFunction;

  constructor(
    scope: Construct,
    id: string,
    props: StactoolsItemGeneratorProps
  ) {
    super(scope, id);

    const timeoutSeconds = props.lambdaTimeoutSeconds ?? 120;
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
      displayName: `${id}-ItemGenTopic`,
    });

    // Subscribe the queue to the topic
    this.topic.addSubscription(
      new snsSubscriptions.SqsSubscription(this.queue)
    );

    // Create the lambda function
    this.lambdaFunction = new lambda.DockerImageFunction(this, "Function", {
      code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, ".."), {
        file: "stactools-item-generator/runtime/Dockerfile",
        platform: Platform.LINUX_AMD64,
        buildArgs: {
          PYTHON_VERSION: lambdaRuntime.toString().replace("python", ""),
        },
      }),
      memorySize: props.memorySize ?? 1024,
      vpc: props.vpc,
      vpcSubnets: props.subnetSelection,
      timeout: Duration.seconds(timeoutSeconds),
      logRetention: logs.RetentionDays.ONE_WEEK,
      environment: {
        ITEM_LOAD_TOPIC_ARN: props.itemLoadTopicArn,
        LOG_LEVEL: "INFO",
        ...props.environment,
      },
      // overwrites defaults with user-provided configurable properties
      ...props.lambdaFunctionOptions,
    });

    // Add SQS event source to the lambda
    this.lambdaFunction.addEventSource(
      new lambdaEventSources.SqsEventSource(this.queue, {
        batchSize: props.batchSize ?? 10,
        reportBatchItemFailures: true,
        maxConcurrency: props.maxConcurrency ?? 100,
      })
    );

    // Grant permissions to publish to the item load topic
    // Note: This will be granted externally since we only have the ARN
    // The consuming construct should handle this permission

    // Create outputs
    new CfnOutput(this, "TopicArn", {
      value: this.topic.topicArn,
      description: "ARN of the StactoolsItemGenerator SNS Topic",
      exportName: "stactools-item-generator-topic-arn",
    });

    new CfnOutput(this, "QueueUrl", {
      value: this.queue.queueUrl,
      description: "URL of the StactoolsItemGenerator SQS Queue",
      exportName: "stactools-item-generator-queue-url",
    });

    new CfnOutput(this, "DeadLetterQueueUrl", {
      value: this.deadLetterQueue.queueUrl,
      description: "URL of the StactoolsItemGenerator Dead Letter Queue",
      exportName: "stactools-item-generator-deadletter-queue-url",
    });

    new CfnOutput(this, "FunctionName", {
      value: this.lambdaFunction.functionName,
      description: "Name of the StactoolsItemGenerator Lambda Function",
      exportName: "stactools-item-generator-function-name",
    });
  }
}
