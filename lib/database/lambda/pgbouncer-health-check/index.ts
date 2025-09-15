import {
  SSMClient,
  SendCommandCommand,
  GetCommandInvocationCommand,
  DescribeInstanceInformationCommand,
} from "@aws-sdk/client-ssm";
import { CloudFormationCustomResourceEvent, Context } from "aws-lambda";
import * as https from "https";
import * as url from "url";
import * as fs from "fs";
import * as path from "path";

const ssmClient = new SSMClient();

interface ResponseData {
  Message?: string;
  Output?: string;
  Reason?: string;
}

interface HealthCheckResult {
  success: boolean;
  output?: string;
  error?: string;
}

const sleep = (ms: number): Promise<void> =>
  new Promise((resolve) => setTimeout(resolve, ms));

async function sendResponse(
  event: CloudFormationCustomResourceEvent,
  context: Context,
  responseStatus: "SUCCESS" | "FAILED",
  responseData: ResponseData,
  physicalResourceId?: string
): Promise<void> {
  const responseBody = JSON.stringify({
    Status: responseStatus,
    Reason:
      responseData.Reason ||
      `See CloudWatch Log Stream: ${context.logStreamName}`,
    PhysicalResourceId: physicalResourceId || context.logStreamName,
    StackId: event.StackId,
    RequestId: event.RequestId,
    LogicalResourceId: event.LogicalResourceId,
    Data: responseData,
  });

  const parsedUrl = url.parse(event.ResponseURL);

  return new Promise((resolve, reject) => {
    const options = {
      hostname: parsedUrl.hostname,
      port: 443,
      path: parsedUrl.path,
      method: "PUT",
      headers: {
        "Content-Type": "",
        "Content-Length": responseBody.length,
      },
    };

    const req = https.request(options, (res) => {
      console.log(`STATUS: ${res.statusCode}`);
      console.log(`HEADERS: ${JSON.stringify(res.headers)}`);
      resolve();
    });

    req.on("error", (err) => {
      console.log("sendResponse Error:", err);
      reject(err);
    });

    req.write(responseBody);
    req.end();
  });
}

async function waitForInstanceReady(
  instanceId: string,
  maxWaitMinutes: number = 8
): Promise<boolean> {
  console.log(
    `Waiting for instance ${instanceId} to be ready for SSM commands...`
  );
  const maxAttempts = maxWaitMinutes * 4; // Check every 15 seconds

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      const command = new DescribeInstanceInformationCommand({
        InstanceInformationFilterList: [
          {
            key: "InstanceIds",
            valueSet: [instanceId],
          },
        ],
      });

      const result = await ssmClient.send(command);

      if (
        result.InstanceInformationList &&
        result.InstanceInformationList.length > 0
      ) {
        const instance = result.InstanceInformationList[0];
        if (instance.PingStatus === "Online") {
          console.log(
            `Instance ${instanceId} is online and ready for SSM commands`
          );
          return true;
        }
        console.log(
          `Instance ${instanceId} ping status: ${instance.PingStatus}, attempt ${attempt}/${maxAttempts}`
        );
      } else {
        console.log(
          `Instance ${instanceId} not found in SSM, attempt ${attempt}/${maxAttempts}`
        );
      }
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Unknown error";
      console.log(
        `Error checking instance readiness (attempt ${attempt}/${maxAttempts}):`,
        errorMessage
      );
    }

    if (attempt < maxAttempts) {
      await sleep(15000); // Wait 15 seconds between attempts
    }
  }

  throw new Error(
    `Instance ${instanceId} did not become ready for SSM commands within ${maxWaitMinutes} minutes`
  );
}

