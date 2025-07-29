from typing import List

from langframe._logical_plan.expressions import AggregateExpr, ColumnExpr, LogicalExpr, SortExpr
from langframe._logical_plan.plans.base import LogicalPlan
from langframe.api.types import (
    ArrayType,
    BooleanType,
    ColumnField,
    Schema,
    StructType,
)


class Projection(LogicalPlan):
    def __init__(self, input: LogicalPlan, exprs: List[LogicalExpr]):
        self._input = input
        self._exprs = exprs
        super().__init__()

    def children(self) -> List[LogicalPlan]:
        return [self._input]

    def _build_schema(self) -> Schema:
        fields = []
        for expr in self._exprs:
            if isinstance(expr, AggregateExpr):
                raise ValueError(
                    "Aggregate expressions are not allowed in projections. "
                    "Please use the agg() method instead."
                )
            fields.append(expr.to_column_field(self._input))
        return Schema(fields)

    def exprs(self) -> List[LogicalExpr]:
        return self._exprs

    def _repr(self) -> str:
        exprs_str = ", ".join(str(expr) for expr in self._exprs)
        return f"Projection(exprs=[{exprs_str}])"

    def with_children(self, children: List[LogicalPlan]) -> LogicalPlan:
        if len(children) != 1:
            raise ValueError("Projection must have exactly one child")
        result = Projection(children[0], self._exprs)
        result.set_cache_info(self.cache_info)
        return result


class Filter(LogicalPlan):
    def __init__(self, input: LogicalPlan, predicate: LogicalExpr):
        self._input = input
        actual_type = predicate.to_column_field(input).data_type
        if actual_type != BooleanType:
            raise ValueError(
                f"Filter predicate must return a boolean value, but got {actual_type}. "
                "Examples of valid filters:\n"
                "- df.filter(col('age') > 18)\n"
                "- df.filter(col('status') == 'active')\n"
                "- df.filter(col('is_valid'))"
            )
        if isinstance(predicate, AggregateExpr):
            raise ValueError(
                "Aggregate expressions are not allowed in projections. "
                "Please use the agg() method instead."
            )
        if isinstance(predicate, SortExpr):
            raise ValueError(
                "Sort expressions are not allowed in projections. "
                "Please use the sort() method instead."
            )
        self._predicate = predicate
        super().__init__()

    def children(self) -> List[LogicalPlan]:
        return [self._input]

    def _build_schema(self) -> Schema:
        return self._input.schema()

    def predicate(self) -> LogicalExpr:
        return self._predicate

    def _repr(self) -> str:
        """Return the representation for the Filter node."""
        return f"Filter(predicate={self._predicate})"

    def with_children(self, children: List[LogicalPlan]) -> LogicalPlan:
        if len(children) != 1:
            raise ValueError("Filter must have exactly one child")
        result = Filter(children[0], self._predicate)
        result.set_cache_info(self.cache_info)
        return result


class Union(LogicalPlan):
    def __init__(self, inputs: List[LogicalPlan]):
        self._inputs = inputs
        super().__init__()

    def children(self) -> List[LogicalPlan]:
        return self._inputs

    def _build_schema(self) -> Schema:
        schemas = [input_plan.schema() for input_plan in self._inputs]

        # Check that all schemas have the same columns and types
        first_schema = schemas[0]
        first_schema_fields = {f.name: f.data_type for f in first_schema.column_fields}

        for schema in schemas[1:]:
            schema_fields = {f.name: f.data_type for f in schema.column_fields}
            if set(schema_fields.keys()) != set(first_schema_fields.keys()):
                raise ValueError(
                    "Cannot union DataFrames with different columns. "
                    "All DataFrames must have exactly the same column names."
                )
            for name, type_ in schema_fields.items():
                if type_ != first_schema_fields[name]:
                    raise ValueError(
                        f"Cannot union DataFrames: column '{name}' must be type {first_schema_fields[name]} "
                        "across all DataFrames. Consider casting columns to matching types before union."
                    )

        return schemas[0]

    def _repr(self) -> str:
        return "Union"

    def with_children(self, children: List[LogicalPlan]) -> LogicalPlan:
        result = Union(children)
        result.set_cache_info(self.cache_info)
        return result


class Limit(LogicalPlan):
    def __init__(self, input: LogicalPlan, n: int):
        self._input = input
        self.n = n
        super().__init__()

    def children(self) -> List[LogicalPlan]:
        return [self._input]

    def _build_schema(self) -> Schema:
        return self._input.schema()

    def _repr(self) -> str:
        return f"Limit(n={self.n})"

    def with_children(self, children: List[LogicalPlan]) -> LogicalPlan:
        if len(children) != 1:
            raise ValueError("Limit must have exactly one child")
        result = Limit(children[0], self.n)
        result.set_cache_info(self.cache_info)
        return result


