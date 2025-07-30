from __future__ import annotations
from typing import TYPE_CHECKING, List, Tuple

import duckdb
import polars as pl
from langframe._backends.local.lineage import OperatorLineage

if TYPE_CHECKING:
    from langframe._backends import LocalSessionState

from langframe._backends.local.physical_plan.base import PhysicalPlan, _with_lineage_uuid


class InMemorySourceExec(PhysicalPlan):
    def __init__(self, df: pl.DataFrame, session_state: LocalSessionState):
        super().__init__(children=[], cache_info=None, session_state=session_state)
        self.df = df

    def _execute(self, child_dfs: List[pl.DataFrame]) -> pl.DataFrame:
        if len(child_dfs) != 0:
            raise ValueError("Unreachable: InMemorySourceExec expects 0 children")

        date_time_columns = _get_date_time_columns(self.df)
        if date_time_columns:
            self.df = _convert_date_time_columns_to_string(self.df, date_time_columns)
        return self.df

    def _build_lineage(
        self,
        leaf_nodes: List[OperatorLineage],
    ) -> Tuple[OperatorLineage, pl.DataFrame]:
        materialize_df = _with_lineage_uuid(self.df)
        source_operator = self._build_source_operator_lineage(materialize_df)
        leaf_nodes.append(source_operator)
        return source_operator, materialize_df


class FileSourceExec(PhysicalPlan):
    def __init__(
        self,
        paths: list[str],
        file_format: str,
        session_state: LocalSessionState,
        options: dict = None,
    ):
        super().__init__(children=[], cache_info=None, session_state=session_state)
        self.path_string = "', '".join(paths)
        self.paths = paths
        self.file_format = file_format
        self.options = options or {}

    def _execute(self, child_dfs: List[pl.DataFrame]) -> pl.DataFrame:
        if child_dfs:
            raise ValueError("Unreachable: SourceExec expects 0 children")

        file_format = self.file_format.lower()
        build_query_fn = {
            "csv": self.session_state.execution._build_read_csv_query,
            "parquet": self.session_state.execution._build_read_parquet_query,
        }.get(file_format)

        if build_query_fn is None:
            raise ValueError(f"Unsupported file format: {self.file_format}")

        query = build_query_fn(self.paths, False, **self.options)
        try:
            arrow_result = duckdb.connect().execute(query).arrow()
        except Exception as e:
            raise ValueError(f"Error reading files. Details: {e}") from e

        df = pl.from_arrow(arrow_result)
        df = _convert_date_time_columns_to_string(df, _get_date_time_columns(df))
        return df

    def _build_lineage(
        self,
        leaf_nodes: List[OperatorLineage],
    ) -> Tuple[OperatorLineage, pl.DataFrame]:
        df = self._execute([])
        materialize_df = _with_lineage_uuid(df)
        source_operator = self._build_source_operator_lineage(materialize_df)
        leaf_nodes.append(source_operator)
        return source_operator, materialize_df


class DuckDBTableSourceExec(PhysicalPlan):
    def __init__(self, table_name: str, session_state: LocalSessionState):
        super().__init__(children=[], cache_info=None, session_state=session_state)
        self.table_name = table_name

    def _execute(self, child_dfs: List[pl.DataFrame]) -> pl.DataFrame:
        if len(child_dfs) != 0:
            raise ValueError("Unreachable: TableSourceExec expects 0 children")
        return self.session_state.catalog.read_df_from_table(self.table_name)

    def _build_lineage(
        self,
        leaf_nodes: List[OperatorLineage],
    ) -> Tuple[OperatorLineage, pl.DataFrame]:
        df = self._execute([])
        materialize_df = _with_lineage_uuid(df)
        source_operator = self._build_source_operator_lineage(materialize_df)
        leaf_nodes.append(source_operator)
        return source_operator, materialize_df


def _convert_date_time_columns_to_string(
    df: pl.DataFrame, date_time_columns: dict[str, pl.DataType]
) -> pl.DataFrame:
    """
    Convert any Date / DateTime columns to a string.
    """
    for col, dtype in date_time_columns.items():
        df = df.with_columns(
            pl.col(col).dt.strftime(_get_date_time_column_format(dtype)).alias(col)
        )
    return df


def _get_date_time_column_format(dtype: pl.DataType) -> str:
    """
    Get the format for the date/time column.
    Note: The formats here are based on what DuckDB supports:
    For date is "yyyy-mm-dd"
    For datetime is "yyyy-mm-dd hh:mm:ss"
    see docs: https://docs.rs/chrono/latest/chrono/format/strftime/index.html
    """
    if dtype == pl.Date:
        return "%F"
    return "%F %T"


def _get_date_time_columns(df: pl.DataFrame) -> dict[str, pl.DataType]:
    """
    Get the names of the Date / DateTime columns.
    """
    return {
        col: df[col].dtype
        for col in df.columns
        if df[col].dtype in [pl.Date, pl.Datetime]
    }
