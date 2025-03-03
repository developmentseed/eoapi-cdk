"""
Handler for AWS Lambda.
"""

import asyncio
import os

from mangum import Mangum

from .config import get_secret_dict

pgstac_secret_arn = os.environ["PGSTAC_SECRET_ARN"]

secret = get_secret_dict(pgstac_secret_arn)
os.environ.update(
    {
        "postgres_host_reader": secret["host"],
        "postgres_host_writer": secret["host"],
        "postgres_dbname": secret["dbname"],
        "postgres_user": secret["username"],
        "postgres_pass": secret["password"],
        "postgres_port": str(secret["port"]),
    }
)

from .app import app

handler = Mangum(app, lifespan="off")


if "AWS_EXECUTION_ENV" in os.environ:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.router.startup())
