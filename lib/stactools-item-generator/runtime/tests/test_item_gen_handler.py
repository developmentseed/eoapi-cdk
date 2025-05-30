import json
import logging
import os
import subprocess
from unittest.mock import patch

import pytest
from stac_pydantic.item import Item
from stactools_item_generator import handler as item_gen_handler
from stactools_item_generator.item import ItemRequest


@pytest.fixture(autouse=True)
def setup_environment(monkeypatch):
    """Set necessary environment variables for tests."""
    monkeypatch.setenv(
        "ITEM_LOAD_TOPIC_ARN", "arn:aws:sns:us-east-1:123456789012:fake-topic"
    )
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")


@pytest.fixture
def mock_context(mocker):
    """Create a mock Lambda context object."""
    mock_ctx = mocker.MagicMock()
    mock_ctx.aws_request_id = "test-request-id"
    mock_ctx.get_remaining_time_in_millis.return_value = 300000  # 5 minutes
    return mock_ctx


@pytest.fixture
def mock_sns_client(mocker):
    """Mock the boto3 SNS client and its publish method."""
    mock_client_instance = mocker.MagicMock()
    mock_client_instance.publish.return_value = {"MessageId": "fake-sns-message-id"}

    mock_boto_client = patch(
        "stactools_item_generator.handler.boto3.client",
        return_value=mock_client_instance,
    ).start()

    yield mock_client_instance

    mock_boto_client.stop()


@pytest.fixture
def mock_create_stac_item(mocker):
    """Mock the create_stac_item function."""
    # Create a realistic-looking mock Item object
    mock_item_dict = {
        "type": "Feature",
        "stac_version": "1.0.0",
        "id": "test_item_id",
        "properties": {
            "datetime": "2023-01-01T00:00:00Z",
        },
        "geometry": {"type": "Point", "coordinates": [0, 0]},
        "links": [],
        "assets": {},
        "bbox": [0, 0, 0, 0],
        "stac_extensions": [],
        "collection": "test_collection",
    }
    mock_item = Item(**mock_item_dict)

    # Patch the function to return our mock item
    mock_func = patch(
        "stactools_item_generator.handler.create_stac_item", return_value=mock_item
    ).start()

    # Store the mock item for easy access
    mock_func.mock_item = mock_item
    mock_func.mock_item_dict = mock_item_dict
    mock_func.mock_item_json = mock_item.model_dump_json()

    yield mock_func

    mock_func.stop()


# --- Helper Function ---


def create_sqs_event(messages: list[dict]) -> dict:
    """Helper function to create an SQS event structure."""
    records = []
    for i, msg_data in enumerate(messages):
        # Simulate the SNS -> SQS structure
        sns_message_str = json.dumps(msg_data)
        sns_notification = {
            "Type": "Notification",
            "MessageId": f"sns-msg-id-{i}",
            "TopicArn": "arn:aws:sns:us-east-1:123456789012:source-topic",
            "Subject": "Test Subject",
            "Message": sns_message_str,
            "Timestamp": "2023-01-01T12:00:00.000Z",
            "SignatureVersion": "1",
        }
        sqs_body_str = json.dumps(sns_notification)
        records.append(
            {
                "messageId": f"sqs-msg-id-{i}",
                "receiptHandle": f"receipt-handle-{i}",
                "body": sqs_body_str,
                "attributes": {
                    "ApproximateReceiveCount": "1",
                    "SentTimestamp": "1672574400000",
                    "SenderId": "ARO...",
                    "ApproximateFirstReceiveTimestamp": "1672574400010",
                },
                "messageAttributes": {},
                "md5OfBody": f"md5-{i}",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:us-east-1:123456789012:your-queue",
                "awsRegion": "us-east-1",
            }
        )
    return {"Records": records}


# --- Test Cases ---


