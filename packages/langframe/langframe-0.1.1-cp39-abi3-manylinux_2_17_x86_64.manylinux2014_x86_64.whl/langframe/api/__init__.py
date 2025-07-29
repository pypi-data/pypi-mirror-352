"""
Query module for semantic operations on DataFrames.
"""

from langframe.api.catalog import Catalog
from langframe.api.column import Column, ColumnOrName
from langframe.api.dataframe import DataFrame, GroupedData, SemanticExtensions
from langframe.api.io import DataFrameReader, DataFrameWriter
from langframe.api.session import ModelConfig, SemanticConfig, Session, SessionConfig
from langframe.api.types import (
    ArrayType,
    BooleanType,
    DataType,
    DocumentPathType,
    DoubleType,
    EmbeddingType,
    FloatType,
    HtmlType,
    IntegerType,
    JsonType,
    MarkdownType,
    StringType,
    StructField,
    StructType,
    TranscriptType,
    ExtractSchema,
    ExtractSchemaField,
    ExtractSchemaList,
    ColumnField,
    Schema,
    ClassifyExample,
    ClassifyExampleCollection,
    JoinExample,
    JoinExampleCollection,
    MapExample,
    MapExampleCollection,
    PredicateExample,
    PredicateExampleCollection,
)

from langframe.api.functions import (
    semantic,
    text,
    array,
    array_agg,
    array_contains,
    array_size,
    asc,
    asc_nulls_first,
    asc_nulls_last,
    avg,
    coalesce,
    collect_list,
    count,
    desc,
    desc_nulls_first,
    desc_nulls_last,
    max,
    mean,
    min,
    struct,
    sum,
    udf,
    when,
    col,
    lit
)

from langframe.api.lineage import Lineage
from langframe.api.metrics import QueryMetrics, LMMetrics, RMMetrics, OperatorMetrics
from langframe.api.error import InvalidExampleCollectionError


__all__ = [
    # Session
    "Session",
    "SessionConfig",
    "ModelConfig",
    "SemanticConfig",
    # IO
    "DataFrameReader",
    "DataFrameWriter",
    # DataFrame
    "DataFrame",
    "GroupedData",
    "SemanticExtensions",
    # Column
    "Column",
    "ColumnOrName",
    # Catalog
    "Catalog",
    # Types
    "ArrayType",
    "BooleanType",
    "DataType",
    "DocumentPathType",
    "DoubleType",
    "EmbeddingType",
    "FloatType",
    "HtmlType",
    "IntegerType",
    "JsonType",
    "MarkdownType",
    "StringType",
    "StructField",
    "StructType",
    "TranscriptType",
    "ExtractSchema",
    "ExtractSchemaField",
    "ExtractSchemaList",
    "ColumnField",
    "Schema",
    "ClassifyExample",
    "ClassifyExampleCollection",
    "JoinExample",
    "JoinExampleCollection",
    "MapExample",
    "MapExampleCollection",
    "PredicateExample",
    "PredicateExampleCollection",
    # Functions
    "semantic",
    "text",
    "array",
    "array_agg",
    "array_contains",
    "array_size",
    "asc",
    "asc_nulls_first",
    "asc_nulls_last",
    "avg",
    "coalesce",
    "collect_list",
    "count",
    "desc",
    "desc_nulls_first",
    "desc_nulls_last",
    "max",
    "mean",
    "min",
    "struct",
    "sum",
    "udf",
    "when",
    "col",
    "lit",
    # Lineage
    "Lineage",
    # Metrics
    "QueryMetrics",
    "LMMetrics",
    "RMMetrics",
    "OperatorMetrics",
    # Error
    "InvalidExampleCollectionError",
]
