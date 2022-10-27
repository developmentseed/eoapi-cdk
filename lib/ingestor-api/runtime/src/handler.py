"""
Entrypoint for Lambda execution.
"""

from mangum import Mangum

from .main import app

handler = Mangum(app, lifespan="off")
