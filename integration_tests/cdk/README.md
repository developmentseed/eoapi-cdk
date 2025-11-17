# Deployment CDK code for eoapi-cdk deployment tests

This is a wrapper CDK code that is used to test a deployment of the `eoapi-cdk` constructs.

## Requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- docker
- node
- AWS credentials environment variables configured to point to an account.

## Installation

From the top level of this repository, install **eoapi-cdk**:

```sh
npm run install:all
npm run build
npm run package
uv sync --group deploy
uv pip install dist/python/*.gz
source .venv/bin/activate
```

Then, go to the integration deploy directory:

```sh
cd integration_tests/cdk
npm install
```

Verify that the `cdk` CLI is available. Since `aws-cdk` is installed as a local dependency, you can use the `npx` node package runner tool, that comes with `npm`.

```sh
npx cdk --version
```

## Deployment

First, synthesize the app

```sh
npx cdk synth --all
```

Then, deploy

```sh
npx cdk deploy --all --require-approval never
```
