"""
Handler for AWS Lambda.
"""

import asyncio
import os

from mangum import Mangum
from stac_fastapi.pgstac.app import app
from stac_fastapi.pgstac.config import PostgresSettings
from stac_fastapi.pgstac.db import close_db_connection, connect_to_db
from utils import get_secret_dict

secret = get_secret_dict(secret_arn_env_var="PGSTAC_SECRET_ARN")
postgres_settings = PostgresSettings(
    postgres_host_reader=secret["host"],
    postgres_host_writer=secret["host"],
    postgres_dbname=secret["dbname"],
    postgres_user=secret["username"],
    postgres_pass=secret["password"],
    postgres_port=int(secret["port"]),
)


@app.on_event("startup")
async def startup_event():
    """Connect to database on startup."""
    print("Setting up DB connection...")
    await connect_to_db(app, postgres_settings=postgres_settings)
    print("DB connection setup.")


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection."""
    print("Closing up DB connection...")
    await close_db_connection(app)
    print("DB connection closed.")


handler = Mangum(app, lifespan="off")


if "AWS_EXECUTION_ENV" in os.environ:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.router.startup())