def test_handler_success_single_message(
    mock_context, mock_sns_client, mock_create_stac_item, caplog
):
    """Test successful processing of a single valid SQS message."""
    # Arrange
    caplog.set_level(logging.INFO)
    item_request_data = {
        "package_name": "stactools-test",
        "group_name": "testgroup",
        "create_item_args": ["input/file.tif"],
        "create_item_options": {"option1": "value1"},
        "collection_id": "test_collection_input",
    }
    event = create_sqs_event([item_request_data])

    # Set up mock to respect collection_id
    mock_item_with_collection = Item(
        **{
            **mock_create_stac_item.mock_item_dict,
            "collection": item_request_data["collection_id"],
        }
    )
    mock_create_stac_item.return_value = mock_item_with_collection
    mock_create_stac_item.mock_item = mock_item_with_collection
    mock_create_stac_item.mock_item_json = mock_item_with_collection.model_dump_json()

    # Act
    result = item_gen_handler.handler(event, mock_context)

    # Assert
    assert result is None  # Successful batch processing returns None

    # Check create_stac_item call
    mock_create_stac_item.assert_called_once()
    call_args, call_kwargs = mock_create_stac_item.call_args
    assert len(call_args) == 1
    assert isinstance(call_args[0], ItemRequest)
    assert call_args[0].package_name == item_request_data["package_name"]
    assert call_args[0].group_name == item_request_data["group_name"]
    assert call_args[0].create_item_args == item_request_data["create_item_args"]
    assert call_args[0].create_item_options == item_request_data["create_item_options"]
    assert call_args[0].collection_id == item_request_data["collection_id"]

    # Check SNS publish call
    mock_sns_client.publish.assert_called_once_with(
        TopicArn=os.environ["ITEM_LOAD_TOPIC_ARN"],
        Message=mock_create_stac_item.mock_item_json,
    )

    # Check logs
    assert "Received batch with 1 records." in caplog.text
    assert f"Processing record: {event['Records'][0]['messageId']}" in caplog.text
    assert (
        f"Parsed ItemRequest for package: {item_request_data['package_name']}"
        in caplog.text
    )
    assert "Successfully created STAC item:" in caplog.text
    assert "Publishing STAC item" in caplog.text
    assert "SNS publish response MessageId: fake-sns-message-id" in caplog.text
    assert "Successfully processed." in caplog.text
    assert "Finished processing batch. All records successful." in caplog.text


def test_handler_success_multiple_messages(
    mock_context, mock_sns_client, mock_create_stac_item, mocker, caplog
):
    """Test successful processing of multiple valid SQS messages."""
    # Arrange
    item_request_data1 = {
        "package_name": "stactools-test1",
        "group_name": "testgroup1",
        "create_item_args": ["input1.tif"],
    }
    item_request_data2 = {
        "package_name": "stactools-test2",
        "group_name": "testgroup2",
        "create_item_args": ["input2.tif"],
        "collection_id": "coll2",
    }
    event = create_sqs_event([item_request_data1, item_request_data2])

    # Configure mock to return different items for each call
    item1_dict = {**mock_create_stac_item.mock_item_dict, "id": "item1"}
    item2_dict = {
        **mock_create_stac_item.mock_item_dict,
        "id": "item2",
        "collection": "coll2",
    }

    item1 = Item(**item1_dict)
    item2 = Item(**item2_dict)

    item1_json = item1.model_dump_json()
    item2_json = item2.model_dump_json()

    mock_create_stac_item.side_effect = [item1, item2]

    # Act
    result = item_gen_handler.handler(event, mock_context)

    # Assert
    assert result is None
    assert mock_create_stac_item.call_count == 2
    assert mock_sns_client.publish.call_count == 2

    # Check publish calls
    assert mock_sns_client.publish.call_args_list[0] == mocker.call(
        TopicArn=os.environ["ITEM_LOAD_TOPIC_ARN"], Message=item1_json
    )
    assert mock_sns_client.publish.call_args_list[1] == mocker.call(
        TopicArn=os.environ["ITEM_LOAD_TOPIC_ARN"], Message=item2_json
    )

    assert "Successfully processed." in caplog.text
    assert caplog.text.count("Successfully processed.") == 2
    assert "Finished processing batch. All records successful." in caplog.text


