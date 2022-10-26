"""
FastAPI application using PGStac.
"""

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from stac_fastapi.api.app import StacApi
from stac_fastapi.pgstac.core import CoreCrudClient
from stac_fastapi.pgstac.db import close_db_connection, connect_to_db
from starlette_cramjam.middleware import CompressionMiddleware

from .config import (
    ApiSettings,
    extensions as PgStacExtensions,
    get_request_model as GETModel,
    post_request_model as POSTModel,
)

api_settings = ApiSettings()

api = StacApi(
    title=api_settings.name,
    api_version=api_settings.version,
    description=api_settings.description or api_settings.name,
    settings=api_settings.load_postgres_settings(),
    extensions=PgStacExtensions,
    client=CoreCrudClient(post_request_model=POSTModel),
    search_get_request_model=GETModel,
    search_post_request_model=POSTModel,
    response_class=ORJSONResponse,
    middlewares=[CompressionMiddleware],
)

app = api.app

# Set all CORS enabled origins
if api_settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=api_settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )


@app.on_event("startup")
async def startup_event():
    """Connect to database on startup."""
    print("Setting up DB connection...")
    await connect_to_db(app)
    print("DB connection setup.")


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection."""
    print("Closing up DB connection...")
    await close_db_connection(app)
    print("DB connection closed.")
