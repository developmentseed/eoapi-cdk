import json
import os
from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from conftest import (
    TEST_COLLECTION_IDS,
    check_item_exists,
    count_collection_items,
    get_all_collection_items,
)
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
