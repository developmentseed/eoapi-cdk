import json
import os
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from conftest import (
    TEST_COLLECTION_IDS,
    check_collection_exists,
    check_item_exists,
    count_collection_items,
    count_collections,
    get_all_collection_items,
    get_collection,
)
from pypgstac.db import PgstacDB
from stac_item_loader.handler import get_pgstac_dsn, handler


def create_sqs_record(item_data, message_id="test-message-id"):
    """Helper to create a mock SQS record with SNS message"""
    sns_message = {"Message": json.dumps(item_data)}
    return {"messageId": message_id, "body": json.dumps(sns_message)}


def create_valid_stac_item(collection_id=TEST_COLLECTION_IDS[0], item_id="test-item"):
    """Create a valid STAC item"""
    return {
        "id": item_id,
        "type": "Feature",
        "collection": collection_id,
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]],
        },
        "bbox": [0, 0, 1, 1],
        "properties": {
            "datetime": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        },
        "assets": {},
        "links": [],
        "stac_version": "1.1.0",
    }


def create_valid_stac_collection(collection_id="test-collection"):
    """Create a valid STAC collection"""
    return {
        "id": collection_id,
        "type": "Collection",
        "title": f"Test Collection {collection_id}",
        "description": f"A test collection with ID {collection_id}",
        "license": "proprietary",
        "extent": {
            "spatial": {"bbox": [[-180, -90, 180, 90]]},
            "temporal": {"interval": [[None, None]]},
        },
        "links": [{"href": "placeholder", "rel": "self"}],
        "stac_version": "1.1.0",
    }


def test_get_pgstac_dsn_missing_env_var():
    """Test get_pgstac_dsn when environment variable is missing"""
    # Save current env var if it exists
    original_value = os.environ.get("PGSTAC_SECRET_ARN")

    # Remove the env var
    if "PGSTAC_SECRET_ARN" in os.environ:
        del os.environ["PGSTAC_SECRET_ARN"]

    # Should raise an error
    with pytest.raises(EnvironmentError):
        get_pgstac_dsn()

    # Restore original value if it existed
    if original_value is not None:
        os.environ["PGSTAC_SECRET_ARN"] = original_value


def test_handler_with_valid_item(mock_aws_context, mock_pgstac_dsn, database_url):
    """Test handler with a valid STAC item"""
    # Create a valid STAC item for our test collection
    collection_id = TEST_COLLECTION_IDS[0]
    item_id = "test-item"
    valid_item = create_valid_stac_item(collection_id=collection_id, item_id=item_id)

    # Create event with one record
    event = {"Records": [create_sqs_record(valid_item, message_id="test-message-1")]}

    # Call handler
    result = handler(event, mock_aws_context)

    # Check result - should be None for successful processing
    assert result is None

    # Verify the item was added to the database
    assert check_item_exists(
        database_url, collection_id, item_id
    ), "Item was not found in the database"


def test_handler_with_valid_items_multiple_collections(
    mock_aws_context, mock_pgstac_dsn, database_url
):
    """Test handler with a valid STAC items for multiple collections"""
    # Create items with unique IDs for easier verification
    items = []
    for i, collection_id in enumerate(TEST_COLLECTION_IDS):
        item_id = f"multi-collection-test-item-{i}"
        items.append(
            (
                collection_id,
                item_id,
                create_valid_stac_item(collection_id=collection_id, item_id=item_id),
            )
        )

    # Create event with one record per collection
    event = {
        "Records": [
            create_sqs_record(
                item_data,
                message_id=f"test-message-{i}",
            )
            for i, (_, _, item_data) in enumerate(items)
        ]
    }

    # Call handler
    result = handler(event, mock_aws_context)

    # Check result - should be None for successful processing
    assert result is None

    # Verify all items were added to their respective collections
    for collection_id, item_id, _ in items:
        assert check_item_exists(
            database_url, collection_id, item_id
        ), f"Item {item_id} was not found in collection {collection_id}"


def test_handler_with_invalid_item(mock_aws_context, mock_pgstac_dsn):
    """Test handler with an invalid STAC item (missing collection)"""
    # Create an invalid STAC item (missing collection)
    invalid_item = create_valid_stac_item()
    del invalid_item["collection"]  # Make it invalid

    message_id = "test-invalid-message"
    event = {"Records": [create_sqs_record(invalid_item, message_id=message_id)]}

    # Call handler
    result = handler(event, mock_aws_context)

    # Should return a failure response
    assert result is not None
    assert "batchItemFailures" in result
    # The message ID of the failed item should be in the response
    assert any(
        failure["itemIdentifier"] == message_id for failure in result["batchItemFailures"]
    )


def test_handler_with_multiple_items(mock_aws_context, mock_pgstac_dsn, database_url):
    """Test handler with multiple valid STAC items"""
    collection_id = TEST_COLLECTION_IDS[0]

    # Create multiple valid items
    item_ids = [f"test-item-{i}" for i in range(3)]
    items = [
        create_valid_stac_item(item_id=item_id, collection_id=collection_id)
        for item_id in item_ids
    ]

    # Create event with multiple records
    event = {
        "Records": [
            create_sqs_record(item, message_id=f"test-message-{i}")
            for i, item in enumerate(items)
        ]
    }

    # Get initial count of items in the collection
    initial_count = count_collection_items(database_url, collection_id)

    # Call handler
    result = handler(event, mock_aws_context)

    # All should succeed
    assert result is None

    # Verify all items were added
    for item_id in item_ids:
        assert check_item_exists(
            database_url, collection_id, item_id
        ), f"Item {item_id} was not found in the database"

    # Verify the count increased by the expected amount
    new_count = count_collection_items(database_url, collection_id)
    assert new_count == initial_count + len(
        items
    ), f"Expected {initial_count + len(items)} items, but found {new_count}"


