import os

from pypgstac.db import PgstacDB
from pypgstac.load import Methods

from .schemas import StacCollection
from .utils import get_db_credentials
from .vedaloader import VEDALoader


def ingest(collection: StacCollection):
    """
    Takes a collection model,
    does necessary preprocessing,
    and loads into the PgSTAC collection table
    """
    try:
        creds = get_db_credentials(os.environ["DB_SECRET_ARN"])
        with PgstacDB(dsn=creds.dsn_string, debug=True) as db:
            loader = VEDALoader(db=db)
            loader.load_collection(
                file=collection,
                insert_mode=Methods.upsert
            )
    except Exception as e:
        print(f"Encountered failure loading collection into pgSTAC: {e}")


def delete(collection_id: str):
    """
    Deletes the collection from the database
    """
    creds = get_db_credentials(os.environ["DB_SECRET_ARN"])
    with PgstacDB(dsn=creds.dsn_string, debug=True) as db:
        loader = VEDALoader(db=db)
        loader.delete_collection(collection_id)
