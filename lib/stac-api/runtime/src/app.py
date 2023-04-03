"""
FastAPI application using PGStac.
"""
import attr
from buildpg import render
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from stac_fastapi.api.app import StacApi
from stac_fastapi.api.routes import create_async_endpoint
from stac_fastapi.pgstac.core import CoreCrudClient
from stac_fastapi.pgstac.db import close_db_connection, connect_to_db
from stac_fastapi.types.search import APIRequest
from starlette_cramjam.middleware import CompressionMiddleware
from starlette.requests import Request
from typing import List
from stac_pydantic import Collection

from .config import ApiSettings
from .config import extensions as PgStacExtensions
from .config import get_request_model as GETModel
from .config import post_request_model as POSTModel

api_settings = ApiSettings()

class CollectionSearchGet(APIRequest):
    """Base arguments for GET Request."""
    keyword: str = None

class SearchCrudClient(CoreCrudClient):
    """CRUD client with custom endpoints."""

    async def collection_keyword_search(
        self,
        keyword: str = None, **kwargs
    ) -> List[Collection]:
        request: Request = kwargs["request"]
        pool = request.app.state.readpool
        print(f"KEYWORD: {keyword}")
        print(f"POOL: {pool}")

        try:
            async with pool.acquire() as conn:
                q, p = render(
                    """
                    SELECT * FROM dashboard.substring_search_collections('blah'::text);
                    """,
                    keyword=keyword,
                )
                print("Q is: ", q)
                print("P is: ", p)
                collections = await conn.fetch(q, *p)
        except Exception as e:
            raise HTTPException(status_code=400, detail=(f"{e}"))

        collections = [Collection(id=row[0], content=row[1]) for row in collections]
        return collections

class SearchStacApi(StacApi):
    client: SearchCrudClient = attr.ib()

    """StacApi with custom endpoints."""
    def register_get_search(self):
        """Register search endpoint (GET /search).
        Returns:
            None
        """
        super().register_get_search()
        self.router.add_api_route(
            name="Search",
            path="/search/collections",
            response_model=List[Collection] if self.settings.enable_response_models else None,
            response_class=self.response_class,
            response_model_exclude_unset=True,
            response_model_exclude_none=True,
            methods=["GET"],
            endpoint=create_async_endpoint(
                self.client.collection_keyword_search,
                CollectionSearchGet,
                self.response_class,
            ),
        )

api = SearchStacApi(
    title=api_settings.name,
    api_version=api_settings.version,
    description=api_settings.description or api_settings.name,
    settings=api_settings.load_postgres_settings(),
    extensions=PgStacExtensions,
    client=SearchCrudClient(post_request_model=POSTModel),
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
