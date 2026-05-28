"""Entrypoint for Lambda execution."""

import asyncio
from typing import Any

from mangum import Mangum

from .main import app


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


_asgi_handler = Mangum(app, lifespan="off", api_gateway_base_path=app.root_path)


def handler(event: Any, context: Any) -> dict[str, Any]:
    """Handle AWS Lambda events with a guaranteed current event loop."""
    _ensure_event_loop()
    return _asgi_handler(event, context)
