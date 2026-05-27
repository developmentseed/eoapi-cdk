"""Handler for AWS Lambda."""

import asyncio
import logging
import os
from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager
from typing import Any

from mangum import Mangum
from snapshot_restore_py import register_after_restore, register_before_snapshot
from stac_fastapi.pgstac.app import app, with_transactions
from stac_fastapi.pgstac.config import PostgresSettings
from stac_fastapi.pgstac.db import close_db_connection, connect_to_db
from utils import get_secret_dict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

_connection_initialized = False
_original_lifespan = app.router.lifespan_context


def _build_postgres_settings() -> PostgresSettings:
    """Fetch credentials from Secrets Manager and build PostgresSettings."""
    logger.info("fetching pgstac secret")
    secret = get_secret_dict(secret_arn_env_var="PGSTAC_SECRET_ARN")
    return PostgresSettings(
        pghost=secret["host"],
        pgdatabase=secret["dbname"],
        pguser=secret["username"],
        pgpassword=secret["password"],
        pgport=int(secret["port"]),
    )


def _close_db_pools() -> None:
    """Close the current database pools if they exist."""
    if hasattr(app, "state") and hasattr(app.state, "readpool") and app.state.readpool:
        try:
            app.state.readpool.close()
        except Exception:
            logger.exception("SnapStart: error closing database readpool")
        finally:
            app.state.readpool = None

    if hasattr(app, "state") and hasattr(app.state, "writepool") and app.state.writepool:
        try:
            app.state.writepool.close()
        except Exception:
            logger.exception("SnapStart: error closing database writepool")
        finally:
            app.state.writepool = None


async def _initialize_connection() -> None:
    """Create fresh database connection pools for the application."""
    global _connection_initialized

    _close_db_pools()
    await connect_to_db(
        app,
        postgres_settings=_build_postgres_settings(),
        add_write_connection_pool=with_transactions,
    )
    _connection_initialized = True


async def _shutdown_connection() -> None:
    """Close the current database connection pools if they exist."""
    global _connection_initialized

    if (
        hasattr(app, "state")
        and hasattr(app.state, "readpool")
        and app.state.readpool
    ):
        await close_db_connection(app)
        app.state.readpool = None

    if hasattr(app, "state") and hasattr(app.state, "writepool"):
        app.state.writepool = None

    _connection_initialized = False


def _run_async(coro: Any) -> Any:
    """Run an async coroutine from a synchronous Lambda initialization hook."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    raise RuntimeError("Cannot run Lambda initialization inside an active event loop")


@register_before_snapshot
def on_snapshot() -> dict[str, int]:
    """Close database connections before Lambda SnapStart takes a snapshot."""
    _close_db_pools()
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

handler = Mangum(
    app,
    lifespan="off",
    text_mime_types=[
        "text/",
        "application/",
    ],
)


if "AWS_EXECUTION_ENV" in os.environ:
    logger.info("Cold start: initializing database connection...")
    _run_async(_initialize_connection())
    logger.info("Database connection initialized.")
