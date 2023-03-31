"""Utilities to bulk load data into pgstac from json/ndjson."""
import logging

from pypgstac.load import Loader as BaseLoader

logger = logging.getLogger(__name__)


class Loader(BaseLoader):
    """Utilities for loading data and updating collection summaries/extents."""

    def __init__(self, db) -> None:
        super().__init__(db)
        self.check_version()
        self.conn = self.db.connect()

    def delete_collection(self, collection_id: str) -> None:
        with self.conn.cursor() as cur:
            with self.conn.transaction():
                logger.info(f"Deleting collection: {collection_id}.")
                cur.execute("SELECT pgstac.delete_collection(%s);", [collection_id])
