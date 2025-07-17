import { aws_lambda as lambda } from "aws-cdk-lib";

export type CustomLambdaFunctionProps = lambda.FunctionProps | any;
export const DEFAULT_PGSTAC_VERSION = "0.9.5";