def test_handler_with_mixed_items(mock_aws_context, mock_pgstac_dsn, database_url):
    """Test handler with a mix of valid and invalid items"""
    collection_id = TEST_COLLECTION_IDS[0]
    valid_item_id = "valid-test-item"
    invalid_item_id = "invalid-item"

    # Create one valid and one invalid item
    valid_item = create_valid_stac_item(
        collection_id=collection_id, item_id=valid_item_id
    )

    invalid_item = create_valid_stac_item(item_id=invalid_item_id)
    del invalid_item["collection"]  # Make it invalid

    valid_message_id = "valid-message"
    invalid_message_id = "invalid-message"

    event = {
        "Records": [
            create_sqs_record(valid_item, message_id=valid_message_id),
            create_sqs_record(invalid_item, message_id=invalid_message_id),
        ]
    }

    # Get initial count
    initial_count = count_collection_items(database_url, collection_id)

    # Call handler
    result = handler(event, mock_aws_context)

    # Should have a partial failure
    assert result is not None
    assert "batchItemFailures" in result
    failures = [f["itemIdentifier"] for f in result["batchItemFailures"]]
    assert invalid_message_id in failures
    assert valid_message_id not in failures

    # Verify only the valid item was added
    assert check_item_exists(
        database_url, collection_id, valid_item_id
    ), "Valid item was not found in the database"

    # Verify count increased by exactly 1
    new_count = count_collection_items(database_url, collection_id)
    assert (
        new_count == initial_count + 1
    ), f"Expected {initial_count + 1} items, but found {new_count}"


def test_handler_with_empty_event(mock_aws_context, mock_pgstac_dsn):
    """Test handler with an empty event"""
    event = {"Records": []}

    # Call handler
    result = handler(event, mock_aws_context)

    # Should succeed with no failures
    assert result is None


def test_handler_with_malformed_sqs_message(mock_aws_context, mock_pgstac_dsn):
    """Test handler with a malformed SQS message"""
    # Create a record with invalid JSON in the body
    record = {"messageId": "malformed-message", "body": "{not valid json"}

    event = {"Records": [record]}

    # Call handler
    result = handler(event, mock_aws_context)

    # Should report the message as failed
    assert result is not None
    assert "batchItemFailures" in result
    assert any(
        f["itemIdentifier"] == "malformed-message" for f in result["batchItemFailures"]
    )


@pytest.mark.parametrize("missing_field", ["id", "type", "geometry", "properties"])
def test_handler_with_missing_required_fields(
    mock_aws_context, mock_pgstac_dsn, missing_field
):
    """Test handler with items missing required STAC fields"""
    item = create_valid_stac_item(collection_id=TEST_COLLECTION_IDS[0])

    # Remove a required field
    if missing_field == "properties.datetime":
        del item["properties"]["datetime"]
    else:
        del item[missing_field]

    message_id = f"missing-{missing_field}"
    event = {"Records": [create_sqs_record(item, message_id=message_id)]}

    # Call handler
    result = handler(event, mock_aws_context)

    # Should report the message as failed
    assert result is not None
    assert "batchItemFailures" in result
    assert any(f["itemIdentifier"] == message_id for f in result["batchItemFailures"])


def test_handler_with_nonexistent_collection(mock_aws_context, mock_pgstac_dsn):
    """Test handler with an item referencing a collection that doesn't exist"""
    # Create an item with a non-existent collection
    item = create_valid_stac_item(collection_id="nonexistent-collection")

    message_id = "nonexistent-collection-message"
    event = {"Records": [create_sqs_record(item, message_id=message_id)]}

    # Call handler
    result = handler(event, mock_aws_context)

    # This might pass or fail depending on if pypgstac enforces collection existence
    # If it fails validation:
    assert result
    assert "batchItemFailures" in result
    assert any(f["itemIdentifier"] == message_id for f in result["batchItemFailures"])


@patch("stac_item_loader.handler.PgstacDB")
def test_handler_with_database_connection_error(
    mock_pgstac_db, mock_aws_context, mock_pgstac_dsn
):
    """Test handler when database connection fails"""
    # Make the database connection raise an exception
    mock_pgstac_db.side_effect = Exception("Database connection error")

    # Create a valid item
    valid_item = create_valid_stac_item(collection_id=TEST_COLLECTION_IDS[0])

    message_id = "db-error-message"
    event = {"Records": [create_sqs_record(valid_item, message_id=message_id)]}

    # Call handler
    result = handler(event, mock_aws_context)

    # Should report the message as failed
    assert result is not None
    assert "batchItemFailures" in result
    assert any(f["itemIdentifier"] == message_id for f in result["batchItemFailures"])


@patch("pypgstac.load.Loader.load_items")
def test_handler_with_load_error(mock_load_items, mock_aws_context, mock_pgstac_dsn):
    """Test handler when item loading fails"""
    # Make the load_items method raise an exception
    mock_load_items.side_effect = Exception("Failed to load items")

    # Create a valid item
    valid_item = create_valid_stac_item(collection_id=TEST_COLLECTION_IDS[0])

    message_id = "load-error-message"
    event = {"Records": [create_sqs_record(valid_item, message_id=message_id)]}

    # Call handler
    result = handler(event, mock_aws_context)

    # Should report the message as failed
    assert result is not None
    assert "batchItemFailures" in result
    assert any(f["itemIdentifier"] == message_id for f in result["batchItemFailures"])


