"""
Handler for AWS Lambda.
"""

import asyncio
import os

from mangum import Mangum
from titiler.pgstac.db import connect_to_db
from titiler.pgstac.main import app
from titiler.pgstac.settings import PostgresSettings
from utils import get_secret_dict

secret = get_secret_dict(secret_arn_env_var="PGSTAC_SECRET_ARN")
postgres_settings = PostgresSettings(
    postgres_host=secret["host"],
    postgres_dbname=secret["dbname"],
    postgres_user=secret["username"],
    postgres_pass=secret["password"],
    postgres_port=int(secret["port"]),
)


@app.on_event("startup")
async def startup_event() -> None:
    """Connect to database on startup."""
    await connect_to_db(app, settings=postgres_settings)


handler = Mangum(app, lifespan="off")


if "AWS_EXECUTION_ENV" in os.environ:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.router.startup())
