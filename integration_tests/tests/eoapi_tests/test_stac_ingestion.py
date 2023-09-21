import time

import pystac
import pytest

INSERTION_WAIT_TIME = 10

# Test validating the collection
pytest.mark.order(0)


def test_validate_collection(test_collection):
    pystac.validation.validate_dict(test_collection)


# Test validating the item
pytest.mark.order(1)


def test_validate_item(test_item):
    pystac.validation.validate_dict(test_item)


# Test inserting collection
pytest.mark.order(2)


def test_insert_collection(stac_ingestion_instance, test_collection):
    response = stac_ingestion_instance.insert_collection(test_collection)
    assert response.status_code in [
        200,
        201,
    ], f"Failed to insert the test_collection :\n{response.text}"
    # Wait for the collection to be inserted
    time.sleep(INSERTION_WAIT_TIME)


# Test inserting item
pytest.mark.order(3)


def test_insert_item(stac_ingestion_instance, test_item):
    response = stac_ingestion_instance.insert_item(test_item)
    assert response.status_code in [
        200,
        201,
    ], f"Failed to insert the test_item :\n{response.text}"
    # Wait for the item to be inserted
    time.sleep(INSERTION_WAIT_TIME)


# Test querying collection and verifying inserted collection
pytest.mark.order(4)


def test_query_collection(stac_ingestion_instance, test_collection):
    response = stac_ingestion_instance.query_collection(test_collection["id"])
    assert response.status_code in [
        200,
        201,
    ], f"Failed to query the test_collection :\n{response.text}"


# Test registering a mosaic and querying its assets
pytest.mark.order(5)


def test_titiler_pgstac(
    stac_ingestion_instance, test_titiler_search_request, test_item
):
    register_response = stac_ingestion_instance.register_mosaic(
        test_titiler_search_request
    )
    assert register_response.status_code in [
        200,
        201,
    ], f"Failed to register the mosaic :\n{register_response.text}"
    search_id = register_response.json()["searchid"]
    # allow for some time for the mosaic to be inserted
    time.sleep(INSERTION_WAIT_TIME)
    asset_query_response = stac_ingestion_instance.list_mosaic_assets(search_id)
    assert asset_query_response.status_code in [
        200,
        201,
    ], "Failed to query the mosaic's assets"
    "for mosaic {search_id} :\n{asset_query_response.text}"
    assets_json = asset_query_response.json()
    # expects a single item in the collection
    assert len(assets_json) == 1
    assert all([k in assets_json[0]["assets"] for k in test_item["assets"].keys()])


# Test querying items and verifying inserted items
pytest.mark.order(6)


def test_query_items(stac_ingestion_instance, test_collection, test_item):
    response = stac_ingestion_instance.query_items(test_collection["id"])
    assert response.status_code in [
        200,
        201,
    ], f"Failed to query the items :\n{response.text}"
    item = response.json()["features"][0]
    assert (
        item["id"] == test_item["id"]
    ), f"Inserted item - {test_item} \n not found in the queried items {item}"


# Test querying collection and verifying inserted collection
pytest.mark.order(7)


def test_delete_collection(stac_ingestion_instance, test_collection):
    response = stac_ingestion_instance.delete_collection(test_collection["id"])
    assert response.status_code in [
        200,
        201,
    ], f"Failed to delete the test_collection :\n{response.text}"


# Run the tests
if __name__ == "__main__":
    pytest.main()
