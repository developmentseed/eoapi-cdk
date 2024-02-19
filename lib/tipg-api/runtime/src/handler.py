"""
Handler for AWS Lambda.
"""

import asyncio
import os

from mangum import Mangum
from utils import load_pgstac_secret

load_pgstac_secret(os.environ["PGSTAC_SECRET_ARN"])  # required for the below imports

from tipg.collections import register_collection_catalog  # noqa: E402
from tipg.database import connect_to_db  # noqa: E402

# skipping linting rule that wants all imports at the top
from tipg.main import app  # noqa: E402
from tipg.settings import CustomSQLSettings  # noqa: E402
from tipg.settings import DatabaseSettings  # noqa: E402
from tipg.settings import PostgresSettings  # noqa: E402; noqa: E402

postgres_settings = PostgresSettings()
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
