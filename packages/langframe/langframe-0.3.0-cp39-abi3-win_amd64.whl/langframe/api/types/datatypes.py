from abc import ABC, abstractmethod
from typing import List, Literal

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

# === Base Classes ===


class DataType(ABC):
    """
    Base class for all data types.

    You won't instantiate this class directly. Instead, use one of the
    concrete types like `StringType`, `ArrayType`, or `StructType`.

    Used for casting, type validation, and schema inference in the DataFrame API.
    """

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        pass

    def __ne__(self, other: object) -> bool:
        return not self == other

    @abstractmethod
    def __hash__(self):
        return super().__hash__()


class _PrimitiveType(DataType):
    """
    Marker class for all primitive type.
    """

    pass


class _StringBackedType(DataType):
    """
    Marker class for all string-backed logical types.
    """

    pass


# === Singleton Primitive Types ===


@dataclass(frozen=True, config=ConfigDict(arbitrary_types_allowed=True))
class _StringType(_PrimitiveType):
    def __str__(self) -> str:
        return "StringType"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _StringType)


@dataclass(frozen=True, config=ConfigDict(arbitrary_types_allowed=True))
class _IntegerType(_PrimitiveType):
    def __str__(self) -> str:
        return "IntegerType"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _IntegerType)


@dataclass(frozen=True, config=ConfigDict(arbitrary_types_allowed=True))
class _FloatType(_PrimitiveType):
    def __str__(self) -> str:
        return "FloatType"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _FloatType)


@dataclass(frozen=True, config=ConfigDict(arbitrary_types_allowed=True))
class _DoubleType(_PrimitiveType):
    def __str__(self) -> str:
        return "DoubleType"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _DoubleType)


@dataclass(frozen=True, config=ConfigDict(arbitrary_types_allowed=True))
class _BooleanType(_PrimitiveType):
    def __str__(self) -> str:
        return "BooleanType"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _BooleanType)


# === Composite and Parameterized Types ===


@dataclass(frozen=True, config=ConfigDict(arbitrary_types_allowed=True))
class ArrayType(DataType):
    """
    A type representing a homogeneous variable-length array (list) of elements.

    Parameters:
        element_type (DataType): The data type of each element in the array.

    Example:
        >>> ArrayType(StringType)
        ArrayType(element_type=StringType)
    """

    element_type: DataType

    def __str__(self) -> str:
        return f"ArrayType(element_type={self.element_type})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ArrayType) and self.element_type == other.element_type


@dataclass(frozen=True, config=ConfigDict(arbitrary_types_allowed=True))
class StructField:
    """
    A field in a StructType. Fields are nullable.

    Attributes:
        name (str): The name of the field.
        data_type (DataType): The data type of the field.
    """

    name: str
    data_type: DataType

    def __str__(self) -> str:
        return f"StructField(name={self.name}, data_type={self.data_type})"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, StructField)
            and self.name == other.name
            and self.data_type == other.data_type
        )


@dataclass(frozen=True, config=ConfigDict(arbitrary_types_allowed=True))
class StructType(DataType):
    """
    A type representing a struct (record) with named fields.

    Parameters:
        fields (List[StructField]): List of field definitions.

    Example:
        >>> StructType([
        ...     StructField("name", StringType),
        ...     StructField("age", IntegerType),
        ... ])
    """

    struct_fields: List[StructField]

    def __str__(self) -> str:
        return f"StructType(struct_fields=[{', '.join([str(field) for field in self.struct_fields])}])"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, StructType) and self.struct_fields == other.struct_fields
        )


@dataclass(frozen=True)
class EmbeddingType(DataType):
    """
    A type representing a fixed-length embedding vector.

    Parameters:
        dimensions (int): The number of dimensions in the embedding vector.
        embedding_model (str): Name of the model used to generate the embedding.

    Example:
        >>> EmbeddingType(384, embedding_model="text-embedding-3-small")
    """

    dimensions: int
    embedding_model: str

    def __str__(self) -> str:
        return (
            f"EmbeddingType(dimensions={self.dimensions}, model={self.embedding_model})"
        )

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, EmbeddingType)
            and self.dimensions == other.dimensions
            and self.embedding_model == other.embedding_model
        )


# === Tagged String Types ===


@dataclass(frozen=True)
class _MarkdownType(_StringBackedType):
    """
    Represents a markdown document.
    """

    def __str__(self) -> str:
        return "MarkdownType"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _MarkdownType)


@dataclass(frozen=True)
class _HtmlType(_StringBackedType):
    """
    Represents a valid HTML document.
    """

    def __str__(self) -> str:
        return "HtmlType"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _HtmlType)


@dataclass(frozen=True)
class _JsonType(_StringBackedType):
    """
    Represents a valid JSON document.
    """

    def __str__(self) -> str:
        return "JsonType"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _JsonType)


@dataclass(frozen=True)
class TranscriptType(_StringBackedType):
    """
    Represents a string containing a transcript in a specific format.
    """

    format: Literal["generic", "srt"]

    def __str__(self) -> str:
        return f"TranscriptType(format='{self.format}')"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, TranscriptType) and self.format == other.format


@dataclass(frozen=True)
class DocumentPathType(_StringBackedType):
    """
    Represents a string containing a a document's local (file system) or remote (URL) path.
    """

    format: Literal["pdf"] = "pdf"

    def __str__(self) -> str:
        return f"DocumentPathType(format='{self.format}')"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, DocumentPathType) and self.format == other.format


def is_dtype_numeric(dtype: DataType) -> bool:
    """Check if a data type is a numeric type."""
    return dtype in (IntegerType, FloatType, DoubleType)


# === Instances of Singleton Types ===
StringType = _StringType()
"""Represents a UTF-8 encoded string value."""

IntegerType = _IntegerType()
"""Represents a signed integer value."""

FloatType = _FloatType()
"""Represents a 32-bit floating-point number."""

DoubleType = _DoubleType()
"""Represents a 64-bit floating-point number."""

BooleanType = _BooleanType()
"""Represents a boolean value. (True/False)"""

MarkdownType = _MarkdownType()
"""Represents a string containing Markdown-formatted text."""

HtmlType = _HtmlType()
"""Represents a string containing raw HTML markup."""

JsonType = _JsonType()
"""Represents a string containing JSON data."""
