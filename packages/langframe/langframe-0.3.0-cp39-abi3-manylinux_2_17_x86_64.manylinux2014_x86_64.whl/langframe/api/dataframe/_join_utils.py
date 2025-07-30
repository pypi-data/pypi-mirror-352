"""
Utility functions for DataFrame join operations.
"""

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from langframe.api.dataframe import DataFrame

from langframe._logical_plan.expressions import (
    EqualityComparisonExpr,
    NumericComparisonExpr,
)
from langframe.api.column import Column, ColumnOrName
from langframe.api.functions import col


def normalize_join_type(how: str) -> str:
    """Normalizes join type to internal representation."""
    if not how:
        return "inner"

    join_type_mapping = {
        "full_outer": "full",
        "fullouter": "full",
        "outer": "full",
        "left_outer": "left",
        "leftouter": "left",
        "right_outer": "right",
        "rightouter": "right",
        "left_semi": "leftsemi",
        "left_anti": "leftanti",
        "right_anti": "rightanti",
    }

    how = join_type_mapping.get(how, how)
    valid_types = {
        "inner",
        "cross",
        "full",
        "left",
        "right",
        "semi",
        "leftsemi",
        "anti",
        "leftanti",
    }

    if how not in valid_types:
        raise ValueError(f"Unsupported join type: {how}")

    return how


def process_single_column_string_join(
    left_df: "DataFrame", right_df: "DataFrame", column: str, how: str
) -> List:
    """Process a single column name join condition."""
    if "anti" in how:
        raise ValueError(
            "Anti joins require a boolean Column expression for the ON condition. "
        )

    if column not in left_df.columns or column not in right_df.columns:
        left_missing = column not in left_df.columns
        right_missing = column not in right_df.columns
        if left_missing and right_missing:
            raise ValueError(f"Join column '{column}' not found in either DataFrame")
        elif left_missing:
            raise ValueError(
                f"Join column '{column}' not found in left DataFrame. "
                f"Left columns are: {', '.join(left_df.columns)}"
            )
        else:
            raise ValueError(
                f"Join column '{column}' not found in right DataFrame. "
                f"Right columns are: {', '.join(right_df.columns)}"
            )

    left_type = (
        col(column)._logical_expr.to_column_field(left_df._logical_plan).data_type
    )
    right_type = (
        col(column)._logical_expr.to_column_field(right_df._logical_plan).data_type
    )
    if left_type != right_type:
        raise ValueError(
            f"Join column '{column}' has mismatched types:\n"
            f"  Left DataFrame: {left_type}\n"
            f"  Right DataFrame: {right_type}\n"
            "The join column must have the same type in both DataFrames"
        )

    return [col(column)._logical_expr]


def process_column_list_join(
    left_df: "DataFrame",
    right_df: "DataFrame",
    columns: List[ColumnOrName],
    how: str,
) -> List:
    """Process a list of join conditions."""
    if not columns:
        return []

    all_strings = all(isinstance(x, str) for x in columns)
    all_columns = all(isinstance(x, Column) for x in columns)

    if not (all_strings or all_columns):
        raise TypeError(
            "Join conditions must be all strings or all Column objects. "
            f"Got a mix of types: {[type(x).__name__ for x in columns]}"
        )

    if all_strings:
        if "anti" in how:
            raise ValueError(
                "Anti joins require boolean Column expressions for the ON condition. "
                "String column names are not supported for anti joins. "
                "Use Column expressions with boolean predicates instead."
            )
        return _validate_and_convert_string_columns(left_df, right_df, columns)

    for column in columns:
        if not isinstance(
            column._logical_expr, NumericComparisonExpr
        ) or not isinstance(column._logical_expr, EqualityComparisonExpr):
            raise ValueError(
                "The ON clause must be a boolean expression comparing columns from both DataFrames, "
                "for example: col('df1.id') == col('df2.id')."
            )

    return [c._logical_expr for c in columns]


def _validate_and_convert_string_columns(
    left_df: "DataFrame", right_df: "DataFrame", columns: List[str]
) -> List:
    """Validate and convert string column names to Column expressions."""
    result = []
    for col_name in columns:
        if col_name not in left_df.columns or col_name not in right_df.columns:
            if col_name not in left_df.columns and col_name not in right_df.columns:
                raise ValueError(
                    f"Join column '{col_name}' not found in either DataFrame.\n"
                    f"Left DataFrame columns: {left_df.columns}\n"
                    f"Right DataFrame columns: {right_df.columns}"
                )
            elif col_name not in left_df.columns:
                raise ValueError(
                    f"Join column '{col_name}' not found in left DataFrame.\n"
                    f"Left DataFrame columns: {left_df.columns}"
                )
            elif col_name not in right_df.columns:
                raise ValueError(
                    f"Join column '{col_name}' not found in right DataFrame.\n"
                    f"Right DataFrame columns: {right_df.columns}"
                )

        left_type = (
            col(col_name)._logical_expr.to_column_field(left_df._logical_plan).data_type
        )
        right_type = (
            col(col_name)
            ._logical_expr.to_column_field(right_df._logical_plan)
            .data_type
        )
        if left_type != right_type:
            raise ValueError(
                f"Join column '{col_name}' has mismatched types:\n"
                f"  Left DataFrame: {left_type}\n"
                f"  Right DataFrame: {right_type}\n"
                "The join column must have the same type in both DataFrames"
            )

        result.append(col(col_name)._logical_expr)
    return result