def test_handler_upsert_existing_item(mock_aws_context, mock_pgstac_dsn, database_url):
    """Test handler correctly updates an existing item via upsert"""
    collection_id = TEST_COLLECTION_IDS[0]
    item_id = "upsert-test-item"

    # Create initial item
    initial_item = create_valid_stac_item(collection_id=collection_id, item_id=item_id)

    # Add a specific property to identify the first version
    initial_item["properties"]["version"] = "1.0"

    # Insert the initial item
    event = {"Records": [create_sqs_record(initial_item, message_id="initial-insert")]}
    handler(event, mock_aws_context)

    # Verify the initial item was inserted
    assert check_item_exists(database_url, collection_id, item_id)

    # Get the inserted item to verify its properties
    items = get_all_collection_items(database_url, collection_id)
    initial_db_item = next((item for item in items if item["id"] == item_id), None)
    assert initial_db_item is not None
    assert initial_db_item["content"]["properties"]["version"] == "1.0"

    # Create an updated version of the same item
    updated_item = create_valid_stac_item(collection_id=collection_id, item_id=item_id)
    updated_item["properties"]["version"] = "2.0"

    # Update the item using the handler
    event = {"Records": [create_sqs_record(updated_item, message_id="update-message")]}
    result = handler(event, mock_aws_context)

    # Check result - should be None for successful processing
    assert result is None

    # Verify the item was updated
    items = get_all_collection_items(database_url, collection_id)
    updated_db_item = next((item for item in items if item["id"] == item_id), None)
    assert updated_db_item is not None
    assert (
        updated_db_item["content"]["properties"]["version"] == "2.0"
    ), "Item was not properly updated with new version"

    # Count should remain the same (1 item was updated, not added)
    count = count_collection_items(database_url, collection_id)
    assert count == len(items), "Item count changed unexpectedly after upsert"


def create_s3_event_notification(bucket_name, object_key):
    """Helper to create a mock S3 event notification"""
    return {
        "Records": [
            {
                "eventSource": "aws:s3",
                "eventName": "ObjectCreated:Put",
                "eventTime": "2023-01-01T12:00:00.000Z",
                "awsRegion": "us-east-1",
                "s3": {
                    "bucket": {"name": bucket_name},
                    "object": {"key": object_key, "size": 1024},
                },
            }
        ]
    }


def create_sqs_record_with_s3_event(
    bucket_name, object_key, message_id="test-s3-message-id"
):
    """Helper to create a mock SQS record containing an S3 event notification via SNS"""
    s3_event = create_s3_event_notification(bucket_name, object_key)
    sns_message = {"Message": json.dumps(s3_event)}
    return {"messageId": message_id, "body": json.dumps(sns_message)}


def test_handler_with_s3_event(mock_aws_context, mock_pgstac_dsn, database_url):
    """Test handler with a valid S3 event notification"""
    collection_id = TEST_COLLECTION_IDS[0]
    item_id = "s3-test-item"
    bucket_name = "test-bucket"
    object_key = "stac/items/test-item.json"

    # Create a valid STAC item that will be "returned" from S3
    valid_item = create_valid_stac_item(collection_id=collection_id, item_id=item_id)

    # Create SQS record containing S3 event notification via SNS
    s3_record = create_sqs_record_with_s3_event(
        bucket_name, object_key, message_id="s3-message-1"
    )
    event = {"Records": [s3_record]}

    # Mock S3 client to return our STAC item
    with patch("stac_item_loader.handler.boto3.session.Session") as mock_session:
        mock_s3_client = MagicMock()
        mock_session.return_value.client.return_value = mock_s3_client

        # Mock S3 get_object response
        mock_response = {"Body": MagicMock()}
        mock_response["Body"].read.return_value = json.dumps(valid_item).encode("utf-8")
        mock_s3_client.get_object.return_value = mock_response

        # Call handler
        result = handler(event, mock_aws_context)

        # Check result - should be None for successful processing
        assert result is None

        # Verify S3 get_object was called with correct parameters
        mock_s3_client.get_object.assert_called_once_with(
            Bucket=bucket_name, Key=object_key
        )

        # Verify the item was added to the database
        assert check_item_exists(
            database_url, collection_id, item_id
        ), "Item from S3 was not found in the database"


def test_handler_with_s3_event_invalid_extension(mock_aws_context, mock_pgstac_dsn):
    """Test handler with S3 event for non-JSON file"""
    bucket_name = "test-bucket"
    object_key = "data/image.tif"  # Not a JSON file

    s3_record = create_sqs_record_with_s3_event(
        bucket_name, object_key, message_id="s3-invalid-ext"
    )
    event = {"Records": [s3_record]}

    # Call handler
    result = handler(event, mock_aws_context)

    # Should report the message as failed
    assert result is not None
    assert "batchItemFailures" in result
    assert any(
        f["itemIdentifier"] == "s3-invalid-ext" for f in result["batchItemFailures"]
    )


