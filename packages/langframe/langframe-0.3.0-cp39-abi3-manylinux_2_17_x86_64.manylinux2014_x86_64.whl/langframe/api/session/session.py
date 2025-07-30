"""
Main session class for interacting with the DataFrame API.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

import pandas as pd
import polars as pl
from langframe._logical_plan.plans import InMemorySource, TableSource
from langframe.api.dataframe import DataFrame
from langframe.api.io.reader import DataFrameReader
from langframe._backends.base import BaseSessionState
from langframe._backends.local.session_state import LocalSessionState


if TYPE_CHECKING:
    from langframe.api.catalog import Catalog

from langframe.api.session.config import SessionConfig
from pydantic import ConfigDict, validate_call

DataLike = Union[
    pl.DataFrame,
    pd.DataFrame,
    Dict[str, List[Any]],
    List[Dict[str, Any]],
    List[List[Any]],
]


class Session:
    """
    The entry point to programming with the DataFrame API.
    Similar to PySpark's SparkSession.
    """

    app_name: str
    _session_state: BaseSessionState
    _reader: DataFrameReader

    def __new__(cls):
        if cls is Session:
            raise TypeError(
                "Direct construction of Session is not allowed. Use Session.get_or_create() to create a Session."
            )
        return super().__new__(cls)

    @classmethod
    def get_or_create(
        cls,
        config: SessionConfig,
    ) -> Session:
        """
        Gets an existing Session or creates a new one with the configured settings.

        Returns:
            A Session instance configured with the provided settings
        """

        if config.remote:
            raise NotImplementedError("Remote sessions are not yet implemented")

        from langframe._backends import LocalSessionManager

        return LocalSessionManager().get_or_create_session(config)

    @classmethod
    def _create_local_session(
        cls,
        config: SessionConfig,
    ) -> Session:
        """Get or create a local session"""
        session = super().__new__(cls)
        session.app_name = config.app_name
        session._session_state = LocalSessionState(config)
        session._reader = DataFrameReader(session._session_state)
        return session

    @property
    def read(self) -> DataFrameReader:
        """
        Returns a DataFrameReader that can be used to read data in as a DataFrame.

        Returns:
            DataFrameReader: A reader interface to read data into DataFrame

        Raises:
            RuntimeError: If the session has been stopped
        """
        return self._reader

    @property
    def catalog(self) -> Catalog:
        """
        Interface for catalog operations on the Session.
        """
        from langframe.api.catalog import Catalog

        return Catalog(self._session_state.catalog)

    def create_dataframe(
        self,
        data: DataLike,
        column_names: Optional[List[str]] = None,
    ) -> DataFrame:
        """
        Create a DataFrame from a variety of Python-native data formats.

        Args:
            data (DataLike): Input data. Must be one of the following:
                - Polars DataFrame
                - Pandas DataFrame
                - dict of column_name -> list of values
                - list of dicts (each dict representing a row)
                - list of lists or tuples (each representing a row), along with `column_names`
            column_names (Optional[List[str]]): Required only if `data` is a list of lists/tuples.
                Specifies the column names for the resulting DataFrame.

        Returns:
            DataFrame: A new DataFrame instance

        Raises:
            ValueError: If the input format is unsupported or inconsistent with provided column names.

        Examples:
            >>> session.create_dataframe(pl.DataFrame(...))
            >>> session.create_dataframe(pd.DataFrame(...))
            >>> session.create_dataframe({"col1": [1, 2], "col2": ["a", "b"]})
            >>> session.create_dataframe([{"col1": 1, "col2": "a"}, {"col1": 2, "col2": "b"}])
            >>> session.create_dataframe([[1, "a"], [2, "b"]], column_names=["col1", "col2"])
        """

        def to_polars(data: Any) -> pl.DataFrame:
            if isinstance(data, pl.DataFrame):
                return data
            elif isinstance(data, pd.DataFrame):
                return pl.from_pandas(data)
            elif isinstance(data, dict):
                return pl.DataFrame(data)
            # else list
            else:
                if not data:
                    raise ValueError("Cannot create DataFrame from empty list")

                if isinstance(data[0], dict):
                    return pl.DataFrame(data)

                if isinstance(data[0], (list, tuple)):
                    if not column_names:
                        raise ValueError(
                            "Schema must be provided when data is a list of lists"
                        )
                    if not isinstance(column_names, (list, tuple)):
                        raise ValueError("Schema must be a list of column names")
                    if len(column_names) != len(data[0]):
                        raise ValueError("Schema length does not match row length")
                    columns = {
                        name: [row[i] for row in data]
                        for i, name in enumerate(column_names)
                    }
                    return pl.DataFrame(columns)

        pl_df = to_polars(data)

        return DataFrame._from_logical_plan(
            InMemorySource(pl_df), self._session_state.execution
        )

    def table(self, table_name: str) -> DataFrame:
        """
        Returns the specified table as a DataFrame.

        Args:
            table_name: Name of the table

        Returns:
            DataFrame: Table as a DataFrame
        """
        if not self._session_state.catalog.does_table_exist(table_name):
            raise ValueError(f"Table {table_name} does not exist")
        return DataFrame._from_logical_plan(
            TableSource(table_name, self._session_state.catalog),
            self._session_state.execution,
        )

    def sql(self, query: str) -> DataFrame:
        """
        WARNING: Unimplemented.
        Executes a SQL query and returns the result as a DataFrame.

        Args:
            query: SQL query to execute

        Returns:
            DataFrame: Query result as a DataFrame
        """
        # todo(rohitrastogi): Figure out plan repr for sql. Will likely need a
        # SQL parser to convert the query into a logical plan, maybe SQLGlot can help with this.
        raise NotImplementedError("SQL queries are not yet implemented")

    def stop(self):
        """Stops the session and closes all connections."""
        self._session_state.stop()


Session.create_dataframe = validate_call(
    config=ConfigDict(strict=True, arbitrary_types_allowed=True)
)(Session.create_dataframe)
Session.createDataFrame = Session.create_dataframe
Session.get_or_create = validate_call(config=ConfigDict(strict=True))(
    Session.get_or_create
)
Session.getOrCreate = Session.get_or_create
Session.table = validate_call(config=ConfigDict(strict=True))(Session.table)
Session.sql = validate_call(config=ConfigDict(strict=True))(Session.sql)
