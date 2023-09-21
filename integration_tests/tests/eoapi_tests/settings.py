from typing import Optional

from pydantic_settings import BaseSettings


class eoapiDeploymentSettings(BaseSettings):
    ingestor_url: str
    stac_api_url: str
    titiler_pgstac_api_url: str
    secret_id: Optional[str] = None
    collections_endpoint: Optional[str] = "/collections"
    items_endpoint: Optional[str] = "/ingestions"
