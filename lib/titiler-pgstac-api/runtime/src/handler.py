"""
Handler for AWS Lambda.
"""

import asyncio
import os
from functools import lru_cache

from mangum import Mangum
from utils import get_secret_dict


@lru_cache(maxsize=1)
def get_db_credentials():
    """Cache the credentials to avoid repeated Secrets Manager calls."""
    pgstac_secret_arn = os.environ.get("PGSTAC_SECRET_ARN")
    if not pgstac_secret_arn:
        raise ValueError("PGSTAC_SECRET_ARN is not set!")
    return get_secret_dict(pgstac_secret_arn)


secret = get_db_credentials()
os.environ.update(
    {
        "postgres_host": secret["host"],
        "postgres_dbname": secret["dbname"],
        "postgres_user": secret["username"],
        "postgres_pass": secret["password"],
        "postgres_port": str(secret["port"]),
    }
)

from titiler.pgstac.db import connect_to_db  # noqa: E402
from titiler.pgstac.main import app  # noqa: E402


@app.on_event("startup")
async def startup_event() -> None:
    """Connect to database on startup."""
    await connect_to_db(app)


handler = Mangum(app, lifespan="off")


if "AWS_EXECUTION_ENV" in os.environ:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.router.startup())
