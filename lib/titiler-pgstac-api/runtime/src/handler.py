"""
Handler for AWS Lambda.
"""

from mangum import Mangum
from config import ApiSettings
from titiler.pgstac.main import app

settings = ApiSettings()
settings.set_postgres_settings()
handler = Mangum(app)
