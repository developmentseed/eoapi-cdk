import { aws_lambda as lambda, CustomResource } from "aws-cdk-lib";
import { Construct } from "constructs";

export type CustomLambdaFunctionProps = lambda.FunctionProps | any;
export const DEFAULT_PGSTAC_VERSION = "0.9.5";

/**
 * Resolves Lambda code by using custom user code if provided,
 * otherwise builds a Docker image with the specified arguments.
 *
 * @param userCode - User-provided custom code (optional)
 * @param dockerBuildPath - Path for Docker build
 * @param dockerBuildOptions - Options for Docker build
 * @returns Lambda code configuration
 */
export function resolveLambdaCode(
  userCode?: lambda.Code,
  dockerBuildPath?: string,
  dockerBuildOptions?: lambda.DockerBuildAssetOptions,
): lambda.Code {
  if (userCode) {
    return userCode;
  }

  if (!dockerBuildPath || !dockerBuildOptions) {
    throw new Error(
      "dockerBuildPath and dockerBuildOptions are required when no custom code is provided",
    );
  }

  return lambda.Code.fromDockerBuild(dockerBuildPath, dockerBuildOptions);
}

/**
 * Type guard to check if a value has the secretBootstrapper property.
 *
 * This is used to detect PgStacDatabase constructs with PgBouncer enabled,
 * which expose a secretBootstrapper CustomResource that completes after
 * the database secret is updated with PgBouncer connection information.
 *
 * @param value - Value to check
 * @returns true if value has a defined secretBootstrapper property
 */
function hasSecretBootstrapper(
  value: any,
): value is { secretBootstrapper: CustomResource } {
  return (
    value &&
    typeof value === "object" &&
    "secretBootstrapper" in value &&
    value.secretBootstrapper !== undefined
  );
}

/**
 * Extracts database dependencies from a database construct if available.
 *
 * For PgStacDatabase with PgBouncer enabled, returns the secretBootstrapper
 * CustomResource which ensures the database secret is fully initialized before
 * dependent resources are created.
 *
 * This is critical for SnapStart Lambda functions, as the snapshot must not
 * be created until the secret contains the correct connection information.
 *
 * @param db - Database construct (may be PgStacDatabase, IDatabaseInstance, etc.)
 * @returns Array of CustomResources to depend on (empty if none available)
 */
export function extractDatabaseDependencies(db: any): CustomResource[] {
  if (hasSecretBootstrapper(db)) {
    return [db.secretBootstrapper];
  }
  return [];
}

/**
 * Creates a Lambda version with optional dependencies for SnapStart.
 *
 * When SnapStart is enabled, the version creation triggers snapshot creation.
 * Dependencies ensure the snapshot isn't created until prerequisites are met,
 * such as database secrets being fully initialized.
 *
 * This prevents race conditions where the SnapStart snapshot might capture
 * incorrect or incomplete configuration.
 *
 * @param scope - CDK construct scope
 * @param id - Construct ID for the version
 * @param lambdaFunction - Lambda function to create a version from
 * @param dependencies - Optional array of resources to depend on
 * @returns Lambda version with dependencies applied
 */
export function createLambdaVersionWithDependencies(
  scope: Construct,
  id: string,
  lambdaFunction: lambda.Function,
  dependencies?: CustomResource[],
): lambda.Version {
  const version = lambdaFunction.currentVersion;

  // Add dependencies to the version resource to ensure proper ordering
  if (dependencies && dependencies.length > 0) {
    dependencies.forEach((dep) => {
      version.node.addDependency(dep);
    });
  }

  return version;
}
