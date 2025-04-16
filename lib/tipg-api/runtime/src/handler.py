"""
Handler for AWS Lambda.
"""

import asyncio
import os

from mangum import Mangum
from tipg.collections import register_collection_catalog
from tipg.database import connect_to_db
from tipg.main import app
from tipg.settings import (
    CustomSQLSettings,
    DatabaseSettings,
    PostgresSettings,
)
from utils import get_secret_dict

secret = get_secret_dict(secret_arn_env_var="PGSTAC_SECRET_ARN")
postgres_settings = PostgresSettings(
    postgres_host=secret["host"],
    postgres_dbname=secret["dbname"],
    postgres_user=secret["username"],
    postgres_pass=secret["password"],
    postgres_port=int(secret["port"]),
)
db_settings = DatabaseSettings()
custom_sql_settings = CustomSQLSettings()


@app.on_event("startup")
async def startup_event() -> None:
    """Connect to database on startup."""
    await connect_to_db(
        app,
        schemas=db_settings.schemas,
        tipg_schema=db_settings.tipg_schema,
        user_sql_files=custom_sql_settings.sql_files,
        settings=postgres_settings,
    )
    await register_collection_catalog(
        app,
        db_settings=db_settings,
    )


handler = Mangum(app, lifespan="off")

if "AWS_EXECUTION_ENV" in os.environ:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.router.startup())
