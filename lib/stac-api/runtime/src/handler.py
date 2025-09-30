"""
Handler for AWS Lambda.
"""

import asyncio
import os

from mangum import Mangum
from snapshot_restore_py import register_after_restore, register_before_snapshot
from stac_fastapi.pgstac.app import app, with_transactions
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

_connection_initialized = False


@register_before_snapshot
def on_snapshot():
    """
    Runtime hook called by Lambda before taking a snapshot.
    We close database connections that shouldn't be in the snapshot.
    """

    # Close any existing database connections before the snapshot is taken
    if hasattr(app, "state") and hasattr(app.state, "readpool") and app.state.readpool:
        try:
            app.state.readpool.close()
            app.state.readpool = None
        except Exception as e:
            print(f"SnapStart: Error closing database readpool: {e}")

    if hasattr(app, "state") and hasattr(app.state, "writepool") and app.state.writepool:
        try:
            app.state.writepool.close()
            app.state.writepool = None
        except Exception as e:
            print(f"SnapStart: Error closing database writepool: {e}")

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
        if hasattr(app.state, "readpool") and app.state.readpool:
            try:
                app.state.readpool.close()
            except Exception as e:
                print(f"SnapStart: Error closing stale readpool: {e}")
            app.state.readpool = None

        if hasattr(app.state, "writepool") and app.state.writepool:
            try:
                app.state.writepool.close()
            except Exception as e:
                print(f"SnapStart: Error closing stale writepool: {e}")
            app.state.writepool = None

        # Create fresh connection pool
        loop.run_until_complete(
            connect_to_db(
                app,
                postgres_settings=postgres_settings,
                add_write_connection_pool=with_transactions,
            )
        )

        _connection_initialized = True

    except Exception as e:
        print(f"SnapStart: Failed to initialize database connection: {e}")
        raise

    return {"statusCode": 200}


@app.on_event("startup")
async def startup_event():
    """Connect to database on startup."""
    print("Setting up DB connection...")
    await connect_to_db(
        app,
        postgres_settings=postgres_settings,
        add_write_connection_pool=with_transactions,
    )
    print("DB connection setup.")


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection."""
    print("Closing up DB connection...")
    await close_db_connection(app)
    print("DB connection closed.")


handler = Mangum(
    app,
    lifespan="off",
    text_mime_types=[
        # Avoid base64 encoding any text/* or application/* mime-types
        "text/",
        "application/",
    ],
)


if "AWS_EXECUTION_ENV" in os.environ:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.router.startup())
