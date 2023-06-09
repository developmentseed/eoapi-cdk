"""
Handler for AWS Lambda.
"""

import os
from mangum import Mangum
from utils import get_secret_dict
from titiler.pgstac.main import app

pgstac_secret_arn = os.environ["PGSTAC_SECRET_ARN"]

secret = get_secret_dict(pgstac_secret_arn)
os.environ.update(
    {
        "postgres_host": secret["host"],
        "postgres_dbname": secret["dbname"],
        "postgres_user": secret["username"],
        "postgres_pass": secret["password"],
        "postgres_port": str(secret["port"]),
    }
)

handler = Mangum(app)
