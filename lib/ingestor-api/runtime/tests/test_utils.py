from unittest.mock import Mock, patch

import pytest
from pypgstac.load import Methods
from src.utils import DbCreds


@pytest.fixture()
def loader():
    with patch("src.utils.Loader", autospec=True) as m:
        yield m


@pytest.fixture()
def pgstacdb():
    with patch("src.utils.PgstacDB", autospec=True) as m:
        m.return_value.__enter__.return_value = Mock()
        yield m


@pytest.fixture()
def dbcreds():
    dbcreds = DbCreds(username="", password="", host="", port=1, dbname="", engine="")
    return dbcreds


def test_load_items(loader, pgstacdb, example_ingestion, dbcreds):
    import src.utils as utils

    ingestions = [example_ingestion]
    utils.load_items(dbcreds, ingestions)
    loader.return_value.load_items.assert_called_once_with(
        file=[i.item.model_dump(mode="json") for i in ingestions],
        insert_mode=Methods.upsert,
    )
