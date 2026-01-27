from aws_cdk import (
    App,
    RemovalPolicy,
    Stack,
    aws_ec2,
    aws_iam,
    aws_rds,
    aws_s3,
    aws_s3_notifications,
)
from config import AppConfig, build_app_config
from constructs import Construct
from eoapi_cdk import (
    PgStacApiLambda,
    PgStacDatabase,
    StacIngestor,
    StacLoader,
    StactoolsItemGenerator,
    TiPgApiLambda,
    TitilerPgstacApiLambda,
)

PGSTAC_VERSION = "0.9.9"


class VpcStack(Stack):
    def __init__(
        self, scope: Construct, app_config: AppConfig, id: str, **kwargs
    ) -> None:
        super().__init__(scope, id=id, tags=app_config.tags, **kwargs)

        self.vpc = aws_ec2.Vpc(
            self,
            "vpc",
            subnet_configuration=[
                aws_ec2.SubnetConfiguration(
                    name="ingress", subnet_type=aws_ec2.SubnetType.PUBLIC, cidr_mask=24
                ),
            ],
        )

        self.vpc.add_interface_endpoint(
            "SecretsManagerEndpoint",
            service=aws_ec2.InterfaceVpcEndpointAwsService.SECRETS_MANAGER,
        )

        self.vpc.add_interface_endpoint(
            "CloudWatchEndpoint",
            service=aws_ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS,
        )

        self.vpc.add_gateway_endpoint(
            "S3", service=aws_ec2.GatewayVpcEndpointAwsService.S3
        )

        self.export_value(
            self.vpc.select_subnets(subnet_type=aws_ec2.SubnetType.PUBLIC)
            .subnets[0]
            .subnet_id
        )
        self.export_value(
            self.vpc.select_subnets(subnet_type=aws_ec2.SubnetType.PUBLIC)
            .subnets[1]
            .subnet_id
        )


class pgStacInfraStack(Stack):
    def __init__(
        self,
        scope: Construct,
        vpc: aws_ec2.Vpc,
        id: str,
        app_config: AppConfig,
        **kwargs,
    ) -> None:
        super().__init__(
            scope,
            id=id,
            tags=app_config.tags,
            **kwargs,
        )

        pgstac_db = PgStacDatabase(
            self,
            "pgstac-db",
            vpc=vpc,
            engine=aws_rds.DatabaseInstanceEngine.postgres(
                version=aws_rds.PostgresEngineVersion.VER_14
            ),
            vpc_subnets=aws_ec2.SubnetSelection(
                subnet_type=aws_ec2.SubnetType.PUBLIC,
            ),
            allocated_storage=app_config.db_allocated_storage,
            instance_type=aws_ec2.InstanceType(app_config.db_instance_type),
            add_pgbouncer=True,
            pgbouncer_instance_props={
                "instanceName": "test-name",
            },
            removal_policy=RemovalPolicy.DESTROY,
            pgstac_version=PGSTAC_VERSION,
        )

        assert pgstac_db.security_group

        pgstac_db.security_group.add_ingress_rule(
            aws_ec2.Peer.any_ipv4(), aws_ec2.Port.tcp(5432)
        )

        stac_api = PgStacApiLambda(
            self,
            "pgstac-api",
            db=pgstac_db.connection_target,
            db_secret=pgstac_db.pgstac_secret,
            api_env={
                "NAME": app_config.build_service_name("STAC API"),
                "description": f"{app_config.stage} STAC API",
                # test that we can use the pgbouncer secret in downstream resources
                "POSTGRES_HOST": pgstac_db.pgstac_secret.secret_value_from_json(
                    "host"
                ).to_string(),
            },
        )

        # make sure stac_api does not try to build before the secret has been boostrapped
        stac_api.node.add_dependency(pgstac_db.secret_bootstrapper)

        TitilerPgstacApiLambda(
            self,
            "titiler-pgstac-api",
            api_env={
                "NAME": app_config.build_service_name("titiler pgSTAC API"),
                "description": f"{app_config.stage} titiler pgstac API",
            },
            db=pgstac_db.connection_target,
            db_secret=pgstac_db.pgstac_secret,
            buckets=[],
            lambda_function_options={
                "allow_public_subnet": True,
            },
        )

        TiPgApiLambda(
            self,
            "tipg-api",
            db=pgstac_db.connection_target,
            db_secret=pgstac_db.pgstac_secret,
            api_env={
                "NAME": app_config.build_service_name("tipg API"),
                "description": f"{app_config.stage} tipg API",
            },
            lambda_function_options={
                "allow_public_subnet": True,
            },
        )

        s3_read_only_role = aws_iam.Role(
            self,
            "S3ReadOnlyRole",
            assumed_by=aws_iam.ServicePrincipal("lambda.amazonaws.com"),
            description="Role with read-only access to S3 buckets",
        )

        s3_read_only_role.add_managed_policy(
            aws_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3ReadOnlyAccess")
        )

        StacIngestor(
            self,
            "ingestor",
            data_access_role=s3_read_only_role,
            stac_db_secret=pgstac_db.pgstac_secret,
            stac_db_security_group=pgstac_db.security_group,
            stac_url=stac_api.url,
            stage="test",
            pgstac_version=PGSTAC_VERSION,
            api_env={
                "JWKS_URL": "",  # no authentication!
            },
        )

        self.stac_loader = StacLoader(
            self,
            "stac-loader",
            pgstac_db=pgstac_db,
            batch_size=500,
            lambda_timeout_seconds=300,
        )

        self.stac_item_generator = StactoolsItemGenerator(
            self,
            "stactools-item-generator",
            item_load_topic_arn=self.stac_loader.topic.topic_arn,
        )

        self.stac_loader.topic.grant_publish(self.stac_item_generator.lambda_function)

        stac_bucket = aws_s3.Bucket(
            self,
            "stac-item-bucket",
        )

        stac_bucket.add_event_notification(
            aws_s3.EventType.OBJECT_CREATED,
            aws_s3_notifications.SnsDestination(self.stac_loader.topic),
            aws_s3.NotificationKeyFilter(suffix=".json"),
        )

        stac_bucket.grant_read(self.stac_loader.lambda_function)


app = App()

app_config = build_app_config()

vpc_stack_id = f"vpc{app_config.project_id}"

vpc_stack = VpcStack(scope=app, app_config=app_config, id=vpc_stack_id)

pgstac_infra_stack_id = f"pgstac{app_config.project_id}"

pgstac_infra_stack = pgStacInfraStack(
    scope=app, vpc=vpc_stack.vpc, app_config=app_config, id=pgstac_infra_stack_id
)

app.synth()
