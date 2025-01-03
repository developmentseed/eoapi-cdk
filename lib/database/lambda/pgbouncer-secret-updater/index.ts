import {
  SecretsManagerClient,
  GetSecretValueCommand,
  PutSecretValueCommand,
} from "@aws-sdk/client-secrets-manager";
import { CloudFormationCustomResourceEvent, Context } from "aws-lambda";
import * as https from "https";
import * as url from "url";

interface ResponseData {
  SecretArn?: string;
  Error?: string;
}

function sendResponse(
  event: CloudFormationCustomResourceEvent,
  context: Context,
  responseStatus: "SUCCESS" | "FAILED",
  responseData: ResponseData,
  physicalResourceId?: string
): Promise<void> {
  return new Promise((resolve, reject) => {
    const responseBody = JSON.stringify({
      Status: responseStatus,
      Reason:
        "See the details in CloudWatch Log Stream: " + context.logStreamName,
      PhysicalResourceId: physicalResourceId || context.logStreamName,
      StackId: event.StackId,
      RequestId: event.RequestId,
      LogicalResourceId: event.LogicalResourceId,
      Data: responseData,
    });

    console.log("Response body:", responseBody);

    const parsedUrl = url.parse(event.ResponseURL);
    const options = {
      hostname: parsedUrl.hostname,
      port: 443,
      path: parsedUrl.path,
      method: "PUT",
      headers: {
        "content-type": "",
        "content-length": responseBody.length,
      },
    };

    const request = https.request(options, (response) => {
      console.log("Status code:", response.statusCode);
      console.log("Status message:", response.statusMessage);
      resolve();
    });

    request.on("error", (error) => {
      console.log("sendResponse Error:", error);
      reject(error);
    });

    request.write(responseBody);
    request.end();
  });
}

const client = new SecretsManagerClient();

interface HandlerEnvironment {
  SOURCE_SECRET_ARN: string;
  TARGET_SECRET_ARN: string;
}

function validateEnvironment(): HandlerEnvironment {
  const { SOURCE_SECRET_ARN, TARGET_SECRET_ARN } = process.env;

  if (!SOURCE_SECRET_ARN) {
    throw new Error("SOURCE_SECRET_ARN environment variable is required");
  }
  if (!TARGET_SECRET_ARN) {
    throw new Error("TARGET_SECRET_ARN environment variable is required");
  }

  return {
    SOURCE_SECRET_ARN,
    TARGET_SECRET_ARN,
  };
}

export const handler = async (
  event: CloudFormationCustomResourceEvent,
  context: Context
) => {
  console.log("Event:", JSON.stringify(event, null, 2));

  try {
    const env = validateEnvironment();

    // Skip processing for DELETE requests, but still send response
    if (event.RequestType === "Delete") {
      await sendResponse(
        event,
        context,
        "SUCCESS",
        {},
        event.PhysicalResourceId
      );
      return;
    }

    const instanceIp = event.ResourceProperties.instanceIp;

    // Get the original secret value
    const getSecretResponse = await client.send(
      new GetSecretValueCommand({
        SecretId: env.SOURCE_SECRET_ARN,
      })
    );

    if (!getSecretResponse.SecretString) {
      throw new Error("Secret string is empty");
    }

    // Parse the secret string
    const secretData = JSON.parse(getSecretResponse.SecretString);

    // Update the host value with the PgBouncer instance IP
    secretData.host = instanceIp;

    // Put the modified secret value
    await client.send(
      new PutSecretValueCommand({
        SecretId: env.TARGET_SECRET_ARN,
        SecretString: JSON.stringify(secretData),
      })
    );

    const physicalResourceId = env.TARGET_SECRET_ARN;
    const responseData = {
      SecretArn: env.TARGET_SECRET_ARN,
    };

    await sendResponse(
      event,
      context,
      "SUCCESS",
      responseData,
      physicalResourceId
    );
  } catch (error: unknown) {
    console.error("Error:", error);
    const errorMessage =
      error instanceof Error ? error.message : "An unknown error occurred";
    await sendResponse(event, context, "FAILED", { Error: errorMessage });
    throw error;
  }
};
