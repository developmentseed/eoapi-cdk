"""
Handler for AWS Lambda.
"""

import asyncio
import os

from mangum import Mangum
from stac_auth_proxy import create_app

app = create_app()
handler = Mangum(app, lifespan="off")


if "AWS_EXECUTION_ENV" in os.environ:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.router.startup())