def test_handler_with_s3_event_s3_error(mock_aws_context, mock_pgstac_dsn):
    """Test handler when S3 get_object fails"""
    bucket_name = "test-bucket"
    object_key = "stac/items/missing-item.json"

    s3_record = create_sqs_record_with_s3_event(
        bucket_name, object_key, message_id="s3-error"
    )
    event = {"Records": [s3_record]}

    # Mock S3 client to raise an exception
    with patch("stac_item_loader.handler.boto3.session.Session") as mock_session:
        mock_s3_client = MagicMock()
        mock_session.return_value.client.return_value = mock_s3_client
        mock_s3_client.get_object.side_effect = Exception("S3 object not found")

        # Call handler
        result = handler(event, mock_aws_context)

        # Should report the message as failed
        assert result is not None
        assert "batchItemFailures" in result
        assert any(f["itemIdentifier"] == "s3-error" for f in result["batchItemFailures"])


def test_handler_with_s3_event_invalid_json(mock_aws_context, mock_pgstac_dsn):
    """Test handler with S3 event that returns invalid JSON"""
    bucket_name = "test-bucket"
    object_key = "stac/items/invalid.json"

    s3_record = create_sqs_record_with_s3_event(
        bucket_name, object_key, message_id="s3-invalid-json"
    )
    event = {"Records": [s3_record]}

    # Mock S3 client to return invalid JSON
    with patch("stac_item_loader.handler.boto3.session.Session") as mock_session:
        mock_s3_client = MagicMock()
        mock_session.return_value.client.return_value = mock_s3_client

        mock_response = {"Body": MagicMock()}
        mock_response["Body"].read.return_value = b"{invalid json content"
        mock_s3_client.get_object.return_value = mock_response

        # Call handler
        result = handler(event, mock_aws_context)

        # Should report the message as failed
        assert result is not None
        assert "batchItemFailures" in result
        assert any(
            f["itemIdentifier"] == "s3-invalid-json" for f in result["batchItemFailures"]
        )


def test_handler_with_s3_event_invalid_stac_item(mock_aws_context, mock_pgstac_dsn):
    """Test handler with S3 event that returns invalid STAC item"""
    bucket_name = "test-bucket"
    object_key = "stac/items/invalid-stac.json"

    s3_record = create_sqs_record_with_s3_event(
        bucket_name, object_key, message_id="s3-invalid-stac"
    )
    event = {"Records": [s3_record]}

    # Create invalid STAC item (missing required fields)
    invalid_stac = {"id": "test", "type": "Feature"}  # Missing required fields

    # Mock S3 client to return invalid STAC item
    with patch("stac_item_loader.handler.boto3.session.Session") as mock_session:
        mock_s3_client = MagicMock()
        mock_session.return_value.client.return_value = mock_s3_client

        mock_response = {"Body": MagicMock()}
        mock_response["Body"].read.return_value = json.dumps(invalid_stac).encode("utf-8")
        mock_s3_client.get_object.return_value = mock_response

        # Call handler
        result = handler(event, mock_aws_context)

        # Should report the message as failed
        assert result is not None
        assert "batchItemFailures" in result
        assert any(
            f["itemIdentifier"] == "s3-invalid-stac" for f in result["batchItemFailures"]
        )


def test_handler_with_mixed_s3_and_sqs_events(
    mock_aws_context, mock_pgstac_dsn, database_url
):
    """Test handler with both S3 and SQS events in the same batch"""
    collection_id = TEST_COLLECTION_IDS[0]

    # Create SQS event with STAC item
    sqs_item_id = "sqs-item"
    sqs_item = create_valid_stac_item(collection_id=collection_id, item_id=sqs_item_id)
    sqs_record = create_sqs_record(sqs_item, message_id="sqs-message")

    # Create S3 event
    s3_item_id = "s3-item"
    s3_item = create_valid_stac_item(collection_id=collection_id, item_id=s3_item_id)
    bucket_name = "test-bucket"
    object_key = "stac/items/s3-item.json"
    s3_record = create_sqs_record_with_s3_event(
        bucket_name, object_key, message_id="s3-message"
    )

    event = {"Records": [sqs_record, s3_record]}

    # Mock S3 client for the S3 event
    with patch("stac_item_loader.handler.boto3.session.Session") as mock_session:
        mock_s3_client = MagicMock()
        mock_session.return_value.client.return_value = mock_s3_client

        mock_response = {"Body": MagicMock()}
        mock_response["Body"].read.return_value = json.dumps(s3_item).encode("utf-8")
        mock_s3_client.get_object.return_value = mock_response

        # Call handler
        result = handler(event, mock_aws_context)

        # Both should succeed
        assert result is None

        # Verify both items were added to the database
        assert check_item_exists(
            database_url, collection_id, sqs_item_id
        ), "SQS item was not found in the database"
        assert check_item_exists(
            database_url, collection_id, s3_item_id
        ), "S3 item was not found in the database"


def test_handler_with_s3_event_binary_content(mock_aws_context, mock_pgstac_dsn):
    """Test handler with S3 event that returns binary content"""
    bucket_name = "test-bucket"
    object_key = "stac/items/binary.json"

    s3_record = create_sqs_record_with_s3_event(
        bucket_name, object_key, message_id="s3-binary"
    )
    event = {"Records": [s3_record]}

    # Mock S3 client to return binary content that can't be decoded as UTF-8
    with patch("stac_item_loader.handler.boto3.session.Session") as mock_session:
        mock_s3_client = MagicMock()
        mock_session.return_value.client.return_value = mock_s3_client

        mock_response = {"Body": MagicMock()}
        # Return binary content that cannot be decoded as UTF-8
        mock_response["Body"].read.return_value = b"\xff\xfe\x00\x00"
        mock_s3_client.get_object.return_value = mock_response

        # Call handler
        result = handler(event, mock_aws_context)

        # Should report the message as failed
        assert result is not None
        assert "batchItemFailures" in result
        assert any(
            f["itemIdentifier"] == "s3-binary" for f in result["batchItemFailures"]
        )


