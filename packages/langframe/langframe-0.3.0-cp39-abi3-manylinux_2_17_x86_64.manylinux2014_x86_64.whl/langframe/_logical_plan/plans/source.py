from __future__ import annotations

from typing import TYPE_CHECKING, List, Literal, Optional

import polars as pl
from langframe._logical_plan.plans.base import LogicalPlan
from langframe.api.types import Schema
from langframe._utils.schema import convert_polars_schema_to_custom_schema

if TYPE_CHECKING:
    from langframe._backends import BaseCatalog
    from langframe._backends import BaseExecution


class InMemorySource(LogicalPlan):
    def __init__(self, source: pl.DataFrame):
        self._source = source
        super().__init__()

    def children(self) -> List[LogicalPlan]:
        return []

    def _build_schema(self) -> Schema:
        return convert_polars_schema_to_custom_schema(self._source.schema)

    def _repr(self) -> str:
        return f"InMemorySource({self.schema()})"

    def with_children(self, children: List[LogicalPlan]) -> LogicalPlan:
        if len(children) != 0:
            raise ValueError("Source must have no children")
        result = InMemorySource(self._source)
        result.set_cache_info(self.cache_info)
        return result


class FileSource(LogicalPlan):
    def __init__(
        self,
        paths: list[str],
        file_format: Literal["csv", "parquet"],
        execution: BaseExecution,
        options: Optional[dict] = None,
    ):
        """
        A lazy FileSource that stores the file path, file format, options, and immediately
        infers the schema using the given session state.
        """
        self._paths = paths
        self._file_format = file_format
        self._options = options or {}
        self._execution = execution
        super().__init__()

    def _build_schema(self) -> Schema:
        """
        Uses DuckDB (via the session state) to perform a minimal read (LIMIT 0)
        and obtain the schema from the file.
        """
        if self._file_format == "csv":
            try:
                return self._execution.infer_schema_from_csv(
                    self._paths, **self._options
                )
            except Exception as e:
                if self._options.get("schema", None):
                    raise ValueError(
                        f"Schema mismatch: The provided schema does not match the structure of the CSV files. "
                        f"Please verify that all required columns are present and correctly typed.\n\n"
                        f"Details: {e}"
                    ) from e
                elif self._options.get("merge_schemas", False):
                    raise ValueError(
                        f"Inconsistent CSV schemas: The files appear to have different structures. "
                        f"If this is expected, try setting merge_schemas=True to allow automatic merging.\n\n"
                        f"Details: {e}"
                    ) from e
                else:
                    raise ValueError(
                        f"Failed to infer schema from CSV files. Details: {e}"
                    ) from e

        elif self._file_format == "parquet":
            try:
                return self._execution.infer_schema_from_parquet(
                    self._paths, **self._options
                )
            except Exception as e:
                if self._options.get("merge_schemas", False):
                    raise ValueError(
                        f"Inconsistent Parquet schemas: The files appear to have different structures. "
                        f"If this is expected, try setting merge_schemas=True to allow automatic merging.\n\n"
                        f"Details: {e}"
                    ) from e
                else:
                    raise ValueError(
                        f"Failed to infer schema from Parquet files. Details: {e}"
                    ) from e

    def children(self) -> List[LogicalPlan]:
        return []

    def _repr(self) -> str:
        return f"FileSource(paths={self._paths}, format={self._file_format})"

    def with_children(self, children: List[LogicalPlan]) -> LogicalPlan:
        if len(children) != 0:
            raise ValueError("Source must have no children")
        result = FileSource(
            self._paths, self._file_format, self._execution, self._options
        )
        result.set_cache_info(self.cache_info)
        return result


class TableSource(LogicalPlan):
    def __init__(self, table_name: str, catalog: BaseCatalog):
        self._table_name = table_name
        self._catalog = catalog
        super().__init__()

    def _build_schema(self) -> Schema:
        if not self._catalog.does_table_exist(self._table_name):
            raise ValueError(
                f"Cannot read from table {self._table_name} because it does not exist!"
            )
        return self._catalog.describe_table(self._table_name)

    def children(self) -> List[LogicalPlan]:
        return []

    def _repr(self) -> str:
        return f"TableSource(table_name={self._table_name})"

    def with_children(self, children: List[LogicalPlan]) -> LogicalPlan:
        if len(children) != 0:
            raise ValueError("Source must have no children")
        result = TableSource(self._table_name, self._catalog)
        result.set_cache_info(self.cache_info)
        return result
