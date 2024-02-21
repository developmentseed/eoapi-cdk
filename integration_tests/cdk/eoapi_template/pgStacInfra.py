from aws_cdk import (
    Stack,
    aws_ec2,
    aws_rds
)
from constructs import Construct
from eoapi_cdk import (
    PgStacApiLambda,
    PgStacDatabase,
    TitilerPgstacApiLambda,
)

from config import AppConfig


class pgStacInfraStack(Stack):
    def __init__(
        self,
        scope: Construct,
        vpc: aws_ec2.Vpc,
        app_config: AppConfig,
        **kwargs,
    ) -> None:
        super().__init__(
            scope,
            id=app_config.build_service_name("pgSTAC-infra"),
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
            instance_type=aws_ec2.InstanceType(app_config.db_instance_type)
        )

        pgstac_db.db.connections.allow_default_port_from_any_ipv4()

        PgStacApiLambda(
            self,
            "pgstac-api",
            api_env={
                "NAME": app_config.build_service_name("STAC API"),
                "description": f"{app_config.stage} STAC API",
            },
            db=pgstac_db.db,
            db_secret=pgstac_db.pgstac_secret
        )

        TitilerPgstacApiLambda(
            self,
            "titiler-pgstac-api",
            api_env={
                "NAME": app_config.build_service_name("titiler pgSTAC API"),
                "description": f"{app_config.stage} titiler pgstac API",
            },
            db=pgstac_db.db,
            db_secret=pgstac_db.pgstac_secret,
            buckets=[],
            lambda_function_options={
                "allow_public_subnet": True,
            },
        )
