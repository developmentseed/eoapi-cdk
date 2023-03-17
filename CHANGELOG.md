## [2.6.2](https://github.com/developmentseed/cdk-pgstac/compare/v2.6.1...v2.6.2) (2023-03-16)


### Bug Fixes

* **ingestor:** queries require sequences ([#23](https://github.com/developmentseed/cdk-pgstac/issues/23)) ([00d71cc](https://github.com/developmentseed/cdk-pgstac/commit/00d71cc1d253e77f1cd11afe9e4b513a577a67a2))

## [2.6.1](https://github.com/developmentseed/cdk-pgstac/compare/v2.6.0...v2.6.1) (2023-03-16)


### Reverts

* Revert "Release 2.7.0. (#21)" (#22) ([f08e8e8](https://github.com/developmentseed/cdk-pgstac/commit/f08e8e8140c15ed608ab16a053641e20603bf7c5)), closes [#21](https://github.com/developmentseed/cdk-pgstac/issues/21) [#22](https://github.com/developmentseed/cdk-pgstac/issues/22)

# [2.6.0](https://github.com/developmentseed/cdk-pgstac/compare/v2.5.1...v2.6.0) (2023-03-10)


### Features

* collection endpoint ([#18](https://github.com/developmentseed/cdk-pgstac/issues/18)) ([d3e9911](https://github.com/developmentseed/cdk-pgstac/commit/d3e991155644d9da08ff7293976a284c252a383b))

## [2.5.1](https://github.com/developmentseed/cdk-pgstac/compare/v2.5.0...v2.5.1) (2022-12-06)


### Bug Fixes

* **ingestor-api:** Correct import path for settings ([be40af7](https://github.com/developmentseed/cdk-pgstac/commit/be40af70326f04d7ed9583569ad49f12da416d6f))

# [2.5.0](https://github.com/developmentseed/cdk-pgstac/compare/v2.4.0...v2.5.0) (2022-12-01)


### Features

* **ingestor:** Add flag to enable requester pays ([efc160d](https://github.com/developmentseed/cdk-pgstac/commit/efc160d3530a70d1fc8f88ef9dce4a4d48456834))

# [2.4.0](https://github.com/developmentseed/cdk-pgstac/compare/v2.3.1...v2.4.0) (2022-11-08)


### Features

* **bastion-host:** Append ec2 instance with 'bastion host' ([4ee8599](https://github.com/developmentseed/cdk-pgstac/commit/4ee8599b5e03799152e07df935be047821554a32))

## [2.3.1](https://github.com/developmentseed/cdk-pgstac/compare/v2.3.0...v2.3.1) (2022-11-08)


### Bug Fixes

* **bastion-host:** `createElasticIp` default to true ([ec99fad](https://github.com/developmentseed/cdk-pgstac/commit/ec99fad9d3606f4ca572229e82d992f3295f9045))

# [2.3.0](https://github.com/developmentseed/cdk-pgstac/compare/v2.2.1...v2.3.0) (2022-11-08)


### Features

* **bastion-host:** Make elastic IP optional ([d77b578](https://github.com/developmentseed/cdk-pgstac/commit/d77b578df0a713a993bfa81709485df7fbc423c3))

## [2.2.1](https://github.com/developmentseed/cdk-pgstac/compare/v2.2.0...v2.2.1) (2022-11-04)


### Bug Fixes

* **stac-db:** Report shared buffers in 8kb units ([d34f2cd](https://github.com/developmentseed/cdk-pgstac/commit/d34f2cd1a833438ffa4e24f062cf16901f8d5584))

# [2.2.0](https://github.com/developmentseed/cdk-pgstac/compare/v2.1.0...v2.2.0) (2022-11-03)


### Features

* **stac-db:** Provide sensible defaults for pgSTAC db parameters ([#1](https://github.com/developmentseed/cdk-pgstac/issues/1)) ([11eb89e](https://github.com/developmentseed/cdk-pgstac/commit/11eb89e45c8a6d4a5b07134b8957a1298f9305c8))

# [2.1.0](https://github.com/developmentseed/cdk-pgstac/compare/v2.0.0...v2.1.0) (2022-11-01)


### Features

* **ingestor-api:** Make apiEnv optional ([5841734](https://github.com/developmentseed/cdk-pgstac/commit/584173458e35a69cd7bc398acd3482dd21c58228))

# [2.0.0](https://github.com/developmentseed/cdk-pgstac/compare/v1.3.0...v2.0.0) (2022-11-01)


### chore

* **ci:** bump version ([d10c5b2](https://github.com/developmentseed/cdk-pgstac/commit/d10c5b2afcd7e38effedb5181a1ed7595b03495f))


### BREAKING CHANGES

* **ci:** Experiencing issues publishing GitHub releases
due to past deleted release. Bumping codebase to 2.0.0 to avoid
future issues.

# [1.3.0](https://github.com/developmentseed/cdk-pgstac/compare/v1.2.0...v1.3.0) (2022-11-01)


### Features

* **ingestor-api:** add StacIngestor construct ([d34c6cd](https://github.com/developmentseed/cdk-pgstac/commit/d34c6cdd2c0df838467289a19c2b96adf1c0777e))
* **stac-api:** export API url from pgStacApi construct ([261dbd2](https://github.com/developmentseed/cdk-pgstac/commit/261dbd2bb85ad895f61922740d211fa8b96c3761))

# [1.2.0](https://github.com/developmentseed/cdk-pgstac/compare/v1.1.0...v1.2.0) (2022-10-26)


### Features

* add bastion host ([de52ad7](https://github.com/developmentseed/cdk-pgstac/commit/de52ad76a2098c85cb4eef6aa0445fcbbea2e618))
* add PgStacApiLambda ([a092a7a](https://github.com/developmentseed/cdk-pgstac/commit/a092a7aee26ac39210fb7ce7023a09905823500c))
* Support customizing bootstrap args ([a23356f](https://github.com/developmentseed/cdk-pgstac/commit/a23356f195db8353f08ac0e1fa278e68b5876817))
