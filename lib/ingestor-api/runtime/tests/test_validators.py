from unittest.mock import MagicMock, patch

import pytest
import requests
from pydantic import AnyHttpUrl
from src import validators


@pytest.fixture
def mock_settings():
    """Fixture to instantiate and patch settings with proper types."""
    from src.config import Settings

    mock_settings = Settings(
        dynamodb_table="test-table",
        stac_url=AnyHttpUrl("https://test-stac.url"),
        data_access_role="arn:aws:iam::123456789012:role/test-role",
        requester_pays=False,
        jwks_url=AnyHttpUrl("https://test-jwks.url"),
        root_path="testing",
    )

    with patch("src.config.settings", mock_settings):
        yield mock_settings


@pytest.fixture
def mock_requests():
    """Fixture to mock requests library."""
    with patch("src.validators.requests") as mock_requests:
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.raise_for_status.return_value = None
        mock_requests.get.return_value = mock_response
        mock_requests.head.return_value = mock_response

        mock_requests.exceptions = requests.exceptions

        yield mock_requests


@pytest.fixture
def mock_boto3():
    """Fixture to mock boto3 library."""
    with patch("src.validators.boto3") as mock_boto3:
        mock_client = MagicMock()
        mock_client.exceptions.ClientError = Exception

        mock_sts_client = MagicMock()
        mock_sts_client.assume_role.return_value = {
            "Credentials": {
                "AccessKeyId": "test_access_key",
                "SecretAccessKey": "test_secret_key",
                "SessionToken": "test_session_token",
            }
        }

        def mock_client_factory(service_name, **kwargs):
            if service_name == "sts":
                return mock_sts_client
            return mock_client

        mock_boto3.client.side_effect = mock_client_factory

        yield mock_boto3, mock_client


class TestValidators:
    def test_collection_exists_success(self, mock_settings, mock_requests):
        """Test collection_exists when the collection exists."""
        validators.collection_exists.cache_clear()

        result = validators.collection_exists("test-collection")

        assert result

        expected_url = f"{mock_settings.stac_url}collections/test-collection"
        mock_requests.get.assert_called_once_with(expected_url)

    def test_collection_exists_failure(self, mock_settings, mock_requests):
        """Test collection_exists when the collection doesn't exist."""
        validators.collection_exists.cache_clear()

        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_requests.get.return_value = mock_response

        with pytest.raises(ValueError) as excinfo:
            validators.collection_exists("nonexistent-collection")

        assert "Invalid collection 'nonexistent-collection'" in str(excinfo.value)
        assert "404 response code" in str(excinfo.value)

    def test_url_is_accessible_success(self, mock_requests):
        """Test url_is_accessible when the URL is accessible."""
        validators.url_is_accessible("https://example.com/asset.tif")

        mock_requests.head.assert_called_once_with("https://example.com/asset.tif")

    def test_url_is_accessible_failure(self, mock_requests):
        """Test url_is_accessible when the URL is not accessible."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=MagicMock(status_code=403, reason="Forbidden")
        )
        mock_requests.head.return_value = mock_response

        with pytest.raises(ValueError) as excinfo:
            validators.url_is_accessible("https://example.com/private.tif")

        assert "Asset not accessible" in str(excinfo.value)

    def test_s3_object_is_accessible_success(self, mock_settings, mock_boto3):
        """Test s3_object_is_accessible when the object is accessible."""
        _, mock_s3_client = mock_boto3

        validators.s3_object_is_accessible("test-bucket", "test-key")

        mock_s3_client.head_object.assert_called_once_with(
            Bucket="test-bucket", Key="test-key"
        )

    def test_s3_object_is_accessible_with_requester_pays(self, mock_settings, mock_boto3):
        """Test s3_object_is_accessible with requester pays enabled."""
        _, mock_s3_client = mock_boto3

        mock_settings.requester_pays = True

        validators.s3_object_is_accessible("test-bucket", "test-key")

        mock_s3_client.head_object.assert_called_once_with(
            Bucket="test-bucket", Key="test-key", RequestPayer="requester"
        )

    def test_s3_object_is_accessible_failure(self, mock_settings, mock_boto3):
        """Test s3_object_is_accessible when the object is not accessible."""
        _, mock_s3_client = mock_boto3

        _ = {"Error": {"Message": "Access Denied"}}
        mock_s3_client.head_object.side_effect = Exception()
        mock_s3_client.head_object.side_effect.__dict__["response"] = {
            "Error": {"Message": "Access Denied"}
        }

        with pytest.raises(ValueError) as excinfo:
            validators.s3_object_is_accessible("test-bucket", "private-key")

        assert "Asset not accessible" in str(excinfo.value)

    def test_get_s3_credentials(self, mock_boto3):
        """Test get_s3_credentials returns the expected credentials."""
        _, _ = mock_boto3

        validators.get_s3_credentials.cache_clear()

        credentials = validators.get_s3_credentials()

        expected_credentials = {
            "aws_access_key_id": "test_access_key",
            "aws_secret_access_key": "test_secret_key",
            "aws_session_token": "test_session_token",
        }
        assert credentials == expected_credentials
