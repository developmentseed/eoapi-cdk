import asyncio
import base64
import json
import os
from typing import Any

import boto3


def get_secret_dict_by_name(secret_name: str) -> dict[str, Any]:
    """Retrieve a JSON secret from AWS Secrets Manager by secret name or ARN."""
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager")
    response = client.get_secret_value(SecretId=secret_name)

    if "SecretString" in response:
        return json.loads(response["SecretString"])

    return json.loads(base64.b64decode(response["SecretBinary"]))


def get_secret_dict(secret_arn_env_var: str) -> dict[str, Any]:
    """Retrieve a JSON secret from AWS Secrets Manager using an env var name."""
    secret_arn = os.environ.get(secret_arn_env_var)
    if not secret_arn:
        raise ValueError(f"{secret_arn_env_var} is not set!")

    return get_secret_dict_by_name(secret_arn)


def ensure_event_loop() -> asyncio.AbstractEventLoop:
    """Return the current event loop, creating and installing one if needed.

    Lambda request handling may enter synchronous code paths that need a current
    loop for container-scoped async initialization before control reaches the
    ASGI adapter.
    """
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


def run_async(coro: Any) -> Any:
    """Run an async coroutine from synchronous Lambda setup code.

    This uses the installed reusable loop instead of ``asyncio.run(...)`` so
    long-lived async resources are not created on a temporary loop that is then
    closed immediately.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        loop = ensure_event_loop()
        return loop.run_until_complete(coro)

    raise RuntimeError("Cannot run Lambda initialization inside an active event loop")
