from abc import ABC, abstractmethod
from typing import List, Optional

from langframe._logical_plan.expressions import (
    ColumnExpr,
    EqualityComparisonExpr,
    LogicalExpr,
    NumericComparisonExpr,
)
from langframe._logical_plan.plans.base import LogicalPlan
from langframe.api.types import (
    ArrayType,
    ColumnField,
    DoubleType,
    FloatType,
    JoinExampleCollection,
    Schema,
    StringType,
)
from langframe.api.types.datatypes import (
    is_dtype_numeric,
)

SIMILARITY_SCORE_COL_NAME = "_similarity_score"


class Join(LogicalPlan):
    def __init__(
        self, left: LogicalPlan, right: LogicalPlan, on: List[LogicalExpr], how: str
    ):
        self._left = left
        self._right = right
        self._on = on
        self._how = how
        super().__init__()

    def children(self) -> List[LogicalPlan]:
        return [self._left, self._right]

    def _build_schema(self) -> Schema:
        unsupported_hows = ["semi", "leftsemi", "anti", "leftanti"]
        if self._how in unsupported_hows:
            raise NotImplementedError(f"Join type {self._how} is not implemented yet!")
        coalesce_columns = []
        for expr in self._on:
            if isinstance(expr, ColumnExpr):
                coalesce_columns.append(expr.name)

            # Common validation for both EqualityComparisonExpr and NumericComparisonExpr
            elif isinstance(expr, (EqualityComparisonExpr, NumericComparisonExpr)):
                if not isinstance(expr.left, ColumnExpr) or not isinstance(
                    expr.right, ColumnExpr
                ):
                    raise NotImplementedError(
                        "Join on expressions must be simple column references for now."
                    )

                # Check that columns exist in the correct schemas
                left_col = expr.left.name
                right_col = expr.right.name
                left_schema = self._left.schema().column_fields
                right_schema = self._right.schema().column_fields

                left_in_schemas = (left_col in left_schema, left_col in right_schema)
                right_in_schemas = (right_col in left_schema, right_col in right_schema)

                if not (
                    (left_in_schemas[0] and right_in_schemas[1])
                    or (left_in_schemas[1] and right_in_schemas[0])
                ):
                    raise ValueError(
                        "Join on expressions must exist in both left and right schemas."
                    )

                # Type validation
                left_type = expr.to_column_field(self._left).data_type
                right_type = expr.to_column_field(self._right).data_type

                if isinstance(expr, EqualityComparisonExpr):
                    if left_type != right_type:
                        raise ValueError(
                            f"Type mismatch in join condition: Cannot compare '{left_col}' ({left_type}) with "
                            f"'{right_col}' ({right_type}). Join on equality comparison requires the same type "
                            f"on both sides."
                        )
                else:  # NumericComparisonExpr
                    if not (
                        is_dtype_numeric(left_type) and is_dtype_numeric(right_type)
                    ):
                        raise ValueError(
                            f"Type mismatch in join condition: Cannot compare '{left_col}' ({left_type}) with "
                            f"'{right_col}' ({right_type}). Numeric comparisons require numeric types on both sides."
                        )

            else:
                raise ValueError(
                    "The ON clause must be a boolean expression comparing columns from both DataFrames, "
                    "for example: col('df1.id') == col('df2.id')."
                )

        # TODO(rohitrastogi): This logic is very similar to the one in _build_select_clause in the planner.
        # We should refactor this to avoid code duplication.
        fields = []
        left_field_names = {
            field.name: field for field in self._left.schema().column_fields
        }
        for col_name in coalesce_columns:
            if col_name in left_field_names:
                fields.append(left_field_names[col_name])

        for field in self._left.schema().column_fields:
            if field.name in coalesce_columns:
                continue
            fields.append(field)

        for field in self._right.schema().column_fields:
            if field.name in coalesce_columns:
                continue

            fields.append(field)

        return Schema(fields)

    def _repr(self) -> str:
        return f"Join(how={self._how}, on={', '.join(str(expr) for expr in self._on)})"

    def on(self) -> List[LogicalExpr]:
        return self._on

    def how(self) -> str:
        return self._how

    def with_children(self, children: List[LogicalPlan]) -> LogicalPlan:
        if len(children) != 2:
            raise ValueError("Join must have exactly two children")
        result = Join(children[0], children[1], self._on, self._how)
        result.set_cache_info(self.cache_info)
        return result


class BaseSemanticJoin(LogicalPlan, ABC):
    def __init__(
        self,
        left: LogicalPlan,
        right: LogicalPlan,
        left_on: LogicalExpr,
        right_on: LogicalExpr,
    ):
        self._left = left
        self._right = right
        self._left_on = left_on
        self._right_on = right_on
        super().__init__()

    @abstractmethod
    def _validate_columns(self) -> None:
        pass

    def _build_schema(self) -> Schema:
        self._validate_columns()
        return Schema(
            self._left.schema().column_fields + self._right.schema().column_fields
        )

    def left_on(self) -> LogicalExpr:
        return self._left_on

    def right_on(self) -> LogicalExpr:
        return self._right_on

    def children(self) -> List[LogicalPlan]:
        return [self._left, self._right]

    @abstractmethod
    def with_children(self, children: List[LogicalPlan]) -> LogicalPlan:
        raise NotImplementedError("Subclasses must implement with_children")


