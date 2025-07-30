"""
Optimizer module for optimizing logical plans.

This module contains the logic for optimizing logical query plans. These classes are not
part of the public API and should not be used directly.
"""

from langframe._logical_plan.optimizer.base import LogicalPlanOptimizer as LogicalPlanOptimizer
from langframe._logical_plan.optimizer.merge_filters_rule import (
    MergeFiltersRule as MergeFiltersRule,
)
from langframe._logical_plan.optimizer.not_filter_pushdown_rule import (
    NotFilterPushdownRule as NotFilterPushdownRule,
)
from langframe._logical_plan.optimizer.semantic_filter_rewrite_rule import (
    SemanticFilterRewriteRule as SemanticFilterRewriteRule,
)
from langframe._logical_plan.optimizer.base import (
    LogicalPlanOptimizerRule as LogicalPlanOptimizerRule,
    OptimizationResult as OptimizationResult,
)

all = [
    "LogicalPlanOptimizerRule",
    "MergeFiltersRule",
    "NotFilterPushdownRule",
    "SemanticFilterRewriteRule",
    "OptimizationResult",
    "LogicalPlanOptimizer",
]
