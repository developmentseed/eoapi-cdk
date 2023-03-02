import logging
from typing import Optional

import boto3
import requests
from authlib.jose import JsonWebKey, JsonWebToken, JWTClaims, KeySet, errors
from cachetools import TTLCache, cached
from fastapi import Depends, HTTPException, Request, security

from . import config, services

logger = logging.getLogger(__name__)

token_scheme = security.HTTPBearer()


def get_settings(request: Request) -> config.Settings:
    return request.app.extra["settings"]


def get_jwks_url(settings: config.Settings = Depends(get_settings)) -> str:
    return settings.jwks_url


@cached(TTLCache(maxsize=1, ttl=3600))
def get_jwks(jwks_url: str = Depends(get_jwks_url)) -> KeySet:
    with requests.get(jwks_url) as response:
        response.raise_for_status()
        return JsonWebKey.import_key_set(response.json())


def decode_token(
    token: security.HTTPAuthorizationCredentials = Depends(token_scheme),
    jwks: KeySet = Depends(get_jwks),
) -> JWTClaims:
    """
    Validate & decode JWT
    """
    try:
        claims = JsonWebToken(["RS256"]).decode(
            s=token.credentials,
            key=jwks,
            claims_options={
                # # Example of validating audience to match expected value
                # "aud": {"essential": True, "values": [APP_CLIENT_ID]}
            },
        )

        if "client_id" in claims:
            # Insert Cognito's `client_id` into `aud` claim if `aud` claim is unset
            claims.setdefault("aud", claims["client_id"])

        claims.validate()
        return claims
    except errors.JoseError:  #
        logger.exception("Unable to decode token")
        raise HTTPException(status_code=403, detail="Bad auth token")


def get_username_from_token(
    claims: Optional[security.HTTPBasicCredentials] = Depends(decode_token),
):
    return claims["sub"]


def get_username_from_request(provided_by: str):
    return provided_by


get_username = (
    get_username_from_token if config.settings.jwks_url else get_username_from_request
)


def get_table(settings: config.Settings = Depends(get_settings)):
    client = boto3.resource("dynamodb")
    return client.Table(settings.dynamodb_table)


def get_db(table=Depends(get_table)) -> services.Database:
    return services.Database(table=table)


def fetch_ingestion(
    ingestion_id: str,
    db: services.Database = Depends(get_db),
    username: str = Depends(get_username),
):
    try:
        return db.fetch_one(username=username, ingestion_id=ingestion_id)
    except services.NotInDb:
        raise HTTPException(
            status_code=404, detail="No ingestion found with provided ID"
        )
