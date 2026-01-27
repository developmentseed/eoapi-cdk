"""
Handler for AWS Lambda.
"""

import asyncio
import os

from mangum import Mangum
from snapshot_restore_py import register_after_restore, register_before_snapshot
from titiler.pgstac.db import connect_to_db
from titiler.pgstac.main import app
from titiler.pgstac.settings import PostgresSettings
from utils import get_secret_dict

secret = get_secret_dict(secret_arn_env_var="PGSTAC_SECRET_ARN")
postgres_settings = PostgresSettings(
    pghost=secret["host"],
    pgdatabase=secret["dbname"],
    pguser=secret["username"],
    pgpassword=secret["password"],
    pgport=int(secret["port"]),
)

_connection_initialized = False


@register_before_snapshot
def on_snapshot():
    """
    Runtime hook called by Lambda before taking a snapshot.
    We close database connections that shouldn't be in the snapshot.
    """

    # Close any existing database connections before the snapshot is taken
    if hasattr(app, "state") and hasattr(app.state, "dbpool") and app.state.dbpool:
        try:
            app.state.dbpool.close()
            app.state.dbpool = None
        except Exception as e:
            print(f"SnapStart: Error closing database pool: {e}")

    return {"statusCode": 200}


@register_after_restore
def on_snap_restore():
    """
    Runtime hook called by Lambda after restoring from a snapshot.
    We recreate database connections that were closed before the snapshot.
    """
    global _connection_initialized

    try:
        # Get the event loop or create a new one
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Close any existing pool (from snapshot)
        if hasattr(app.state, "dbpool") and app.state.dbpool:
            try:
                app.state.dbpool.close()
            except Exception as e:
                print(f"SnapStart: Error closing stale pool: {e}")
            app.state.dbpool = None

        # Create fresh connection pool
        loop.run_until_complete(connect_to_db(app, settings=postgres_settings))

        _connection_initialized = True

    except Exception as e:
        print(f"SnapStart: Failed to initialize database connection: {e}")
        raise

    return {"statusCode": 200}


@app.on_event("startup")
async def startup_event() -> None:
    """Connect to database on startup."""
    await connect_to_db(app, settings=postgres_settings)


handler = Mangum(app, lifespan="off")


if "AWS_EXECUTION_ENV" in os.environ:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.router.startup())