def test_handler_partial_failure_create_item(
    mock_context, mock_sns_client, mock_create_stac_item, caplog
):
    """Test partial batch failure when create_stac_item raises an error."""
    # Arrange
    item_request_data_ok = {
        "package_name": "stactools-ok",
        "group_name": "okgroup",
        "create_item_args": ["ok.tif"],
        "collection_id": "coll_ok",
    }
    item_request_data_fail = {
        "package_name": "stactools-fail",
        "group_name": "failgroup",
        "create_item_args": ["fail.tif"],
    }
    event = create_sqs_event([item_request_data_ok, item_request_data_fail])

    # Set up mock to succeed for first call and fail for second
    mock_item_ok_dict = {
        **mock_create_stac_item.mock_item_dict,
        "id": "item_ok",
        "collection": "coll_ok",
    }
    mock_item_ok = Item(**mock_item_ok_dict)
    mock_item_ok_json = mock_item_ok.model_dump_json()

    # Simulate subprocess error
    mock_exception = subprocess.CalledProcessError(
        returncode=1,
        cmd=["uvx", "..."],
        output="stdout data",
        stderr="stderr error message",
    )

    mock_create_stac_item.side_effect = [mock_item_ok, mock_exception]

    # Act
    result = item_gen_handler.handler(event, mock_context)

    # Assert
    expected_failures = [{"itemIdentifier": event["Records"][1]["messageId"]}]
    assert result == {"batchItemFailures": expected_failures}

    # Check calls
    assert mock_create_stac_item.call_count == 2
    mock_sns_client.publish.assert_called_once_with(
        TopicArn=os.environ["ITEM_LOAD_TOPIC_ARN"], Message=mock_item_ok_json
    )

    # Check logs
    assert f"[{event['Records'][0]['messageId']}] Successfully processed." in caplog.text
    assert (
        f"[{event['Records'][1]['messageId']}] Subprocess command failed:" in caplog.text
    )
    assert "stderr error message" in caplog.text
    assert f"[{event['Records'][1]['messageId']}] Marked as failed." in caplog.text
    assert "Finished processing batch. 1 failure(s) reported." in caplog.text


def test_handler_partial_failure_json_decode(
    mock_context, mock_sns_client, mock_create_stac_item, caplog
):
    """Test partial batch failure when JSON decoding fails."""
    # Arrange
    item_request_data_ok = {
        "package_name": "stactools-ok",
        "group_name": "okgroup",
        "create_item_args": ["ok.tif"],
        "collection_id": "coll_ok",
    }
    invalid_json_body = (
        '{"Message": "{"key": "value", }", "Type": "Notification"}'  # Invalid JSON
    )

    event = create_sqs_event([item_request_data_ok])
    # Add malformed record
    malformed_record = {
        "messageId": "sqs-msg-id-malformed",
        "receiptHandle": "receipt-handle-malformed",
        "body": invalid_json_body,
        "attributes": {},
        "messageAttributes": {},
        "md5OfBody": "md5-malformed",
        "eventSource": "aws:sqs",
        "eventSourceARN": "arn:aws:sqs:us-east-1:123456789012:your-queue",
        "awsRegion": "us-east-1",
    }
    event["Records"].append(malformed_record)

    # Configure mock for good record
    mock_item_ok_dict = {
        **mock_create_stac_item.mock_item_dict,
        "id": "item_ok",
        "collection": "coll_ok",
    }
    mock_item_ok = Item(**mock_item_ok_dict)
    mock_item_ok_json = mock_item_ok.model_dump_json()
    mock_create_stac_item.return_value = mock_item_ok

    # Act
    result = item_gen_handler.handler(event, mock_context)

    # Assert
    expected_failures = [{"itemIdentifier": malformed_record["messageId"]}]
    assert result == {"batchItemFailures": expected_failures}

    # Check calls
    mock_create_stac_item.assert_called_once()
    mock_sns_client.publish.assert_called_once_with(
        TopicArn=os.environ["ITEM_LOAD_TOPIC_ARN"], Message=mock_item_ok_json
    )

    # Check logs
    assert f"[{malformed_record['messageId']}] Failed to decode JSON:" in caplog.text
    assert f"Problematic data (SQS Body): {invalid_json_body}" in caplog.text
    assert f"[{malformed_record['messageId']}] Marked as failed." in caplog.text


