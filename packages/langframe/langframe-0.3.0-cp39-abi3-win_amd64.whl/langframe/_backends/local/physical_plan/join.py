from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional, Tuple

import polars as pl
from langframe._logical_plan.plans import CacheInfo
from langframe._backends.local.semantic_operators import Join as SemanticJoin
from langframe._backends.local.semantic_operators import SimJoin as SemanticSimJoin
from langframe._backends.local.semantic_operators.sim_join import (
    LEFT_ON_COL_NAME,
    RIGHT_ON_COL_NAME,
    SIMILARITY_SCORE_COL_NAME,
)
from langframe._utils.misc import generate_unique_arrow_view_name
from langframe._backends.local.lineage import OperatorLineage
from langframe.api.types import JoinExampleCollection

if TYPE_CHECKING:
    from langframe._backends import LocalSessionState

from langframe._backends.local.physical_plan.base import PhysicalPlan, _with_lineage_uuid


class JoinExec(PhysicalPlan):
    def __init__(
        self,
        left: PhysicalPlan,
        right: PhysicalPlan,
        query_str: str,
        cache_info: Optional[CacheInfo],
        session_state: LocalSessionState,
    ):
        super().__init__(
            [left, right], cache_info=cache_info, session_state=session_state
        )
        self._query_str = query_str

    def _execute_join_query(
        self, left_df: pl.DataFrame, right_df: pl.DataFrame, query_str: str
    ) -> pl.DataFrame:
        """Execute the join query using DuckDB"""
        db_conn = self.session_state.intermediate_df_client.db_conn
        view_suffix = generate_unique_arrow_view_name()
        db_conn.register(f"left_{view_suffix}", left_df)
        db_conn.register(f"right_{view_suffix}", right_df)
        try:
            arrow_result = db_conn.execute(query_str).arrow()
            return pl.from_arrow(arrow_result)

        finally:
            db_conn.execute(f"DROP VIEW IF EXISTS left_{view_suffix}")
            db_conn.execute(f"DROP VIEW IF EXISTS right_{view_suffix}")

    def _execute(self, child_dfs: List[pl.DataFrame]) -> pl.DataFrame:
        if len(child_dfs) != 2:
            raise ValueError("Unreachable: JoinExec expects 2 children")
        try:
            joined_df = self._execute_join_query(
                child_dfs[0], child_dfs[1], self._query_str
            )
        except Exception as e:
            raise ValueError(
                f"Failed to execute join query: {self._query_str}\nError: {str(e)}"
            ) from e
        return joined_df

    def _build_lineage(
        self,
        leaf_nodes: List[OperatorLineage],
    ) -> Tuple[OperatorLineage, pl.DataFrame]:
        left_operator, left_df = self.children[0]._build_lineage(leaf_nodes)
        right_operator, right_df = self.children[1]._build_lineage(leaf_nodes)

        left_df = left_df.rename({"_uuid": "_left_uuid"})
        right_df = right_df.rename({"_uuid": "_right_uuid"})
        rewritten_query = self._rewrite_join_query()
        try:
            joined_df = self._execute_join_query(left_df, right_df, rewritten_query)
        except Exception as e:
            raise ValueError(
                f"Failed to execute join query: {rewritten_query}\nError: {str(e)}"
            ) from e
        materialize_df = _with_lineage_uuid(joined_df)
        backwards_df_left = materialize_df.select(["_uuid", "_left_uuid"]).rename(
            {"_left_uuid": "_backwards_uuid"}
        )
        backwards_df_right = materialize_df.select(["_uuid", "_right_uuid"]).rename(
            {"_right_uuid": "_backwards_uuid"}
        )

        materialize_df = materialize_df.drop(["_left_uuid", "_right_uuid"])
        operator = self._build_binary_operator_lineage(
            materialize_df=materialize_df,
            left_child=(left_operator, backwards_df_left),
            right_child=(right_operator, backwards_df_right),
        )
        return operator, materialize_df

    # TODO(rohitrastogi): This is a hack to get the lineage join query to work without messing
    # with the planner too much.
    def _rewrite_join_query(self):
        sql_query = self._query_str
        new_columns = "left_df._left_uuid, right_df._right_uuid"
        from_pos = sql_query.lower().find("from")
        new_sql = sql_query[:from_pos] + ", " + new_columns + " " + sql_query[from_pos:]
        return new_sql


