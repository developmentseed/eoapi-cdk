import {
    aws_lambda as lambda,
    aws_logs as logs,
    Duration,
  } from "aws-cdk-lib";

export interface CustomLambdaFunctionOptions {

    /***
     * The runtime environment for the Lambda function that you are uploading.
     */
    readonly runtime: lambda.Runtime;

    /**
     * The function execution time (in seconds) after which Lambda terminates the function.
     */
    readonly timeout: Duration;

    /**
     * The amount of memory, in MB, that is allocated to your Lambda function.
     */
    readonly memorySize: number;

    /**
     * handler for the lambda function
     */
    readonly handler: string;

    /**
     * log retention period for the lambda function
     */
    readonly logRetention: logs.RetentionDays;

  }
