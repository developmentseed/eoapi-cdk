import os
from datetime import datetime
from typing import TYPE_CHECKING, Iterator, List, Optional, Sequence

from boto3.dynamodb.types import TypeDeserializer

from .dependencies import get_table
from .config import settings
from .schemas import Ingestion, Status
from .utils import get_db_credentials, load_items

if TYPE_CHECKING:
    from aws_lambda_typing import context as context_
    from aws_lambda_typing import events
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
    table = get_table(settings)
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
        load_items(
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
