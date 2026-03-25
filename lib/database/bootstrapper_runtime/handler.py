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


DEFAULT_PG_CRON_SCHEDULE = "*/10 * * * *"  # every 10 minutes


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
        sql.SQL("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s"), [db_name]
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
def _is_enabled(params: dict, key: str) -> bool:
    """Parse a string boolean CloudFormation custom resource property.

    CloudFormation custom resource properties are always strings, so boolean
    flags are passed as ``"TRUE"`` or ``"FALSE"``. Callers must check that the
    key is present before calling this function; absent keys are a no-op and
    should not reach this function.

    Args:
        params: ResourceProperties dict from the CloudFormation event.
        key: Property name to look up.

    Returns:
        True if the property value is ``"TRUE"`` (case-insensitive).
    """
    return str(params.get(key, "FALSE")).upper() == "TRUE"


def _apply_pgstac_setting(cursor, name: str, enabled: bool) -> None:
    """Upsert or delete a row in the pgstac_settings table.

    When ``enabled`` is True, upserts ``'on'``. When False, deletes the row so
    pgstac reverts to its built-in default. When the setting is absent from
    params entirely, this function should not be called — absent means no-op.

    Args:
        cursor: Database cursor with ``search_path`` including the pgstac schema.
        name: Setting name (primary key in pgstac_settings).
        enabled: Whether to enable or disable the setting.
    """
    if enabled:
        cursor.execute(
            sql.SQL(
                "INSERT INTO pgstac_settings (name, value) VALUES ({name}, 'on') "
                "ON CONFLICT ON CONSTRAINT pgstac_settings_pkey DO UPDATE SET value = excluded.value;"
            ).format(name=sql.Literal(name))
        )
    else:
        cursor.execute(
            sql.SQL("DELETE FROM pgstac_settings WHERE name = {name};").format(
                name=sql.Literal(name)
            )
        )


def customization(cursor, params) -> None:
    """Apply pgSTAC database customizations based on the provided params.

    Each setting follows honest boolean semantics:

    - ``"TRUE"``  → enable (upsert ``'on'`` in pgstac_settings)
    - ``"FALSE"`` → disable (delete from pgstac_settings, reverting to pgstac default)
    - absent      → no-op (the database is left exactly as-is)

    This means the flags are safe to use as true booleans, and upgrading without
    changing config never silently alters a manually-managed setting.

    ref: https://github.com/stac-utils/pgstac/blob/main/docs/src/pgstac.md
    """
    if "context" in params:
        _apply_pgstac_setting(cursor, "context", _is_enabled(params, "context"))

    if "mosaic_index" in params:
        if _is_enabled(params, "mosaic_index"):
            cursor.execute(
                sql.SQL(
                    "CREATE INDEX IF NOT EXISTS searches_mosaic ON searches ((true)) "
                    "WHERE metadata->>'type'='mosaic';"
                )
            )
        else:
            cursor.execute(sql.SQL("DROP INDEX IF EXISTS searches_mosaic;"))

    # Enable automatic spatial/temporal extent updates on item ingest.
    # For large ingests, combine with use_queue=TRUE to reduce transaction overhead.
    if "update_collection_extent" in params:
        _apply_pgstac_setting(
            cursor,
            "update_collection_extent",
            _is_enabled(params, "update_collection_extent"),
        )

    # Enable asynchronous queue processing for extent updates.
    # Requires pg_cron to periodically invoke CALL pgstac.run_queued_queries().
    if "use_queue" in params:
        _apply_pgstac_setting(cursor, "use_queue", _is_enabled(params, "use_queue"))


def unregister_pg_cron(cursor) -> None:
    """Remove the run_queued_queries pg_cron job if it exists.

    Safe to call even if pg_cron is not installed or the job does not exist.

    Args:
        cursor: Database cursor connected to the ``postgres`` database as a superuser.
    """
    cursor.execute(sql.SQL("SELECT 1 FROM pg_extension WHERE extname = 'pg_cron';"))
    if cursor.fetchone():
        cursor.execute(
            sql.SQL(
                "SELECT cron.unschedule(jobid) FROM cron.job "
                "WHERE jobname = 'pgstac-run-queued-queries';"
            )
        )


def set_database_search_path(cursor, db_name: str) -> None:
    """Set the default search_path for all connections to the pgSTAC database.

    Uses ``ALTER DATABASE`` so the setting applies to every session (including
    pg_cron background workers, which start with no ``search_path``). This is
    preferred over per-user or per-connection settings because it is a single
    authoritative place.

    The cursor must be connected as a superuser (the RDS admin user).

    Args:
        cursor: Database cursor connected as a superuser.
        db_name: Name of the pgSTAC database to configure.
    """
    cursor.execute(
        sql.SQL("ALTER DATABASE {db_name} SET search_path TO pgstac, public;").format(
            db_name=sql.Identifier(db_name),
        )
    )


def register_pg_cron(cursor, db_name: str, schedule: str) -> None:
    """Install the pg_cron extension and schedule run_queued_queries.

    pg_cron can only be installed in the ``postgres`` database, so the cursor
    must be connected there as a superuser. ``cron.schedule_in_database`` is
    used to run the job against the pgSTAC database. The job is upserted by
    name so repeated bootstrap runs are safe.

    pg_cron must be listed in ``shared_preload_libraries`` in the RDS parameter
    group before this will succeed.

    Args:
        cursor: Database cursor connected to the ``postgres`` database as a superuser.
        db_name: Name of the pgSTAC database where run_queued_queries will run.
        schedule: Cron schedule expression (e.g. ``"*/5 * * * *"``).
    """
    cursor.execute(sql.SQL("CREATE EXTENSION IF NOT EXISTS pg_cron;"))
    cursor.execute(
        sql.SQL(
            "SELECT cron.schedule_in_database({job_name}, {schedule}, 'CALL pgstac.run_queued_queries();', {db_name});"
        ).format(
            job_name=sql.Literal("pgstac-run-queued-queries"),
            schedule=sql.Literal(schedule),
            db_name=sql.Literal(db_name),
        )
    )


def handler(event, context):
    """Lambda Handler."""
    print(f"Handling {event}")

    physicalResourceId = event.get("PhysicalResourceId") or context.log_stream_name
    if event["RequestType"] not in ["Create", "Update"]:
        return send(
            event,
            context,
            "SUCCESS",
            {"msg": "No action to be taken"},
            physicalResourceId=physicalResourceId,
        )

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

                print(
                    f"Setting default search_path for '{eoapi_params['dbname']}' database..."
                )
                set_database_search_path(
                    cursor=cur,
                    db_name=eoapi_params["dbname"],
                )

                if "use_queue" in params:
                    if _is_enabled(params, "use_queue"):
                        schedule = params.get(
                            "pg_cron_schedule", DEFAULT_PG_CRON_SCHEDULE
                        )
                        print(
                            f"Scheduling pg_cron job 'pgstac-run-queued-queries' "
                            f"with schedule '{schedule}'..."
                        )
                        register_pg_cron(
                            cursor=cur,
                            db_name=eoapi_params["dbname"],
                            schedule=schedule,
                        )
                    else:
                        print(
                            "Removing pg_cron job 'pgstac-run-queued-queries' if present..."
                        )
                        unregister_pg_cron(cursor=cur)

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
        send(
            event,
            context,
            "FAILED",
            {"message": str(e)},
            physicalResourceId=physicalResourceId,
        )
        raise e

    print("Complete.")
    return send(event, context, "SUCCESS", {}, physicalResourceId=physicalResourceId)
