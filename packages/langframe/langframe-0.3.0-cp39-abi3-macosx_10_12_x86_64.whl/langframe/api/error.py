
"""
Langframe error hierarchy.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from langframe.api.types import DataType


# Base exception
class LangframeError(Exception):
    """Base exception for all langframe errors."""

    pass


# 1. Configuration Errors
class ConfigurationError(LangframeError):
    """Errors during session configuration or initialization."""

    pass


class SessionError(ConfigurationError):
    """Session lifecycle errors."""

    pass


# 2. Validation Errors
class ValidationError(LangframeError):
    """Invalid usage of public APIs or incorrect arguments."""

    pass


class InvalidExampleCollectionError(ValidationError):
    """Exception raised when a semantic example collection is invalid."""

    pass


# 3. Plan Errors
class PlanError(LangframeError):
    """Errors during logical plan construction and validation."""

    pass


class ColumnNotFoundError(PlanError):
    """Column doesn't exist."""

    def __init__(self, column_name: str, available_columns: List[str]):
        self.column_name = column_name
        self.available_columns = available_columns
        super().__init__(
            f"Column '{column_name}' not found. "
            f"Available columns: {', '.join(sorted(available_columns))}"
        )


class TypeMismatchError(PlanError):
    """Type validation errors."""

    def __init__(self, expected: DataType, actual: DataType, context: str):
        self.expected = expected
        self.actual = actual
        self.context = context
        super().__init__(f"{context}: expected {expected}, got {actual}")


# 4. Catalog Errors
class CatalogError(LangframeError):
    """Catalog and table management errors."""

    pass


class TableNotFoundError(CatalogError):
    """Table doesn't exist."""

    def __init__(self, table_name: str, database: str):
        self.table_name = table_name
        self.database = database
        super().__init__(f"Table '{database}.{table_name}' does not exist")


class TableAlreadyExistsError(CatalogError):
    """Table already exists."""

    def __init__(self, table_name: str, database: Optional[str] = None):
        self.table_name = table_name
        self.database = database
        if database:
            table_ref = f"{database}.{table_name}"
        else:
            table_ref = table_name
        super().__init__(
            f"Table '{table_ref}' already exists. "
            f"Use mode='overwrite' to replace the existing table."
        )


class DatabaseNotFoundError(CatalogError):
    """Database doesn't exist."""

    def __init__(self, database_name: str):
        self.database_name = database_name
        super().__init__(f"Database '{database_name}' does not exist")


class DatabaseAlreadyExistsError(CatalogError):
    """Database already exists."""

    def __init__(self, database_name: str):
        self.database_name = database_name
        super().__init__(f"Database '{database_name}' already exists")


# 5. Execution Errors
class ExecutionError(LangframeError):
    """Errors during physical plan execution."""

    pass


# 6. Lineage Errors
class LineageError(LangframeError):
    """Errors during lineage traversal."""

    pass


# 7. Internal Errors
class InternalError(LangframeError):
    """Internal invariant violations."""

    pass
