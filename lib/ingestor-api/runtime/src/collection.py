import os

from pypgstac.db import PgstacDB
from pypgstac.load import Methods

from .loader import Loader
from .schemas import StacCollection
from .utils import get_db_credentials


def ingest(collection: StacCollection):
    """
    Takes a collection model,
    does necessary preprocessing,
    and loads into the PgSTAC collection table
    """
    creds = get_db_credentials(os.environ["DB_SECRET_ARN"])
    with PgstacDB(dsn=creds.dsn_string, debug=True) as db:
        loader = Loader(db=db)
        loader.load_collection(file=collection, insert_mode=Methods.upsert)


def delete(collection_id: str):
    """
    Deletes the collection from the database
    """
    creds = get_db_credentials(os.environ["DB_SECRET_ARN"])
    with PgstacDB(dsn=creds.dsn_string, debug=True) as db:
        loader = Loader(db=db)
        loader.delete_collection(collection_id)
