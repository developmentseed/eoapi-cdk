import os

from fastapi import HTTPException
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
    try:
        creds = get_db_credentials(os.environ["DB_SECRET_ARN"])
        with PgstacDB(dsn=creds.dsn_string, debug=True) as db:
            loader = Loader(db=db)
            loader.load_collections(
                file=[collection.model_dump(mode="json")], insert_mode=Methods.upsert
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Encountered failure loading collection into pgSTAC: {e}",
        ) from e


def delete(collection_id: str):
    """
    Deletes the collection from the database
    """
    creds = get_db_credentials(os.environ["DB_SECRET_ARN"])
    with PgstacDB(dsn=creds.dsn_string, debug=True) as db:
        loader = Loader(db=db)
        loader.delete_collection(collection_id)
