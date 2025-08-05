"""
Handler for AWS Lambda.
"""

from mangum import Mangum
from stac_auth_proxy import create_app

app = create_app()
handler = Mangum(app, lifespan="off")