class Explode(LogicalPlan):
    def __init__(self, input: LogicalPlan, expr: LogicalExpr):
        self._input = input
        self._expr = expr
        super().__init__()

    def children(self) -> list[LogicalPlan]:
        return [self._input]

    def _build_schema(self) -> Schema:
        input_schema = self._input.schema()
        exploded_field = self._expr.to_column_field(self._input)

        if not isinstance(exploded_field.data_type, ArrayType):
            raise ValueError(
                f"Explode operator expected an array column for field {exploded_field.name}, "
                f"but received {exploded_field.data_type} instead."
            )

        new_fields = []
        for field in input_schema.column_fields:
            if field.name == exploded_field.name:
                new_field = ColumnField(
                    name=field.name, data_type=exploded_field.data_type.element_type
                )
                new_fields.append(new_field)
            else:
                new_fields.append(field)

        if exploded_field.name not in {f.name for f in input_schema.column_fields}:
            new_field = ColumnField(
                name=exploded_field.name,
                data_type=exploded_field.data_type.element_type,
            )
            new_fields.append(new_field)

        return Schema(column_fields=new_fields)

    def _repr(self) -> str:
        return f"Explode({self._expr})"

    def with_children(self, children: List[LogicalPlan]) -> LogicalPlan:
        if len(children) != 1:
            raise ValueError("Explode must have exactly one child")
        result = Explode(children[0], self._expr)
        result.set_cache_info(self.cache_info)
        return result


class DropDuplicates(LogicalPlan):
    def __init__(
        self,
        input: LogicalPlan,
        subset: List[ColumnExpr],
    ):
        self._input = input
        self.subset = subset
        super().__init__()

    def children(self) -> List[LogicalPlan]:
        return [self._input]

    def _build_schema(self) -> Schema:
        return self._input.schema()

    def _repr(self) -> str:
        return f"DropDuplicates(subset={', '.join(str(expr) for expr in self.subset)})"

    def with_children(self, children: List[LogicalPlan]) -> LogicalPlan:
        if len(children) != 1:
            raise ValueError("DropDuplicates must have exactly one child")
        result = DropDuplicates(children[0], self.subset)
        result.set_cache_info(self.cache_info)
        return result

    def _subset(self) -> List[str]:
        subset: List[str] = []
        for col in self.subset:
            subset.append(str(col))
        return subset


class Sort(LogicalPlan):
    def __init__(
        self,
        input: LogicalPlan,
        sort_exprs: List[SortExpr],
    ):
        self._input = input
        self._sort_exprs = sort_exprs
        super().__init__()

    def children(self) -> List[LogicalPlan]:
        return [self._input]

    def _build_schema(self) -> Schema:
        return self._input.schema()

    def sort_exprs(self) -> List[LogicalExpr]:
        return self._sort_exprs

    def _repr(self) -> str:
        return f"Sort(cols={', '.join(str(expr) for expr in self._sort_exprs)})"

    def with_children(self, children: List[LogicalPlan]) -> LogicalPlan:
        if len(children) != 1:
            raise ValueError("Sort must have exactly one child")
        result = Sort(children[0], self._sort_exprs)
        result.set_cache_info(self.cache_info)
        return result


class Unnest(LogicalPlan):
    def __init__(self, input: LogicalPlan, exprs: List[ColumnExpr]):
        self._input = input
        self._exprs = exprs
        super().__init__()

    def children(self) -> List[LogicalPlan]:
        return [self._input]

    def _build_schema(self) -> Schema:
        column_fields = []
        for field in self._input.schema().column_fields:
            if field.name in {expr.name for expr in self._exprs}:
                if isinstance(field.data_type, StructType):
                    for field_ in field.data_type.struct_fields:
                        column_fields.append(
                            ColumnField(name=field_.name, data_type=field_.data_type)
                        )
                else:
                    raise ValueError(
                        f"Unnest operator expected a struct column for field {field.name}, "
                        f"but received {field.data_type} instead."
                    )
            else:
                column_fields.append(field)
        return Schema(column_fields)

    def _repr(self) -> str:
        return f"Unnest(exprs={', '.join(str(expr) for expr in self._exprs)})"

    def col_names(self) -> List[str]:
        return [expr.name for expr in self._exprs]

    def with_children(self, children: List[LogicalPlan]) -> LogicalPlan:
        if len(children) != 1:
            raise ValueError("Unnest must have exactly one child")
        result = Unnest(children[0], self._exprs)
        result.set_cache_info(self.cache_info)
        return result
