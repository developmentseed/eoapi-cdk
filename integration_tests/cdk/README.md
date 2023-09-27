This is a non-forked version of [eoapi-template](https://github.com/developmentseed/eoapi-template).

# Deployment CDK code for eoapi-cdk integration tests

This is a wrapper CDK code that provides the `eoapi-cdk` deployment to run integration tests on the latest releases of the `eoapi-cdk` constructs.

## Requirements

- python
- docker
- node
- AWS credentials environment variables configured to point to an account. 
- **Optional** a `config.yaml` file to override the default deployment settings defined in `config.py`.

## Installation

Install python dependencies with 

```
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Install the latest `eoapi-cdk` either from PyPI:

```
pip install eoapi-cdk
```

Or alternatively, compile and package from the root of this repository to get the python version of the constructs locally.

Also install node dependencies with 

```
npm install
```

Verify that the `cdk` CLI is available. Since `aws-cdk` is installed as a local dependency, you can use the `npx` node package runner tool, that comes with `npm`.

```
npx cdk --version
```

## Deployment

First, synthesize the app 

```
npx cdk synth --all
```

Then, deploy

```
npx cdk deploy --all --require-approval never
```