import os
from unittest.mock import Mock, patch

import pytest
import src.collection as collection
from fastapi import HTTPException
from pypgstac.load import Methods
from src.utils import DbCreds


@pytest.fixture()
def loader():
    with patch("src.collection.Loader", autospec=True) as m:
        yield m


@pytest.fixture()
def pgstacdb():
    with patch("src.collection.PgstacDB", autospec=True) as m:
        m.return_value.__enter__.return_value = Mock()
        yield m


def test_load_collections(stac_collection, loader, pgstacdb):
    with patch(
        "src.collection.get_db_credentials",
        return_value=DbCreds(
            username="", password="", host="", port=1, dbname="", engine=""
        ),
    ):
        os.environ["DB_SECRET_ARN"] = ""
        collection.ingest(stac_collection)

    loader.return_value.load_collections.assert_called_once_with(
        file=[stac_collection.model_dump(mode="json")],
        insert_mode=Methods.upsert,
    )


def test_ingest_loader_error(stac_collection, pgstacdb):
    """Test handling of errors during the loading process."""
    with patch(
        "src.collection.get_db_credentials",
        return_value=DbCreds(
            username="", password="", host="", port=1, dbname="", engine=""
        ),
    ):
        os.environ["DB_SECRET_ARN"] = ""

        with patch("src.collection.Loader") as mock_loader:
            mock_loader_instance = Mock()
            mock_loader.return_value = mock_loader_instance
            mock_loader_instance.load_collections.side_effect = Exception(
                "Invalid collection data"
            )

            with pytest.raises(HTTPException) as excinfo:
                collection.ingest(stac_collection)

            assert excinfo.value.status_code == 500
            assert "Invalid collection data" in str(excinfo.value.detail)


def test_ingest_missing_environment_variable(stac_collection):
    """Test handling when the required environment variable is missing."""
    if "DB_SECRET_ARN" in os.environ:
        del os.environ["DB_SECRET_ARN"]

    with pytest.raises(HTTPException) as excinfo:
        collection.ingest(stac_collection)

    assert "DB_SECRET_ARN" in str(excinfo.value)


def test_ingest_credentials_error(stac_collection):
    """Test handling of errors during credential retrieval."""
    with patch(
        "src.collection.get_db_credentials",
        side_effect=Exception("Failed to retrieve credentials"),
    ):
        os.environ["DB_SECRET_ARN"] = ""

        with pytest.raises(HTTPException) as excinfo:
            collection.ingest(stac_collection)

        assert excinfo.value.status_code == 500
        assert "Failed to retrieve credentials" in str(excinfo.value.detail)
