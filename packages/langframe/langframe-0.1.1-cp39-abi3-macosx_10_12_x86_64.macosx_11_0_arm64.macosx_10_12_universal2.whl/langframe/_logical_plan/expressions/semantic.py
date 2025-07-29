from __future__ import annotations

from abc import ABC
from enum import Enum, EnumType
from typing import TYPE_CHECKING, List, Optional

from langframe.api.types import (
    ClassifyExampleCollection,
    MapExampleCollection,
    PredicateExampleCollection,
)
from pydantic import BaseModel

if TYPE_CHECKING:
    from langframe._logical_plan import LogicalPlan

import langframe._utils.misc as utils
from langframe._logical_plan.expressions.aggregate import AggregateExpr
from langframe._logical_plan.expressions.base import LogicalExpr
from langframe._logical_plan.expressions.basic import ColumnExpr
from langframe.api.types import (
    ArrayType,
    BooleanType,
    FloatType,
    StringType,
)
from langframe._utils.schema import convert_pydantic_type_to_custom_struct_type
from langframe.api.types.schema import ColumnField


class SemanticExpr(LogicalExpr, ABC):
    """Marker abstract class for semantic expressions."""

    pass


class SemanticMapExpr(SemanticExpr):
    def __init__(
        self, instruction: str, examples: Optional[MapExampleCollection] = None
    ):
        self.instruction = instruction
        self.exprs = [
            ColumnExpr(parsed_col)
            for parsed_col in utils.parse_instruction(instruction)
        ]
        if not self.exprs:
            raise ValueError(
                "semantic.map instruction requires at least one templated column."
            )
        self.examples = None
        if examples:
            examples._validate_with_instruction(instruction)
            self.examples = examples

    def __str__(self):
        instruction_hash = utils.get_content_hash(self.instruction)
        exprs_str = ", ".join(str(expr) for expr in self.exprs)
        return f"semantic.map_{instruction_hash}({exprs_str})"

    def to_column_field(self, plan: LogicalPlan) -> ColumnField:
        for arg in self.exprs:
            expr_field = arg.to_column_field(plan)
            if expr_field.data_type != StringType:
                raise TypeError(
                    f"Type mismatch: Cannot apply semantic.map to non-string type. "
                    f"Type: {expr_field.data_type}. "
                    f"Only StringType is supported."
                )
        return ColumnField(str(self), StringType)

    def children(self) -> List[LogicalExpr]:
        return self.exprs


class SemanticExtractExpr(SemanticExpr):
    def __init__(self, expr: LogicalExpr, schema: type[BaseModel]):
        super().__init__()
        self.expr = expr
        self.schema = schema

    def __str__(self):
        schema_hash = utils.get_content_hash(str(self.schema))
        expr_str = str(self.expr)
        return f"semantic.extract_{schema_hash}({expr_str})"

    def to_column_field(self, plan: LogicalPlan) -> ColumnField:
        expr_field = self.expr.to_column_field(plan)
        if expr_field.data_type != StringType:
            raise TypeError(
                f"Type mismatch: Cannot apply semantic.extract to non-string type. "
                f"Type: {expr_field.data_type}. "
                f"Only StringType is supported."
            )
        return ColumnField(
            str(self), convert_pydantic_type_to_custom_struct_type(self.schema)
        )

    def children(self) -> List[LogicalExpr]:
        return [self.expr]


class SemanticPredExpr(SemanticExpr):
    def __init__(
        self,
        instruction: str,
        examples: Optional[PredicateExampleCollection] = None,
    ):
        self.instruction = instruction
        self.exprs = [
            ColumnExpr(parsed_col)
            for parsed_col in utils.parse_instruction(instruction)
        ]
        if not self.exprs:
            raise ValueError(
                "semantic.predicate instruction requires at least one templated column."
            )
        self.examples = None
        if examples:
            examples._validate_with_instruction(instruction)
            self.examples = examples

    def __str__(self):
        instruction_hash = utils.get_content_hash(self.instruction)
        exprs_str = ", ".join(str(expr) for expr in self.exprs)
        return f"semantic.predicate_{instruction_hash}({exprs_str})"

    def to_column_field(self, plan: LogicalPlan) -> ColumnField:
        for arg in self.exprs:
            expr_field = arg.to_column_field(plan)
            if expr_field.data_type != StringType:
                raise TypeError(
                    f"Type mismatch: Cannot apply semantic.predicate to non-string type. "
                    f"Type: {expr_field.data_type}. "
                    f"Only StringType is supported."
                )
        return ColumnField(str(self), BooleanType)

    def children(self) -> List[LogicalExpr]:
        return self.exprs


