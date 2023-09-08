import base64
import json
from datetime import timedelta
from typing import TYPE_CHECKING, List
from unittest.mock import call, patch

import pytest
from fastapi.encoders import jsonable_encoder

if TYPE_CHECKING:
    from fastapi.testclient import TestClient
    from src import schemas, services

ingestion_endpoint = "/ingestions"


@pytest.fixture()
def collection_exists():
    with patch("src.validators.collection_exists", return_value=True) as m:
        yield m


@pytest.fixture()
def collection_missing():
    def bad_collection(collection_id: str):
        raise ValueError("MOCKED MISSING COLLECTION ERROR")

    with patch("src.validators.collection_exists", side_effect=bad_collection) as m:
        yield m


@pytest.fixture()
def asset_exists():
    with patch("src.validators.url_is_accessible", return_value=True) as m:
        yield m


@pytest.fixture()
def asset_missing():
    def bad_asset_url(href: str):
        raise ValueError("MOCKED INACCESSIBLE URL ERROR")

    with patch("src.validators.url_is_accessible", side_effect=bad_asset_url) as m:
        yield m


class TestCreate:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        api_client: "TestClient",
        mock_table: "services.Table",
        example_ingestion: "schemas.Ingestion",
    ):
        from src import services

        self.api_client = api_client
        self.mock_table = mock_table
        self.db = services.Database(self.mock_table)
        self.example_ingestion = example_ingestion

    def test_unauthenticated_create(self):
        response = self.api_client.post(
            ingestion_endpoint,
            json=jsonable_encoder(self.example_ingestion.item),
        )

        assert response.status_code == 403

    def test_create(self, client_authenticated, collection_exists, asset_exists):
        response = self.api_client.post(
            ingestion_endpoint,
            json=jsonable_encoder(self.example_ingestion.item),
        )

        assert response.status_code == 201
        assert collection_exists.called_once_with(
            self.example_ingestion.item.collection
        )

        stored_data = self.db.fetch_many(status="queued")["items"]
        assert len(stored_data) == 1
        assert json.loads(stored_data[0].json(by_alias=True)) == response.json()

    def test_validates_missing_collection(
        self, client_authenticated, collection_missing, asset_exists
    ):
        response = self.api_client.post(
            ingestion_endpoint,
            json=jsonable_encoder(self.example_ingestion.item),
        )

        collection_missing.assert_called_once_with(
            collection_id=self.example_ingestion.item.collection
        )
        assert response.status_code == 422, "should get validation error"
        assert (
            len(self.db.fetch_many(status="queued")["items"]) == 0
        ), "data should not be stored in DB"

    def test_validates_missing_assets(
        self, client_authenticated, collection_exists, asset_missing
    ):
        response = self.api_client.post(
            ingestion_endpoint,
            json=jsonable_encoder(self.example_ingestion.item),
        )

        collection_exists.assert_called_once_with(
            collection_id=self.example_ingestion.item.collection
        )
        asset_missing.assert_has_calls(
            [
                call(href=asset.href)
                for asset in self.example_ingestion.item.assets.values()
            ],
            any_order=True,
        )
        assert response.status_code == 422, "should get validation error"
        for asset_type in self.example_ingestion.item.assets.keys():
            assert any(
                [
                    err["loc"] == ["body", "assets", asset_type, "href"]
                    for err in response.json()["detail"]
                ]
            ), "should reference asset type in validation error response"
        assert (
            len(self.db.fetch_many(status="queued")["items"]) == 0
        ), "data should not be stored in DB"


class TestList:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        api_client: "TestClient",
        mock_table: "services.Table",
        example_ingestion: "schemas.Ingestion",
    ):
        self.api_client = api_client
        self.mock_table = mock_table
        self.example_ingestion = example_ingestion

    def populate_table(self, count=100) -> List["schemas.Ingestion"]:
        example_ingestions = []
        for i in range(count):
            ingestion = self.example_ingestion.copy()
            ingestion.id = str(i)
            ingestion.created_at = ingestion.created_at + timedelta(hours=i)
            self.mock_table.put_item(Item=ingestion.dynamodb_dict())
            example_ingestions.append(ingestion)
        return example_ingestions

    def test_simple_lookup(self):
        self.mock_table.put_item(Item=self.example_ingestion.dynamodb_dict())
        ingestion = jsonable_encoder(self.example_ingestion)
        response = self.api_client.get(ingestion_endpoint)
        assert response.status_code == 200
        assert response.json() == {
            "items": [ingestion],
            "next": None,
        }

    def test_next_response(self):
        example_ingestions = self.populate_table(100)

        limit = 25
        expected_next = json.loads(
            example_ingestions[limit - 1].json(
                include={"created_by", "id", "status", "created_at"}
            )
        )

        response = self.api_client.get(ingestion_endpoint, params={"limit": limit})
        assert response.status_code == 200
        assert json.loads(base64.b64decode(response.json()["next"])) == expected_next
        assert response.json()["items"] == jsonable_encoder(example_ingestions[:limit])

    @pytest.mark.skip(reason="Test is currently broken")
    def test_get_next_page(self):
        example_ingestions = self.populate_table(100)

        limit = 25
        next_param = base64.b64encode(
            example_ingestions[limit - 1]
            .json(include={"created_by", "id", "status", "created_at"})
            .encode()
        )

        response = self.api_client.get(
            ingestion_endpoint, params={"limit": limit, "next": next_param}
        )
        assert response.status_code == 200
        assert response.json()["items"] == [
            json.loads(ingestion.json(by_alias=True))
            for ingestion in example_ingestions[limit : limit * 2]
        ]
