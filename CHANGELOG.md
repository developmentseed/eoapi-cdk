# [11.1.0](https://github.com/developmentseed/eoapi-cdk/compare/v11.0.0...v11.1.0) (2026-01-30)


### Features

* only re-deploy db bootstrap if code or config parameters change ([#225](https://github.com/developmentseed/eoapi-cdk/issues/225)) ([ef48d98](https://github.com/developmentseed/eoapi-cdk/commit/ef48d982f50a107396975854fc0b00d39ce2f4b2))

# [11.0.0](https://github.com/developmentseed/eoapi-cdk/compare/v10.4.3...v11.0.0) (2026-01-27)


* feat!: upgrade to latest major/minor versions of core runtime libraries ([#224](https://github.com/developmentseed/eoapi-cdk/issues/224)) ([da42aea](https://github.com/developmentseed/eoapi-cdk/commit/da42aeaf028a7f80df751e9def47d4c1daae2d7a))


### BREAKING CHANGES

* upgrade to titiler-pgstac>=2.0.0,<2.1.0,
deps: upgrade to tipg>=1.3,<1.4
deps: upgrade to stac-fastapi-pgstac>=6.2,<6.3

## [10.4.3](https://github.com/developmentseed/eoapi-cdk/compare/v10.4.2...v10.4.3) (2026-01-24)


### Bug Fixes

* **deps:** upgrade python packages in uv.lock files ([#222](https://github.com/developmentseed/eoapi-cdk/issues/222)) ([6d6a3d4](https://github.com/developmentseed/eoapi-cdk/commit/6d6a3d49efcc1375dbb0d90cbf3c5a6fb96b773c))

## [10.4.2](https://github.com/developmentseed/eoapi-cdk/compare/v10.4.1...v10.4.2) (2025-12-19)


### Bug Fixes

* add pgbouncer secretBootstrapper as a dependency for lambda functions ([#221](https://github.com/developmentseed/eoapi-cdk/issues/221)) ([6b141e9](https://github.com/developmentseed/eoapi-cdk/commit/6b141e93e0c2a60658047e1d8bbd569e0ff0b312))

## [10.4.1](https://github.com/developmentseed/eoapi-cdk/compare/v10.4.0...v10.4.1) (2025-12-01)


### Bug Fixes

* node lambda version ([#216](https://github.com/developmentseed/eoapi-cdk/issues/216)) ([f777304](https://github.com/developmentseed/eoapi-cdk/commit/f777304130b15e1be56a7203db4c175ba95b2c2d))

# [10.4.0](https://github.com/developmentseed/eoapi-cdk/compare/v10.3.0...v10.4.0) (2025-11-03)


### Features

* update runtime versions, use uv in docker builds ([#208](https://github.com/developmentseed/eoapi-cdk/issues/208)) ([1a228e1](https://github.com/developmentseed/eoapi-cdk/commit/1a228e1f4c91499b5a2b62e76a59736648ec3168))

# [10.3.0](https://github.com/developmentseed/eoapi-cdk/compare/v10.2.5...v10.3.0) (2025-09-30)


### Features

* add option to enable SnapStart for Lambda functions ([#198](https://github.com/developmentseed/eoapi-cdk/issues/198)) ([b377a56](https://github.com/developmentseed/eoapi-cdk/commit/b377a5624781bf66aa677cbf40aee80352886851))

## [10.2.5](https://github.com/developmentseed/eoapi-cdk/compare/v10.2.4...v10.2.5) (2025-09-26)


### Bug Fixes

* refactor Lambda constructs to only build custom image if provided ([#187](https://github.com/developmentseed/eoapi-cdk/issues/187)) ([31d0ec0](https://github.com/developmentseed/eoapi-cdk/commit/31d0ec0f786a5ac00ffbbacfc2215828d5922fd4))

## [10.2.4](https://github.com/developmentseed/eoapi-cdk/compare/v10.2.3...v10.2.4) (2025-09-16)


### Bug Fixes

* fix typo in distribute.yaml ([f981c01](https://github.com/developmentseed/eoapi-cdk/commit/f981c01558395303ee3feb8f5076c4d6d7338d59))

## [10.2.3](https://github.com/developmentseed/eoapi-cdk/compare/v10.2.2...v10.2.3) (2025-09-16)


### Bug Fixes

* upgrade node-version ([ca58ef9](https://github.com/developmentseed/eoapi-cdk/commit/ca58ef9a580c66224945a0f82225e8535dde34e6))

## [10.2.2](https://github.com/developmentseed/eoapi-cdk/compare/v10.2.1...v10.2.2) (2025-09-15)


### Bug Fixes

* fix upload path for npmjs ([#185](https://github.com/developmentseed/eoapi-cdk/issues/185)) ([f6d59b8](https://github.com/developmentseed/eoapi-cdk/commit/f6d59b81138c1bf7e5ecbc0c75b90629ce8062c5))

## [10.2.1](https://github.com/developmentseed/eoapi-cdk/compare/v10.2.0...v10.2.1) (2025-09-15)


### Bug Fixes

* add token permissions for OIDC publishing ([#184](https://github.com/developmentseed/eoapi-cdk/issues/184)) ([6641cfa](https://github.com/developmentseed/eoapi-cdk/commit/6641cfab582725625057ebc3292750d3a65d37d3))

# [10.2.0](https://github.com/developmentseed/eoapi-cdk/compare/v10.1.1...v10.2.0) (2025-09-15)


### Features

* pgbouncer health check ([#183](https://github.com/developmentseed/eoapi-cdk/issues/183)) ([d560291](https://github.com/developmentseed/eoapi-cdk/commit/d560291aaa2e43b4f5327d26ed1e7db69bc71362))

## [10.1.1](https://github.com/developmentseed/eoapi-cdk/compare/v10.1.0...v10.1.1) (2025-08-21)


### Bug Fixes

* include libexpat.so.1 in the titiler code package ([#182](https://github.com/developmentseed/eoapi-cdk/issues/182)) ([b461ec0](https://github.com/developmentseed/eoapi-cdk/commit/b461ec0dfa57e9ef6316e17ca8e79cd1cbc58459))

# [10.1.0](https://github.com/developmentseed/eoapi-cdk/compare/v10.0.0...v10.1.0) (2025-08-15)


### Features

* **python:** bump to 3.12 ([#178](https://github.com/developmentseed/eoapi-cdk/issues/178)) ([2a62011](https://github.com/developmentseed/eoapi-cdk/commit/2a62011a99bbef92ceb125496c7405e3516caed8))

# [10.0.0](https://github.com/developmentseed/eoapi-cdk/compare/v9.2.1...v10.0.0) (2025-08-08)


### Features

* **stac-api:** retry the stac-fastapi-pgstac version bump release ([#175](https://github.com/developmentseed/eoapi-cdk/issues/175)) ([151c6b8](https://github.com/developmentseed/eoapi-cdk/commit/151c6b8773a3cfdbc6811dd5400ae208b2539761))


### BREAKING CHANGES

* **stac-api:** pgstac envvar names changed

## [9.2.1](https://github.com/developmentseed/eoapi-cdk/compare/v9.2.0...v9.2.1) (2025-07-29)


### Bug Fixes

* **stac-api:** avoid base64 encoding application/geo+json data ([#172](https://github.com/developmentseed/eoapi-cdk/issues/172)) ([51a1df0](https://github.com/developmentseed/eoapi-cdk/commit/51a1df03388b4d3715a58445126b7fd34bfefc13))

# [9.2.0](https://github.com/developmentseed/eoapi-cdk/compare/v9.1.1...v9.2.0) (2025-07-22)


### Features

* add stac-auth-proxy construct ([#171](https://github.com/developmentseed/eoapi-cdk/issues/171)) ([f36ebaa](https://github.com/developmentseed/eoapi-cdk/commit/f36ebaa93395d5d80b5db795f09746b17c0ed58b))

## [9.1.1](https://github.com/developmentseed/eoapi-cdk/compare/v9.1.0...v9.1.1) (2025-07-17)


### Bug Fixes

* expose api gateway utility constructs ([#169](https://github.com/developmentseed/eoapi-cdk/issues/169)) ([c2bed73](https://github.com/developmentseed/eoapi-cdk/commit/c2bed7337e9742979cefaadb74291c4adcd76dd7))

# [9.1.0](https://github.com/developmentseed/eoapi-cdk/compare/v9.0.0...v9.1.0) (2025-07-17)


### Features

* add PrivateLambdaApiGateway construct for VPC-integrated API Gateway ([#168](https://github.com/developmentseed/eoapi-cdk/issues/168)) ([5d6c2b3](https://github.com/developmentseed/eoapi-cdk/commit/5d6c2b33cbb06b28ac226142717c431500739b51))

# [9.0.0](https://github.com/developmentseed/eoapi-cdk/compare/v8.3.3...v9.0.0) (2025-07-17)


* feat!: expose API runtime constructs (#167) ([ce9df07](https://github.com/developmentseed/eoapi-cdk/commit/ce9df0709c2e6d7e2d5b0c474f4f991c92fa79b1)), closes [#167](https://github.com/developmentseed/eoapi-cdk/issues/167)


### BREAKING CHANGES

* This update will change the internal node IDs of the constructs. This will cause the Lambdas and API Gateways to be redeployed when upgrading eoapi-cdk. Being that both services are stateless, this should not cause issues unless a developer has made manual modifications or manual references to the deployed lambdas/api gateways.

## [8.3.3](https://github.com/developmentseed/eoapi-cdk/compare/v8.3.2...v8.3.3) (2025-07-09)


### Bug Fixes

* stactools-item-generator issues ([12591c5](https://github.com/developmentseed/eoapi-cdk/commit/12591c5bea32b53ffe62f3601f0f9d23bb4246f5))

## [8.3.2](https://github.com/developmentseed/eoapi-cdk/compare/v8.3.1...v8.3.2) (2025-07-06)


### Bug Fixes

* add unique prefix to stactools-item-generator export names ([#164](https://github.com/developmentseed/eoapi-cdk/issues/164)) ([5f5d88b](https://github.com/developmentseed/eoapi-cdk/commit/5f5d88bbc450857aaa70e5e582ba3de404ab756c))

## [8.3.1](https://github.com/developmentseed/eoapi-cdk/compare/v8.3.0...v8.3.1) (2025-07-03)


### Bug Fixes

* add stack name to exportNames in StacLoader ([#162](https://github.com/developmentseed/eoapi-cdk/issues/162)) ([372b677](https://github.com/developmentseed/eoapi-cdk/commit/372b677ba416f11407b10020b26493e07985d49c))

# [8.3.0](https://github.com/developmentseed/eoapi-cdk/compare/v8.2.3...v8.3.0) (2025-07-03)


### Features

* add collection loading capability ([#160](https://github.com/developmentseed/eoapi-cdk/issues/160)) ([adbf49b](https://github.com/developmentseed/eoapi-cdk/commit/adbf49bf6371f65dcd54790801e5b68345b35479))

## [8.2.3](https://github.com/developmentseed/eoapi-cdk/compare/v8.2.2...v8.2.3) (2025-06-11)


### Bug Fixes

* pin to numpy>=2.2.6,<2.3.0 and numexpr>=2.10.0<2.10.1 ([#154](https://github.com/developmentseed/eoapi-cdk/issues/154)) ([94d8f34](https://github.com/developmentseed/eoapi-cdk/commit/94d8f34982ba41f4fc895306a641830ad1ffa6d8))

## [8.2.2](https://github.com/developmentseed/eoapi-cdk/compare/v8.2.1...v8.2.2) (2025-06-03)


### Bug Fixes

* add option to create collection if missing ([#152](https://github.com/developmentseed/eoapi-cdk/issues/152)) ([83f0e1e](https://github.com/developmentseed/eoapi-cdk/commit/83f0e1e7f04b36d8b749cb64488e18b598ce4990))

## [8.2.1](https://github.com/developmentseed/eoapi-cdk/compare/v8.2.0...v8.2.1) (2025-06-03)


### Bug Fixes

* add vpc, subnet_selection, lambaFunctionOptions props ([#151](https://github.com/developmentseed/eoapi-cdk/issues/151)) ([eb48205](https://github.com/developmentseed/eoapi-cdk/commit/eb48205920d2efd1c8f664f68de9445ef0bd22c7))

# [8.2.0](https://github.com/developmentseed/eoapi-cdk/compare/v8.1.1...v8.2.0) (2025-05-30)


### Features

* add stactools-item-generator and stac-item-loader constructs ([#150](https://github.com/developmentseed/eoapi-cdk/issues/150)) ([371f6c3](https://github.com/developmentseed/eoapi-cdk/commit/371f6c36619ee9112da155293d573db5d30f1ba5))

## [8.1.1](https://github.com/developmentseed/eoapi-cdk/compare/v8.1.0...v8.1.1) (2025-04-30)


### Bug Fixes

* upgrade pgbouncer ami to ubuntu 24.04 ([#148](https://github.com/developmentseed/eoapi-cdk/issues/148)) ([292e94f](https://github.com/developmentseed/eoapi-cdk/commit/292e94fc35ece766be84197c08caddf9ec6f2b12))

# [8.1.0](https://github.com/developmentseed/eoapi-cdk/compare/v8.0.3...v8.1.0) (2025-04-24)


### Features

* add pgbouncerInstanceProps parameter to PgstacDatabase ([#139](https://github.com/developmentseed/eoapi-cdk/issues/139)) ([add27ec](https://github.com/developmentseed/eoapi-cdk/commit/add27ec2e8242e5477b06ec8854c2d763a2795f1))

## [8.0.3](https://github.com/developmentseed/eoapi-cdk/compare/v8.0.2...v8.0.3) (2025-04-16)


### Bug Fixes

* update tipg startup for 1.0 ([#144](https://github.com/developmentseed/eoapi-cdk/issues/144)) ([ae68e70](https://github.com/developmentseed/eoapi-cdk/commit/ae68e70ed98c6a2ae52275fd0b6b83a0c17989b3)), closes [#143](https://github.com/developmentseed/eoapi-cdk/issues/143)

## [8.0.2](https://github.com/developmentseed/eoapi-cdk/compare/v8.0.1...v8.0.2) (2025-03-11)


### Bug Fixes

* refactor to keep database pgstac and ingestor pypgstac in sync ([#137](https://github.com/developmentseed/eoapi-cdk/issues/137)) ([cdf1a66](https://github.com/developmentseed/eoapi-cdk/commit/cdf1a6629905384b697ef00c39b1a6b10d15b592))

## [8.0.1](https://github.com/developmentseed/eoapi-cdk/compare/v8.0.0...v8.0.1) (2025-03-11)


### Bug Fixes

* disable transaction extensions by default ([#136](https://github.com/developmentseed/eoapi-cdk/issues/136)) ([18822f0](https://github.com/developmentseed/eoapi-cdk/commit/18822f09cb6794020cf348a361939e234db4b834))

# [8.0.0](https://github.com/developmentseed/eoapi-cdk/compare/v7.6.3...v8.0.0) (2025-03-11)


### Features

* update versions for pgstac, stac-fastapi-pgstac, titiler-pgstac, and tipg ([507cc99](https://github.com/developmentseed/eoapi-cdk/commit/507cc991e72c2369666e72abe41cf53be0ce29d4))


### BREAKING CHANGES

* Major version updates to core dependencies require client code changes.

## [7.6.3](https://github.com/developmentseed/eoapi-cdk/compare/v7.6.2...v7.6.3) (2025-03-07)


### Bug Fixes

* reject items without a collection ID ([#133](https://github.com/developmentseed/eoapi-cdk/issues/133)) ([595b0be](https://github.com/developmentseed/eoapi-cdk/commit/595b0be1c5632b74231ce5ed5c350aed5fe8bb83))

## [7.6.2](https://github.com/developmentseed/eoapi-cdk/compare/v7.6.1...v7.6.2) (2025-03-06)


### Bug Fixes

* use model_dump(mode="json") for serializing STAC objects ([#131](https://github.com/developmentseed/eoapi-cdk/issues/131)) ([2117b52](https://github.com/developmentseed/eoapi-cdk/commit/2117b524fb4c99ded23048f5b71eb3492568008b))

## [7.6.1](https://github.com/developmentseed/eoapi-cdk/compare/v7.6.0...v7.6.1) (2025-02-28)


### Bug Fixes

* update types for url config parameters to be compatible with str ([#127](https://github.com/developmentseed/eoapi-cdk/issues/127)) ([cab4c0e](https://github.com/developmentseed/eoapi-cdk/commit/cab4c0e3d71261d1feefcb38e5fb40dccb530b57))

# [7.6.0](https://github.com/developmentseed/eoapi-cdk/compare/v7.5.1...v7.6.0) (2025-02-27)


### Features

* update ingestor-api runtime dependencies ([#125](https://github.com/developmentseed/eoapi-cdk/issues/125)) ([562955d](https://github.com/developmentseed/eoapi-cdk/commit/562955d02f925e3ce8101cc2f64dfab6553c28b8))

## [7.5.1](https://github.com/developmentseed/eoapi-cdk/compare/v7.5.0...v7.5.1) (2025-02-06)


### Bug Fixes

* ensure db bootstrapper runs on each deploy ([#124](https://github.com/developmentseed/eoapi-cdk/issues/124)) ([bb4bff8](https://github.com/developmentseed/eoapi-cdk/commit/bb4bff8fd4a93fea6cce4bd7fcb8de60807ee37a))

# [7.5.0](https://github.com/developmentseed/eoapi-cdk/compare/v7.4.2...v7.5.0) (2025-02-04)


### Features

* configure pgstac version in custom properties ([#123](https://github.com/developmentseed/eoapi-cdk/issues/123)) ([a29ea21](https://github.com/developmentseed/eoapi-cdk/commit/a29ea216dbb4631081f052c312ee9c7957276dae))

## [7.4.2](https://github.com/developmentseed/eoapi-cdk/compare/v7.4.1...v7.4.2) (2025-02-03)


### Bug Fixes

* ensure dependency secret update function completes ([#120](https://github.com/developmentseed/eoapi-cdk/issues/120)) ([90cdc89](https://github.com/developmentseed/eoapi-cdk/commit/90cdc89381f36528172e0035d50a174f7f1ee330))
* upgrade workflow versions ([#121](https://github.com/developmentseed/eoapi-cdk/issues/121)) ([45e72dd](https://github.com/developmentseed/eoapi-cdk/commit/45e72dd7cf20ae32e1b643ffcafd54bcac2cfd1e))

## [7.4.2](https://github.com/developmentseed/eoapi-cdk/compare/v7.4.1...v7.4.2) (2025-02-03)


### Bug Fixes

* ensure dependency secret update function completes ([#120](https://github.com/developmentseed/eoapi-cdk/issues/120)) ([90cdc89](https://github.com/developmentseed/eoapi-cdk/commit/90cdc89381f36528172e0035d50a174f7f1ee330))

## [7.4.1](https://github.com/developmentseed/eoapi-cdk/compare/v7.4.0...v7.4.1) (2025-01-24)


### Bug Fixes

* install packaging>=24.2 with twine ([#118](https://github.com/developmentseed/eoapi-cdk/issues/118)) ([caaf9e3](https://github.com/developmentseed/eoapi-cdk/commit/caaf9e3bd18593447a005eddf1d6bcef823b7d3b))

# [7.4.0](https://github.com/developmentseed/eoapi-cdk/compare/v7.3.0...v7.4.0) (2025-01-24)


### Features

* add pgbouncer ([#114](https://github.com/developmentseed/eoapi-cdk/issues/114)) ([5952858](https://github.com/developmentseed/eoapi-cdk/commit/5952858d280c753a423d79c0ab5f4da549792a11))

# [7.3.0](https://github.com/developmentseed/eoapi-cdk/compare/v7.2.1...v7.3.0) (2024-12-10)


### Bug Fixes

* update units for effectiveCacheSize and tempBuffers ([#112](https://github.com/developmentseed/eoapi-cdk/issues/112)) ([2e3d728](https://github.com/developmentseed/eoapi-cdk/commit/2e3d72820dedc252f15692f1d327630e6fa3f5e6))


### Features

* set search_path to include pgstac for eoapi user ([#111](https://github.com/developmentseed/eoapi-cdk/issues/111)) ([0470dcf](https://github.com/developmentseed/eoapi-cdk/commit/0470dcfb2bf7f6940dbbb1f0033c8e3fe129bdb7))

## [7.2.1](https://github.com/developmentseed/eoapi-cdk/compare/v7.2.0...v7.2.1) (2024-08-20)


### Bug Fixes

* install compilation dependency for numexpr ([#109](https://github.com/developmentseed/eoapi-cdk/issues/109)) ([2762944](https://github.com/developmentseed/eoapi-cdk/commit/2762944344512bda476d1924a58feef2b0c4a7aa))

# [7.2.0](https://github.com/developmentseed/eoapi-cdk/compare/v7.1.0...v7.2.0) (2024-05-14)


### Features

* overwrite host headers when custom domain name ([#105](https://github.com/developmentseed/eoapi-cdk/issues/105)) ([e52887f](https://github.com/developmentseed/eoapi-cdk/commit/e52887fcbd3ba662a4754bd4a066774589425ba7))

# [7.1.0](https://github.com/developmentseed/eoapi-cdk/compare/v7.0.1...v7.1.0) (2024-03-13)


### Features

* update runtimes and add pgstac customization options ([#100](https://github.com/developmentseed/eoapi-cdk/issues/100)) ([9e49e7e](https://github.com/developmentseed/eoapi-cdk/commit/9e49e7ea55d2fb9ea4b63c9f713b6caa4cad0249)), closes [#102](https://github.com/developmentseed/eoapi-cdk/issues/102)

## [7.0.1](https://github.com/developmentseed/eoapi-cdk/compare/v7.0.0...v7.0.1) (2024-02-23)


### Bug Fixes

* dependencies ([#97](https://github.com/developmentseed/eoapi-cdk/issues/97)) ([b09b510](https://github.com/developmentseed/eoapi-cdk/commit/b09b51002b1b2d7fd73ec27d763cd3a511fec2dc))

# [7.0.0](https://github.com/developmentseed/eoapi-cdk/compare/v6.1.0...v7.0.0) (2024-02-22)


### Features

* add integration tests ([#69](https://github.com/developmentseed/eoapi-cdk/issues/69)) ([17eec16](https://github.com/developmentseed/eoapi-cdk/commit/17eec16b944e4ca489ddcd610aeef2c1c8a5f203))


### BREAKING CHANGES

* clients need to provide aws_lambda.AssetCode to configure their apps. Solely the python application and the requirements.txt file is not supported anymore.

* fix a couple bugs found in the first changes

* avoid maintaining custom interfaces for configurable lambda properties. Allow the user to provide anything and let the CDK method raise error and overwrite values defined within our construct. Make this clear in the documentation

* expose bootstrapper props in pgstacdatabase construct constructor

* merge database and boostrapper files to solve casting bug

* bump and harmonize pypgstac to 0.7.10 across apps

* bump cachetools

* some changes to allow for less security

* bump python to 3.11

* change base image for bootstrapper to use python 311

* fix linting issues

* move integration tests to step before release, improve naming of workflows

* lint

* fix moto requirement

* test to fix deployment : try adding s3 endpoint and force allow public subnet

* lint and make lambda functions more configurable

* moving deploy to a separate workflow

* remove useless dependencies in deployment tests, turn on pull request trigger to check the action works

* when tearing down the infrastructure, synthesize the cloud formation assets into another directory to avoid conflicts

* update readmes and revive the artifact download in python distribution

# [6.1.0](https://github.com/developmentseed/eoapi-cdk/compare/v6.0.2...v6.1.0) (2023-11-12)


### Features

* **stac-browser:** configurable config file in stac browser deployment ([#84](https://github.com/developmentseed/eoapi-cdk/issues/84)) ([b86ad1a](https://github.com/developmentseed/eoapi-cdk/commit/b86ad1a8cb1fb92628f6450c1c8b05258d78280b))

## [6.0.2](https://github.com/developmentseed/eoapi-cdk/compare/v6.0.1...v6.0.2) (2023-11-02)


### Bug Fixes

* **bootstrapper:** fix httpx response ([#81](https://github.com/developmentseed/eoapi-cdk/issues/81)) ([b879076](https://github.com/developmentseed/eoapi-cdk/commit/b8790766818b0048e2192849a34f462997a08c0e))

## [6.0.1](https://github.com/developmentseed/eoapi-cdk/compare/v6.0.0...v6.0.1) (2023-11-01)


### Bug Fixes

* **ingestor-api-handler:** fix docs endpoint ([#82](https://github.com/developmentseed/eoapi-cdk/issues/82)) ([d134c77](https://github.com/developmentseed/eoapi-cdk/commit/d134c77f84363b3e4560176ccd810b55b6855f07))

# [6.0.0](https://github.com/developmentseed/eoapi-cdk/compare/v5.4.1...v6.0.0) (2023-10-31)


### Features

* custom runtimes, optional VPC, python 3.11 ([#74](https://github.com/developmentseed/eoapi-cdk/issues/74)) ([ba6bf09](https://github.com/developmentseed/eoapi-cdk/commit/ba6bf09651caae8537df7ee737dbf6d0bf975f41))


### BREAKING CHANGES

* the `bootstrapper` construct was deleted and is no longer available. In addition, we switched from `PythonFunction` to `Function` for all lambdas.

## [5.4.1](https://github.com/developmentseed/eoapi-cdk/compare/v5.4.0...v5.4.1) (2023-10-05)


### Bug Fixes

* synchronize pgstac versions -> 0.7.9 across constructs ([c6bb921](https://github.com/developmentseed/eoapi-cdk/commit/c6bb9213f745f1161d193b120083fac1e7943eb5))

# [5.4.0](https://github.com/developmentseed/eoapi-cdk/compare/v5.3.0...v5.4.0) (2023-09-05)


### Features

* custom runtimes option for titiler and ingestor ([#66](https://github.com/developmentseed/eoapi-cdk/issues/66)) ([3aaedae](https://github.com/developmentseed/eoapi-cdk/commit/3aaedaef86da558eac163348771a545b789ed8b9))

# [5.3.0](https://github.com/developmentseed/eoapi-cdk/compare/v5.2.0...v5.3.0) (2023-09-01)


### Features

* add STAC browser option ([#64](https://github.com/developmentseed/eoapi-cdk/issues/64)) ([36499d2](https://github.com/developmentseed/eoapi-cdk/commit/36499d21be710edde5bc9d625acff17edf7a81d6))

# [5.2.0](https://github.com/developmentseed/eoapi-cdk/compare/v5.1.0...v5.2.0) (2023-08-30)


### Features

* tipg-api ([#62](https://github.com/developmentseed/eoapi-cdk/issues/62)) ([24faa85](https://github.com/developmentseed/eoapi-cdk/commit/24faa85fc4f1ccb6406768b9f43a4cb095dac0cf))

# [5.1.0](https://github.com/developmentseed/eoapi-cdk/compare/v5.0.0...v5.1.0) (2023-08-21)


### Features

* custom domain names for apis ([#63](https://github.com/developmentseed/eoapi-cdk/issues/63)) ([c9eeb00](https://github.com/developmentseed/eoapi-cdk/commit/c9eeb00c2d66bf923f3029743e1c9746f7752c5e)), closes [#61](https://github.com/developmentseed/eoapi-cdk/issues/61)

# [5.0.0](https://github.com/developmentseed/eoapi-cdk/compare/v4.2.3...v5.0.0) (2023-07-12)


### Features

* rename repository to eoapi-cdk ([#59](https://github.com/developmentseed/eoapi-cdk/issues/59)) ([1ed2bb3](https://github.com/developmentseed/eoapi-cdk/commit/1ed2bb3d00328327ada96ce9daaadd940b534285))


### BREAKING CHANGES

* rename repository to eoapi-cdk

## [4.2.3](https://github.com/developmentseed/cdk-pgstac/compare/v4.2.2...v4.2.3) (2023-06-30)


### Bug Fixes

* **ingestor-api:** add stack name to ingestor-api apigateway export name ([#48](https://github.com/developmentseed/cdk-pgstac/issues/48)) ([2fdd1e8](https://github.com/developmentseed/cdk-pgstac/commit/2fdd1e8fe4b3b7e82657bcf95bf628eecdb9aa22))

## [4.2.2](https://github.com/developmentseed/cdk-pgstac/compare/v4.2.1...v4.2.2) (2023-06-16)


### Bug Fixes

* **titiler-pgstac-api:** fix destination path in titiler pgstac Dockerfile COPY command ([#46](https://github.com/developmentseed/cdk-pgstac/issues/46)) ([302bd22](https://github.com/developmentseed/cdk-pgstac/commit/302bd22fd3ff5af7335bb9285be798fb550cf19b))

## [4.2.1](https://github.com/developmentseed/cdk-pgstac/compare/v4.2.0...v4.2.1) (2023-06-12)


### Bug Fixes

* **bootstrapper:** bootstrapper should use httpx ([#45](https://github.com/developmentseed/cdk-pgstac/issues/45)) ([36bb361](https://github.com/developmentseed/cdk-pgstac/commit/36bb361cf65caa1ae9a633eb8e39066106f02258))

# [4.2.0](https://github.com/developmentseed/cdk-pgstac/compare/v4.1.0...v4.2.0) (2023-06-09)


### Features

* **titiler-pgstac-api:** add titiler-pgstac endpoint ([#42](https://github.com/developmentseed/cdk-pgstac/issues/42)) ([a02acef](https://github.com/developmentseed/cdk-pgstac/commit/a02acef3ed78049dd55c242a5b04bfc627c53661))

# [4.1.0](https://github.com/developmentseed/cdk-pgstac/compare/v4.0.0...v4.1.0) (2023-05-30)


### Features

* **stac-api:** add stac api lambda function field ([#43](https://github.com/developmentseed/cdk-pgstac/issues/43)) ([3a91a37](https://github.com/developmentseed/cdk-pgstac/commit/3a91a37ec329c09a66c85c23adfb1afb1345ba16))

# [4.0.0](https://github.com/developmentseed/cdk-pgstac/compare/v3.0.1...v4.0.0) (2023-04-25)


### Features

* **ingestor-api:** expose ingestor handler role ([#39](https://github.com/developmentseed/cdk-pgstac/issues/39)) ([559f3a9](https://github.com/developmentseed/cdk-pgstac/commit/559f3a91d4d712302aa5661539d495b2ee299f83))


### BREAKING CHANGES

* **ingestor-api:** the role name is automatically generated by AWS and thus users can not use the name that
was specified before, but should directly interact with the new property we are adding.

* change name of variable to comply with formatting rules, remove readonly statement

## [3.0.1](https://github.com/developmentseed/cdk-pgstac/compare/v3.0.0...v3.0.1) (2023-04-14)


### Bug Fixes

* **bootstraper:** fix version inconsistencies and [#19](https://github.com/developmentseed/cdk-pgstac/issues/19) regressions ([#34](https://github.com/developmentseed/cdk-pgstac/issues/34)) ([ebeac2a](https://github.com/developmentseed/cdk-pgstac/commit/ebeac2a1b36ff5825157bea8e76392a14d613b91))

# [3.0.0](https://github.com/developmentseed/cdk-pgstac/compare/v2.6.3...v3.0.0) (2023-04-04)


### Code Refactoring

* **bootstrapper:** remove VEDA logic ([#29](https://github.com/developmentseed/cdk-pgstac/issues/29)) ([e98039e](https://github.com/developmentseed/cdk-pgstac/commit/e98039ef4ace023faa205f0b0d1ad0efec38a69f))


### BREAKING CHANGES

* **bootstrapper:** remove dashboard schema and functions from the database bootstrapper and remove automatic collection summary udpate from ingestor.

## [2.6.3](https://github.com/developmentseed/cdk-pgstac/compare/v2.6.2...v2.6.3) (2023-03-28)


### Bug Fixes

* **ingestor-api:** store STAC item as string in DynamoDB ([#26](https://github.com/developmentseed/cdk-pgstac/issues/26)) ([bd7a1fa](https://github.com/developmentseed/cdk-pgstac/commit/bd7a1fa799cc9765df2939a444593205efa6bf4d))

## [2.6.2](https://github.com/developmentseed/cdk-pgstac/compare/v2.6.1...v2.6.2) (2023-03-16)


### Bug Fixes

* **ingestor-api:** queries require sequences ([#23](https://github.com/developmentseed/cdk-pgstac/issues/23)) ([00d71cc](https://github.com/developmentseed/cdk-pgstac/commit/00d71cc1d253e77f1cd11afe9e4b513a577a67a2))

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

* **ingestor-api:** Add flag to enable requester pays ([efc160d](https://github.com/developmentseed/cdk-pgstac/commit/efc160d3530a70d1fc8f88ef9dce4a4d48456834))

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
