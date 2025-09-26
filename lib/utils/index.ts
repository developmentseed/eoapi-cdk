import { aws_lambda as lambda } from "aws-cdk-lib";

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
  dockerBuildOptions?: lambda.DockerBuildAssetOptions
): lambda.Code {
  if (userCode) {
    return userCode;
  }

  if (!dockerBuildPath || !dockerBuildOptions) {
    throw new Error(
      "dockerBuildPath and dockerBuildOptions are required when no custom code is provided"
    );
  }

  return lambda.Code.fromDockerBuild(dockerBuildPath, dockerBuildOptions);
}
