import {
    aws_lambda as lambda,
  } from "aws-cdk-lib";

export type CustomLambdaFunctionProps = lambda.FunctionProps | any;
