"""
Reader interface for loading DataFrames from external storage systems.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Literal, Optional, Union

from langframe.api.types import Schema
from langframe.api.types.datatypes import _PrimitiveType

if TYPE_CHECKING:
    from langframe.api.dataframe import DataFrame
    from langframe._backends import BaseSessionState

from langframe._logical_plan.plans import FileSource


class DataFrameReader:
    """
    Interface used to load a DataFrame from external storage systems.
    Similar to PySpark's DataFrameReader.
    """

    def __init__(self, session_state: BaseSessionState):
        """
        Creates a DataFrameReader.

        Args:
            session: The session to use for reading
        """
        self._options: Dict[str, Any] = {}
        self._session_state = session_state

    def csv(
        self,
        paths: Union[str, Path, list[Union[str, Path]]],
        schema: Optional[Schema] = None,
        merge_schemas: bool = False,
    ) -> DataFrame:
        """
        Load a DataFrame from one or more CSV files.

        Args:
            paths: A single file path, a glob pattern (e.g., "data/*.csv"), or a list of paths.
            schema: (optional) A complete schema definition of column names and their types.
                - For e.g.:
                    - Schema([ColumnField(name="id", data_type=IntegerType), ColumnField(name="name", data_type=StringType)])
                - If provided, all files must match this schema exactly—all column names must be present, and values must be
                convertible to the specified types. Partial schemas are not allowed.
            merge_schemas: Whether to merge schemas across all files.
                - If True: Column names are unified across files. Missing columns are filled with nulls. Column types are
                inferred and widened as needed.
                - If False (default): Only accepts columns from the first file. Column types from the first file are
                inferred and applied across all files. If subsequent files do not have the same column name and order as the first file, an error is raised.
                - The "first file" is defined as:
                    - The first file in lexicographic order (for glob patterns), or
                    - The first file in the provided list (for lists of paths).

        Notes:
            - The first row in each file is assumed to be a header row.
            - Delimiters (e.g., comma, tab) are automatically inferred.
            - You may specify either `schema` or `merge_schemas=True`, but not both.
            - Any date/datetime columns are cast to strings during ingestion.

        Raises:
            ValueError: If both `schema` and `merge_schemas=True` are provided.
            ValueError: If any path does not end with `.csv`.
            ValueError: If schemas cannot be merged or if there's a schema mismatch when merge_schemas=False.

        Examples:
            >>> df = session.read.csv("file.csv")
            >>> df = session.read.csv("data/*.csv", merge_schemas=True)
            >>> df = session.read.csv(["a.csv", "b.csv"], schema={"id": IntegerType, "value": FloatType})
        """
        if schema is not None and merge_schemas:
            raise ValueError("Cannot provide both schema and merge_schemas=True")
        if schema is not None:
            for col_field in schema.column_fields:
                if not isinstance(
                    col_field.data_type,
                    _PrimitiveType,
                ):
                    raise ValueError(
                        f"Invalid column type for Schema: ColumnField(name='{col_field.name}', data_type={type(col_field.data_type).__name__}). "
                        f"Expected one of: IntegerType, FloatType, DoubleType, BooleanType, or StringType. as data_type"
                        f"Example: Schema([ColumnField(name='id', data_type=IntegerType), ColumnField(name='name', data_type=StringType)])"
                    )
        options = {
            "schema": schema,
            "merge_schemas": merge_schemas,
        }
        return self._read_file(
            paths, file_format="csv", file_extension=".csv", **options
        )

    def parquet(
        self,
        paths: Union[str, Path, list[Union[str, Path]]],
        merge_schemas: bool = False,
    ) -> DataFrame:
        """
        Load a DataFrame from one or more Parquet files.

        Args:
            paths: A single file path, a glob pattern (e.g., "data/*.parquet"), or a list of paths.
            merge_schemas: If True, infers and merges schemas across all files.
                Missing columns are filled with nulls, and differing types are widened to a common supertype.

        Behavior:
            - If `merge_schemas=False` (default), all files must match the schema of the first file exactly.
            Subsequent files must contain all columns from the first file with compatible data types.
            If any column is missing or has incompatible types, an error is raised.
            - If `merge_schemas=True`, column names are unified across all files, and data types are automatically
            widened to accommodate all values.
            - The "first file" is defined as:
                - The first file in lexicographic order (for glob patterns), or
                - The first file in the provided list (for lists of paths).

        Notes:
            - Date and datetime columns are cast to strings during ingestion.

        Raises:
            ValueError: If any file does not have a `.parquet` extension.
            ValueError: If schemas cannot be merged or if there's a schema mismatch when merge_schemas=False.

        Examples:
            >>> df = session.read.parquet("file.parquet")
            >>> df = session.read.parquet("data/*.parquet")
            >>> df = session.read.parquet(["a.parquet", "b.parquet"], merge_schemas=True)
        """
        options = {
            "merge_schemas": merge_schemas,
        }
        return self._read_file(
            paths, file_format="parquet", file_extension=".parquet", **options
        )

    def _read_file(
        self,
        paths: Union[str, Path, list[Union[str, Path]]],
        file_format: Literal["csv", "parquet"],
        file_extension: str,
        **options,
    ) -> DataFrame:
        """
        Internal helper method to read files of a specific format.

        Args:
            paths: Path(s) to the file(s). Can be a single path or a list of paths.
            file_format: Format of the file (e.g., "csv", "parquet").
            file_extension: Expected file extension (e.g., ".csv", ".parquet").
            **options: Additional options to pass to the file reader.

        Returns:
            DataFrame loaded from the specified file(s).

        Raises:
            ValueError: If any path doesn't end with the expected file extension.
            TypeError: If paths is not a string, Path, or list of strings/Paths.
        """
        # Validate paths type
        if not isinstance(paths, (str, Path, list)):
            raise TypeError(
                f"Expected paths to be str, Path, or list, got {type(paths).__name__}"
            )

        # Convert to list if it's a single path
        if isinstance(paths, (str, Path)):
            paths_list = [paths]
        else:
            # Validate each item in the list
            for i, path in enumerate(paths):
                if not isinstance(path, (str, Path)):
                    raise TypeError(
                        f"Expected path at index {i} to be str or Path, got {type(path).__name__}"
                    )
            paths_list = paths

        # Validate file extensions
        for path in paths_list:
            if not str(path).endswith(file_extension):
                raise ValueError(f"Path must end with '{file_extension}': {path}")

        # Convert all paths to strings
        paths_str = [str(p) for p in paths_list]

        logical_node = FileSource(
            paths=paths_str,
            file_format=file_format,
            execution=self._session_state.execution,
            options=options,
        )
        from langframe.api.dataframe import DataFrame

        return DataFrame._from_logical_plan(logical_node, self._session_state.execution)
