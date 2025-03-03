"""API settings.
Based on https://github.com/developmentseed/eoAPI/tree/master/src/eoapi/stac"""

import base64
import json
from typing import Any, Optional

import boto3

# from stac_fastapi.pgstac.extensions import QueryExtension
from pydantic import model_validator
from stac_fastapi.pgstac.config import Settings
from stac_fastapi.pgstac.version import __version__ as stac_fastapi_pgstac_version


def get_secret_dict(secret_name: str):
    """Retrieve secrets from AWS Secrets Manager

    Args:
        secret_name (str): name of aws secrets manager secret containing database connection secrets

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


class ApiSettings(Settings):
    """API settings"""

    name: str = "stac-fastapi-pgstac"
    version: str = stac_fastapi_pgstac_version
    description: Optional[str] = None
    cachecontrol: str = "public, max-age=3600"
    debug: bool = False

    pgstac_secret_arn: Optional[str]

    @model_validator(mode="before")
    def get_postgres_setting(cls, data: Any) -> Any:
        if arn := data.get("pgstac_secret_arn"):
            secret = get_secret_dict(arn)
            data.update(
                {
                    "postgres_host_reader": secret["host"],
                    "postgres_host_writer": secret["host"],
                    "postgres_dbname": secret["dbname"],
                    "postgres_user": secret["username"],
                    "postgres_pass": secret["password"],
                    "postgres_port": secret["port"],
                }
            )

        return data
