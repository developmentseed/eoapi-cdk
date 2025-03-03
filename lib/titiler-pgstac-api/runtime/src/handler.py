"""
Handler for AWS Lambda.
"""

import asyncio
import os

from .utils import get_secret_dict

pgstac_secret_arn = os.environ["PGSTAC_SECRET_ARN"]

secret = get_secret_dict(pgstac_secret_arn)
os.environ.update(
    {
        "postgres_host": secret["host"],
        "postgres_dbname": secret["dbname"],
        "postgres_user": secret["username"],
        "postgres_pass": secret["password"],
        "postgres_port": str(secret["port"]),
    }
)

from mangum import Mangum
from titiler.pgstac.db import connect_to_db  # noqa: E402
from titiler.pgstac.main import app  # noqa: E402
from titiler.pgstac.settings import PostgresSettings
from utils import get_secret_dict


@app.on_event("startup")
async def startup_event() -> None:
    """Connect to database on startup."""
    pgstac_secret_arn = os.getenv("PGSTAC_SECRET_ARN")
    if not pgstac_secret_arn:
        raise ValueError("PGSTAC_SECRET_ARN is not set!")

    secret = get_secret_dict(pgstac_secret_arn)
    await connect_to_db(
        app,
        settings=PostgresSettings(
            postgres_user=secret["username"],
            postgres_pass=secret["password"],
            postgres_host=secret["host"],
            postgres_port=secret["port"],
            postgres_dbname=secret["dbname"],
        ),
    )


handler = Mangum(app, lifespan="off")


if "AWS_EXECUTION_ENV" in os.environ:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.router.startup())
