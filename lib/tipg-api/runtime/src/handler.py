"""
Handler for AWS Lambda.
"""

import asyncio
import os
from mangum import Mangum
from utils import get_secret_dict
from tipg.main import app
from tipg.collections import register_collection_catalog
from tipg.database import connect_to_db
from tipg.settings import (
    CustomSQLSettings,
    DatabaseSettings,
    PostgresSettings,
)

pgstac_secret_arn = os.environ["PGSTAC_SECRET_ARN"]
secret = get_secret_dict(pgstac_secret_arn)

postgres_settings = PostgresSettings(
    postgres_user=secret["username"],
    postgres_pass=secret["password"],
    postgres_host=secret["host"],
    postgres_port=secret["port"],
    postgres_dbname=secret["dbname"],
)
db_settings = DatabaseSettings()
custom_sql_settings = CustomSQLSettings()


@app.on_event("startup")
async def startup_event() -> None:
    """Connect to database on startup."""
    await connect_to_db(
        app,
        settings=postgres_settings,
        schemas=db_settings.schemas,
        user_sql_files=custom_sql_settings.sql_files,
    )
    await register_collection_catalog(
        app,
        schemas=db_settings.schemas,
        tables=db_settings.tables,
        exclude_tables=db_settings.exclude_tables,
        exclude_table_schemas=db_settings.exclude_table_schemas,
        functions=db_settings.functions,
        exclude_functions=db_settings.exclude_functions,
        exclude_function_schemas=db_settings.exclude_function_schemas,
        spatial=db_settings.only_spatial_tables,
    )


handler = Mangum(app, lifespan="off")

if "AWS_EXECUTION_ENV" in os.environ:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.router.startup())
