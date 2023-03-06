import os

from pypgstac.db import PgstacDB

from .schemas import StacCollection
from .utils import (
    IngestionType,
    convert_decimals_to_float,
    get_db_credentials,
    load_into_pgstac,
)
from .vedaloader import VEDALoader


def ingest(collection: StacCollection):
    """
    Takes a collection model,
    does necessary preprocessing,
    and loads into the PgSTAC collection table
    """
    creds = get_db_credentials(os.environ["DB_SECRET_ARN"])
    collection = [
        convert_decimals_to_float(collection.dict(by_alias=True, exclude_unset=True))
    ]
    with PgstacDB(dsn=creds.dsn_string, debug=True) as db:
        load_into_pgstac(db=db, ingestions=collection, table=IngestionType.collections)


def delete(collection_id: str):
    """
    Deletes the collection from the database
    """
    creds = get_db_credentials(os.environ["DB_SECRET_ARN"])
    with PgstacDB(dsn=creds.dsn_string, debug=True) as db:
        loader = VEDALoader(db=db)
        loader.delete_collection(collection_id)
