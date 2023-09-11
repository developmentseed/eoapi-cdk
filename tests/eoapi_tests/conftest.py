import pytest
from ingestion import StacIngestion


@pytest.fixture(scope="module")
def stac_ingestion_instance():
    return StacIngestion()


@pytest.fixture(scope="module")
def test_collection(stac_ingestion_instance):
    return stac_ingestion_instance.get_test_collection()


@pytest.fixture(scope="module")
def test_item(stac_ingestion_instance):
    return stac_ingestion_instance.get_test_item()


@pytest.fixture(scope="module")
def test_titiler_search_request(stac_ingestion_instance):
    return stac_ingestion_instance.get_test_titiler_search_request()
