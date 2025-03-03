"""
FastAPI application using PGStac.
"""

from brotli_asgi import BrotliMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from stac_fastapi.api.app import StacApi
from stac_fastapi.api.middleware import ProxyHeaderMiddleware
from stac_fastapi.pgstac.app import (
    application_extensions,
    collections_get_request_model,
    get_request_model,
    items_get_request_model,
    post_request_model,
)
from stac_fastapi.pgstac.core import CoreCrudClient
from stac_fastapi.pgstac.db import close_db_connection, connect_to_db
from starlette.middleware import Middleware

from .config import ApiSettings

settings = ApiSettings()

api = StacApi(
    app=FastAPI(
        openapi_url=settings.openapi_url,
        docs_url=settings.docs_url,
        redoc_url=None,
        root_path=settings.root_path,
        title=settings.stac_fastapi_title,
        version=settings.stac_fastapi_version,
        description=settings.stac_fastapi_description,
    ),
    settings=settings,
    extensions=application_extensions,
    client=CoreCrudClient(pgstac_search_model=post_request_model),
    response_class=ORJSONResponse,
    items_get_request_model=items_get_request_model,
    search_get_request_model=get_request_model,
    search_post_request_model=post_request_model,
    collections_get_request_model=collections_get_request_model,
    middlewares=[
        Middleware(BrotliMiddleware),
        Middleware(ProxyHeaderMiddleware),
    ],
)
app = api.app

# Set all CORS enabled origins
if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
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
