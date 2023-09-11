import json
import os

import boto3
import pystac
import requests
from pystac import STACValidationError
from settings import eoapiDeploymentSettings


class StacIngestion:

    """Class representing various test operations"""

    def __init__(self):
        self.eoapi_deployment_settings = eoapiDeploymentSettings()
        self.current_file_path = os.path.dirname(os.path.abspath(__file__))
        self.headers = self.get_headers()

    def validate_collection(self, collection):
        try:
            pystac.validation.validate_dict(collection)
        except STACValidationError:
            raise STACValidationError("Validation failed for the collection")

    def validate_item(self, item):
        try:
            pystac.validation.validate_dict(item)
        except STACValidationError:
            raise STACValidationError("Validation failed for the item")

    def get_authentication_token(self) -> str:
        if not self.eoapi_deployment_settings.secret_id:
            raise ValueError("You should provide a secret id")

        client = boto3.client("secretsmanager", region_name="us-west-2")

        try:
            res_secret = client.get_secret_value(
                SecretId=self.eoapi_deployment_settings.secret_id
            )
        except client.exceptions.ResourceNotFoundException:
            raise Exception(
                "Unable to find a secret for "
                "{self.eoapi_deployment_settings.secret_id}. "
                "\n\nHint: Check your stage and service id."
                "Also, verify that the correct "
                "AWS_PROFILE is set on your environment."
            )

        # Authentication - Get TOKEN
        secret = json.loads(res_secret["SecretString"])
        client_secret = secret["client_secret"]
        client_id = secret["client_id"]
        cognito_domain = secret["cognito_domain"]
        scope = secret["scope"]

        res_token = requests.post(
            f"{cognito_domain}/oauth2/token",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
            auth=(client_id, client_secret),
            data={
                "grant_type": "client_credentials",
                # A space-separated list of scopes
                # to request for the generated access token.
                "scope": scope,
            },
        )

        token = res_token.json()["access_token"]
        return token

    def get_headers(self) -> dict:
        if self.eoapi_deployment_settings.secret_id:
            return {
                "headers": {
                    "Authorization": f"bearer {self.get_authentication_token()}"
                }
            }
        else:
            return {"params": {"provided_by": "eoapi-tests"}}

    def insert_collection(self, collection):
        response = requests.post(
            self.eoapi_deployment_settings.ingestor_url
            + self.eoapi_deployment_settings.collections_endpoint,
            json=collection,
            **self.headers,
        )
        return response

    def insert_item(self, item):
        response = requests.post(
            self.eoapi_deployment_settings.ingestor_url
            + self.eoapi_deployment_settings.items_endpoint,
            json=item,
            **self.headers,
        )
        return response

    def query_collection(self, collection_id):
        response = requests.get(
            self.eoapi_deployment_settings.stac_api_url
            + self.eoapi_deployment_settings.collections_endpoint
            + f"/{collection_id}"
        )
        return response

    def query_items(self, collection_id):
        response = requests.get(
            self.eoapi_deployment_settings.stac_api_url
            + self.eoapi_deployment_settings.collections_endpoint
            + f"/{collection_id}/items"
        )
        return response

    def register_mosaic(self, search_request):
        response = requests.post(
            self.eoapi_deployment_settings.titiler_pgstac_api_url + "/mosaic/register",
            json=search_request,
        )
        return response

    def list_mosaic_assets(self, search_id):
        """list the assets of the first tile"""
        response = requests.get(
            self.eoapi_deployment_settings.titiler_pgstac_api_url
            + f"/mosaic/{search_id}/tiles/0/0/0/assets"
        )
        return response

    def get_test_collection(self):
        with open(
            os.path.join(self.current_file_path, "fixtures", "test_collection.json"),
            "r",
        ) as f:
            test_collection = json.load(f)
        return test_collection

    def get_test_item(self):
        with open(
            os.path.join(self.current_file_path, "fixtures", "test_item.json"), "r"
        ) as f:
            test_item = json.load(f)
        return test_item

    def get_test_titiler_search_request(self):
        with open(
            os.path.join(
                self.current_file_path, "fixtures", "test_titiler_search_request.json"
            ),
            "r",
        ) as f:
            test_titiler_search_request = json.load(f)
        return test_titiler_search_request

    def delete_collection(self, collection_id):
        response = requests.delete(
            self.eoapi_deployment_settings.ingestor_url
            + self.eoapi_deployment_settings.collections_endpoint
            + f"/{collection_id}",
            **self.headers,
        )
        return response