class SemanticReduceExpr(SemanticExpr, AggregateExpr):
    def __init__(self, instruction: str):
        self.instruction = instruction
        self.exprs = [
            ColumnExpr(parsed_col)
            for parsed_col in utils.parse_instruction(instruction)
        ]
        if not self.exprs:
            raise ValueError(
                "semantic.reduce instruction requires at least one templated column."
            )

    def __str__(self):
        instruction_hash = utils.get_content_hash(self.instruction)
        exprs_str = ", ".join(str(expr) for expr in self.exprs)
        return f"semantic.reduce_{instruction_hash}({exprs_str})"

    def to_column_field(self, plan: LogicalPlan) -> ColumnField:
        for arg in self.exprs:
            expr_field = arg.to_column_field(plan)
            if expr_field.data_type != StringType:
                raise TypeError(
                    f"Type mismatch: Cannot apply semantic.reduce to non-string type. "
                    f"Type: {expr_field.data_type}. "
                    f"Only string types are supported."
                )
        return ColumnField(str(self), StringType)

    def children(self) -> List[LogicalExpr]:
        return self.exprs


class SemanticClassifyExpr(SemanticExpr):
    def __init__(
        self,
        expr: LogicalExpr,
        labels: List[str] | EnumType,
        examples: Optional[ClassifyExampleCollection] = None,
    ):
        self.expr = expr
        self.labels = (
            self._transform_labels_list_into_enum(labels)
            if isinstance(labels, list)
            else labels
        )
        self.examples = None
        if examples:
            examples._validate_with_enum(self.labels)
            self.examples = examples

    def __str__(self):
        formatted_labels = "[" + ", ".join(f"'{label}'" for label in self.labels) + "]"
        return f"semantic.classify({self.expr}, {formatted_labels})"

    def to_column_field(self, plan: LogicalPlan) -> ColumnField:
        if self.expr.to_column_field(plan).data_type != StringType:
            raise TypeError(
                f"Type mismatch: Cannot apply semantic.classify to non-string type. "
                f"Type: {self.expr.to_column_field(plan).data_type}. "
                f"Only StringType is supported."
            )

        if not isinstance(self.labels, List) and not isinstance(
            next(iter(self.labels)).value, str
        ):
            raise TypeError(
                f"Type mismatch: Cannot apply semantic.classify to an enum that is not a string. "
                f"Type: {self.expr.to_column_field(plan).data_type}. "
                f"Only string enums are supported."
            )

        return ColumnField(str(self), StringType)

    def children(self) -> List[LogicalExpr]:
        return [self.expr]

    def _transform_labels_list_into_enum(self, labels: list[str]) -> EnumType:
        """
        Transforms a list of labels into an Enum.
        """
        label_enum_values = []
        for label_str in labels:
            label_enum_values.append(
                (
                    self._transform_value_into_enum_name(label_str),
                    label_str,
                )
            )

        return Enum("Label", label_enum_values)

    def _transform_value_into_enum_name(self, label_value: str) -> str:
        """
        Transforms a label value into an enum name.
        >>> SemClassifyDataFrame._trasnform_value_into_enum_name("General Inquiry") returns "GENERAL_INQUIRY"
        """
        return label_value.upper().replace(" ", "_")


class AnalyzeSentimentExpr(SemanticExpr):
    def __init__(
        self,
        expr: LogicalExpr,
    ):
        self.expr = expr

    def __str__(self):
        return f"semantic.analyze_sentiment({self.expr})"

    def to_column_field(self, plan: LogicalPlan) -> ColumnField:
        if self.expr.to_column_field(plan).data_type != StringType:
            raise TypeError(
                f"Type mismatch: Cannot apply semantic.analyze_sentiment to non-string type. "
                f"Type: {self.expr.to_column_field(plan).data_type}. "
                f"Only StringType is supported."
            )
        return ColumnField(str(self), StringType)

    def children(self) -> List[LogicalExpr]:
        return [self.expr]


class EmbeddingsExpr(SemanticExpr):
    """Expression for generating embeddings for a string column.

    This expression creates a new column of embeddings for each value in the input string column.
    The embeddings are a list of floats generated using RM
    """

    def __init__(self, expr: LogicalExpr):
        self.expr = expr

    def __str__(self) -> str:
        return f"semantic.embed({self.expr})"

    def expr(self) -> LogicalExpr:
        return self.expr

    def to_column_field(self, plan: LogicalPlan) -> ColumnField:
        input_field = self.expr.to_column_field(plan)
        if input_field.data_type != StringType:
            raise TypeError(
                f"semantic.embed requires column of type string as input, got {input_field.data_type}"
            )
        return ColumnField(name=str(self), data_type=ArrayType(element_type=FloatType))

    def children(self) -> List[LogicalExpr]:
        return [self.expr]
