"""
Custom resource lambda handler to bootstrap Postgres db.
Source: https://github.com/developmentseed/eoAPI/blob/master/deployment/handlers/db_handler.py
"""

import json
import logging

import boto3
import httpx
import psycopg
from psycopg import sql
from psycopg.conninfo import make_conninfo
from pypgstac.db import PgstacDB
from pypgstac.migrate import Migrate

logger = logging.getLogger("eoapi-bootstrap")


def send(
    event,
    context,
    responseStatus,
    responseData,
    physicalResourceId=None,
    noEcho=False,
):
    """
    Copyright 2016 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
    This file is licensed to you under the AWS Customer Agreement (the "License").
    You may not use this file except in compliance with the License.
    A copy of the License is located at http://aws.amazon.com/agreement/ .
    This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or implied.
    See the License for the specific language governing permissions and limitations under the License.

    Send response from AWS Lambda.

    Note: The cfnresponse module is available only when you use the ZipFile property to write your source code.
    It isn't available for source code that's stored in Amazon S3 buckets.
    For code in buckets, you must write your own functions to send responses.
    """
    responseBody = {}
    responseBody["Status"] = responseStatus
    responseBody["Reason"] = (
        "See the details in CloudWatch Log Stream: " + context.log_stream_name
    )
    responseBody["PhysicalResourceId"] = physicalResourceId or context.log_stream_name
    responseBody["StackId"] = event["StackId"]
    responseBody["RequestId"] = event["RequestId"]
    responseBody["LogicalResourceId"] = event["LogicalResourceId"]
    responseBody["NoEcho"] = noEcho
    responseBody["Data"] = responseData

    json_responseBody = json.dumps(responseBody)
    print("Response body:\n     " + json_responseBody)

    try:
        response = httpx.put(
            event["ResponseURL"],
            data=json_responseBody,
            headers={"content-type": "", "content-length": str(len(json_responseBody))},
            timeout=30,
        )
        print("Status code: ", response.status_code)
        logger.debug(f"OK - Status code: {response.status_code}")

    except Exception as e:
        print("send(..) failed executing httpx.put(..): " + str(e))
        logger.debug(f"NOK - failed executing PUT requests:  {e}")


def get_secret(secret_name):
    """Get Secrets from secret manager."""
    print(f"Fetching {secret_name}")
    client = boto3.client(service_name="secretsmanager")
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])


def create_db(cursor, db_name: str) -> None:
    """Create DB."""
    cursor.execute(
        sql.SQL("SELECT 1 FROM pg_catalog.pg_database " "WHERE datname = %s"), [db_name]
    )
    if cursor.fetchone():
        print(f"    database {db_name} exists, not creating DB")
    else:
        print(f"    database {db_name} not found, creating...")
        cursor.execute(
            sql.SQL("CREATE DATABASE {db_name}").format(db_name=sql.Identifier(db_name))
        )


def create_user(cursor, username: str, password: str) -> None:
    """Create User."""
    cursor.execute(
        sql.SQL(
            "DO $$ "
            "BEGIN "
            "  IF NOT EXISTS ( "
            "       SELECT 1 FROM pg_roles "
            "       WHERE rolname = {user}) "
            "  THEN "
            "    CREATE USER {username} "
            "    WITH PASSWORD {password}; "
            "  ELSE "
            "    ALTER USER {username} "
            "    WITH PASSWORD {password}; "
            "  END IF; "
            "END "
            "$$; "
        ).format(username=sql.Identifier(username), password=password, user=username)
    )


def update_user_permissions(cursor, db_name: str, username: str) -> None:
    """Update eoAPI user permissions."""
    cursor.execute(
        sql.SQL(
            "GRANT CONNECT ON DATABASE {db_name} TO {username};"
            "GRANT CREATE ON DATABASE {db_name} TO {username};"  # Allow schema creation
            "GRANT USAGE ON SCHEMA public TO {username};"
            "ALTER DEFAULT PRIVILEGES IN SCHEMA public "
            "GRANT ALL PRIVILEGES ON TABLES TO {username};"
            "ALTER DEFAULT PRIVILEGES IN SCHEMA public "
            "GRANT ALL PRIVILEGES ON SEQUENCES TO {username};"
            "GRANT pgstac_read TO {username};"
            "GRANT pgstac_ingest TO {username};"
            "GRANT pgstac_admin TO {username};"
        ).format(
            db_name=sql.Identifier(db_name),
            username=sql.Identifier(username),
        )
    )


def register_extensions(cursor) -> None:
    """Add PostGIS extension."""
    cursor.execute(sql.SQL("CREATE EXTENSION IF NOT EXISTS postgis;"))