def test_handler_with_valid_collection(mock_aws_context, mock_pgstac_dsn, database_url):
    """Test handler with a valid STAC collection"""
    collection_id = "test-new-collection"
    valid_collection = create_valid_stac_collection(collection_id=collection_id)

    # Create event with one collection record
    event = {
        "Records": [
            create_sqs_record(valid_collection, message_id="test-collection-message-1")
        ]
    }

    # Call handler
    result = handler(event, mock_aws_context)

    # Check result - should be None for successful processing
    assert result is None

    # Verify the collection was added to the database
    assert check_collection_exists(
        database_url, collection_id
    ), "Collection was not found in the database"


def test_handler_with_multiple_collections(
    mock_aws_context, mock_pgstac_dsn, database_url
):
    """Test handler with multiple valid STAC collections"""
    collection_ids = [f"test-multi-collection-{i}" for i in range(3)]
    collections = [
        create_valid_stac_collection(collection_id=collection_id)
        for collection_id in collection_ids
    ]

    # Create event with multiple collection records
    event = {
        "Records": [
            create_sqs_record(collection, message_id=f"test-collection-message-{i}")
            for i, collection in enumerate(collections)
        ]
    }

    # Get initial count of collections
    initial_count = count_collections(database_url)

    # Call handler
    result = handler(event, mock_aws_context)

    # All should succeed
    assert result is None

    # Verify all collections were added
    for collection_id in collection_ids:
        assert check_collection_exists(
            database_url, collection_id
        ), f"Collection {collection_id} was not found in the database"

    # Verify the count increased by the expected amount
    new_count = count_collections(database_url)
    assert new_count == initial_count + len(
        collections
    ), f"Expected {initial_count + len(collections)} collections, but found {new_count}"


def test_handler_with_invalid_collection(mock_aws_context, mock_pgstac_dsn):
    """Test handler with an invalid STAC collection (missing required fields)"""
    # Create an invalid STAC collection (missing extent)
    invalid_collection = create_valid_stac_collection()
    del invalid_collection["extent"]  # Make it invalid

    message_id = "test-invalid-collection-message"
    event = {"Records": [create_sqs_record(invalid_collection, message_id=message_id)]}

    # Call handler
    result = handler(event, mock_aws_context)

    # Should return a failure response
    assert result is not None
    assert "batchItemFailures" in result
    # The message ID of the failed collection should be in the response
    assert any(
        failure["itemIdentifier"] == message_id for failure in result["batchItemFailures"]
    )


def test_handler_with_mixed_collections_and_items(
    mock_aws_context, mock_pgstac_dsn, database_url
):
    """Test handler with a mix of collections and items"""
    # Create a new collection
    collection_id = "test-mixed-collection"
    collection = create_valid_stac_collection(collection_id=collection_id)

    # Create an item for the existing test collection
    existing_collection_id = TEST_COLLECTION_IDS[0]
    item_id = "test-mixed-item"
    item = create_valid_stac_item(collection_id=existing_collection_id, item_id=item_id)

    collection_message_id = "mixed-collection-message"
    item_message_id = "mixed-item-message"

    event = {
        "Records": [
            create_sqs_record(collection, message_id=collection_message_id),
            create_sqs_record(item, message_id=item_message_id),
        ]
    }

    # Get initial counts
    initial_collection_count = count_collections(database_url)
    initial_item_count = count_collection_items(database_url, existing_collection_id)

    # Call handler
    result = handler(event, mock_aws_context)

    # Both should succeed
    assert result is None

    # Verify the collection was added
    assert check_collection_exists(
        database_url, collection_id
    ), "Collection was not found in the database"

    # Verify the item was added
    assert check_item_exists(
        database_url, existing_collection_id, item_id
    ), "Item was not found in the database"

    # Verify counts increased correctly
    new_collection_count = count_collections(database_url)
    new_item_count = count_collection_items(database_url, existing_collection_id)

    assert new_collection_count == initial_collection_count + 1
    assert new_item_count == initial_item_count + 1


def test_handler_with_collection_from_s3(mock_aws_context, mock_pgstac_dsn, database_url):
    """Test handler with a valid STAC collection from S3"""
    collection_id = "test-s3-collection"
    bucket_name = "test-bucket"
    object_key = "stac/collections/test-collection.json"

    # Create a valid STAC collection that will be "returned" from S3
    valid_collection = create_valid_stac_collection(collection_id=collection_id)

    # Create SQS record containing S3 event notification via SNS
    s3_record = create_sqs_record_with_s3_event(
        bucket_name, object_key, message_id="s3-collection-message-1"
    )
    event = {"Records": [s3_record]}

    # Mock S3 client to return our STAC collection
    with patch("stac_item_loader.handler.boto3.session.Session") as mock_session:
        mock_s3_client = MagicMock()
        mock_session.return_value.client.return_value = mock_s3_client

        # Mock S3 get_object response
        mock_response = {"Body": MagicMock()}
        mock_response["Body"].read.return_value = json.dumps(valid_collection).encode(
            "utf-8"
        )
        mock_s3_client.get_object.return_value = mock_response

        # Call handler
        result = handler(event, mock_aws_context)

        # Check result - should be None for successful processing
        assert result is None

        # Verify S3 get_object was called with correct parameters
        mock_s3_client.get_object.assert_called_once_with(
            Bucket=bucket_name, Key=object_key
        )

        # Verify the collection was added to the database
        assert check_collection_exists(
            database_url, collection_id
        ), "Collection from S3 was not found in the database"


