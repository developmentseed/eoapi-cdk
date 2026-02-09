import base64
import json
import logging
import os
from collections import defaultdict
from datetime import datetime
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

CollectionRecords = DefaultDict[str, Tuple[Dict[str, Any], str, datetime]]
CollectionItems = DefaultDict[str, Dict[str, Tuple[Dict[str, Any], str, datetime]]]


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


def parse_message_data(message_id: str, message_str: str) -> Dict[str, Any]:
    """Parse message data, handling both S3 events and direct STAC JSON."""
    if is_s3_event(message_str):
        logger.debug(f"[{message_id}] Processing S3 event notification")
        return process_s3_event(message_str)
    else:
        return json.loads(message_str)


def store_item_if_newer(
    items_by_collection: DefaultDict[
        str, Dict[str, Tuple[Dict[str, Any], str, datetime]]
    ],
    item: Item,
    message_id: str,
    sns_timestamp: datetime,
) -> None:
    """Store item if it's newer than existing version."""
    if not item.collection:
        raise KeyError(f"item {item.id} is missing a collection id!")

    existing = items_by_collection[item.collection].get(item.id)
    if existing is None or sns_timestamp > existing[2]:
        if existing:
            logger.debug(
                f"[{message_id}] Replacing older version of item {item.id} "
                f"(old timestamp: {existing[2]}, new timestamp: {sns_timestamp})"
            )
        items_by_collection[item.collection][item.id] = (
            item.model_dump(mode="json"),
            message_id,
            sns_timestamp,
        )
    else:
        logger.debug(
            f"[{message_id}] Skipping older version of item {item.id} "
            f"(existing timestamp: {existing[2]}, message timestamp: {sns_timestamp})"
        )


def store_collection_if_newer(
    collections_dict: CollectionRecords,
    collection: Collection,
    message_id: str,
    sns_timestamp: datetime,
) -> None:
    """Store collection if it's newer than existing version."""
    existing = collections_dict.get(collection.id)
    if existing is None or sns_timestamp > existing[2]:
        if existing:
            logger.debug(
                f"[{message_id}] Replacing older version of collection {collection.id} "
                f"(old timestamp: {existing[2]}, new timestamp: {sns_timestamp})"
            )
        collections_dict[collection.id] = (
            collection.model_dump(mode="json"),
            message_id,
            sns_timestamp,
        )
    else:
        logger.debug(
            f"[{message_id}] Skipping older version of collection {collection.id} "
            f"(existing timestamp: {existing[2]}, message timestamp: {sns_timestamp})"
        )


def process_record(
    record: Dict[str, Any],
    collections_dict: CollectionRecords,
    items_by_collection: CollectionItems,
) -> Optional[BatchItemFailure]:
    """Process a single SQS record and return failure if processing fails."""
    message_id = record.get("messageId")
    if not message_id:
        logger.warning("Record missing messageId, cannot report failure for it.")
        return None

    try:
        sqs_body_str = record["body"]
        logger.debug(f"[{message_id}] SQS message body: {sqs_body_str}")
        sns_notification = json.loads(sqs_body_str)

        message_str = sns_notification["Message"]
        logger.debug(f"[{message_id}] SNS Message content: {message_str}")

        sns_timestamp_str = sns_notification["Timestamp"]
        sns_timestamp = datetime.fromisoformat(sns_timestamp_str.replace("Z", "+00:00"))
        logger.debug(f"[{message_id}] SNS Timestamp: {sns_timestamp}")

        message_data = parse_message_data(message_id, message_str)

        if message_data["type"] == "Feature":
            item = Item(**message_data)
            store_item_if_newer(items_by_collection, item, message_id, sns_timestamp)
        elif message_data["type"] == "Collection":
            collection = Collection(**message_data)
            store_collection_if_newer(
                collections_dict, collection, message_id, sns_timestamp
            )
        else:
            raise ValueError(
                f"expected either a 'Feature' or a 'Collection', received a {message_data['type']}"
            )

        logger.debug(f"[{message_id}] Successfully processed.")
        return None

    except (ValueError, KeyError, ValidationError, json.JSONDecodeError) as e:
        logger.error(f"[{message_id}] Failed with error: {e}", extra=record)
        return {"itemIdentifier": message_id}
    except Exception as e:
        logger.error(f"[{message_id}] Unexpected error: {e}", extra=record)
        return {"itemIdentifier": message_id}


def load_collections_to_db(
    collections_dict: DefaultDict[str, Tuple[Dict[str, Any], str, datetime]],
    pgstac_dsn: str,
) -> List[BatchItemFailure]:
    """Load collections to database and return failures."""
    if not collections_dict:
        return []

    collections = [collection for collection, _, _ in collections_dict.values()]
    message_ids = [msg_id for _, msg_id, _ in collections_dict.values()]

    try:
        with PgstacDB(dsn=pgstac_dsn) as db:
            loader = Loader(db=db)
            logger.info("loading collections into database.")
            loader.load_collections(
                file=collections,  # type: ignore
                insert_mode=Methods.upsert,
            )
            logger.info(f"successfully loaded {len(collections)} collections.")
        return []
    except Exception as e:
        logger.error(f"failed to load collections: {str(e)}")
        return [{"itemIdentifier": message_id} for message_id in message_ids]


def ensure_collection_exists(
    db: PgstacDB, loader: Loader, collection_id: str, items: List[Dict[str, Any]]
) -> None:
    """Create a placeholder collection if it doesn't exist and environment allows."""
    if not os.getenv("CREATE_COLLECTIONS_IF_MISSING"):
        return

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
                spatial=SpatialExtent(bbox=[(-180, -90, 180, 90)]),
                temporal=TimeInterval(interval=[[None, None]]),
            ),
            stac_version=items[0]["stac_version"],
        )
        loader.load_collections(
            [collection.model_dump()],  # type: ignore
            insert_mode=Methods.upsert,
        )


def load_items_for_collection(
    collection_id: str,
    items_dict: Dict[str, Tuple[Dict[str, Any], str, datetime]],
    pgstac_dsn: str,
) -> List[BatchItemFailure]:
    """Load items for a single collection to database and return failures."""
    items = [item_data for item_data, _, _ in items_dict.values()]
    message_ids = [msg_id for _, msg_id, _ in items_dict.values()]

    logger.debug(
        f"[{collection_id}] Processing {len(items)} unique items from {len(items_dict)} dict entries. Item IDs: {list(items_dict.keys())}"
    )

    try:
        with PgstacDB(dsn=pgstac_dsn) as db:
            loader = Loader(db=db)
            ensure_collection_exists(db, loader, collection_id, items)

            logger.info(f"[{collection_id}] loading items into database.")
            loader.load_items(
                file=items,  # type: ignore
                insert_mode=Methods.upsert,
            )
            logger.info(f"[{collection_id}] successfully loaded {len(items)} items.")
        return []
    except Exception as e:
        logger.error(f"[{collection_id}] failed to load items: {str(e)}")
        return [{"itemIdentifier": msg_id} for msg_id in message_ids]


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
    collections_dict: CollectionRecords = defaultdict(tuple)
    items_by_collection: CollectionItems = defaultdict(dict)

    for record in records:
        if failure := process_record(record, collections_dict, items_by_collection):
            batch_failures.append(failure)

    batch_failures.extend(load_collections_to_db(collections_dict, pgstac_dsn))

    for collection_id, items_dict in items_by_collection.items():
        batch_failures.extend(
            load_items_for_collection(collection_id, items_dict, pgstac_dsn)
        )

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
