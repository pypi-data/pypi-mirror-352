from pathlib import Path

import polars as pl
from polars._typing import IntoExpr
from polars.plugins import register_plugin_function

PLUGIN_PATH = Path(__file__).parents[3]


def md_extract(expr: IntoExpr, selector: str) -> pl.Expr:
    return register_plugin_function(
        plugin_path=PLUGIN_PATH,
        function_name="md_extract_expr",  # Must match the Rust function name
        args=expr,
        kwargs={"selector": selector},
        is_elementwise=True,
    )


def md_exists(expr: IntoExpr, selector: str) -> pl.Expr:
    return register_plugin_function(
        plugin_path=PLUGIN_PATH,
        function_name="md_exists_expr",
        args=expr,
        kwargs={"selector": selector},
        is_elementwise=True,
    )


def md_structure(expr: IntoExpr) -> pl.Expr:
    return register_plugin_function(
        plugin_path=PLUGIN_PATH,
        function_name="md_structure_expr",
        args=expr,
        is_elementwise=True,
    )


def apply_schema(expr: IntoExpr, schema_str: str) -> pl.Expr:
    return register_plugin_function(
        plugin_path=PLUGIN_PATH,
        function_name="apply_schema_expr",
        args=expr,
        kwargs={"schema_str": schema_str},
        is_elementwise=True,
    )


def group_schema(expr: IntoExpr) -> pl.Expr:
    return register_plugin_function(
        plugin_path=PLUGIN_PATH,
        function_name="superset_schema_expr",
        args=expr,
        is_elementwise=False,  # Important: cumulative aggregation
        returns_scalar=True,  # Returns a single scalar (1-row Series)
    )


def transform_md(expr: IntoExpr, schema_str: str) -> pl.Expr:
    return register_plugin_function(
        plugin_path=PLUGIN_PATH,
        function_name="transform_md_expr",
        args=expr,
        kwargs={"schema_str": schema_str},
        is_elementwise=True,
    )


@pl.api.register_expr_namespace("markdown")
class MarkdownExtractor:
    def __init__(self, expr: pl.Expr) -> None:
        self._expr = expr

    def extract(self, selector: str) -> pl.Expr:
        """Extract markdown content using the provided selector."""
        return md_extract(self._expr, selector)

    def exists(self, selector: str) -> pl.Expr:
        """Check if markdown content exists using the provided selector."""
        return md_exists(self._expr, selector)

    def structure(self) -> pl.Expr:
        """Get the structure of the markdown content."""
        return md_structure(self._expr)

    def apply_schema(self, schema_str: str) -> pl.Expr:
        """Apply a superset schema to the markdown."""
        return apply_schema(self._expr, schema_str)

    def group_schema(self) -> pl.Expr:
        """Group the schema of the markdown."""
        return group_schema(self._expr)

    def transform(self, schema_str: str) -> pl.Expr:
        """Transform the markdown using the provided schema."""
        return transform_md(self._expr, schema_str)