def test_handler_upsert_existing_collection(
    mock_aws_context, mock_pgstac_dsn, database_url
):
    """Test handler correctly updates an existing collection via upsert"""
    collection_id = "upsert-test-collection"

    # Create initial collection
    initial_collection = create_valid_stac_collection(collection_id=collection_id)
    initial_collection["title"] = "Initial Title"

    # Insert the initial collection
    event = {
        "Records": [
            create_sqs_record(initial_collection, message_id="initial-collection-insert")
        ]
    }
    handler(event, mock_aws_context)

    # Verify the initial collection was inserted
    assert check_collection_exists(database_url, collection_id)

    # Get the inserted collection to verify its properties
    initial_db_collection = get_collection(database_url, collection_id)
    assert initial_db_collection is not None
    assert initial_db_collection["content"]["title"] == "Initial Title"

    # Create an updated version of the same collection
    updated_collection = create_valid_stac_collection(collection_id=collection_id)
    updated_collection["title"] = "Updated Title"

    # Update the collection using the handler
    event = {
        "Records": [
            create_sqs_record(updated_collection, message_id="update-collection-message")
        ]
    }
    result = handler(event, mock_aws_context)

    # Check result - should be None for successful processing
    assert result is None

    # Verify the collection was updated
    updated_db_collection = get_collection(database_url, collection_id)
    assert updated_db_collection is not None
    assert (
        updated_db_collection["content"]["title"] == "Updated Title"
    ), "Collection was not properly updated with new title"

    # Count should remain the same (1 collection was updated, not added)
    # We can't easily check this without knowing the exact initial count


@patch("pypgstac.load.Loader.load_collections")
def test_handler_with_collection_load_error(
    mock_load_collections, mock_aws_context, mock_pgstac_dsn
):
    """Test handler when collection loading fails"""
    # Make the load_collections method raise an exception
    mock_load_collections.side_effect = Exception("Failed to load collections")

    # Create a valid collection
    valid_collection = create_valid_stac_collection(collection_id="error-test-collection")

    message_id = "collection-load-error-message"
    event = {"Records": [create_sqs_record(valid_collection, message_id=message_id)]}

    # Call handler
    result = handler(event, mock_aws_context)

    # Should report the message as failed
    assert result is not None
    assert "batchItemFailures" in result
    assert any(f["itemIdentifier"] == message_id for f in result["batchItemFailures"])


def test_handler_with_unknown_type(mock_aws_context, mock_pgstac_dsn):
    """Test handler with unknown STAC type (neither Feature nor Collection)"""
    # Create an object with unknown type
    unknown_object = {
        "id": "test-unknown",
        "type": "Catalog",  # Neither Feature nor Collection
        "description": "A test catalog",
        "stac_version": "1.1.0",
    }

    message_id = "unknown-type-message"
    event = {"Records": [create_sqs_record(unknown_object, message_id=message_id)]}

    # Call handler
    result = handler(event, mock_aws_context)

    # Should return a failure response
    assert result is not None
    assert "batchItemFailures" in result
    # The message ID of the failed object should be in the response
    assert any(
        failure["itemIdentifier"] == message_id for failure in result["batchItemFailures"]
    )


@pytest.mark.parametrize("missing_field", ["id", "type", "extent", "license"])
def test_handler_with_collection_missing_required_fields(
    mock_aws_context, mock_pgstac_dsn, missing_field
):
    """Test handler with collections missing required STAC fields"""
    collection = create_valid_stac_collection(collection_id="missing-field-collection")

    # Remove a required field
    del collection[missing_field]

    message_id = f"collection-missing-{missing_field}"
    event = {"Records": [create_sqs_record(collection, message_id=message_id)]}

    # Call handler
    result = handler(event, mock_aws_context)

    # Should report the message as failed
    assert result is not None
    assert "batchItemFailures" in result
    assert any(f["itemIdentifier"] == message_id for f in result["batchItemFailures"])


def test_handler_with_mixed_valid_invalid_collections(
    mock_aws_context, mock_pgstac_dsn, database_url
):
    """Test handler with a mix of valid and invalid collections"""
    valid_collection_id = "valid-collection"
    valid_collection = create_valid_stac_collection(collection_id=valid_collection_id)

    invalid_collection = create_valid_stac_collection(collection_id="invalid-collection")
    del invalid_collection["extent"]  # Make it invalid

    valid_message_id = "valid-collection-message"
    invalid_message_id = "invalid-collection-message"

    event = {
        "Records": [
            create_sqs_record(valid_collection, message_id=valid_message_id),
            create_sqs_record(invalid_collection, message_id=invalid_message_id),
        ]
    }

    # Get initial count
    initial_count = count_collections(database_url)

    # Call handler
    result = handler(event, mock_aws_context)

    # Should have a partial failure
    assert result is not None
    assert "batchItemFailures" in result
    failures = [f["itemIdentifier"] for f in result["batchItemFailures"]]
    assert invalid_message_id in failures
    assert valid_message_id not in failures

    # Verify only the valid collection was added
    assert check_collection_exists(
        database_url, valid_collection_id
    ), "Valid collection was not found in the database"

    # Verify count increased by exactly 1
    new_count = count_collections(database_url)
    assert (
        new_count == initial_count + 1
    ), f"Expected {initial_count + 1} collections, but found {new_count}"


