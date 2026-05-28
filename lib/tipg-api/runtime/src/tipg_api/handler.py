"""Handler for AWS Lambda."""

import logging
import os
from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager
from typing import Any

from mangum import Mangum
from snapshot_restore_py import register_after_restore, register_before_snapshot
from tipg.collections import register_collection_catalog
from tipg.database import connect_to_db
from tipg.main import app
from tipg.settings import (
    CustomSQLSettings,
    DatabaseSettings,
    PostgresSettings,
)
from utils import ensure_event_loop, get_secret_dict, run_async

logger = logging.getLogger(__name__)

db_settings = DatabaseSettings()
custom_sql_settings = CustomSQLSettings()

_connection_initialized = False
_original_lifespan = app.router.lifespan_context


def _build_postgres_settings() -> PostgresSettings:
    """Fetch credentials from Secrets Manager and build PostgresSettings."""
    secret = get_secret_dict(secret_arn_env_var="PGSTAC_SECRET_ARN")
    return PostgresSettings(
        postgres_host=secret["host"],
        postgres_dbname=secret["dbname"],
        postgres_user=secret["username"],
        postgres_pass=secret["password"],
        postgres_port=int(secret["port"]),
    )


def _close_db_pool() -> None:
    """Close the current database pool if one exists."""
    if hasattr(app, "state") and hasattr(app.state, "pool") and app.state.pool:
        try:
            app.state.pool.close()
        except Exception:
            logger.exception("SnapStart: error closing database pool")
        finally:
            app.state.pool = None


async def _initialize_connection() -> None:
    """Create a fresh database connection pool and register collections."""
    global _connection_initialized

    _close_db_pool()
    await connect_to_db(
        app,
        schemas=db_settings.schemas,
        tipg_schema=db_settings.tipg_schema,
        user_sql_files=custom_sql_settings.sql_files,
        settings=_build_postgres_settings(),
    )
    await register_collection_catalog(
        app,
        db_settings=db_settings,
    )
    _connection_initialized = True


async def _shutdown_connection() -> None:
    """Close the current database pool if it exists."""
    global _connection_initialized

    _close_db_pool()
    _connection_initialized = False


@register_before_snapshot
def on_snapshot() -> dict[str, int]:
    """Close database connections before Lambda SnapStart takes a snapshot."""
    _close_db_pool()
    return {"statusCode": 200}


@register_after_restore
def on_snap_restore() -> dict[str, int]:
    """Recreate database connections after Lambda SnapStart restores a snapshot."""
    try:
        run_async(_initialize_connection())
    except Exception:
        logger.exception("SnapStart: failed to initialize database connection")
        raise

    return {"statusCode": 200}


@asynccontextmanager
async def lifespan(app_instance) -> AsyncIterator[Mapping[str, Any] | None]:
    """Wrap the upstream lifespan with database setup and teardown.

    We keep the app's lifespan wiring intact for non-Lambda contexts, but the
    Lambda runtime below uses ``Mangum(..., lifespan="off")`` and performs
    connection setup explicitly. In sandbox testing, Mangum lifespan handling
    was not a drop-in replacement for Lambda-container-scoped pool reuse.
    """
    async with _original_lifespan(app_instance) as state:
        await _initialize_connection()
        try:
            yield state
        finally:
            await _shutdown_connection()


app.router.lifespan_context = lifespan

# The Lambda runtime initializes long-lived async resources on an installed
# reusable loop, then hands request execution to Mangum. ``ensure_event_loop``
# is a defensive step for those synchronous initialization paths. It is not here
# because normal FastAPI route execution cannot run without it.
_asgi_handler = Mangum(app, lifespan="off")


def handler(event: Any, context: Any) -> dict[str, Any]:
    """Handle AWS Lambda events with a reusable installed event loop.

    This supports synchronous Lambda-side async setup such as cold-start and
    SnapStart restore initialization before control passes to Mangum.
    """
    ensure_event_loop()
    return _asgi_handler(event, context)


if "AWS_EXECUTION_ENV" in os.environ:
    # Avoid ``asyncio.run(...)`` here. It would create the pool on a temporary
    # loop and then close it, which is a poor fit for container-scoped async
    # resources that should live on the installed reusable loop.
    run_async(_initialize_connection())