###############################################################################
# PgSTAC Customization
###############################################################################
def customization(cursor, params) -> None:
    """
    CUSTOMIZED YOUR PGSTAC DATABASE

    ref: https://github.com/stac-utils/pgstac/blob/main/docs/src/pgstac.md

    """
    if str(params.get("context", "FALSE")).upper() == "TRUE":
        # Add CONTEXT=ON
        pgstac_settings = """
        INSERT INTO pgstac_settings (name, value)
        VALUES ('context', 'on')
        ON CONFLICT ON CONSTRAINT pgstac_settings_pkey DO UPDATE SET value = excluded.value;"""
        cursor.execute(sql.SQL(pgstac_settings))

    if str(params.get("mosaic_index", "TRUE")).upper() == "TRUE":
        # Create index of searches with `mosaic`` type
        cursor.execute(
            sql.SQL(
                "CREATE INDEX IF NOT EXISTS searches_mosaic ON searches ((true)) WHERE metadata->>'type'='mosaic';"
            )
        )


def handler(event, context):
    """Lambda Handler."""
    print(f"Handling {event}")

    if event["RequestType"] not in ["Create", "Update"]:
        return send(event, context, "SUCCESS", {"msg": "No action to be taken"})

    try:
        params = event["ResourceProperties"]

        # Admin (AWS RDS) user/password/dbname parameters
        admin_params = get_secret(params["conn_secret_arn"])

        # Custom eoAPI user/password/dbname parameters
        eoapi_params = get_secret(params["new_user_secret_arn"])

        print("Connecting to RDS...")
        rds_conninfo = make_conninfo(
            dbname=admin_params.get("dbname", "postgres"),
            user=admin_params["username"],
            password=admin_params["password"],
            host=admin_params["host"],
            port=admin_params["port"],
        )
        with psycopg.connect(rds_conninfo, autocommit=True) as conn:
            with conn.cursor() as cur:
                print(f"Creating eoAPI '{eoapi_params['dbname']}' database...")
                create_db(
                    cursor=cur,
                    db_name=eoapi_params["dbname"],
                )

                print(f"Creating eoAPI '{eoapi_params['username']}' user...")
                create_user(
                    cursor=cur,
                    username=eoapi_params["username"],
                    password=eoapi_params["password"],
                )

        # Install postgis and pgstac on the eoapi database with
        # superuser permissions
        print(f"Connecting to eoAPI '{eoapi_params['dbname']}' database...")
        eoapi_db_admin_conninfo = make_conninfo(
            dbname=eoapi_params["dbname"],
            user=admin_params["username"],
            password=admin_params["password"],
            host=admin_params["host"],
            port=admin_params["port"],
        )
        with psycopg.connect(eoapi_db_admin_conninfo, autocommit=True) as conn:
            with conn.cursor() as cur:
                print(f"Registering Extension in '{eoapi_params['dbname']}' database...")
                register_extensions(cursor=cur)

            print("Starting PgSTAC Migration ")
            with PgstacDB(connection=conn, debug=True) as pgdb:
                print(f"Current PgSTAC Version: {pgdb.version}")

                print(f"Running migrations to PgSTAC {params['pgstac_version']}...")
                Migrate(pgdb).run_migration(params["pgstac_version"])

        with psycopg.connect(
            eoapi_db_admin_conninfo,
            autocommit=True,
            options="-c search_path=pgstac,public -c application_name=pgstac",
        ) as conn:
            print("Customize PgSTAC database...")
            # Update permissions to eoAPI user to assume pgstac_* roles
            with conn.cursor() as cur:
                print(f"Update '{eoapi_params['username']}' permissions...")
                update_user_permissions(
                    cursor=cur,
                    db_name=eoapi_params["dbname"],
                    username=eoapi_params["username"],
                )

                customization(cursor=cur, params=params)

        # Make sure the user can access the database
        eoapi_user_dsn = "postgresql://{user}:{password}@{host}:{port}/{dbname}".format(
            dbname=eoapi_params["dbname"],
            user=eoapi_params["username"],
            password=eoapi_params["password"],
            host=admin_params["host"],
            port=admin_params["port"],
        )
        print("Checking eoAPI user access to the PgSTAC database...")
        with PgstacDB(dsn=eoapi_user_dsn, debug=True) as pgdb:
            print(
                f"    OK - User has access to pgstac db, pgstac schema version: {pgdb.version}"
            )

    except Exception as e:
        print(f"Unable to bootstrap database with exception={e}")
        send(event, context, "FAILED", {"message": str(e)})
        raise e

    print("Complete.")
    return send(event, context, "SUCCESS", {})
