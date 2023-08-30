import base64
import json
import boto3
import os


def load_pgstac_secret(secret_name: str):
    """Retrieve secrets from AWS Secrets Manager

    Args:
        secret_name (str): name of aws secrets manager secret containing database connection secrets
        profile_name (str, optional): optional name of aws profile for use in debugger only

    Returns:
        secrets (dict): decrypted secrets in dict
    """

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager")

    get_secret_value_response = client.get_secret_value(SecretId=secret_name)

    if "SecretString" in get_secret_value_response:
        secret = json.loads(get_secret_value_response["SecretString"])
    else:
        secret = json.loads(base64.b64decode(get_secret_value_response["SecretBinary"]))

    try:
        os.environ.update(
            {
                "postgres_host": secret["host"],
                "postgres_dbname": secret["dbname"],
                "postgres_user": secret["username"],
                "postgres_pass": secret["password"],
                "postgres_port": str(secret["port"]),
            }
        )
    except Exception as ex:
        print("Could not load the pgstac environment variables from the secret")
        raise ex