def test_handler_with_malformed_sns_message(mock_aws_context, mock_pgstac_dsn):
    """Test handler with a malformed SNS message"""
    # Create a record with invalid SNS structure
    record = {
        "messageId": "malformed-sns-message",
        "body": json.dumps({"InvalidField": "missing Message field"}),
    }

    event = {"Records": [record]}

    # Call handler
    result = handler(event, mock_aws_context)

    # Should report the message as failed
    assert result is not None
    assert "batchItemFailures" in result
    assert any(
        f["itemIdentifier"] == "malformed-sns-message"
        for f in result["batchItemFailures"]
    )


def test_handler_with_empty_sns_message(mock_aws_context, mock_pgstac_dsn):
    """Test handler with an empty SNS message"""
    # Create a record with empty SNS message
    record = {"messageId": "empty-sns-message", "body": json.dumps({"Message": ""})}

    event = {"Records": [record]}

    # Call handler
    result = handler(event, mock_aws_context)

    # Should report the message as failed
    assert result is not None
    assert "batchItemFailures" in result
    assert any(
        f["itemIdentifier"] == "empty-sns-message" for f in result["batchItemFailures"]
    )


def test_handler_with_sqs_record_missing_message_id(mock_aws_context, mock_pgstac_dsn):
    """Test handler with SQS record missing messageId"""
    # Create a record without messageId
    record = {"body": json.dumps({"Message": json.dumps(create_valid_stac_item())})}

    event = {"Records": [record]}

    # Call handler - should complete without crashing
    result = handler(event, mock_aws_context)

    # Should succeed since the record without messageId is skipped
    assert result is None


def test_is_s3_event_function():
    """Test the is_s3_event helper function"""
    from stac_item_loader.handler import is_s3_event

    # Test with S3 event
    s3_event = json.dumps(create_s3_event_notification("bucket", "key"))
    assert is_s3_event(s3_event) is True

    # Test with STAC item
    stac_item = json.dumps(create_valid_stac_item())
    assert is_s3_event(stac_item) is False

    # Test with arbitrary JSON
    other_json = json.dumps({"some": "data"})
    assert is_s3_event(other_json) is False


def test_process_s3_event_function(mock_aws_context):
    """Test the process_s3_event helper function"""
    from stac_item_loader.handler import process_s3_event

    bucket_name = "test-bucket"
    object_key = "stac/items/test.json"
    valid_item = create_valid_stac_item()

    # Create S3 event message
    s3_event = create_s3_event_notification(bucket_name, object_key)
    message_str = json.dumps(s3_event)

    # Mock S3 client to return our STAC item
    with patch("stac_item_loader.handler.boto3.session.Session") as mock_session:
        mock_s3_client = MagicMock()
        mock_session.return_value.client.return_value = mock_s3_client

        mock_response = {"Body": MagicMock()}
        mock_response["Body"].read.return_value = json.dumps(valid_item).encode("utf-8")
        mock_s3_client.get_object.return_value = mock_response

        # Call function
        result = process_s3_event(message_str)

        # Verify result
        assert result == valid_item

        # Verify S3 was called correctly
        mock_s3_client.get_object.assert_called_once_with(
            Bucket=bucket_name, Key=object_key
        )


def test_process_s3_event_with_no_records():
    """Test process_s3_event with message containing no records"""
    from stac_item_loader.handler import process_s3_event

    # Create message with empty Records
    message_str = json.dumps({"Records": []})

    # Should raise ValueError
    with pytest.raises(ValueError, match="no S3 event records"):
        process_s3_event(message_str)


def test_process_s3_event_with_multiple_records():
    """Test process_s3_event with message containing multiple records"""
    from stac_item_loader.handler import process_s3_event

    # Create message with multiple records
    s3_event = {
        "Records": [
            create_s3_event_notification("bucket1", "key1")["Records"][0],
            create_s3_event_notification("bucket2", "key2")["Records"][0],
        ]
    }
    message_str = json.dumps(s3_event)

    # Should raise ValueError
    with pytest.raises(ValueError, match="more than one S3 event record"):
        process_s3_event(message_str)


@patch.dict(os.environ, {"CREATE_COLLECTIONS_IF_MISSING": "true"})
def test_handler_creates_missing_collection(
    mock_aws_context, mock_pgstac_dsn, database_url
):
    """Test that collections are created when CREATE_COLLECTIONS_IF_MISSING is set and collection doesn't exist"""
    missing_collection_id = "missing-test-collection"
    item_id = "test-item-missing-collection"

    with PgstacDB(dsn=database_url) as db:
        result = db.query_one(
            f"SELECT count(*) as count from collections where id = '{missing_collection_id}'"
        )
        assert result == 0, "Collection should not exist initially"

    valid_item = create_valid_stac_item(
        collection_id=missing_collection_id, item_id=item_id
    )

    event = {"Records": [create_sqs_record(valid_item, message_id="test-message-1")]}
    result = handler(event, mock_aws_context)

    assert result is None

    with PgstacDB(dsn=database_url) as db:
        result = db.query_one(
            f"SELECT count(*) as count from collections where id = '{missing_collection_id}'"
        )
        assert result == 1, "Collection should have been created"

    assert check_item_exists(
        database_url, missing_collection_id, item_id
    ), "Item was not found in the database"


