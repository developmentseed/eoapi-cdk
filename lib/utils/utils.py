import base64
import json
import os

import boto3


def get_secret_dict(secret_arn_env_var: str):
    """Retrieve secrets from AWS Secrets Manager

    Args:
        secret_arn_env_var (str): environment variable that contains the secret ARN

    Returns:
        secrets (dict): decrypted secrets in dict
    """
    secret_arn = os.environ.get(secret_arn_env_var)
    if not secret_arn:
        raise ValueError(f"{secret_arn_env_var} is not set!")

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager")

    get_secret_value_response = client.get_secret_value(SecretId=secret_arn)

    if "SecretString" in get_secret_value_response:
        return json.loads(get_secret_value_response["SecretString"])
    else:
        return json.loads(base64.b64decode(get_secret_value_response["SecretBinary"]))
