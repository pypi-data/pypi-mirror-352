from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, List, Literal, Tuple

if TYPE_CHECKING:
    from langframe._backends import LocalSessionState

import polars as pl
from langframe._logical_plan.plans import CacheInfo
from langframe._backends.local.physical_plan import PhysicalPlan
from langframe._backends.local.lineage import OperatorLineage
from langframe.api.types import Schema

logger = logging.getLogger(__name__)


class FileSinkExec(PhysicalPlan):
    """Physical plan node for file sink operations."""

    def __init__(
        self,
        child: PhysicalPlan,
        path: str,
        file_type: str,
        mode: Literal["error", "overwrite", "ignore"],
        cache_info: CacheInfo,
        session_state: LocalSessionState,
    ):
        super().__init__(
            children=[child], cache_info=cache_info, session_state=session_state
        )
        self.path = path
        self.file_type = file_type.lower()
        self.mode = mode

    def _execute(self, child_dfs: List[pl.DataFrame]) -> pl.DataFrame:
        if len(child_dfs) != 1:
            raise ValueError("FileSink expects exactly one child DataFrame")
        file_exists = os.path.exists(self.path)
        if self.mode == "error" and file_exists:
            raise ValueError(f"File {self.path} already exists and mode is 'error'")
        if self.mode == "ignore" and file_exists:
            logger.warning(f"File {self.path} already exists, ignoring write.")
            return pl.DataFrame()

        df = child_dfs[0]
        if self.file_type == "csv":
            df.write_csv(self.path)
        elif self.file_type == "parquet":
            df.write_parquet(self.path)
        else:
            raise ValueError(f"Unsupported file type: {self.file_type}")

        return pl.DataFrame()

    def _build_lineage(
        self,
        leaf_nodes: List[OperatorLineage],
    ) -> Tuple[OperatorLineage, pl.DataFrame]:
        """
        Build the lineage graph for this sink operation.

        Returns:
                A LineageGraph representing the operation
        """
        raise RuntimeError("FileSink does not support lineage")


class DuckDBTableSinkExec(PhysicalPlan):
    """Physical plan node for DuckDB table sink operations."""

    def __init__(
        self,
        child: PhysicalPlan,
        table_name: str,
        mode: Literal["error", "overwrite", "ignore"],
        cache_info: CacheInfo,
        session_state: LocalSessionState,
        schema: Schema,
    ):
        super().__init__(
            children=[child], cache_info=cache_info, session_state=session_state
        )
        self.table_name = table_name
        self.mode = mode
        self.schema = schema

    def _execute(self, child_dfs: List[pl.DataFrame]) -> pl.DataFrame:
        if len(child_dfs) != 1:
            raise ValueError("TableSink expects exactly one child DataFrame")
        df = child_dfs[0]
        table_exists = self.session_state.catalog.does_table_exist(self.table_name)
        if table_exists:
            if self.mode == "error":
                raise ValueError(
                    f"Table {self.table_name} already exists and mode is 'error'"
                )
            if self.mode == "ignore":
                logger.warning(
                    f"Table {self.table_name} already exists, ignoring write."
                )
                return pl.DataFrame()
            if self.mode == "append":
                self.session_state.catalog.insert_df_to_table(
                    df, self.table_name, self.schema
                )
            elif self.mode == "overwrite":
                self.session_state.catalog.replace_table_with_df(
                    df, self.table_name, self.schema
                )
        else:
            self.session_state.catalog.write_df_to_table(
                df, self.table_name, self.schema
            )

        return pl.DataFrame()

    def _build_lineage(
        self,
        leaf_nodes: List[OperatorLineage],
    ) -> Tuple[OperatorLineage, pl.DataFrame]:
        """
        Build the lineage graph for this sink operation.

        Returns:
            A LineageGraph representing the operation
        """
        raise RuntimeError("TableSink does not support lineage")
