"""API settings.
Based on https://github.com/developmentseed/eoAPI/tree/master/src/eoapi/stac"""
import base64
import json
from typing import Optional

import boto3
import pydantic
from stac_fastapi.api.models import create_get_request_model, create_post_request_model

# from stac_fastapi.pgstac.extensions import QueryExtension
from stac_fastapi.extensions.core import (
    ContextExtension,
    FieldsExtension,
    FilterExtension,
    QueryExtension,
    SortExtension,
    TokenPaginationExtension,
)
from stac_fastapi.pgstac.config import Settings
from stac_fastapi.pgstac.types.search import PgstacSearch


def get_secret_dict(secret_name: str):
    """Retrieve secrets from AWS Secrets Manager

    Args:
        secret_name (str): name of aws secrets manager secret containing database connection secrets
        profile_name (str, optional): optional name of aws profile for use in debugger only

    Returns:
        secrets (dict): decrypted secrets in dict
    """

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager")

    get_secret_value_response = client.get_secret_value(SecretId=secret_name)

    if "SecretString" in get_secret_value_response:
        return json.loads(get_secret_value_response["SecretString"])
    else:
        return json.loads(base64.b64decode(get_secret_value_response["SecretBinary"]))


class ApiSettings(pydantic.BaseSettings):
    """API settings"""

    name: str = "asdi-stac-api"
    version: str = "0.1"
    description: Optional[str] = None
    cors_origins: str = "*"
    cachecontrol: str = "public, max-age=3600"
    debug: bool = False

    pgstac_secret_arn: Optional[str]

    @pydantic.validator("cors_origins")
    def parse_cors_origin(cls, v):
        """Parse CORS origins."""
        return [origin.strip() for origin in v.split(",")]

    def load_postgres_settings(self) -> "Settings":
        """Load postgres connection params from AWS secret"""

        if self.pgstac_secret_arn:
            secret = get_secret_dict(self.pgstac_secret_arn)

            return Settings(
                postgres_host_reader=secret["host"],
                postgres_host_writer=secret["host"],
                postgres_dbname=secret["dbname"],
                postgres_user=secret["username"],
                postgres_pass=secret["password"],
                postgres_port=secret["port"],
            )
        else:
            return Settings()

    class Config:
        """model config"""

        env_file = ".env"


extensions = [
    FilterExtension(),
    QueryExtension(),
    SortExtension(),
    FieldsExtension(),
    TokenPaginationExtension(),
    ContextExtension(),
]
post_request_model = create_post_request_model(extensions, base_model=PgstacSearch)
get_request_model = create_get_request_model(extensions)
