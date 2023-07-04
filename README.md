# pgSTAC CDK construct

eoapi-cdk is a package of [AWS CDK constructs](https://docs.aws.amazon.com/prescriptive-guidance/latest/best-practices-cdk-typescript-iac/constructs-best-practices.html) designed to encapsulate eoAPI runtime code and best practices as simple reusable components.   

For more background on the included services see [The Earth Observation API](https://eoapi.dev/)

## Included constructs
Detailed API docs for the constructs can be found [here](https://developmentseed.org/cdk-pgstac/).

### Bastion Host
A bastion host is a secure gatewaty that provides access to resources in a private subnet.  In this case the eoAPI's pgSTAC instance.

![Alt text](/diagrams/bastion_diagram.png)

For more background on bastion hosts in AWS see [this article](https://dev.to/aws-builders/bastion-host-in-aws-vpc-2i63).

And for configuration instructions for this construct see [the docs](https://developmentseed.org/cdk-pgstac/#bastionhost-).

### pgSTAC Database
An [RDS](https://aws.amazon.com/rds/) instance with [pgSTAC](https://github.com/stac-utils/pgstac) installed and the Postgres parameters optimized for the selected instance type.

### STAC Ingestor
An API for large scale STAC data ingestion and validation into a pgSTAC instance. 

![ingestor](/diagrams/ingestor_diagram.png)

Authentication for the STAC Ingestor API can be configured with JWTs authenticated by JWKS.  To learn more about securing FastAPI applications with this approach see [Securing FastAPI with JWKS (AWS Cognito, Auth0)](https://alukach.com/posts/fastapi-rs256-jwt/).

A sample Cognito-based authentication system is available at [aws-asdi-auth](https://github.com/developmentseed/aws-asdi-auth).

### STAC API
A STAC API implementation using [stac-fastapi](https://github.com/stac-utils/stac-fastapi) with a [pgSTAC backend](https://github.com/stac-utils/stac-fastapi-pgstac). Packaged as a complete runtime for deployment with API Gateway and Lambda. 

### pgSTAC Titiler API
A complete dynamic tiling API using [https://github.com/stac-utils/titiler-pgstac] to create dynamic mosaics of assets based on [STAC Search queries](https://github.com/radiantearth/stac-api-spec/tree/master/item-search).  Packaged as a complete runtime for deployment with API Gateway and Lambda and fully integrated with the pgSTAC Database construct. 

## Published Packages

- https://pypi.org/project/cdk-pgstac/
- https://www.npmjs.com/package/cdk-pgstac/

## Release

Versioning is automatically handled via [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) and [Semantic Release](https://semantic-release.gitbook.io/semantic-release/).

_Warning_: If you rebase `main`, you must ensure that the commits referenced by tags point to commits that are within the `main` branch. If a commit references a commit that is no longer on the `main` branch, Semantic Release will fail to detect the correct version of the project. [More information](https://github.com/semantic-release/semantic-release/issues/1121#issuecomment-517945233).


