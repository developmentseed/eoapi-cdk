from aws_cdk import App, RemovalPolicy, Stack, aws_ec2, aws_rds
from config import AppConfig, build_app_config
from constructs import Construct
from eoapi_cdk import (
    PgStacApiLambda,
    PgStacDatabase,
    TiPgApiLambda,
    TitilerPgstacApiLambda,
)


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
            removal_policy=RemovalPolicy.DESTROY,
        )

        assert pgstac_db.security_group

        pgstac_db.security_group.add_ingress_rule(
            aws_ec2.Peer.any_ipv4(), aws_ec2.Port.tcp(5432)
        )

        PgStacApiLambda(
            self,
            "pgstac-api",
            connection_target=pgstac_db.connection_target,
            db_secret=pgstac_db.pgstac_secret,
            api_env={
                "NAME": app_config.build_service_name("STAC API"),
                "description": f"{app_config.stage} STAC API",
            },
        )

        TitilerPgstacApiLambda(
            self,
            "titiler-pgstac-api",
            api_env={
                "NAME": app_config.build_service_name("titiler pgSTAC API"),
                "description": f"{app_config.stage} titiler pgstac API",
            },
            connection_target=pgstac_db.connection_target,
            db_secret=pgstac_db.pgstac_secret,
            buckets=[],
            lambda_function_options={
                "allow_public_subnet": True,
            },
        )

        TiPgApiLambda(
            self,
            "tipg-api",
            connection_target=pgstac_db.connection_target,
            db_secret=pgstac_db.pgstac_secret,
            api_env={
                "NAME": app_config.build_service_name("tipg API"),
                "description": f"{app_config.stage} tipg API",
            },
            lambda_function_options={
                "allow_public_subnet": True,
            },
        )


app = App()

app_config = build_app_config()

vpc_stack_id = f"vpc{app_config.project_id}"

vpc_stack = VpcStack(scope=app, app_config=app_config, id=vpc_stack_id)

pgstac_infra_stack_id = f"pgstac{app_config.project_id}"

pgstac_infra_stack = pgStacInfraStack(
    scope=app, vpc=vpc_stack.vpc, app_config=app_config, id=pgstac_infra_stack_id
)

app.synth()
