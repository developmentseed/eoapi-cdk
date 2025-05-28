import base64
import json
import logging
import os
from collections import defaultdict
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    DefaultDict,
    Dict,
    List,
    Optional,
    TypedDict,
)

import boto3.session
from pydantic import ValidationError
from pypgstac.db import PgstacDB
from pypgstac.load import Loader, Methods
from stac_pydantic.item import Item

if TYPE_CHECKING:
    from aws_lambda_typing.context import Context
else:
    Context = Annotated[object, "Context object"]

logger = logging.getLogger()
if logger.hasHandlers():
    logger.handlers.clear()

log_handler = logging.StreamHandler()  # <--- Renamed handler variable

log_level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
log_level = logging._nameToLevel.get(log_level_name, logging.INFO)
logger.setLevel(log_level)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log_handler.setFormatter(formatter)
logger.addHandler(log_handler)


class BatchItemFailure(TypedDict):
    itemIdentifier: str


class PartialBatchFailureResponse(TypedDict):
    batchItemFailures: List[BatchItemFailure]


def get_secret_dict(secret_name: str) -> Dict:
    """Retrieve secrets from AWS Secrets Manager

    Args:
        secret_name (str): name of aws secrets manager secret containing database connection secrets
        profile_name (str, optional): optional name of aws profile for use in debugger only

    Returns:
        secrets (dict): decrypted secrets in dict
    """

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager")

    get_secret_value_response = client.get_secret_value(SecretId=secret_name)

    if "SecretString" in get_secret_value_response:
        return json.loads(get_secret_value_response["SecretString"])
    else:
        return json.loads(base64.b64decode(get_secret_value_response["SecretBinary"]))


def get_pgstac_dsn() -> str:
    secret_arn = os.getenv("PGSTAC_SECRET_ARN")
    if not secret_arn:
        logger.error("Environment variable PGSTAC_SECRET_ARN is not set.")
        raise EnvironmentError("PGSTAC_SECRET_ARN must be set")

    secret_dict = get_secret_dict(secret_name=secret_arn)

    return f"postgres://{secret_dict['username']}:{secret_dict['password']}@{secret_dict['host']}:{secret_dict['port']}/{secret_dict['dbname']}"


def handler(
    event: Dict[str, Any], context: Context
) -> Optional[PartialBatchFailureResponse]:
    records = event.get("Records", [])
    aws_request_id = getattr(context, "aws_request_id", "N/A")
    remaining_time = getattr(context, "get_remaining_time_in_millis", lambda: "N/A")()

    logger.info(f"Received batch with {len(records)} records.")
    logger.debug(
        f"Lambda Context: RequestId={aws_request_id}, RemainingTime={remaining_time}ms"
    )
    pgstac_dsn = get_pgstac_dsn()

    batch_item_failures: List[BatchItemFailure] = []

    items_by_collection: DefaultDict[str, List[Dict[str, Any]]] = defaultdict(list)
    message_ids_by_collection: DefaultDict[str, List[str]] = defaultdict(list)
    for record in records:
        message_id = record.get("messageId")
        if not message_id:
            logger.warning("Record missing messageId, cannot report failure for it.")
            continue

        try:
            sqs_body_str = record["body"]
            logger.debug(f"[{message_id}] SQS message body: {sqs_body_str}")
            sns_notification = json.loads(sqs_body_str)

            message_str = sns_notification["Message"]
            logger.debug(f"[{message_id}] SNS Message content: {message_str}")

            message_data = json.loads(message_str)
            item = Item(**message_data)

            # validate item
            if not item.collection:
                raise KeyError(f"item {item.id} is missing a collection id!")

            items_by_collection[item.collection].append(item.model_dump(mode="json"))
            message_ids_by_collection[item.collection].append(message_id)
            logger.info(f"[{message_id}] Successfully processed.")

        except (ValueError, KeyError, ValidationError, json.JSONDecodeError) as e:
            logger.error(f"[{message_id}] Failed with error: {e}", extra=record)
            batch_item_failures.append({"itemIdentifier": message_id})

    for collection_id, items in items_by_collection.items():
        try:
            with PgstacDB(dsn=pgstac_dsn) as db:
                loader = Loader(db=db)
                logger.info(f"[{collection_id}] loading items into database.")
                loader.load_items(
                    file=items,  # type: ignore
                    # use insert_ignore to avoid overwritting existing items or upsert to replace
                    insert_mode=Methods.upsert,
                )
                logger.info(f"[{collection_id}] successfully loaded items.")
        except Exception as e:
            logger.error(f"[{collection_id}] failed to load items: {str(e)}")

            batch_item_failures.extend(
                [
                    {"itemIdentifier": message_id}
                    for message_id in message_ids_by_collection[collection_id]
                ]
            )

    if batch_item_failures:
        logger.warning(
            f"Finished processing batch. {len(batch_item_failures)} failure(s) reported."
        )
        logger.info(
            f"Returning failed item identifiers: {[f['itemIdentifier'] for f in batch_item_failures]}"
        )
        return {"batchItemFailures": batch_item_failures}
    else:
        logger.info("Finished processing batch. All records successful.")
        return None
