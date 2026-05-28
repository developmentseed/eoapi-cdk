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
    loop = _ensure_event_loop()
    loop.run_until_complete(app.router.startup())
