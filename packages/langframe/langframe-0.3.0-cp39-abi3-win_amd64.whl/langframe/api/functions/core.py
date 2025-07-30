from typing import Any

from langframe._logical_plan.expressions import LiteralExpr
from langframe.api.column import Column
from pydantic import ConfigDict, validate_call


@validate_call(config=ConfigDict(strict=True))
def col(col_name: str) -> Column:
    """Creates a Column expression referencing a column in the DataFrame.

    Args:
        col_name: Name of the column to reference

    Returns:
        A Column expression for the specified column

    Raises:
        TypeError: If colName is not a string
    """
    return Column._from_column_name(col_name)


def lit(value: Any) -> Column:
    """Creates a Column expression representing a literal value.

    Args:
        value: The literal value to create a column for

    Returns:
        A Column expression representing the literal value

    Raises:
        ValueError: If the type of the value cannot be inferred
    """
    try:
        inferred_type = Column._infer_literal_type(value)
    except ValueError as e:
        raise ValueError(f"`lit` failed to infer type for value `{value}`") from e
    literal_expr = LiteralExpr(value, inferred_type)
    return Column._from_logical_expr(literal_expr)
