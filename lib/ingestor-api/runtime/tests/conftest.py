import os

import boto3
import pytest
from fastapi.testclient import TestClient
from moto import mock_dynamodb, mock_ssm
from stac_pydantic import Item


@pytest.fixture
def test_environ():
    # Mocked AWS Credentials for moto (best practice recommendation from moto)
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"

    # Config mocks
    os.environ["DYNAMODB_TABLE"] = "test_table"
    os.environ["JWKS_URL"] = "https://test-jwks.url"
    os.environ["STAC_URL"] = "https://test-stac.url"
    os.environ["DATA_ACCESS_ROLE"] = "arn:aws:iam::123456789012:role/test-role"
    os.environ["DB_SECRET_ARN"] = "testing"


@pytest.fixture
def mock_ssm_parameter_store():
    with mock_ssm():
        yield boto3.client("ssm")


@pytest.fixture
def app(test_environ, mock_ssm_parameter_store):
    from src.main import app

    return app


@pytest.fixture
def api_client(app):
    return TestClient(app)


@pytest.fixture
def mock_table(app, test_environ):
    from src import dependencies
    from src.config import settings

    with mock_dynamodb():
        client = boto3.resource("dynamodb")
        mock_table = client.create_table(
            TableName=settings.dynamodb_table,
            AttributeDefinitions=[
                {"AttributeName": "created_by", "AttributeType": "S"},
                {"AttributeName": "id", "AttributeType": "S"},
                {"AttributeName": "status", "AttributeType": "S"},
                {"AttributeName": "created_at", "AttributeType": "S"},
            ],
            KeySchema=[
                {"AttributeName": "created_by", "KeyType": "HASH"},
                {"AttributeName": "id", "KeyType": "RANGE"},
            ],
            BillingMode="PAY_PER_REQUEST",
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "status",
                    "KeySchema": [
                        {"AttributeName": "status", "KeyType": "HASH"},
                        {"AttributeName": "created_at", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
        )
        app.dependency_overrides[dependencies.get_table] = lambda: mock_table
        yield mock_table
        app.dependency_overrides.pop(dependencies.get_table)


@pytest.fixture
def example_stac_item():
    return {
        "stac_version": "1.0.0",
        "stac_extensions": [],
        "type": "Feature",
        "id": "20201211_223832_CS2",
        "bbox": [
            172.91173669923782,
            1.3438851951615003,
            172.95469614953714,
            1.3690476620161975,
        ],
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [172.91173669923782, 1.3438851951615003],
                    [172.95469614953714, 1.3438851951615003],
                    [172.95469614953714, 1.3690476620161975],
                    [172.91173669923782, 1.3690476620161975],
                    [172.91173669923782, 1.3438851951615003],
                ]
            ],
        },
        "properties": {
            "datetime": "2020-12-11T22:38:32.125000Z",
            "eo:cloud_cover": 1,
        },
        "collection": "simple-collection",
        "links": [
            {
                "rel": "collection",
                "href": "./collection.json",
                "type": "application/json",
                "title": "Simple Example Collection",
            },
            {
                "rel": "root",
                "href": "./collection.json",
                "type": "application/json",
                "title": "Simple Example Collection",
            },
            {
                "rel": "parent",
                "href": "./collection.json",
                "type": "application/json",
                "title": "Simple Example Collection",
            },
        ],
        "assets": {
            "visual": {
                "href": "https://TEST_API.com/open-cogs/stac-examples/20201211_223832_CS2.tif",  # noqa
                "type": "image/tiff; application=geotiff; profile=cloud-optimized",
                "title": "3-Band Visual",
                "roles": ["visual"],
            },
            "thumbnail": {
                "href": "https://TEST_API.com/open-cogs/stac-examples/20201211_223832_CS2.jpg",  # noqa
                "title": "Thumbnail",
                "type": "image/jpeg",
                "roles": ["thumbnail"],
            },
        },
    }


@pytest.fixture
def example_stac_collection():
    return {
        "id": "simple-collection",
        "type": "Collection",
        "stac_extensions": [
            "https://stac-extensions.github.io/eo/v1.0.0/schema.json",
            "https://stac-extensions.github.io/projection/v1.0.0/schema.json",
            "https://stac-extensions.github.io/view/v1.0.0/schema.json",
        ],
        "item_assets": {
            "data": {
                "type": "image/tiff; application=geotiff; profile=cloud-optimized",
                "roles": ["data"],
            }
        },
        "stac_version": "1.0.0",
        "description": "A simple collection demonstrating core catalog fields with links to a couple of items",
        "title": "Simple Example Collection",
        "providers": [
            {
                "name": "Remote Data, Inc",
                "description": "Producers of awesome spatiotemporal assets",
                "roles": ["producer", "processor"],
                "url": "http://remotedata.io",
            }
        ],
        "extent": {
            "spatial": {
                "bbox": [
                    [
                        172.91173669923782,
                        1.3438851951615003,
                        172.95469614953714,
                        1.3690476620161975,
                    ]
                ]
            },
            "temporal": {
                "interval": [["2020-12-11T22:38:32.125Z", "2020-12-14T18:02:31.437Z"]]
            },
        },
        "license": "CC-BY-4.0",
        "summaries": {
            "platform": ["cool_sat1", "cool_sat2"],
            "constellation": ["ion"],
            "instruments": ["cool_sensor_v1", "cool_sensor_v2"],
            "gsd": {"minimum": 0.512, "maximum": 0.66},
            "eo:cloud_cover": {"minimum": 1.2, "maximum": 1.2},
            "proj:epsg": {"minimum": 32659, "maximum": 32659},
            "view:sun_elevation": {"minimum": 54.9, "maximum": 54.9},
            "view:off_nadir": {"minimum": 3.8, "maximum": 3.8},
            "view:sun_azimuth": {"minimum": 135.7, "maximum": 135.7},
        },
        "links": [
            {
                "rel": "root",
                "href": "./collection.json",
                "type": "application/json",
                "title": "Simple Example Collection",
            },
            {
                "rel": "item",
                "href": "./simple-item.json",
                "type": "application/geo+json",
                "title": "Simple Item",
            },
            {
                "rel": "item",
                "href": "./core-item.json",
                "type": "application/geo+json",
                "title": "Core Item",
            },
            {
                "rel": "item",
                "href": "./extended-item.json",
                "type": "application/geo+json",
                "title": "Extended Item",
            },
            {
                "rel": "self",
                "href": "https://raw.githubusercontent.com/radiantearth/stac-spec/v1.0.0/examples/collection.json",
                "type": "application/json",
            },
        ],
    }


@pytest.fixture
def client(app):
    """
    Return an API Client
    """
    app.dependency_overrides = {}
    return TestClient(app)


@pytest.fixture
def client_authenticated(app):
    """
    Returns an API client which skips the authentication
    """
    from src.dependencies import get_username

    app.dependency_overrides[get_username] = lambda: "test_user"
    return TestClient(app)


@pytest.fixture
def stac_collection(example_stac_collection):
    from src import schemas

    return schemas.StacCollection(**example_stac_collection)


@pytest.fixture
def example_ingestion(example_stac_item):
    from src import schemas

    return schemas.Ingestion(
        id=example_stac_item["id"],
        created_by="test-user",
        status=schemas.Status.queued,
        item=Item.parse_obj(example_stac_item),
    )
