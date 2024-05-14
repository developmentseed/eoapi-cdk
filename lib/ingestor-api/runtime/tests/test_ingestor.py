from unittest.mock import patch

import pytest


@pytest.fixture()
def dynamodb_stream_event():
    return {"Records": None}


@pytest.fixture()
def get_queued_ingestions(example_ingestion):
    with patch(
        "src.ingestor.get_queued_ingestions",
        return_value=iter([example_ingestion]),
        autospec=True,
    ) as m:
        yield m


@pytest.fixture()
def get_db_credentials():
    with patch("src.ingestor.get_db_credentials", return_value="", autospec=True) as m:
        yield m


@pytest.fixture()
def load_items():
    with patch("src.ingestor.load_items", return_value=0, autospec=True) as m:
        yield m


@pytest.fixture()
def get_table(mock_table):
    with patch("src.ingestor.get_table", return_value=mock_table, autospec=True) as m:
        yield m


def test_handler(
    monkeypatch,
    test_environ,
    dynamodb_stream_event,
    example_ingestion,
    get_queued_ingestions,
    get_db_credentials,
    load_items,
    get_table,
    mock_table,
):
    import src.ingestor as ingestor

    ingestor.handler(dynamodb_stream_event, {})
    load_items.assert_called_once_with(
        creds="",
        ingestions=[example_ingestion],
    )
    response = mock_table.get_item(
        Key={"created_by": example_ingestion.created_by, "id": example_ingestion.id}
    )
    assert response["Item"]["status"] == "succeeded"
