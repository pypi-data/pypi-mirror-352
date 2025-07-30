"""
Logical plan module for query representation.

Note: These classes are not part of the public API and should not be used directly.
"""

from langframe._logical_plan.plans.aggregate import Aggregate
from langframe._logical_plan.plans.aggregate import (
    SemanticAggregate
)
from langframe._logical_plan.plans.base import CacheInfo
from langframe._logical_plan.plans.base import LogicalPlan
from langframe._logical_plan.plans.join import Join
from langframe._logical_plan.plans.join import SemanticJoin
from langframe._logical_plan.plans.join import (
    SemanticSimilarityJoin
)
from langframe._logical_plan.plans.sink import FileSink
from langframe._logical_plan.plans.sink import TableSink
from langframe._logical_plan.plans.source import FileSource
from langframe._logical_plan.plans.source import InMemorySource
from langframe._logical_plan.plans.source import TableSource
from langframe._logical_plan.plans.transform import DropDuplicates
from langframe._logical_plan.plans.transform import Explode
from langframe._logical_plan.plans.transform import Filter
from langframe._logical_plan.plans.transform import Limit
from langframe._logical_plan.plans.transform import Projection
from langframe._logical_plan.plans.transform import Sort
from langframe._logical_plan.plans.transform import Union
from langframe._logical_plan.plans.transform import Unnest as Unnest

__all__ = [
    "Aggregate",
    "SemanticAggregate",
    "CacheInfo",
    "LogicalPlan",
    "Join",
    "SemanticJoin",
    "SemanticSimilarityJoin",
    "FileSink",
    "TableSink",
    "FileSource",
    "InMemorySource",
    "TableSource",
    "DropDuplicates",
    "Explode",
    "Filter",
    "Limit",
    "Projection",
    "Sort",
    "Union",
    "Unnest",
]