def test_handler_partial_failure_validation(
    mock_context, mock_sns_client, mock_create_stac_item, caplog
):
    """Test partial batch failure when ItemRequest validation fails."""
    # Arrange
    item_request_data_ok = {
        "package_name": "stactools-ok",
        "group_name": "okgroup",
        "create_item_args": ["ok.tif"],
    }
    item_request_data_invalid = {
        # Missing required field 'package_name'
        "group_name": "invalidgroup",
        "create_item_args": ["invalid.tif"],
    }
    event = create_sqs_event([item_request_data_ok, item_request_data_invalid])

    # Configure mock for good record
    mock_item_ok_dict = {**mock_create_stac_item.mock_item_dict, "id": "item_ok"}
    mock_item_ok = Item(**mock_item_ok_dict)
    mock_item_ok_json = mock_item_ok.model_dump_json()
    mock_create_stac_item.return_value = mock_item_ok

    # Act
    result = item_gen_handler.handler(event, mock_context)

    # Assert
    expected_failures = [{"itemIdentifier": event["Records"][1]["messageId"]}]
    assert result == {"batchItemFailures": expected_failures}

    # Check calls
    mock_create_stac_item.assert_called_once()
    mock_sns_client.publish.assert_called_once_with(
        TopicArn=os.environ["ITEM_LOAD_TOPIC_ARN"], Message=mock_item_ok_json
    )

    # Check logs
    assert (
        f"[{event['Records'][1]['messageId']}] Failed to validate ItemRequest:"
        in caplog.text
    )
    assert "Validation errors:" in caplog.text
    invalid_request_str = json.dumps(item_request_data_invalid)
    assert (
        f"Problematic data (SNS Message or SQS Body): {invalid_request_str}"
        in caplog.text
    )
    assert f"[{event['Records'][1]['messageId']}] Marked as failed." in caplog.text


def test_handler_all_records_fail(
    mock_context, mock_sns_client, mock_create_stac_item, caplog
):
    """Test when all records in a batch fail."""
    # Arrange
    invalid_request_1 = {
        # Missing required fields
        "create_item_args": ["file1.tif"]
    }
    invalid_request_2 = {
        # Missing required fields
        "create_item_args": ["file2.tif"]
    }
    event = create_sqs_event([invalid_request_1, invalid_request_2])

    # Act
    result = item_gen_handler.handler(event, mock_context)

    # Assert
    expected_failures = [
        {"itemIdentifier": event["Records"][0]["messageId"]},
        {"itemIdentifier": event["Records"][1]["messageId"]},
    ]
    assert result == {"batchItemFailures": expected_failures}

    # Check calls - should never call these since validation fails
    mock_create_stac_item.assert_not_called()
    mock_sns_client.publish.assert_not_called()

    # Check logs
    assert "Finished processing batch. 2 failure(s) reported." in caplog.text


def test_handler_empty_batch(
    mock_context, mock_sns_client, mock_create_stac_item, caplog
):
    """Test handling an empty batch of records."""
    # Arrange
    event = {"Records": []}

    # Act
    result = item_gen_handler.handler(event, mock_context)

    # Assert
    assert result is None
    mock_create_stac_item.assert_not_called()
    mock_sns_client.publish.assert_not_called()
    assert "Received batch with 0 records." in caplog.text
    assert "Finished processing batch. All records successful." in caplog.text


def test_handler_with_general_exception(
    mock_context, mock_sns_client, mock_create_stac_item, caplog
):
    """Test handling of unexpected exceptions during processing."""
    # Arrange
    item_request_data = {
        "package_name": "stactools-test",
        "group_name": "testgroup",
        "create_item_args": ["input/file.tif"],
    }
    event = create_sqs_event([item_request_data])
    message_id = event["Records"][0]["messageId"]

    # Set up mock to raise an unexpected exception
    mock_create_stac_item.side_effect = Exception("Unexpected error during processing")

    # Act
    result = item_gen_handler.handler(event, mock_context)

    # Assert
    expected_failures = [{"itemIdentifier": message_id}]
    assert result == {"batchItemFailures": expected_failures}

    # Check logs - updated to match the actual log message format
    assert (
        f"[{message_id}] An unexpected error occurred processing record: Unexpected error during processing"
        in caplog.text
    )
    assert "Unexpected error" in caplog.text
    assert f"[{message_id}] Marked as failed." in caplog.text


def test_handler_sns_publish_failure(
    mock_context, mock_sns_client, mock_create_stac_item, caplog
):
    """Test handling of SNS publish failures."""
    # Arrange
    item_request_data = {
        "package_name": "stactools-test",
        "group_name": "testgroup",
        "create_item_args": ["input/file.tif"],
    }
    event = create_sqs_event([item_request_data])

    # Configure mock to simulate SNS publish failure
    mock_sns_client.publish.side_effect = Exception("SNS publish failed")

    # Act
    result = item_gen_handler.handler(event, mock_context)

    # Assert
    expected_failures = [{"itemIdentifier": event["Records"][0]["messageId"]}]
    assert result == {"batchItemFailures": expected_failures}

    # Check logs
    assert "SNS publish failed" in caplog.text
    assert f"[{event['Records'][0]['messageId']}] Marked as failed." in caplog.text
