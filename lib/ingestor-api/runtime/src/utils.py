from typing import Sequence

import boto3
import pydantic
from pypgstac.db import PgstacDB
from pypgstac.load import Methods
from fastapi.encoders import jsonable_encoder

from .loader import Loader
from .schemas import Ingestion


class DbCreds(pydantic.BaseModel):
    username: str
    password: str
    host: str
    port: int
    dbname: str
    engine: str

    @property
    def dsn_string(self) -> str:
        return f"{self.engine}://{self.username}:{self.password}@{self.host}:{self.port}/{self.dbname}"  # noqa


def get_db_credentials(secret_arn: str) -> DbCreds:
    """
    Load pgSTAC database credentials from AWS Secrets Manager.
    """
    print("Fetching DB credentials...")
    session = boto3.session.Session(region_name=secret_arn.split(":")[3])
    client = session.client(service_name="secretsmanager")
    response = client.get_secret_value(SecretId=secret_arn)
    return DbCreds.parse_raw(response["SecretString"])


def load_items(creds: DbCreds, ingestions: Sequence[Ingestion]):
    """
    Bulk insert STAC records into pgSTAC.
    """
    with PgstacDB(dsn=creds.dsn_string, debug=True) as db:
        loader = Loader(db=db)

        # serialize to JSON-friendly dicts (won't be necessary in Pydantic v2, https://github.com/pydantic/pydantic/issues/1409#issuecomment-1423995424)
        items = jsonable_encoder(i.item for i in ingestions)
        loading_result = loader.load_items(
            file=items,
            # use insert_ignore to avoid overwritting existing items or upsert to replace
            insert_mode=Methods.upsert,
        )

        return loading_result
