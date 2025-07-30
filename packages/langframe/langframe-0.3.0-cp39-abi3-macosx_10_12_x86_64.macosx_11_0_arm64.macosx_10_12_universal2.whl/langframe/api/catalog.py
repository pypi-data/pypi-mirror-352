from typing import List

from langframe._backends import BaseCatalog
from langframe.api.types import Schema
from pydantic import ConfigDict, validate_call


class Catalog:
    """
    Entry point for catalog operations.

    The Catalog provides methods to interact with and manage database tables,
    including listing available tables, describing table schemas, and dropping tables.
    """

    def __init__(self, catalog: BaseCatalog):
        self.catalog = catalog

    @validate_call(config=ConfigDict(strict=True))
    def does_catalog_exist(self, catalog_name: str) -> bool:
        """
        Checks if a catalog with the specified name exists.

        Args:
            catalog_name (str): Name of the catalog to check.

        Returns:
            bool: True if the catalog exists, False otherwise.

        Example:
            >>> session.catalog.does_catalog_exist('my_catalog')
            True
        """
        return self.catalog.does_catalog_exist(catalog_name)

    def get_current_catalog(self) -> str:
        """
        Returns the name of the current catalog.

        Returns:
            str: The name of the current catalog.

        Example:
            >>> session.catalog.get_current_catalog()
            'default'
        """
        return self.catalog.get_current_catalog()

    @validate_call(config=ConfigDict(strict=True))
    def set_current_catalog(self, catalog_name: str) -> None:
        """
        Sets the current catalog.

        Args:
            catalog_name (str): Name of the catalog to set as current.

        Raises:
            ValueError: If the specified catalog doesn't exist.

        Example:
            >>> session.catalog.set_current_catalog('my_catalog')
        """
        self.catalog.set_current_catalog(catalog_name)

    def list_catalogs(self) -> List[str]:
        """
        Returns a list of available catalogs.

        Returns:
            List[str]: A list of catalog names available in the system.
            Returns an empty list if no catalogs are found.

        Example:
            >>> session.catalog.list_catalogs()
            ['default', 'my_catalog', 'other_catalog']
        """
        return self.catalog.list_catalogs()

    @validate_call(config=ConfigDict(strict=True))
    def does_database_exist(self, database_name: str) -> bool:
        """
        Checks if a database with the specified name exists.

        Args:
            database_name (str): Fully qualified or relative database name to check.

        Returns:
            bool: True if the database exists, False otherwise.

        Example:
            >>> session.catalog.does_database_exist('my_database')
            True
        """
        return self.catalog.does_database_exist(database_name)

    def get_current_database(self) -> str:
        """
        Returns the name of the current database in the current catalog.

        Returns:
            str: The name of the current database.

        Example:
            >>> session.catalog.get_current_database()
            'default'
        """
        return self.catalog.get_current_database()

    @validate_call(config=ConfigDict(strict=True))
    def set_current_database(self, database_name: str) -> None:
        """
        Sets the current database.
        Args:
            database_name (str): Fully qualified or relative database name to set as current.

        Raises:
            ValueError: If the specified database doesn't exist.

        Example:
            >>> session.catalog.set_current_database('my_database')
        """
        self.catalog.set_current_database(database_name)

    def list_databases(self) -> List[str]:
        """
        Returns a list of databases in the current catalog.

        Returns:
            List[str]: A list of database names in the current catalog.
            Returns an empty list if no databases are found.

        Example:
            >>> session.catalog.list_databases()
            ['default', 'my_database', 'other_database']
        """
        return self.catalog.list_databases()

    @validate_call(config=ConfigDict(strict=True))
    def create_database(
        self, database_name: str, ignore_if_exists: bool = True
    ) -> bool:
        """
        Creates a new database.

        Args:
            database_name (str): Fully qualified or relative database name to create.
            ignore_if_exists (bool, optional): If True, return False when the database
                already exists. If False, raise an error when the database already exists.
                Defaults to True.

        Raises:
            ValueError: If the database already exists and ignore_if_exists is False,
                or if there's another error during the create operation.

        Returns:
            bool: True if the database was created successfully, False if the database
                already exists and ignore_if_exists is True.

        Example:
            >>> session.catalog.create_database('my_database')
            True
            >>> session.catalog.create_database('my_database', ignore_if_exists=True)
            False
            >>> session.catalog.create_database('my_database', ignore_if_exists=False)
            # Raises ValueError
        """
        return self.catalog.create_database(database_name, ignore_if_exists)

    @validate_call(config=ConfigDict(strict=True))
    def drop_database(
        self,
        database_name: str,
        cascade: bool = False,
        ignore_if_not_exists: bool = True,
    ) -> bool:
        """
        Drops a database.

        Args:
            database_name (str): Fully qualified or relative database name to drop.
            cascade (bool, optional): If True, drop all tables in the database.
                Defaults to False.
            ignore_if_not_exists (bool, optional): If True, silently return if the database
                doesn't exist. If False, raise an error if the database doesn't exist.
                Defaults to True.

        Raises:
            ValueError: If the database does not exist and ignore_if_not_exists is False, if the current database is being dropped, 
                if the database is not empty and cascade is False, or if another error occurs during the drop operation

        Example:
            # Assume 'my_database' does not exist
            >>> session.catalog.drop_database('my_database')
            # returns False
            >>> session.catalog.drop_database('my_database', ignore_if_not_exists=False)
            # Raises ValueError
        """
        return self.catalog.drop_database(database_name, cascade, ignore_if_not_exists)

    @validate_call(config=ConfigDict(strict=True))
    def does_table_exist(self, table_name: str) -> bool:
        """
        Checks if a table with the specified name exists.

        Args:
            table_name (str): Fully qualified or relative table name to check.

        Returns:
            bool: True if the table exists, False otherwise.

        Example:
            >>> session.catalog.does_table_exist('my_table')
            True
        """
        return self.catalog.does_table_exist(table_name)

    def list_tables(self) -> List[str]:
        """
        Returns a list of tables stored in the current database.

        This method queries the current database to retrieve all available table names.

        Returns:
            List[str]: A list of table names stored in the database.
            Returns an empty list if no tables are found.

        Example:
            >>> session.catalog.list_tables()
            ['table1', 'table2', 'table3']
        """
        return self.catalog.list_tables()

    @validate_call(config=ConfigDict(strict=True))
    def describe_table(self, table_name: str) -> Schema:
        """
        Returns the schema of the specified table.

        Args:
            table_name (str): Fully qualified or relative table name to describe.

        Returns:
            Schema: A schema object describing the table's structure with field names and types.

        Raises:
            ValueError: If the table doesn't exist.

        Example:
            >>> # For a table created with: CREATE TABLE t1 (id int);
            >>> session.catalog.describe_table('t1')
            Schema([
                ColumnField('id', IntegerType),
            ])
        """
        return self.catalog.describe_table(table_name)

    @validate_call(config=ConfigDict(strict=True))
    def drop_table(self, table_name: str, ignore_if_not_exists: bool = True) -> bool:
        """
        Drops the specified table.

        By default this method will return False if the table doesn't exist.

        Args:
            table_name (str): Fully qualified or relative table name to drop.
            ignore_if_not_exists (bool, optional): If True, return False when the table
                doesn't exist. If False, raise an error when the table doesn't exist.
                Defaults to True.

        Returns:
            bool: True if the table was dropped successfully, False if the table
                didn't exist and ignore_if_not_exist is True.

        Raises:
            ValueError: If the table doesn't exist and ignore_if_not_exists is False,
                or if there's another error during the drop operation.

        Example:
            >>> # For an existing table 't1'
            >>> session.catalog.drop_table('t1')
            True

            >>> # For a non-existent table 't2'
            >>> session.catalog.drop_table('t2', ignore_if_not_exists=True)
            False
            >>> session.catalog.drop_table('t2', ignore_if_not_exists=False)
            # Raises ValueError
        """
        return self.catalog.drop_table(table_name, ignore_if_not_exists)

    @validate_call(config=ConfigDict(strict=True))
    def create_table(
        self, table_name: str, schema: Schema, ignore_if_exists: bool = True
    ) -> bool:
        """
        Creates a new table.

        Args:
            table_name (str): Fully qualified or relative table name to create.
            schema (Schema): Schema of the table to create.
            ignore_if_exists (bool, optional): If True, return False when the table
                already exists. If False, raise an error when the table already exists.
                Defaults to True.

        Returns:
            bool: True if the table was created successfully, False if the table
                already exists and ignore_if_exists is True.

        Raises:
            ValueError: If the table already exists and ignore_if_exists is False,
                or if there's another error during the create operation.
        Example:
            >>> session.catalog.create_table('my_table', Schema([
                ColumnField('id', IntegerType),
            ]))
            True
            >>> session.catalog.create_table('my_table', Schema([
                ColumnField('id', IntegerType),
            ]), ignore_if_exists=True)
            False
            >>> session.catalog.create_table('my_table', Schema([
                ColumnField('id', IntegerType),
            ]), ignore_if_exists=False)
            # Raises ValueError
        """
        return self.catalog.create_table(table_name, schema, ignore_if_exists)

    # Spark-style camelCase aliases
    doesCatalogExist = does_catalog_exist
    getCurrentCatalog = get_current_catalog
    setCurrentCatalog = set_current_catalog
    listCatalogs = list_catalogs
    doesDatabaseExist = does_database_exist
    getCurrentDatabase = get_current_database
    setCurrentDatabase = set_current_database
    listTables = list_tables
    describeTable = describe_table
    dropTable = drop_table
    createTable = create_table
