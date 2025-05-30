"""AWS Lambda handler for STAC Item Generation."""

import json
import logging
import os
import subprocess
import traceback
from typing import TYPE_CHECKING, Annotated, Any, Dict, List, Optional, TypedDict

import boto3
from pydantic import ValidationError

if TYPE_CHECKING:
    from aws_lambda_typing.context import Context
else:
    Context = Annotated[object, "Context object"]

from stactools_item_generator.item import ItemRequest, create_stac_item

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


def get_topic_arn() -> str:
    item_load_topic_arn = os.environ.get("ITEM_LOAD_TOPIC_ARN")
    if not item_load_topic_arn:
        logger.error("Environment variable ITEM_LOAD_TOPIC_ARN is not set.")
        raise EnvironmentError("ITEM_LOAD_TOPIC_ARN must be set")

    return item_load_topic_arn


def process_record(record: Dict[str, Any], sns_client) -> None:
    """
    Processes a single SQS record (within a batch).
    Extracts the request, calls create_stac_item, and publishes the result.
    Raises exceptions on failure.
    """
    message_id = record.get("messageId", "UNKNOWN_ID")
    logger.info(f"Processing record: {message_id}")
    message_str = None
    try:
        sqs_body_str = record["body"]
        logger.debug(f"[{message_id}] SQS message body: {sqs_body_str}")
        sns_notification = json.loads(sqs_body_str)

        message_str = sns_notification["Message"]
        logger.debug(f"[{message_id}] SNS Message content: {message_str}")

        message_data = json.loads(message_str)
        item_request = ItemRequest(**message_data)
        logger.info(
            f"[{message_id}] Parsed ItemRequest for package: {item_request.package_name}"
        )
        logger.debug(f"[{message_id}] Full ItemRequest: {item_request.model_dump_json()}")

        stac_item = create_stac_item(item_request)
        logger.info(f"[{message_id}] Successfully created STAC item: {stac_item.id}")
        logger.debug(
            f"[{message_id}] Generated STAC Item JSON (sample): "
            f"{ {k: v for k, v in stac_item.model_dump().items() if k in ['id', 'collection', 'properties']} }"
        )

        stac_item_json = stac_item.model_dump_json()

        item_load_topic_arn = get_topic_arn()
        logger.info(
            f"[{message_id}] Publishing STAC item {stac_item.id} to {item_load_topic_arn}"
        )
        response = sns_client.publish(
            TopicArn=item_load_topic_arn,
            Message=stac_item_json,
        )
        logger.info(
            f"[{message_id}] SNS publish response MessageId: {response.get('MessageId')}"
        )

    except json.JSONDecodeError as e:
        logger.error(f"[{message_id}] Failed to decode JSON: {e}")
        logger.error(f"[{message_id}] Problematic data (SQS Body): {record.get('body')}")
        raise
    except ValidationError as e:
        logger.error(f"[{message_id}] Failed to validate ItemRequest: {e}")
        logger.error(f"[{message_id}] Validation errors:\n{e.errors()}")
        problem_data = message_str if message_str is not None else record.get("body")
        logger.error(
            f"[{message_id}] Problematic data (SNS Message or SQS Body): {problem_data}"
        )
        raise
    except (
        subprocess.CalledProcessError
    ) as e:  # <--- Catching the imported exception type
        logger.error(f"[{message_id}] Subprocess command failed:")
        logger.error(f"[{message_id}] Command: {' '.join(e.cmd)}")
        logger.error(f"[{message_id}] Return code: {e.returncode}")
        logger.error(f"[{message_id}] Stdout: {e.stdout}")
        logger.error(f"[{message_id}] Stderr: {e.stderr}")
        raise
    except Exception as e:
        logger.error(
            f"[{message_id}] An unexpected error occurred processing record: {e}"
        )
        logger.error(traceback.format_exc())
        raise


class BatchItemFailure(TypedDict):
    itemIdentifier: str


class PartialBatchFailureResponse(TypedDict):
    batchItemFailures: List[BatchItemFailure]


def handler(
    event: Dict[str, Any], context: Context
) -> Optional[PartialBatchFailureResponse]:
    """
    AWS Lambda handler function triggered by SQS with batching enabled.

    Processes messages in batches, attempts to generate STAC items, publishes
    successful results to SNS, and reports partial batch failures to SQS.
    """
    try:
        sns_client = boto3.client("sns", region_name=os.getenv("AWS_DEFAULT_REGION"))
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise EnvironmentError("AWS_DEFAULT_REGION must be set") from e

    records = event.get("Records", [])
    aws_request_id = getattr(context, "aws_request_id", "N/A")
    remaining_time = getattr(context, "get_remaining_time_in_millis", lambda: "N/A")()

    logger.info(f"Received batch with {len(records)} records.")
    logger.debug(
        f"Lambda Context: RequestId={aws_request_id}, RemainingTime={remaining_time}ms"
    )

    batch_item_failures: List[BatchItemFailure] = []

    for record in records:
        message_id = record.get("messageId")
        if not message_id:
            logger.warning("Record missing messageId, cannot report failure for it.")
            continue

        try:
            process_record(record, sns_client)
            logger.info(f"[{message_id}] Successfully processed.")

        except Exception:
            logger.error(f"[{message_id}] Marked as failed.")
            batch_item_failures.append({"itemIdentifier": message_id})

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
