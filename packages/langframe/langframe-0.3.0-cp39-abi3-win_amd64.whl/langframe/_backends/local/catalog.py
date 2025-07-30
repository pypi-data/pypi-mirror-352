import logging
import re
import threading
from typing import List, Tuple

import duckdb
import polars as pl
from langframe._utils.misc import generate_unique_arrow_view_name
from langframe._backends import BaseCatalog
from langframe._backends.local.schema_storage import (
    SYSTEM_SCHEMA_NAME,
    SchemaStorage,
)
from langframe.api.types import (
    Schema,
)
from langframe._utils.schema import convert_custom_schema_to_polars_schema

logger = logging.getLogger(__name__)

DB_IGNORE_LIST = [
    "main",
    "information_schema",
    "pg_catalog",
    SYSTEM_SCHEMA_NAME,
]
DEFAULT_CATALOG_NAME = "typedef_default"
DEFAULT_DATABASE_NAME = "typedef_default"


class DuckDBTransaction:
    """
    A context manager for DuckDB transactions.
    """

    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        """Start a transaction when entering the context."""
        logger.debug("Beginning DuckDB transaction")
        self.connection.execute("BEGIN TRANSACTION")
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Commit transaction if no exceptions, otherwise rollback and log error."""
        if exc_type is None:
            # No exception occurred, commit the transaction
            logger.debug("Committing DuckDB transaction")
            self.connection.execute("COMMIT")
        else:
            # Exception occurred, rollback the transaction and log error
            logger.error(
                f"Rolling back DuckDB transaction due to error: {exc_type.__name__}: {str(exc_val)}"
            )
            self.connection.execute("ROLLBACK")
            # Don't suppress the exception
            return False


class LocalCatalog(BaseCatalog):
    """
    A catalog for local execution mode. Implements the BaseCatalog - all table reads and writes should go through this class for unified table name canonicalization.
    A single DuckDB connection is threadsafe, but serializes access to the database. This is ok for local execution mode.
    """

    def __init__(self, connection: duckdb.DuckDBPyConnection):
        self.db_conn: duckdb.DuckDBPyConnection = connection
        self.lock = threading.RLock()
        self.create_database(DEFAULT_DATABASE_NAME)
        self.set_current_database(DEFAULT_DATABASE_NAME)
        self.schema_storage = SchemaStorage(self.db_conn)
        self.schema_storage.initialize_system_schema()

    def does_catalog_exist(self, catalog_name: str) -> bool:
        """Checks if a catalog with the specified name exists."""
        return catalog_name.lower() == DEFAULT_CATALOG_NAME

    def get_current_catalog(self) -> str:
        """Get the name of the current catalog."""
        return DEFAULT_CATALOG_NAME

    def set_current_catalog(self, catalog_name: str) -> None:
        """Set the current catalog."""
        if catalog_name.lower() != DEFAULT_CATALOG_NAME:
            raise ValueError(
                f"Invalid catalog name '{catalog_name}'. Only the default catalog '{DEFAULT_CATALOG_NAME}' is supported in local execution mode."
            )
        # No actual action needed to set the catalog in this local setup

    def list_catalogs(self) -> List[str]:
        """Get a list of all catalogs."""
        return [DEFAULT_CATALOG_NAME]

    def does_database_exist(self, database_name: str) -> bool:
        """Checks if a database with the specified name exists."""
        with self.lock:
            try:
                schema = self.db_conn.execute(
                    "SELECT schema_name FROM duckdb_schemas() WHERE schema_name = ?;",
                    (database_name,),
                ).fetchone()
                return schema is not None
            except Exception as e:
                raise ValueError(f"Failed to check if database exists: {e}") from e

    def get_current_database(self) -> str:
        """Get the name of the current database in the current catalog."""
        with self.lock:
            try:
                return self.db_conn.execute("SELECT current_schema();").fetchone()[0]
            except Exception as e:
                raise ValueError(f"Failed to get current database: {e}") from e

    def create_database(
        self, database_name: str, ignore_if_exists: bool = True
    ) -> bool:
        """Create a new database."""
        with self.lock:
            try:
                if self.does_database_exist(database_name):
                    if ignore_if_exists:
                        return False
                    raise ValueError(f"Database {database_name} already exists!")
                self.db_conn.execute(f'CREATE SCHEMA IF NOT EXISTS "{database_name}";')
                return True
            except Exception as e:
                raise ValueError(
                    f"Failed to create database: {database_name}: {e}"
                ) from e

    def drop_database(
        self,
        database_name: str,
        cascade: bool = False,
        ignore_if_not_exists: bool = True,
    ) -> bool:
        """Drop a database."""
        with self.lock:
            try:
                if database_name == self.get_current_database():
                    raise ValueError(
                        f"Cannot drop the current database '{database_name}'. Switch to another database first."
                    )

                if not self.does_database_exist(database_name):
                    if not ignore_if_not_exists:
                        raise ValueError(f"Database {database_name} does not exist!")
                    return False
                with DuckDBTransaction(self.db_conn):
                    if cascade:
                        self.db_conn.execute(
                            f'DROP SCHEMA IF EXISTS "{database_name}" CASCADE;'
                        )
                    else:
                        self.db_conn.execute(
                            f'DROP SCHEMA IF EXISTS "{database_name}";'
                        )
                    self.schema_storage.delete_database_schemas(database_name)
                return True
            except Exception as e:
                raise ValueError(
                    f"Failed to drop database: {database_name}: {e}"
                ) from e

    def list_databases(self) -> List[str]:
        """Get a list of all databases in the current catalog."""
        with self.lock:
            try:
                schemas = self.db_conn.execute(
                    "SELECT schema_name FROM duckdb_schemas();"
                ).fetchall()
                return [
                    schema[0] for schema in schemas if schema[0] not in DB_IGNORE_LIST
                ]
            except Exception as e:
                raise ValueError(f"Failed to list databases: {e}") from e

    def set_current_database(self, database_name: str) -> None:
        """Set the current database in the current catalog."""
        with self.lock:
            try:
                if not self.does_database_exist(database_name):
                    raise ValueError(f"Database {database_name} does not exist!")
                self.db_conn.execute(f'USE "{database_name}";')
            except Exception as e:
                raise ValueError(f"Failed to set current database: {e}") from e

    def does_table_exist(self, table_name: str) -> bool:
        """Checks if a table with the specified name exists."""
        with self.lock:
            try:
                database_name, simple_table_name = self._parse_table_name(table_name)
                table = self.db_conn.execute(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = ? AND table_name = ?;",
                    (database_name, simple_table_name),
                ).fetchone()
                return table is not None
            except Exception as e:
                raise ValueError(f"Failed to check if table exists: {e}") from e

    def list_tables(self) -> List[str]:
        """Get a list of all tables in the current database."""
        with self.lock:
            try:
                result = self.db_conn.execute(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = ? AND table_type = 'BASE TABLE'
                    """,
                    (self.get_current_database(),),
                )
                result_list = result.fetchall()

                if len(result_list) > 0:
                    return [str(element[0]) for element in result_list]
                return []
            except Exception as e:
                raise ValueError(
                    f"Failed to list tables in database '{self.get_current_database()}': {e}"
                ) from e

    def describe_table(self, table_name: str) -> Schema:
        """Get the schema of the specified table."""
        with self.lock:
            try:
                database_name, simple_table_name = self._parse_table_name(table_name)
                maybe_schema = self.schema_storage.get_schema(
                    database_name, simple_table_name
                )
                if maybe_schema is None:
                    raise ValueError(f"Table '{table_name}' does not exist!")
                return maybe_schema
            except Exception as e:
                raise ValueError(f"Failed to describe table: {table_name}: {e}") from e

    def drop_table(self, table_name: str, ignore_if_not_exists: bool = True) -> bool:
        """Drop a table."""
        with self.lock:
            try:
                if not self.does_table_exist(table_name):
                    if not ignore_if_not_exists:
                        raise ValueError(f"Table {table_name} does not exist!")
                    return False
                database_name, simple_table_name = self._parse_table_name(table_name)
                with DuckDBTransaction(self.db_conn):
                    sql = f"DROP TABLE IF EXISTS {self._build_qualified_table_name(database_name, simple_table_name)}"
                    self.db_conn.execute(sql)
                    self.schema_storage.delete_schema(database_name, simple_table_name)
                return True
            except Exception as e:
                raise ValueError(f"Failed to drop table: {table_name}: {e}") from e

    def create_table(
        self, table_name: str, schema: Schema, ignore_if_exists: bool = True
    ) -> bool:
        """Create a new table."""
        temp_view_name = generate_unique_arrow_view_name()
        with self.lock:
            try:
                if self.does_table_exist(table_name):
                    if not ignore_if_exists:
                        raise ValueError(f"Table {table_name} already exists!")
                    return False
                polars_schema = convert_custom_schema_to_polars_schema(schema)
                database_name, simple_table_name = self._parse_table_name(table_name)
                with DuckDBTransaction(self.db_conn):
                    self.db_conn.register(
                        temp_view_name, pl.DataFrame(schema=polars_schema)
                    )
                    # trunk-ignore-begin(bandit/B608): No major risk of SQL injection here, because queries run on a client side DuckDB instance.
                    self.db_conn.execute(
                        f"CREATE TABLE IF NOT EXISTS {self._build_qualified_table_name(database_name, simple_table_name)} AS SELECT * FROM {temp_view_name} WHERE 1=0"
                    )
                    self.schema_storage.save_schema(
                        database_name, simple_table_name, schema
                    )
                return True
            except Exception as e:
                raise ValueError(f"Failed to create table: {table_name}: {e}") from e
            finally:
                self.db_conn.execute(f"DROP VIEW IF EXISTS {temp_view_name}")
                # trunk-ignore-end(bandit/B608)

    def write_df_to_table(self, df: pl.DataFrame, table_name: str, schema: Schema):
        """Write a Polars dataframe to a table in the current database."""
        temp_view_name = generate_unique_arrow_view_name()
        with self.lock:
            try:
                database_name, bare_table_name = self._parse_table_name(table_name)
                # trunk-ignore-begin(bandit/B608)
                with DuckDBTransaction(self.db_conn):
                    self.db_conn.register(temp_view_name, df)
                    self.db_conn.execute(
                        f"CREATE TABLE IF NOT EXISTS {self._build_qualified_table_name(database_name, bare_table_name)} AS SELECT * FROM {temp_view_name}"
                    )
                    self.schema_storage.save_schema(
                        database_name, bare_table_name, schema
                    )
            except Exception as e:
                raise ValueError(
                    f"Failed to create table and write dataframe: {table_name}: {e}"
                ) from e
            finally:
                self.db_conn.execute(f"DROP VIEW IF EXISTS {temp_view_name}")
            # trunk-ignore-end(bandit/B608)

    def insert_df_to_table(self, df: pl.DataFrame, table_name: str, schema: Schema):
        """Insert a Polars dataframe into a table in the current database."""
        temp_view_name = generate_unique_arrow_view_name()
        with self.lock:
            if self.does_table_exist(table_name):
                if self.describe_table(table_name) != schema:
                    raise ValueError(
                        f"Table '{table_name}' already exists with a different schema!\n"
                        f"Existing schema: {self.describe_table(table_name)}\n"
                        f"New schema: {schema}\n"
                        "To replace the existing table, use mode='overwrite'."
                    )
            try:
                database_name, bare_table_name = self._parse_table_name(table_name)
                # trunk-ignore-begin(bandit/B608)
                self.db_conn.register(temp_view_name, df)
                self.db_conn.execute(
                    f"INSERT INTO {self._build_qualified_table_name(database_name, bare_table_name)} SELECT * FROM {temp_view_name}"
                )
            except Exception as e:
                raise ValueError(
                    f"Failed to insert dataframe into table: {table_name}: {e}"
                ) from e
            finally:
                self.db_conn.execute(f"DROP VIEW IF EXISTS {temp_view_name}")
            # trunk-ignore-end(bandit/B608)

    def replace_table_with_df(self, df: pl.DataFrame, table_name: str, schema: Schema):
        """Replace a table in the current database with a Polars dataframe."""
        temp_view_name = generate_unique_arrow_view_name()
        with self.lock:
            try:
                database_name, bare_table_name = self._parse_table_name(table_name)
                # trunk-ignore-begin(bandit/B608)
                with DuckDBTransaction(self.db_conn):
                    self.db_conn.register(temp_view_name, df)
                    self.db_conn.execute(
                        f"CREATE OR REPLACE TABLE {self._build_qualified_table_name(database_name, bare_table_name)} AS SELECT * FROM {temp_view_name}"
                    )
                    self.schema_storage.save_schema(
                        database_name, bare_table_name, schema
                    )
            except Exception as e:
                raise ValueError(f"Failed to overwrite table: {table_name}: {e}") from e
            finally:
                self.db_conn.execute(f"DROP VIEW IF EXISTS {temp_view_name}")
        # trunk-ignore-end(bandit/B608)

    def read_df_from_table(self, table_name: str) -> pl.DataFrame:
        """Read a Polars dataframe from a DuckDB table in the current database."""
        database_name, bare_table_name = self._parse_table_name(table_name)
        try:
            # trunk-ignore-begin(bandit/B608)
            return self.db_conn.execute(
                f"SELECT * FROM {self._build_qualified_table_name(database_name, bare_table_name)}"
            ).pl()
            # trunk-ignore-end(bandit/B608)
        except Exception as e:
            raise ValueError(
                f"Failed to read dataframe from table: {table_name}: {e}"
            ) from e

    def _build_qualified_table_name(
        self, database_name: str, bare_table_name: str
    ) -> str:
        return f'"{database_name}"."{bare_table_name}"'

    def _parse_table_name(self, table_name: str) -> Tuple[str, str]:
        """
        Parse a table name into database and table components,
        handling DuckDB's naming conventions.

        Args:
            table_name: The table name string to parse.
                Examples:
                    - "table"
                    - "schema.table"
                    - "catalog.schema.table"
                    - '"table.with.dots"'
                    - '"schema.table".name'
                    - '"catalog name"."schema name"."table name"'

        Returns:
            A tuple containing (schema_name, table_name).
        Raises:
            ValueError: For invalid table name formats.
        """
        # Regex pattern to match quoted identifiers
        quoted_pattern = r'"([^"]*)"'
        quoted_parts = re.findall(quoted_pattern, table_name)
        table_name_no_quotes = re.sub(quoted_pattern, "QUOTED_PART", table_name)
        parts = table_name_no_quotes.split(".")

        restored_parts = []
        part_index = 0
        for part in parts:
            if part == "QUOTED_PART":
                restored_parts.append(f'"{quoted_parts[part_index]}"')
                part_index += 1
            else:
                restored_parts.append(part)
        db_name = self.get_current_database()
        simple_table_name = table_name

        if len(restored_parts) == 1:
            simple_table_name = restored_parts[0]
        elif len(restored_parts) == 2:
            db_name, simple_table_name = restored_parts
        elif len(restored_parts) == 3:
            catalog_name, db_name, simple_table_name = restored_parts
            if catalog_name.lower() != DEFAULT_CATALOG_NAME:
                raise ValueError(
                    f"Invalid catalog name '{catalog_name}'. Only '{DEFAULT_CATALOG_NAME}' is supported in local execution mode."
                )
        else:
            raise ValueError(f"Invalid table name format: {table_name}")

        return db_name, simple_table_name
