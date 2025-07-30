"""
Physical plan module for internal query execution.

This module contains the physical execution plan classes that implement
the actual execution logic for query operations. These classes are not
part of the public API and should not be used directly.
"""

from langframe._backends.local.physical_plan.aggregate import AggregateExec as AggregateExec
from langframe._backends.local.physical_plan.aggregate import (
    SemanticAggregateExec as SemanticAggregateExec,
)
from langframe._backends.local.physical_plan.base import PhysicalPlan as PhysicalPlan
from langframe._backends.local.physical_plan.join import JoinExec as JoinExec
from langframe._backends.local.physical_plan.join import SemanticJoinExec as SemanticJoinExec
from langframe._backends.local.physical_plan.join import (
    SemanticSimilarityJoinExec as SemanticSimilarityJoinExec,
)
from langframe._backends.local.physical_plan.sink import (
    DuckDBTableSinkExec as DuckDBTableSinkExec,
)
from langframe._backends.local.physical_plan.sink import FileSinkExec as FileSinkExec
from langframe._backends.local.physical_plan.source import (
    DuckDBTableSourceExec as DuckDBTableSourceExec,
)
from langframe._backends.local.physical_plan.source import FileSourceExec as FileSourceExec
from langframe._backends.local.physical_plan.source import (
    InMemorySourceExec as InMemorySourceExec,
)
from langframe._backends.local.physical_plan.transform import (
    DropDuplicatesExec as DropDuplicatesExec,
)
from langframe._backends.local.physical_plan.transform import ExplodeExec as ExplodeExec
from langframe._backends.local.physical_plan.transform import FilterExec as FilterExec
from langframe._backends.local.physical_plan.transform import LimitExec as LimitExec
from langframe._backends.local.physical_plan.transform import ProjectionExec as ProjectionExec
from langframe._backends.local.physical_plan.transform import SortExec as SortExec
from langframe._backends.local.physical_plan.transform import UnionExec as UnionExec
from langframe._backends.local.physical_plan.transform import UnnestExec as UnnestExec

__all__ = [
    "AggregateExec",
    "SemanticAggregateExec",
    "PhysicalPlan",
    "JoinExec",
    "SemanticJoinExec",
    "SemanticSimilarityJoinExec",
    "DuckDBTableSinkExec",
    "FileSinkExec",
    "DuckDBTableSourceExec",
    "FileSourceExec",
    "InMemorySourceExec",
    "DropDuplicatesExec",
    "ExplodeExec",
    "FilterExec",
    "LimitExec",
    "ProjectionExec",
    "SortExec",
    "UnionExec",
    "UnnestExec",
]
