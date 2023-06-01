"""titiler pgstac API settings."""
import base64
import json
from typing import Optional, Any
import os

import boto3
import pydantic


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

    pgstac_secret_arn: str

    name: str = "titiler pgstac api"
    version: str = "0.1"
    description: Optional[str] = None
    cors_origins: str = "*"
    cachecontrol: str = "public, max-age=3600"
    debug: bool = False

    @pydantic.validator("cors_origins")
    def parse_cors_origin(cls, v):
        """Parse CORS origins."""
        return [origin.strip() for origin in v.split(",")]

    def set_postgres_settings(self):
        """Export postgres connection params to environment variables from DB AWS secret"""

        secret = get_secret_dict(self.pgstac_secret_arn)

        os.environ.update({
            "postgres_host": secret["host"],
            "postgres_dbname": secret["dbname"],
            "postgres_user": secret["username"],
            "postgres_pass": secret["password"],
            "postgres_port": str(secret["port"]),
        })            

    class Config:
        """model config"""

        env_file = ".env"
