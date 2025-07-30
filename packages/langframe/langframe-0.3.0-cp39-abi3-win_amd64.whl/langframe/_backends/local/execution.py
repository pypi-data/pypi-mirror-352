from __future__ import annotations

import json
import logging
import os
from typing import TYPE_CHECKING, Any, Dict, Literal, Optional, Tuple

import duckdb
import polars as pl
from langframe._logical_plan import LogicalPlan
from langframe.api.metrics import QueryMetrics
from langframe._backends.local.transpiler import convert_logical_plan_to_physical_plan
from langframe._backends import BaseExecution
from langframe._backends.local.lineage import LocalLineage
from langframe._utils.schema import convert_polars_schema_to_custom_schema
from langframe.api.types.datatypes import (
    BooleanType,
    DoubleType,
    FloatType,
    IntegerType,
    StringType,
)
from langframe.api.types.schema import Schema

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from langframe._backends import LocalSessionState


class LocalExecution(BaseExecution):
    session_state: LocalSessionState

    def __init__(self, session_state: LocalSessionState):
        self.session_state = session_state

    def collect(
        self, plan: LogicalPlan, n: Optional[int] = None
    ) -> Tuple[pl.DataFrame, QueryMetrics]:
        """Execute a logical plan and return a Polars DataFrame and query metrics."""
        self.session_state._check_active()
        physical_plan = convert_logical_plan_to_physical_plan(plan, self.session_state)
        df, metrics = physical_plan.execute()
        if n is not None:
            df = df.limit(n)
        return df, metrics

    def show(self, plan: LogicalPlan, n: int = 10) -> Tuple[str, QueryMetrics]:
        """Execute a logical plan and return a string representation of the sample rows of the DataFrame and query metrics."""
        self.session_state._check_active()
        physical_plan = convert_logical_plan_to_physical_plan(plan, self.session_state)
        df, metrics = physical_plan.execute()
        with pl.Config(
            fmt_str_lengths=1000,
            set_tbl_hide_dataframe_shape=True,
            set_tbl_hide_column_data_types=True,
            tbl_rows=min(n, df.height),
        ):
            output = str(df)
        return output, metrics

    def count(self, plan: LogicalPlan) -> Tuple[int, QueryMetrics]:
        """Execute a logical plan and return the number of rows in the DataFrame and query metrics."""
        self.session_state._check_active()
        physical_plan = convert_logical_plan_to_physical_plan(plan, self.session_state)
        df, metrics = physical_plan.execute()
        return df.shape[0], metrics

    def build_lineage(self, plan: LogicalPlan) -> LocalLineage:
        """Build a lineage graph from a logical plan."""
        self.session_state._check_active()
        physical_plan = convert_logical_plan_to_physical_plan(plan, self.session_state)
        lineage_graph = physical_plan.build_lineage()
        return LocalLineage(lineage_graph, self.session_state)

    def save_as_table(
        self,
        logical_plan: LogicalPlan,
        table_name: str,
        mode: Literal["error", "append", "overwrite", "ignore"],
    ) -> QueryMetrics:
        """Execute the logical plan and save the result as a table in the current database."""
        self.session_state._check_active()
        table_exists = self.session_state.catalog.does_table_exist(table_name)

        if table_exists:
            if mode == "error":
                raise ValueError(f"Table {table_name} already exists!")
            if mode == "ignore":
                logger.warning(f"Table {table_name} already exists, ignoring write.")
                return QueryMetrics()
            if mode == "append":
                saved_schema = self.session_state.catalog.describe_table(table_name)
                plan_schema = logical_plan.schema()
                if saved_schema != plan_schema:
                    raise ValueError(
                        f"Table '{table_name}' already exists with a different schema!\n"
                        f"Existing schema: {saved_schema}\n"
                        f"New schema: {plan_schema}\n"
                        "To replace the existing table, use mode='overwrite'."
                    )
        physical_plan = convert_logical_plan_to_physical_plan(
            logical_plan, self.session_state
        )
        _, metrics = physical_plan.execute()

        return metrics

    def save_to_file(
        self,
        logical_plan: LogicalPlan,
        file_path: str,
        mode: Literal["error", "overwrite", "ignore"] = "error",
    ) -> QueryMetrics:
        """Execute the logical plan and save the result to a file."""
        self.session_state._check_active()

        file_exists = os.path.exists(file_path)
        if mode == "error" and file_exists:
            raise ValueError(f"File {file_path} already exists and mode is 'error'")
        if mode == "ignore" and file_exists:
            logger.warning(f"File {file_path} already exists, ignoring write.")
            return QueryMetrics()

        physical_plan = convert_logical_plan_to_physical_plan(
            logical_plan, self.session_state
        )
        _, metrics = physical_plan.execute()
        return metrics

    def infer_schema_from_csv(
        self, paths: list[str], **options: Dict[str, Any]
    ) -> Schema:
        """Infer the schema of a CSV file."""
        self.session_state._check_active()
        query = self._build_read_csv_query(paths, True, **options)
        return self._infer_schema_from_file_scan_query(query)

    def infer_schema_from_parquet(
        self, paths: list[str], **options: Dict[str, Any]
    ) -> Schema:
        """Infer the schema of a Parquet file."""
        self.session_state._check_active()
        query = self._build_read_parquet_query(paths, True, **options)
        return self._infer_schema_from_file_scan_query(query)

    def _infer_schema_from_file_scan_query(self, query: str) -> Schema:
        """Helper method to infer schema from a DuckDB file scan query."""
        duckdb_conn = duckdb.connect()
        duckdb_conn.execute("PRAGMA disable_optimizer")
        arrow_table = duckdb_conn.execute(query).arrow()
        polars_schema = pl.from_arrow(arrow_table).schema
        return convert_polars_schema_to_custom_schema(polars_schema)

    def _build_read_csv_query(
        self, paths: list[str], infer_schema: bool, **options: Dict[str, Any]
    ) -> str:
        """Helper method to build a DuckDB read CSV query."""
        merge_schemas = options.get("merge_schemas", False)
        schema: Optional[Schema] = options.get("schema", None)
        duckdb_schema: Dict[str, str] = {}
        paths_str = "', '".join(paths)
        # trunk-ignore-begin(bandit/B608)
        if schema:
            for col_field in schema.column_fields:
                duckdb_type: str | None = None
                if col_field.data_type == StringType:
                    duckdb_type = "VARCHAR"
                elif col_field.data_type == IntegerType:
                    duckdb_type = "BIGINT"
                elif col_field.data_type == FloatType:
                    duckdb_type = "FLOAT"
                elif col_field.data_type == DoubleType:
                    duckdb_type = "DOUBLE"
                elif col_field.data_type == BooleanType:
                    duckdb_type = "BOOLEAN"
                else:
                    raise ValueError(f"Unsupported data type: {col_field.data_type}")
                duckdb_schema[col_field.name] = duckdb_type
            duckdb_schema_string = json.dumps(duckdb_schema).replace('"', "'")
            query = f"SELECT * FROM read_csv(['{paths_str}'], columns = {duckdb_schema_string})"
        elif merge_schemas:
            query = f"SELECT * FROM read_csv(['{paths_str}'], union_by_name=true)"
        else:
            query = f"SELECT * FROM read_csv(['{paths_str}'])"
        if infer_schema:
            query = f"{query} WHERE 1=0"
        # trunk-ignore-end(bandit/B608)
        return query

    def _build_read_parquet_query(
        self, paths: list[str], infer_schema: bool, **options: Dict[str, Any]
    ) -> str:
        """Helper method to build a DuckDB read Parquet query."""
        merge_schemas = options.get("merge_schemas", False)
        paths_str = "', '".join(paths)
        # trunk-ignore-begin(bandit/B608)
        if merge_schemas:
            query = f"SELECT * FROM read_parquet(['{paths_str}'], union_by_name=true)"
        else:
            query = f"SELECT * FROM read_parquet(['{paths_str}'])"
        if infer_schema:
            query = f"{query} WHERE 1=0"
        # trunk-ignore-end(bandit/B608)
        return query
