from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, List

if TYPE_CHECKING:
    from langframe._logical_plan import LogicalPlan

from langframe._logical_plan.expressions.base import LogicalExpr
from langframe.api.types import (
    ArrayType,
    BooleanType,
    ColumnField,
    DataType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)
from langframe.api.types.datatypes import (
    _PrimitiveType,
)


class ColumnExpr(LogicalExpr):
    """Expression representing a column reference."""

    def __init__(self, name: str):
        self.name = name

    def __str__(self) -> str:
        return self.name

    def to_column_field(self, plan: LogicalPlan) -> ColumnField:
        column_field = next(
            (f for f in plan.schema().column_fields if f.name == self.name), None
        )
        if column_field is None:
            raise ValueError(
                f"Column '{self.name}' not found in schema. "
                f"Available columns: {', '.join(sorted(f.name for f in plan.schema().column_fields))}"
            )
        return column_field

    def children(self) -> List[LogicalExpr]:
        return []


class LiteralExpr(LogicalExpr):
    """Expression representing a literal value."""

    def __init__(self, literal: Any, data_type: _PrimitiveType):
        self.literal = literal
        self.data_type = data_type

    def __str__(self) -> str:
        return f"lit({self.literal})"

    def to_column_field(self, plan: LogicalPlan) -> ColumnField:
        return ColumnField(str(self), self.data_type)

    def children(self) -> List[LogicalExpr]:
        return []


class AliasExpr(LogicalExpr):
    """Expression representing a column alias."""

    def __init__(self, expr: LogicalExpr, name: str):
        self.expr = expr
        self.name = name

    def __str__(self) -> str:
        return f"{self.expr} AS {self.name}"

    def to_column_field(self, plan: LogicalPlan) -> ColumnField:
        return ColumnField(str(self.name), self.expr.to_column_field(plan).data_type)

    def children(self) -> List[LogicalExpr]:
        return [self.expr]


class SortExpr(LogicalExpr):
    """Expression representing a column sorted in ascending or descending order."""

    def __init__(self, expr: LogicalExpr, ascending=True, nulls_last=False):
        self.expr = expr
        self.ascending = ascending
        self.nulls_last = nulls_last

    def __str__(self) -> str:
        direction = "asc" if self.ascending else "desc"
        return f"{direction}({self.expr})"

    def to_column_field(self, plan: LogicalPlan) -> ColumnField:
        return ColumnField(str(self), self.expr.to_column_field(plan).data_type)

    def column_expr(self) -> LogicalExpr:
        return self.expr

    def children(self) -> List[LogicalExpr]:
        return [self.expr]


class IndexExpr(LogicalExpr):
    """Expression representing an index or field access operation."""

    def __init__(self, expr: LogicalExpr, index: Any):
        self.expr = expr
        self.index = index

    def __str__(self) -> str:
        return f"{self.expr}[{self.index}]"

    def to_column_field(self, plan: LogicalPlan) -> ColumnField:
        if not isinstance(
            self.expr.to_column_field(plan).data_type, (ArrayType, StructType)
        ):
            raise TypeError(
                f"Type mismatch: Cannot apply get_item to non-array, non-struct types. "
                f"Type: {self.expr.to_column_field(plan).data_type}. "
                f"Only array and struct types are supported."
            )

        if isinstance(
            self.expr.to_column_field(plan).data_type, ArrayType
        ) and isinstance(self.index, int):
            return ColumnField(
                str(self), self.expr.to_column_field(plan).data_type.element_type
            )

        elif isinstance(
            self.expr.to_column_field(plan).data_type, StructType
        ) and isinstance(self.index, str):
            for field in self.expr.to_column_field(plan).data_type.struct_fields:
                if field.name == self.index:
                    return ColumnField(str(self), field.data_type)
            raise ValueError(
                f"Field '{self.index}' not found in struct. Available fields: {', '.join(sorted(f.name for f in self.expr.to_column_field(plan).data_type.struct_fields))}"
            )

        else:
            raise TypeError(
                f"Type mismatch: Cannot apply get_item with {type(self.index).__name__} index to {type(self.expr.to_column_field(plan).data_type).__name__}. "
                f"Array types require integer indices, struct types require string field names."
            )

    def children(self) -> List[LogicalExpr]:
        return [self.expr]


