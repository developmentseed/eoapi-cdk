# STAC API Lambda runtime notes

This runtime uses a small event-loop helper layer around `Mangum(app, lifespan="off")`.

## Why this exists

We built a separate Lambda sandbox to understand FastAPI + Mangum + `asyncio` behavior in the eoapi-cdk deployment pattern. The goal was to explain why the runtime does explicit async initialization for database pools instead of relying on FastAPI startup hooks alone.

Observed behavior from that sandbox:

- Ordinary FastAPI route execution under Mangum worked without calling `ensure_event_loop()` first.
- The synchronous Lambda handler did not always have a running loop, but route execution inside Mangum did.
- `asyncio.run(...)` created long-lived async resources on a temporary loop that was different from the later request-handling loop.
- Under the sandbox setup, FastAPI startup/lifespan with Mangum `lifespan="auto"` ran per invocation rather than once per warm container.
- SnapStart restore hooks were synchronous, so async resource recreation still needed a reusable installed loop.

These were sandbox observations, not universal AWS guarantees. We use them as rationale for the runtime pattern below.

## Recommended eoapi-cdk pattern

For Lambda-container-scoped async resources such as database pools, eoapi-cdk prefers:

- explicit async initialization through a reusable installed event loop
- `Mangum(app, lifespan="off")`
- `ensure_event_loop()` before delegating to Mangum
- SnapStart before-snapshot and after-restore hooks when SnapStart is enabled

This means `ensure_event_loop()` is defensive support for synchronous setup paths such as cold-start initialization and SnapStart restore. It is not documented as a requirement for normal FastAPI route execution.

## Practical guidance

- Do not use `asyncio.run(...)` for long-lived async pools or clients created at import time.
- Do not assume FastAPI startup/lifespan under Mangum is a drop-in replacement for Lambda-container-scoped pool initialization.
- If SnapStart is enabled, close network resources before snapshot and recreate them after restore.

See [`src/stac_api/handler.py`](src/stac_api/handler.py) and [`../../utils/utils.py`](../../utils/utils.py) for the runtime implementation.
