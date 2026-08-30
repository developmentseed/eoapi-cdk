"""
Handler for AWS Lambda.
"""

import asyncio
import os
from typing import Any

from mangum import Mangum
from stac_auth_proxy import create_app


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


app = create_app()
_asgi_handler = Mangum(app, lifespan="off")


def handler(event: Any, context: Any) -> dict[str, Any]:
    """Handle AWS Lambda events with a guaranteed current event loop."""
    _ensure_event_loop()
    return _asgi_handler(event, context)


if "AWS_EXECUTION_ENV" in os.environ:
    # Run the application's lifespan startup once per container.
    #
    # This previously called `app.router.startup()`, which Starlette 1.0 removed --
    # raising `AttributeError: 'APIRouter' object has no attribute 'startup'` at
    # import and making every invocation return a 500. stac-auth-proxy requires
    # `starlette>=1.0.1`, so this affects every deployment.
    #
    # `Router.startup()` would not have been correct even where it still exists: it
    # only ran the legacy `on_startup` handlers, and stac-auth-proxy registers none.
    # Its startup work (upstream health checks, conformance checks) lives in the
    # lifespan context that `create_app` wires via `lifespan=build_lifespan(...)`.
    #
    # Mangum's `lifespan="auto"`/`"on"` is not a substitute: Mangum runs the lifespan
    # around *every* invocation, which would repeat those upstream health and
    # conformance checks on each request. Entering the context once here keeps the
    # original intent -- start up once, on cold start.
    #
    # The context is deliberately left open for the life of the container and kept
    # in a module-level name so it is not garbage collected; Lambda gives no reliable
    # shutdown hook to exit it from.
    _loop = _ensure_event_loop()
    _lifespan_ctx = app.router.lifespan_context(app)
    _loop.run_until_complete(_lifespan_ctx.__aenter__())