async function checkPgBouncerHealth(
  instanceId: string
): Promise<HealthCheckResult> {
  console.log(`Running health check on instance ${instanceId}`);

  // Load health check script from file
  const scriptPath = path.join(__dirname, "health-check.sh");
  let healthCheckScript: string;

  try {
    healthCheckScript = fs.readFileSync(scriptPath, "utf8");
  } catch (error) {
    console.error("Failed to load health check script:", error);
    return {
      success: false,
      error: `Failed to load health check script: ${error}`,
    };
  }

  // Use the entire script as a single command
  const healthCheckCommands = [healthCheckScript];

  const command = new SendCommandCommand({
    InstanceIds: [instanceId],
    DocumentName: "AWS-RunShellScript",
    Parameters: {
      commands: healthCheckCommands,
      executionTimeout: ["600"], // 10 minutes timeout
    },
    Comment: "PgBouncer comprehensive health check with setup validation",
    TimeoutSeconds: 600,
  });

  try {
    console.log("Sending SSM command...");
    const result = await ssmClient.send(command);
    const commandId = result.Command?.CommandId;

    if (!commandId) {
      return {
        success: false,
        error: "Failed to get command ID from SSM response",
      };
    }

    console.log(`Command sent with ID: ${commandId}`);

    // Wait for command to complete
    const maxAttempts = 60; // 10 minutes with 10-second intervals
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      await sleep(10000); // Wait 10 seconds between status checks

      try {
        const invocationCommand = new GetCommandInvocationCommand({
          CommandId: commandId,
          InstanceId: instanceId,
        });

        const invocation = await ssmClient.send(invocationCommand);

        console.log(
          `Command status (attempt ${attempt}): ${invocation.Status}`
        );

        if (invocation.Status === "Success") {
          console.log("Health check passed!");
          console.log("STDOUT:", invocation.StandardOutputContent);
          return {
            success: true,
            output: invocation.StandardOutputContent,
          };
        } else if (invocation.Status === "Failed") {
          console.log("Health check failed!");
          console.log("STDOUT:", invocation.StandardOutputContent);
          console.log("STDERR:", invocation.StandardErrorContent);
          return {
            success: false,
            error: `Health check failed: ${invocation.StandardErrorContent}`,
            output: invocation.StandardOutputContent,
          };
        } else if (
          ["Cancelled", "TimedOut", "Cancelling"].includes(
            invocation.Status || ""
          )
        ) {
          return {
            success: false,
            error: `Health check ${invocation.Status?.toLowerCase()}`,
          };
        }
        // Continue waiting for InProgress, Pending, Delayed states
      } catch (error: any) {
        if (error.name === "InvocationDoesNotExist") {
          console.log(
            `Command invocation not yet available (attempt ${attempt})`
          );
          continue;
        }
        throw error;
      }
    }

    return {
      success: false,
      error: "Health check timed out waiting for command completion",
    };
  } catch (error) {
    const errorMessage =
      error instanceof Error ? error.message : "Unknown error";
    console.log("Error running health check:", error);
    return {
      success: false,
      error: `Health check error: ${errorMessage}`,
    };
  }
}

export const handler = async (
  event: CloudFormationCustomResourceEvent,
  context: Context
): Promise<void> => {
  console.log("Event:", JSON.stringify(event, null, 2));

  const instanceId = event.ResourceProperties?.InstanceId;
  const requestType = event.RequestType;

  try {
    if (requestType === "Delete") {
      console.log("Delete request - no action needed");
      await sendResponse(event, context, "SUCCESS", {});
      return;
    }

    if (!instanceId) {
      throw new Error("InstanceId is required");
    }

    console.log(`Processing ${requestType} request for instance ${instanceId}`);

    // Wait for instance to be ready for SSM
    await waitForInstanceReady(instanceId);

    // Run health check
    const healthResult = await checkPgBouncerHealth(instanceId);

    if (healthResult.success) {
      console.log("PgBouncer health check passed");
      await sendResponse(
        event,
        context,
        "SUCCESS",
        {
          Message: "PgBouncer is healthy",
        },
        `pgbouncer-health-${instanceId}`
      );
    } else {
      console.log("PgBouncer health check failed:", healthResult.error);
      await sendResponse(
        event,
        context,
        "FAILED",
        {
          Reason: `PgBouncer health check failed: ${healthResult.error}`,
        },
        `pgbouncer-health-${instanceId}`
      );
    }
  } catch (error) {
    const errorMessage =
      error instanceof Error ? error.message : "Unknown error occurred";
    console.log("Handler error:", error);
    await sendResponse(
      event,
      context,
      "FAILED",
      {
        Reason: errorMessage,
      },
      `pgbouncer-health-${instanceId || "unknown"}`
    );
  }
};
