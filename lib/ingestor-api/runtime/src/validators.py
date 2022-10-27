import boto3
import functools
import requests


@functools.cache
def get_s3_credentials():
    from .main import settings

    print("Fetching S3 Credentials...")

    response = boto3.client("sts").assume_role(
        RoleArn=settings.data_access_role,
        RoleSessionName="stac-ingestor-data-validation",
    )
    return {
        "aws_access_key_id": response["Credentials"]["AccessKeyId"],
        "aws_secret_access_key": response["Credentials"]["SecretAccessKey"],
        "aws_session_token": response["Credentials"]["SessionToken"],
    }


def s3_object_is_accessible(bucket: str, key: str):
    """
    Ensure we can send HEAD requests to S3 objects.
    """
    client = boto3.client("s3", **get_s3_credentials())
    try:
        client.head_object(Bucket=bucket, Key=key)
    except client.exceptions.ClientError as e:
        raise ValueError(
            f"Asset not accessible: {e.__dict__['response']['Error']['Message']}"
        )


def url_is_accessible(href: str):
    """
    Ensure URLs are accessible via HEAD requests.
    """
    try:
        requests.head(href).raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise ValueError(
            f"Asset not accessible: {e.response.status_code} {e.response.reason}"
        )


@functools.cache
def collection_exists(collection_id: str) -> bool:
    """
    Ensure collection exists in STAC
    """
    from .main import settings

    url = "/".join(
        f'{url.strip("/")}' for url in [settings.stac_url, "collections", collection_id]
    )

    if (response := requests.get(url)).ok:
        return True

    raise ValueError(
        f"Invalid collection '{collection_id}', received "
        f"{response.status_code} response code from STAC API"
    )