class ArrayExpr(LogicalExpr):
    def __init__(self, args: List[LogicalExpr]):
        self.args = args

    def __str__(self):
        return f"array({', '.join(str(arg) for arg in self.args)})"

    def to_column_field(self, plan: LogicalPlan) -> ColumnField:
        for arg in self.args:
            if (
                arg.to_column_field(plan).data_type
                != self.args[0].to_column_field(plan).data_type
            ):
                raise TypeError(
                    f"Type mismatch: Cannot apply array to non-matching types. "
                    f"Type: {arg.to_column_field(plan).data_type}. "
                    f"All elements must be of the same type."
                )
        return ColumnField(
            str(self), ArrayType(self.args[0].to_column_field(plan).data_type)
        )

    def children(self) -> List[LogicalExpr]:
        return self.args


class StructExpr(LogicalExpr):
    def __init__(self, args: List[LogicalExpr]):
        self.args = args

    def __str__(self):
        return f"struct({', '.join(str(field) for field in self.args)})"

    def to_column_field(self, plan: LogicalPlan) -> ColumnField:
        struct_fields = []
        for arg in self.args:
            struct_fields.append(
                StructField(str(arg), arg.to_column_field(plan).data_type)
            )

        return ColumnField(str(self), StructType(struct_fields))

    def children(self) -> List[LogicalExpr]:
        return self.args


class UDFExpr(LogicalExpr):
    def __init__(
        self,
        func: Callable,
        args: List[LogicalExpr],
        return_type: DataType,
    ):
        self.func = func
        self.args = args
        self.return_type = return_type

    def __str__(self):
        args_str = ", ".join(str(arg) for arg in self.args)
        return f"{self.func.__name__}({args_str})"

    def to_column_field(self, plan: LogicalPlan) -> ColumnField:
        for arg in self.args:
            _ = arg.to_column_field(plan)
        return ColumnField(str(self), self.return_type)

    def children(self) -> List[LogicalExpr]:
        return self.args


class IsNullExpr(LogicalExpr):
    def __init__(self, expr: LogicalExpr, is_null: bool):
        self.expr = expr
        self.is_null = is_null

    def __str__(self):
        return f"{self.expr} IS {'' if self.is_null else 'NOT'} NULL"

    def to_column_field(self, plan: LogicalPlan) -> ColumnField:
        return ColumnField(str(self), BooleanType)

    def children(self) -> List[LogicalExpr]:
        return [self.expr]


class ArrayLengthExpr(LogicalExpr):
    def __init__(self, expr: LogicalExpr):
        self.expr = expr

    def __str__(self):
        return f"array_size({self.expr})"

    def to_column_field(self, plan: LogicalPlan) -> ColumnField:
        if not isinstance(self.expr.to_column_field(plan).data_type, ArrayType):
            raise TypeError(
                f"Type mismatch: Cannot apply array_size to non-array types. "
                f"Type: {self.expr.to_column_field(plan).data_type}. "
                f"Only array types are supported."
            )
        return ColumnField(str(self), IntegerType)

    def children(self) -> List[LogicalExpr]:
        return [self.expr]


class ArrayContainsExpr(LogicalExpr):
    def __init__(self, expr: LogicalExpr, value: LogicalExpr):
        self.expr = expr
        self.other = value

    def __str__(self):
        return f"array_contains({self.expr}, {self.other})"

    def to_column_field(self, plan: LogicalPlan) -> ColumnField:
        if not isinstance(self.expr.to_column_field(plan).data_type, ArrayType):
            raise TypeError(
                f"Type mismatch: Cannot apply array_contains to non-array types. "
                f"Type: {self.expr.to_column_field(plan).data_type}. "
                f"Only array types are supported."
            )
        # Polars does not support nested types in array_contains in all cases, so disallow it
        # to avoid inconsistent behavior.
        if not isinstance(self.other.to_column_field(plan).data_type, _PrimitiveType):
            raise TypeError(
                f"Type mismatch: Cannot apply array_contains to nested types. "
                f"Type: {self.other.to_column_field(plan).data_type}. "
                f"Only primitive types are supported."
            )
        if (
            self.expr.to_column_field(plan).data_type.element_type
            != self.other.to_column_field(plan).data_type
        ):
            raise TypeError(
                f"Type mismatch: Cannot apply array_contains to non-matching types. "
                f"Array type: {self.expr.to_column_field(plan).data_type}. "
                f"Value type: {self.other.to_column_field(plan).data_type}."
            )
        return ColumnField(str(self), BooleanType)

    def children(self) -> List[LogicalExpr]:
        return [self.expr, self.other]


