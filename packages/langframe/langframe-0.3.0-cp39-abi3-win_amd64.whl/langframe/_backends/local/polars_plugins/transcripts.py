from pathlib import Path

import polars as pl
from polars._typing import IntoExpr
from polars.plugins import register_plugin_function

PLUGIN_PATH = Path(__file__).parents[3]


def ts_format(expr: IntoExpr) -> pl.Expr:
    return register_plugin_function(
        plugin_path=PLUGIN_PATH,
        function_name="ts_format_expr",
        args=expr,
        is_elementwise=True,
    )


def ts_transform(expr: IntoExpr, format: str) -> pl.Expr:
    return register_plugin_function(
        plugin_path=PLUGIN_PATH,
        function_name="ts_transform_expr",
        args=expr,
        kwargs={"format": format},
        is_elementwise=True,
    )


@pl.api.register_expr_namespace("transcript")
class TranscriptExtractor:
    def __init__(self, expr: pl.Expr) -> None:
        self._expr = expr

    def format(self) -> pl.Expr:
        """Identify the transcript format."""
        return ts_format(self._expr)

    def transform(self, format: str) -> pl.Expr:
        """Transform the transcript into a structured format."""
        return ts_transform(self._expr, format)
