"""Utilities to bulk load data into pgstac from json/ndjson."""
import logging

from pypgstac.load import Loader

logger = logging.getLogger(__name__)


class VEDALoader(Loader):
    """Utilities for loading data and updating collection summaries/extents."""

    def __init__(self, db) -> None:
        super().__init__(db)
        self.check_version()
        self.conn = self.db.connect()

    def update_collection_summaries(self, collection_id: str) -> None:
        """Update collection-level summaries for a single collection.
        This includes dashboard summaries (i.e. datetime and cog_default) as well as
        STAC-conformant bbox and temporal extent."""

        with self.conn.cursor() as cur:
            with self.conn.transaction():
                logger.info(
                    "Updating dashboard summaries for collection: {}.".format(
                        collection_id
                    )
                )
                cur.execute(
                    "SELECT dashboard.update_collection_default_summaries(%s)",
                    collection_id,
                )
                logger.info("Updating bbox for collection: {}.".format(collection_id))
                cur.execute("SELECT pgstac.collection_bbox(%s)", collection_id)
                logger.info(
                    "Updating temporal extent for collection: {}.".format(collection_id)
                )
                cur.execute(
                    "SELECT pgstac.collection_temporal_extent(%s)", collection_id
                )

    def delete_collection(self, collection_id: str) -> None:
        with self.conn.cursor() as cur:
            with self.conn.transaction():
                logger.info(f"Deleting collection: {collection_id}.")
                cur.execute("SELECT pgstac.delete_collection(%s);", (collection_id,))