class CastExpr(LogicalExpr):
    def __init__(self, expr: LogicalExpr, dest_type: DataType):
        self.expr = expr
        self.dest_type = dest_type

    def __str__(self):
        return f"cast({self.expr} as {self.dest_type})"

    def to_column_field(self, plan: LogicalPlan) -> ColumnField:
        def _cast_helper(source_type, dest_type, plan):
            """Helper function to check if a type can be cast."""
            try:
                # Use LiteralExpr as a dummy LogicalExpr to check recursively if a source type can be cast to a destination type.
                CastExpr(LiteralExpr(None, source_type), dest_type).to_column_field(
                    plan
                )
                return True
            except TypeError:
                return False

        source_type = self.expr.to_column_field(plan).data_type
        dest_type = self.dest_type

        # If types are the same, return the original column field
        if source_type == dest_type:
            return ColumnField(str(self), dest_type)

        # Rule 1: Allow casting between primitive types
        if isinstance(source_type, _PrimitiveType) and isinstance(
            dest_type, _PrimitiveType
        ):
            # Note: Polars does not support casting string to boolean, so we disallow it.
            if source_type == StringType and dest_type == BooleanType:
                raise TypeError(
                    "Unsupported type conversion: Cannot cast string to boolean."
                )
            return ColumnField(str(self), dest_type)

        # Rule 2: Allow casting between arrays if element types can be cast
        if isinstance(source_type, ArrayType) and isinstance(dest_type, ArrayType):
            if not _cast_helper(source_type.element_type, dest_type.element_type, plan):
                raise TypeError(
                    f"Cannot cast array elements from {source_type.element_type} to {dest_type.element_type}"
                )
            return ColumnField(str(self), dest_type)

        # Rule 3: Allow casting between structs if fields are compatible
        if isinstance(source_type, StructType) and isinstance(dest_type, StructType):
            source_fields = {f.name: f.data_type for f in source_type.struct_fields}
            dest_fields = {f.name: f.data_type for f in dest_type.struct_fields}

            for name, dest_field_type in dest_fields.items():
                if name not in source_fields or not _cast_helper(
                    source_fields[name], dest_field_type, plan
                ):
                    raise TypeError(
                        f"Cannot cast struct field '{name}' from {source_fields.get(name)} to {dest_field_type}"
                    )

            return ColumnField(str(self), dest_type)

        # Rule 4: Disallow unsupported type conversions
        raise TypeError(
            f"Cannot cast from {source_type} to {dest_type}. Unsupported type conversion."
        )

    def children(self) -> List[LogicalExpr]:
        return [self.expr]


class NotExpr(LogicalExpr):
    def __init__(self, expr: LogicalExpr):
        self.expr = expr

    def __str__(self):
        return f"NOT {self.expr}"

    def to_column_field(self, plan: LogicalPlan) -> ColumnField:
        if self.expr.to_column_field(plan).data_type != BooleanType:
            raise TypeError(
                f"Type mismatch: Cannot apply NOT to non-boolean types. "
                f"Type: {self.expr.to_column_field(plan).data_type}. "
                f"Only boolean types are supported."
            )
        return ColumnField(str(self), BooleanType)

    def children(self) -> List[LogicalExpr]:
        return [self.expr]


class CoalesceExpr(LogicalExpr):
    def __init__(self, exprs: List[LogicalExpr]):
        self.exprs = exprs

    def __str__(self) -> str:
        return f"coalesce({', '.join(str(expr) for expr in self.exprs)})"

    def to_column_field(self, plan: LogicalPlan) -> ColumnField:
        expr_types = [(arg, arg.to_column_field(plan).data_type) for arg in self.exprs]
        data_types = {data_type for _, data_type in expr_types}

        if len(data_types) > 1:
            type_details = [f"{expr}: {dtype}" for expr, dtype in expr_types]
            type_info = "\n  ".join(type_details)

            raise TypeError(
                f"All expressions in coalesce must have the same data type, but found {len(data_types)} different types:\n  {type_info}"
            )

        data_type = next(iter(data_types))
        return ColumnField(name=str(self), data_type=data_type)

    def children(self) -> List[LogicalExpr]:
        return [self.exprs]
