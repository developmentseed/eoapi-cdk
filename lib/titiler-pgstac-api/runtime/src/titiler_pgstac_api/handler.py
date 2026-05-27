"""Handler for AWS Lambda."""

import asyncio
import logging
import os
from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager
from typing import Any

from mangum import Mangum
from snapshot_restore_py import register_after_restore, register_before_snapshot
from titiler.pgstac.db import close_db_connection, connect_to_db
from titiler.pgstac.main import app
from titiler.pgstac.settings import PostgresSettings
from utils import get_secret_dict

logger = logging.getLogger(__name__)

_connection_initialized = False
_original_lifespan = app.router.lifespan_context


def _build_postgres_settings() -> PostgresSettings:
    """Fetch credentials from Secrets Manager and build PostgresSettings."""
    secret = get_secret_dict(secret_arn_env_var="PGSTAC_SECRET_ARN")
    return PostgresSettings(
        pghost=secret["host"],
        pgdatabase=secret["dbname"],
        pguser=secret["username"],
        pgpassword=secret["password"],
        pgport=int(secret["port"]),
    )


def _close_db_pool() -> None:
    """Close the current database pool if one exists."""
    if hasattr(app, "state") and hasattr(app.state, "dbpool") and app.state.dbpool:
        try:
            app.state.dbpool.close()
        except Exception:
            logger.exception("SnapStart: error closing database pool")
        finally:
            app.state.dbpool = None


async def _initialize_connection() -> None:
    """Create a fresh database connection pool for the application."""
    global _connection_initialized

    _close_db_pool()
    await connect_to_db(app, settings=_build_postgres_settings())
    _connection_initialized = True


async def _shutdown_connection() -> None:
    """Close the current database connection pool if it exists."""
    global _connection_initialized

    if hasattr(app, "state") and hasattr(app.state, "dbpool") and app.state.dbpool:
        await close_db_connection(app)
        app.state.dbpool = None

    _connection_initialized = False


def _ensure_event_loop() -> asyncio.AbstractEventLoop:
    """Return the current event loop, creating and installing one if needed."""
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        pass

    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


def _run_async(coro: Any) -> Any:
    """Run an async coroutine from a synchronous Lambda initialization hook."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        loop = _ensure_event_loop()
        return loop.run_until_complete(coro)

    raise RuntimeError("Cannot run Lambda initialization inside an active event loop")


@register_before_snapshot
def on_snapshot() -> dict[str, int]:
    """Close database connections before Lambda SnapStart takes a snapshot."""
    _close_db_pool()
    return {"statusCode": 200}


@register_after_restore
def on_snap_restore() -> dict[str, int]:
    """Recreate database connections after Lambda SnapStart restores a snapshot."""
    try:
        _run_async(_initialize_connection())
    except Exception:
        logger.exception("SnapStart: failed to initialize database connection")
        raise

    return {"statusCode": 200}


@asynccontextmanager
async def lifespan(app_instance) -> AsyncIterator[Mapping[str, Any] | None]:
    """Wrap the upstream lifespan with database setup and teardown."""
    async with _original_lifespan(app_instance) as state:
        await _initialize_connection()
        try:
            yield state
        finally:
            await _shutdown_connection()


app.router.lifespan_context = lifespan

_asgi_handler = Mangum(app, lifespan="off")


def handler(event: Any, context: Any) -> dict[str, Any]:
    """Handle AWS Lambda events with a guaranteed current event loop."""
    _ensure_event_loop()
    return _asgi_handler(event, context)


if "AWS_EXECUTION_ENV" in os.environ:
    _run_async(_initialize_connection())