class SemanticJoin(BaseSemanticJoin):
    def __init__(
        self,
        left: LogicalPlan,
        right: LogicalPlan,
        left_on: ColumnExpr,
        right_on: ColumnExpr,
        join_instruction: str,
        examples: Optional[JoinExampleCollection] = None,
    ):
        self._join_instruction = join_instruction
        self._examples = examples
        super().__init__(left, right, left_on, right_on)

    def _validate_columns(self) -> None:
        left_schema = self._left.schema()
        right_schema = self._right.schema()
        left_columns = {field.name: field for field in left_schema.column_fields}
        right_columns = {field.name: field for field in right_schema.column_fields}

        if self._left_on.name not in left_columns:
            raise ValueError(
                f"Column '{self._left_on.name}' not found in left DataFrame. "
                f"Available columns: {', '.join(sorted(left_columns.keys()))}"
            )
        if self._right_on.name not in right_columns:
            raise ValueError(
                f"Column '{self._right_on.name}' not found in right DataFrame. "
                f"Available columns: {', '.join(sorted(right_columns.keys()))}"
            )
        if left_columns[self._left_on.name].data_type != StringType:
            raise TypeError(
                f"Type mismatch: Cannot apply semantic.join on a non-string type. "
                f"Type: {left_columns[self._left_on.name].data_type}. "
                f"Only string types are supported."
            )
        if right_columns[self._right_on.name].data_type != StringType:
            raise TypeError(
                f"Type mismatch: Cannot apply semantic.join on a non-string type. "
                f"Type: {right_columns[self._right_on.name].data_type}. "
                f"Only string types are supported."
            )

    def join_instruction(self) -> str:
        return self._join_instruction

    def examples(self) -> Optional[JoinExampleCollection]:
        return self._examples

    def _repr(self) -> str:
        return (
            f"SemanticJoin(left_on={self._left_on.name}, "
            f"right_on={self._right_on.name}, join_instruction={self._join_instruction})"
        )

    def with_children(self, children: List[LogicalPlan]) -> LogicalPlan:
        if len(children) != 2:
            raise ValueError(f"SemanticJoin expects 2 children, got {len(children)}")

        result = SemanticJoin(
            left=children[0],
            right=children[1],
            left_on=self._left_on,
            right_on=self._right_on,
            join_instruction=self._join_instruction,
            examples=self._examples,
        )
        result.set_cache_info(self.cache_info)
        return result


class SemanticSimilarityJoin(BaseSemanticJoin):
    def __init__(
        self,
        left: LogicalPlan,
        right: LogicalPlan,
        left_on: LogicalExpr,
        right_on: LogicalExpr,
        k: int,
        return_similarity_scores: bool = False,
    ):
        self._k = k
        self._return_similarity_scores = return_similarity_scores
        super().__init__(left, right, left_on, right_on)

    def _validate_columns(self) -> None:
        left_dtype = self._left_on.to_column_field(self._left).data_type
        if left_dtype != ArrayType(element_type=FloatType):
            raise TypeError(
                f"Type mismatch: Cannot apply semantic.sim_join on column that is not embeddings type (List[float]): "
                f"left_on argument is type:({left_dtype}). "
                f"Create an embeddings column using semantic.embed() first."
            )
        right_dtype = self._right_on.to_column_field(self._right).data_type
        if right_dtype != ArrayType(element_type=FloatType):
            raise TypeError(
                f"Type mismatch: Cannot apply semantic.sim_join on column that is not embeddings type (List[float]): "
                f"right_on argument is type:({right_dtype}). "
                f"Create an embeddings column using semantic.embed() first."
            )

    def k(self) -> int:
        return self._k

    def return_similarity_scores(self) -> bool:
        return self._return_similarity_scores

    def _repr(self) -> str:
        return (
            f"SemanticSimilarityJoin(left_on={self._left_on.name}, "
            f"right_on={self._right_on.name}, k={self._k}, "
            f"return_similarity_scores={self._return_similarity_scores})"
        )

    def _build_schema(self) -> Schema:
        self._validate_columns()
        # add scores field if requested by user.
        additional_fields = []
        if self._return_similarity_scores:
            additional_fields.append(
                ColumnField(
                    name=SIMILARITY_SCORE_COL_NAME,
                    data_type=DoubleType,
                )
            )
        return Schema(
            self._left.schema().column_fields
            + self._right.schema().column_fields
            + additional_fields
        )

    def with_children(self, children: List[LogicalPlan]) -> LogicalPlan:
        if len(children) != 2:
            raise ValueError(
                f"SemanticSimilarityJoin expects 2 children, got {len(children)}"
            )

        result = SemanticSimilarityJoin(
            left=children[0],
            right=children[1],
            left_on=self._left_on,
            right_on=self._right_on,
            k=self._k,
            return_similarity_scores=self._return_similarity_scores,
        )
        result.set_cache_info(self.cache_info)
        return result
