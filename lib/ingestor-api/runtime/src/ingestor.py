from datetime import datetime
import os
import decimal
from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Optional, Sequence

import boto3
from boto3.dynamodb.types import TypeDeserializer
import orjson
import pydantic
from pypgstac.load import Methods
from pypgstac.db import PgstacDB

from .dependencies import get_settings, get_table
from .schemas import Ingestion, Status
from .vedaloader import VEDALoader

if TYPE_CHECKING:
    from aws_lambda_typing import context as context_, events
    from aws_lambda_typing.events.dynamodb_stream import DynamodbRecord


def get_queued_ingestions(records: List["DynamodbRecord"]) -> Iterator[Ingestion]:
    deserializer = TypeDeserializer()
    for record in records:
        # Parse Record
        parsed = {
            k: deserializer.deserialize(v)
            for k, v in record["dynamodb"]["NewImage"].items()
        }
        ingestion = Ingestion.construct(**parsed)
        if ingestion.status == Status.queued:
            yield ingestion


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


def convert_decimals_to_float(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    DynamoDB stores floats as Decimals. We want to convert them back to floats
    before inserting them into pgSTAC to avoid any issues when the records are
    converted to JSON by pgSTAC.
    """

    def decimal_to_float(obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        raise TypeError

    return orjson.loads(
        orjson.dumps(
            item,
            default=decimal_to_float,
        )
    )


def load_into_pgstac(creds: DbCreds, ingestions: Sequence[Ingestion]):
    """
    Bulk insert STAC records into pgSTAC.
    """
    with PgstacDB(dsn=creds.dsn_string, debug=True) as db:
        loader = VEDALoader(db=db)

        items = [
            # NOTE: Important to deserialize values to convert decimals to floats
            convert_decimals_to_float(i.item)
            for i in ingestions
        ]

        print(f"Ingesting {len(items)} items")
        loading_result = loader.load_items(
            file=items,
            # use insert_ignore to avoid overwritting existing items or upsert to replace
            insert_mode=Methods.upsert,
        )

        # Trigger update on summaries and extents
        collections = set([item.collection for item in items])
        for collection in collections:
            loader.update_collection_summaries(collection)

        return loading_result


def update_dynamodb(
    ingestions: Sequence[Ingestion],
    status: Status,
    message: Optional[str] = None,
):
    """
    Bulk update DynamoDB with ingestion results.
    """
    # Update records in DynamoDB
    print(f"Updating ingested items status in DynamoDB, marking as {status}...")
    table = get_table(get_settings())
    with table.batch_writer(overwrite_by_pkeys=["created_by", "id"]) as batch:
        for ingestion in ingestions:
            batch.put_item(
                Item=ingestion.copy(
                    update={
                        "status": status,
                        "message": message,
                        "updated_at": datetime.now(),
                    }
                ).dynamodb_dict()
            )


def handler(event: "events.DynamoDBStreamEvent", context: "context_.Context"):
    # Parse input
    ingestions = list(get_queued_ingestions(event["Records"]))
    if not ingestions:
        print("No queued ingestions to process")
        return

    # Insert into PgSTAC DB
    outcome = Status.succeeded
    message = None
    try:
        load_into_pgstac(
            creds=get_db_credentials(os.environ["DB_SECRET_ARN"]),
            ingestions=ingestions,
        )
    except Exception as e:
        print(f"Encountered failure loading items into pgSTAC: {e}")
        outcome = Status.failed
        message = str(e)

    # Update DynamoDB with outcome
    update_dynamodb(
        ingestions=ingestions,
        status=outcome,
        message=message,
    )

    print("Completed batch...")
