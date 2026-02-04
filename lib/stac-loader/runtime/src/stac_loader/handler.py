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
    Tuple,
    TypedDict,
)

import boto3.session
from pydantic import ValidationError
from pypgstac.db import PgstacDB
from pypgstac.load import Loader, Methods
from stac_pydantic.collection import Collection, Extent, SpatialExtent, TimeInterval
from stac_pydantic.item import Item
from stac_pydantic.links import Link, Links

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

botocore_logger = logging.getLogger("botocore")
botocore_logger.setLevel(logging.WARN)


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


def is_s3_event(message_str: str) -> bool:
    """Check if the event data is an S3 event notification."""
    return "aws:s3" in message_str


def get_stac_object_from_s3(bucket_name: str, object_key: str) -> Dict[str, Any]:
    """Fetch STAC JSON from S3."""
    session = boto3.session.Session()
    s3_client = session.client("s3")

    try:
        logger.debug(f"Fetching STAC object from s3://{bucket_name}/{object_key}")
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        content = response["Body"].read()

        try:
            stac_json = content.decode("utf-8")
        except UnicodeDecodeError as e:
            logger.error(
                f"Failed to decode S3 object as UTF-8: s3://{bucket_name}/{object_key}"
            )
            raise ValueError("S3 object is not valid UTF-8 text") from e

        stac_data = json.loads(stac_json)
        logger.debug(
            f"Successfully parsed STAC metadata from S3: {stac_data.get('id', 'unknown')}"
        )

        return stac_data

    except Exception as e:
        logger.error(
            f"Failed to fetch STAC metadata from s3://{bucket_name}/{object_key}: {e}"
        )
        raise


def process_s3_event(message_str: str) -> Dict[str, Any]:
    """Process an S3 event notification and return STAC metadata."""
    try:
        message_data = json.loads(message_str)
        records: List[Dict[str, Any]] = message_data.get("Records", [])
        if not records:
            raise ValueError("no S3 event records!")
        elif len(records) > 1:
            raise ValueError("more than one S3 event record!")

        s3_data = records[0]["s3"]
        bucket_name = s3_data["bucket"]["name"]
        object_key = s3_data["object"]["key"]

        # Validate that this looks like a STAC file
        if not object_key.endswith((".json", ".geojson")):
            raise ValueError(
                f"S3 object key does not appear to be a STAC document: {object_key}"
            )

        stac_data = get_stac_object_from_s3(bucket_name, object_key)

        return stac_data

    except KeyError as e:
        logger.error(f"S3 event missing required field: {e}")
        raise ValueError(f"Invalid S3 event structure: missing {e}") from e
    except Exception as e:
        logger.error(f"Failed to process S3 event: {e}")
        raise


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

    batch_failures: List[BatchItemFailure] = []

    collections_dict: DefaultDict[str, Tuple[Dict[str, Any], str]] = defaultdict()
    # Track items by collection and item id to deduplicate within a batch
    # Maps: collection_id -> item_id -> (item_data, message_id)
    items_by_collection: DefaultDict[str, Dict[str, Tuple[Dict[str, Any], str]]] = (
        defaultdict(dict)
    )

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

            if is_s3_event(message_str):
                logger.debug(f"[{message_id}] Processing S3 event notification")
                message_data = process_s3_event(message_str)
            else:
                message_data = json.loads(message_str)

            if message_data["type"] == "Feature":
                item = Item(**message_data)

                if not item.collection:
                    raise KeyError(f"item {item.id} is missing a collection id!")

                # Store item by id, replacing any previous version in this batch
                items_by_collection[item.collection][item.id] = (
                    item.model_dump(mode="json"),
                    message_id,
                )
            elif message_data["type"] == "Collection":
                collection = Collection(**message_data)
                collections_dict[collection.id] = (
                    collection.model_dump(mode="json"),
                    message_id,
                )
            else:
                raise ValueError(
                    f"expected either a 'Feature' or a 'Collection', received a {message_data['type']}"
                )

            logger.debug(f"[{message_id}] Successfully processed.")

        except (ValueError, KeyError, ValidationError, json.JSONDecodeError) as e:
            logger.error(f"[{message_id}] Failed with error: {e}", extra=record)
            batch_failures.append({"itemIdentifier": message_id})
        except Exception as e:
            logger.error(f"[{message_id}] Unexpected error: {e}", extra=record)
            batch_failures.append({"itemIdentifier": message_id})

    if collections_dict:
        collections = [collection for collection, _ in collections_dict.values()]
        message_ids = [msg_id for _, msg_id in collections_dict.values()]
        try:
            with PgstacDB(dsn=pgstac_dsn) as db:
                loader = Loader(db=db)
                logger.info("loading collections into database.")
                loader.load_collections(
                    file=collections,  # type: ignore
                    insert_mode=Methods.upsert,
                )
                logger.info(f"successfully loaded {len(collections)} collections.")
        except Exception as e:
            logger.error(f"failed to load collections: {str(e)}")
            batch_failures.extend(
                [{"itemIdentifier": message_id} for message_id in message_ids]
            )

    for collection_id, items_dict in items_by_collection.items():
        # Extract items and message_ids from the dict structure
        items = [item_data for item_data, _ in items_dict.values()]
        message_ids = [msg_id for _, msg_id in items_dict.values()]

        logger.debug(
            f"[{collection_id}] Processing {len(items)} unique items from {len(items_dict)} dict entries. Item IDs: {list(items_dict.keys())}"
        )

        try:
            with PgstacDB(dsn=pgstac_dsn) as db:
                loader = Loader(db=db)
                if os.getenv("CREATE_COLLECTIONS_IF_MISSING"):
                    collection_exists = db.query_one(
                        f"SELECT count(*) as count from collections where id = '{collection_id}'"
                    )
                    if not collection_exists:
                        logger.info(
                            f"[{collection_id}] loading collection into database because it is missing."
                        )
                        collection = Collection(
                            id=collection_id,
                            description=collection_id,
                            links=Links([Link(href="placeholder", rel="self")]),
                            type="Collection",
                            license="proprietary",
                            extent=Extent(
                                spatial=SpatialExtent(bbox=[[-180, -90, 180, 90]]),
                                temporal=TimeInterval(interval=[[None, None]]),
                            ),
                            stac_version=items[0]["stac_version"],
                        )
                        loader.load_collections(
                            [collection.model_dump()],  # type: ignore
                            insert_mode=Methods.upsert,
                        )

                logger.info(f"[{collection_id}] loading items into database.")
                loader.load_items(
                    file=items,  # type: ignore
                    insert_mode=Methods.upsert,
                )
                logger.info(f"[{collection_id}] successfully loaded {len(items)} items.")
        except Exception as e:
            logger.error(f"[{collection_id}] failed to load items: {str(e)}")

            batch_failures.extend([{"itemIdentifier": msg_id} for msg_id in message_ids])

    if batch_failures:
        logger.warning(
            f"Finished processing batch. {len(batch_failures)} failure(s) reported."
        )
        logger.info(
            f"Returning failed item identifiers: {[f['itemIdentifier'] for f in batch_failures]}"
        )
        return {"batchItemFailures": batch_failures}
    else:
        logger.info("Finished processing batch. All records successful.")
        return None