def test_handler_does_not_create_collection_without_env_var(
    mock_aws_context, mock_pgstac_dsn, database_url
):
    """Test that collections are NOT created when CREATE_COLLECTIONS_IF_MISSING env var is not set"""
    if "CREATE_COLLECTIONS_IF_MISSING" in os.environ:
        del os.environ["CREATE_COLLECTIONS_IF_MISSING"]

    missing_collection_id = "missing-test-collection-2"
    item_id = "test-item-missing-collection-2"

    with PgstacDB(dsn=database_url) as db:
        result = db.query_one(
            f"SELECT count(*) as count from collections where id = '{missing_collection_id}'"
        )
        assert result == 0, "Collection should not exist initially"

    valid_item = create_valid_stac_item(
        collection_id=missing_collection_id, item_id=item_id
    )

    event = {"Records": [create_sqs_record(valid_item, message_id="test-message-1")]}
    result = handler(event, mock_aws_context)

    assert result is not None
    assert "batchItemFailures" in result
    assert any(
        failure["itemIdentifier"] == "test-message-1"
        for failure in result["batchItemFailures"]
    )

    with PgstacDB(dsn=database_url) as db:
        result = db.query_one(
            f"SELECT count(*) as count from collections where id = '{missing_collection_id}'"
        )
        assert result == 0, "Collection should not have been created"

    assert not check_item_exists(
        database_url, missing_collection_id, item_id
    ), "Item should not have been added to the database"


@patch.dict(os.environ, {"CREATE_COLLECTIONS_IF_MISSING": "true"})
def test_handler_does_not_recreate_existing_collection(
    mock_aws_context, mock_pgstac_dsn, database_url
):
    """Test that existing collections are not recreated when they already exist"""
    existing_collection_id = TEST_COLLECTION_IDS[0]
    item_id = "test-item-existing-collection"

    with PgstacDB(dsn=database_url) as db:
        original_collection = db.query_one(
            f"SELECT * from collections where id = '{existing_collection_id}'"
        )
        assert original_collection is not None, "Test collection should exist"

    valid_item = create_valid_stac_item(
        collection_id=existing_collection_id, item_id=item_id
    )

    event = {"Records": [create_sqs_record(valid_item, message_id="test-message-1")]}
    result = handler(event, mock_aws_context)

    assert result is None

    with PgstacDB(dsn=database_url) as db:
        current_collection = db.query_one(
            f"SELECT * from collections where id = '{existing_collection_id}'"
        )
        assert (
            current_collection == original_collection
        ), "Existing collection should not have been modified"

    assert check_item_exists(
        database_url, existing_collection_id, item_id
    ), "Item was not found in the database"


@patch.dict(os.environ, {"CREATE_COLLECTIONS_IF_MISSING": "true"})
def test_handler_creates_collection_with_multiple_items(
    mock_aws_context, mock_pgstac_dsn, database_url
):
    """Test that collection creation works with multiple items from the same missing collection"""
    missing_collection_id = "missing-test-collection-multi"
    item_ids = ["test-item-1", "test-item-2", "test-item-3"]

    with PgstacDB(dsn=database_url) as db:
        result = db.query_one(
            f"SELECT count(*) as count from collections where id = '{missing_collection_id}'"
        )
        assert result == 0, "Collection should not exist initially"

    items = [
        create_valid_stac_item(collection_id=missing_collection_id, item_id=item_id)
        for item_id in item_ids
    ]

    event = {
        "Records": [
            create_sqs_record(item, message_id=f"test-message-{i}")
            for i, item in enumerate(items)
        ]
    }

    result = handler(event, mock_aws_context)

    assert result is None

    with PgstacDB(dsn=database_url) as db:
        result = db.query_one(
            f"SELECT count(*) as count from collections where id = '{missing_collection_id}'"
        )
        assert result == 1, "Collection should have been created exactly once"

    for item_id in item_ids:
        assert check_item_exists(
            database_url, missing_collection_id, item_id
        ), f"Item {item_id} was not found in the database"


@patch.dict(os.environ, {"CREATE_COLLECTIONS_IF_MISSING": "true"})
@patch("pypgstac.load.Loader.load_collections")
def test_handler_collection_creation_failure(
    mock_load_collections, mock_aws_context, mock_pgstac_dsn, database_url
):
    """Test collection creation failure handling"""
    mock_load_collections.side_effect = Exception("Failed to create collection")

    missing_collection_id = "missing-test-collection-fail"
    item_id = "test-item-collection-fail"

    with PgstacDB(dsn=database_url) as db:
        result = db.query_one(
            f"SELECT count(*) as count from collections where id = '{missing_collection_id}'"
        )
        assert result == 0, "Collection should not exist initially"

    valid_item = create_valid_stac_item(
        collection_id=missing_collection_id, item_id=item_id
    )

    event = {"Records": [create_sqs_record(valid_item, message_id="test-message-1")]}
    result = handler(event, mock_aws_context)

    assert result is not None
    assert "batchItemFailures" in result
    assert any(
        failure["itemIdentifier"] == "test-message-1"
        for failure in result["batchItemFailures"]
    )

    with PgstacDB(dsn=database_url) as db:
        result = db.query_one(
            f"SELECT count(*) as count from collections where id = '{missing_collection_id}'"
        )
        assert result == 0, "Collection should not have been created due to failure"

    assert not check_item_exists(
        database_url, missing_collection_id, item_id
    ), "Item should not have been added to the database"
