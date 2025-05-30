from unittest.mock import patch

import pytest
from pypgstac.db import PgstacDB
from pypgstac.load import Loader
from pypgstac.migrate import Migrate
from pytest_postgresql.janitor import DatabaseJanitor
from stac_pydantic.collection import Collection, Extent, SpatialExtent, TimeInterval
from stac_pydantic.links import Link, Links

TEST_COLLECTION_IDS = ["test-collection-1", "test-collection-2"]


class MockContext:
    """Mock AWS Lambda context"""

    def __init__(self):
        self.aws_request_id = "test-request-id"

    def get_remaining_time_in_millis(self):
        return 30000


@pytest.fixture(scope="session")
def database(postgresql_proc):
    """Create Database Fixture."""
    with DatabaseJanitor(
        user=postgresql_proc.user,
        host=postgresql_proc.host,
        port=postgresql_proc.port,
        dbname="test_db",
        version=postgresql_proc.version,
        password="password",
    ) as jan:
        yield jan


@pytest.fixture(scope="session")
def database_url(database):
    """Install pgstac on the database and load a collection"""
    db_url = f"postgresql://{database.user}:{database.password}@{database.host}:{database.port}/{database.dbname}"

    with PgstacDB(dsn=db_url) as db:
        migrator = Migrate(db)
        migrator.run_migration()

        test_collections = [
            Collection(
                id=collection_id,
                description="test",
                stac_version="1.1.0",
                links=Links([Link(href="http://test/test-collection", rel="self")]),
                extent=Extent(
                    spatial=SpatialExtent(bbox=[[0, 0, 1, 1]]),
                    temporal=TimeInterval(
                        interval=[["2025-01-01T00:00:00Z", "2025-01-02T00:00:00Z"]]
                    ),
                ),
                type="Collection",
                license="license",
            ).model_dump(mode="json")
            for collection_id in TEST_COLLECTION_IDS
        ]

        loader = Loader(db)
        loader.load_collections(test_collections)  # type: ignore

    return db_url


@pytest.fixture
def mock_aws_context():
    return MockContext()


@pytest.fixture
def mock_pgstac_dsn(database_url):
    """Mock the get_pgstac_dsn function to return the test database URL"""
    with patch("stac_item_loader.handler.get_pgstac_dsn", return_value=database_url):
        yield


@pytest.fixture(autouse=True)
def cleanup_test_items(database_url):
    """
    Fixture to clean up test items after each test.
    The autouse=True makes this run automatically for each test.
    """
    yield

    # After the test completes, clean up items that match our test pattern
    with PgstacDB(dsn=database_url) as db:
        query = """
        DELETE FROM pgstac.items
        """
        db.query(query)


def check_item_exists(database_url, collection_id, item_id):
    """
    Check if an item with the given ID exists in the specified collection.

    Args:
        database_url: Connection string for the database
        collection_id: The collection ID to check
        item_id: The item ID to check

    Returns:
        bool: True if the item exists, False otherwise
    """
    with PgstacDB(dsn=database_url) as db:
        # Direct SQL query to check if the item exists
        query = """
        SELECT COUNT(*)
        FROM pgstac.items
        WHERE collection = %s AND id = %s
        """

        result = list(db.query(query, (collection_id, item_id)))
        return result[0][0] > 0


def get_all_collection_items(database_url, collection_id):
    """
    Get all items in a collection from the database.

    Args:
        database_url: Connection string for the database
        collection_id: The collection ID to query

    Returns:
        list: List of item dictionaries
    """
    with PgstacDB(dsn=database_url) as db:
        query = """
        SELECT id, collection, content
        FROM pgstac.items
        WHERE collection = %s
        """

        result = list(db.query(query, (collection_id,)))
        return [{"id": row[0], "collection": row[1], "content": row[2]} for row in result]


def count_collection_items(database_url, collection_id):
    """
    Count the number of items in a collection.

    Args:
        database_url: Connection string for the database
        collection_id: The collection ID to count items for

    Returns:
        int: Number of items in the collection
    """
    with PgstacDB(dsn=database_url) as db:
        query = """
        SELECT COUNT(*)
        FROM pgstac.items
        WHERE collection = %s
        """

        result = list(db.query(query, (collection_id,)))
        return result[0][0]
