# pgSTAC CDK construct

## Published Packages

- https://pypi.org/project/cdk-pgstac/
- https://www.npmjs.com/package/cdk-pgstac/

## Release

Versioning is automatically handled via [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) and [Semantic Release](https://semantic-release.gitbook.io/semantic-release/).

_Warning_: If you rebase `main`, you must ensure that the commits referenced by tags point to commits that are within the `main` branch. If a commit references a commit that is no longer on the `main` branch, Semantic Release will fail to detect the correct version of the project. [More information](https://github.com/semantic-release/semantic-release/issues/1121#issuecomment-517945233).

## Local Development

```bash
docker-compose up
docker exec db python3 /asset/handler.py
```