class SemanticJoinExec(PhysicalPlan):
    def __init__(
        self,
        left: PhysicalPlan,
        right: PhysicalPlan,
        left_on_name: str,
        right_on_name: str,
        join_instruction: str,
        cache_info: Optional[CacheInfo],
        session_state: LocalSessionState,
        examples: Optional[JoinExampleCollection] = None,
    ):
        super().__init__(
            [left, right], cache_info=cache_info, session_state=session_state
        )
        self.examples = examples
        self.join_instruction = join_instruction
        self.left_on_name = left_on_name
        self.right_on_name = right_on_name

    def _execute(self, child_dfs: List[pl.DataFrame]) -> pl.DataFrame:
        if len(child_dfs) != 2:
            raise ValueError("Unreachable: SemanticJoinExec expects 2 children")

        left_df = child_dfs[0]
        right_df = child_dfs[1]
        return SemanticJoin(
            left_df,
            right_df,
            self.left_on_name,
            self.right_on_name,
            self.join_instruction,
            self.session_state.app_name,
            examples=self.examples,
        ).execute()

    def _build_lineage(
        self,
        leaf_nodes: List[OperatorLineage],
    ) -> Tuple[OperatorLineage, pl.DataFrame]:
        left_operator, left_df = self.children[0]._build_lineage(leaf_nodes)
        right_operator, right_df = self.children[1]._build_lineage(leaf_nodes)

        left_df = left_df.rename({"_uuid": "_left_uuid"})
        right_df = right_df.rename({"_uuid": "_right_uuid"})

        joined_df = self._execute([left_df, right_df])

        materialize_df = _with_lineage_uuid(joined_df)
        backwards_df_left = materialize_df.select(["_uuid", "_left_uuid"]).rename(
            {"_left_uuid": "_backwards_uuid"}
        )
        backwards_df_right = materialize_df.select(["_uuid", "_right_uuid"]).rename(
            {"_right_uuid": "_backwards_uuid"}
        )

        materialize_df = materialize_df.drop(["_left_uuid", "_right_uuid"])
        operator = self._build_binary_operator_lineage(
            materialize_df=materialize_df,
            left_child=(left_operator, backwards_df_left),
            right_child=(right_operator, backwards_df_right),
        )

        return operator, materialize_df


class SemanticSimilarityJoinExec(PhysicalPlan):
    def __init__(
        self,
        left: PhysicalPlan,
        right: PhysicalPlan,
        left_on: str | pl.Expr,
        right_on: str | pl.Expr,
        k: int,
        cache_info: Optional[CacheInfo],
        session_state: LocalSessionState,
        return_similarity_scores: bool = False,
    ):
        super().__init__(
            [left, right], cache_info=cache_info, session_state=session_state
        )
        self.left_on = left_on
        self.right_on = right_on
        self.k = k
        self.return_similarity_scores = return_similarity_scores

    def _execute(self, child_dfs: List[pl.DataFrame]) -> pl.DataFrame:
        if len(child_dfs) != 2:
            raise ValueError(
                "Unreachable: SemanticSimilarityJoinExec expects 2 children"
            )

        left_df, right_df = child_dfs

        # Normalize both join sides to standard column names
        left_df, left_was_expr, left_orig_name = self._normalize_column(
            left_df, self.left_on, LEFT_ON_COL_NAME
        )
        right_df, right_was_expr, right_orig_name = self._normalize_column(
            right_df, self.right_on, RIGHT_ON_COL_NAME
        )

        # TODO(rohitrastogi): Avoid regenerating embeddings if semantic index already exists
        result = SemanticSimJoin(left_df, right_df, self.k).execute()

        if not self.return_similarity_scores:
            result = result.drop(SIMILARITY_SCORE_COL_NAME)

        # Restore original column names or drop temporary columns
        result = self._restore_column(
            result, left_was_expr, left_orig_name, LEFT_ON_COL_NAME
        )
        result = self._restore_column(
            result, right_was_expr, right_orig_name, RIGHT_ON_COL_NAME
        )

        return result

    def _build_lineage(
        self,
        leaf_nodes: List[OperatorLineage],
    ) -> Tuple[OperatorLineage, pl.DataFrame]:
        left_operator, left_df = self.children[0]._build_lineage(leaf_nodes)
        right_operator, right_df = self.children[1]._build_lineage(leaf_nodes)

        left_df = left_df.rename({"_uuid": "_left_uuid"})
        right_df = right_df.rename({"_uuid": "_right_uuid"})

        joined_df = self._execute([left_df, right_df])

        materialize_df = _with_lineage_uuid(joined_df)
        backwards_df_left = materialize_df.select(["_uuid", "_left_uuid"]).rename(
            {"_left_uuid": "_backwards_uuid"}
        )
        backwards_df_right = materialize_df.select(["_uuid", "_right_uuid"]).rename(
            {"_right_uuid": "_backwards_uuid"}
        )

        materialize_df = materialize_df.drop(["_left_uuid", "_right_uuid"])
        operator = self._build_binary_operator_lineage(
            materialize_df=materialize_df,
            left_child=(left_operator, backwards_df_left),
            right_child=(right_operator, backwards_df_right),
        )
        return operator, materialize_df

    @staticmethod
    def _normalize_column(
        df: pl.DataFrame, col: str | pl.Expr, alias: str
    ) -> tuple[pl.DataFrame, bool, str]:
        """
        Normalize a column (by expression or name) to a given alias.

        Returns:
            - New DataFrame
            - Whether it was an expression (i.e., needs to be dropped later)
            - Original name if it was a string
        """
        if isinstance(col, pl.Expr):
            return df.with_columns(col.alias(alias)), True, None
        else:
            return df.rename({col: alias}), False, col

    @staticmethod
    def _restore_column(
        df: pl.DataFrame, was_expr: bool, original_name: Optional[str], alias: str
    ) -> pl.DataFrame:
        """
        Restore a column to its original name or drop a temporary column.

        Args:
            df: DataFrame to restore
            was_expr: Whether the column was an expression (i.e., needs to be dropped)
            original_name: Original name of the column if it was a string
        """
        if was_expr:
            return df.drop(alias)
        else:
            return df.rename({alias: original_name})
