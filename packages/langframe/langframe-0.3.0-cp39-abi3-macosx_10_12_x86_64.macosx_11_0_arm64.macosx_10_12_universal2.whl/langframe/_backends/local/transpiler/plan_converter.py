from typing import TYPE_CHECKING, List

from langframe._logical_plan.expressions import (
    ColumnExpr,
    EqualityComparisonExpr,
    LogicalExpr,
    NumericComparisonExpr,
)
from langframe._logical_plan.plans import (
    Aggregate,
    DropDuplicates,
    Explode,
    FileSink,
    FileSource,
    Filter,
    InMemorySource,
    Join,
    Limit,
    LogicalPlan,
    Projection,
    SemanticAggregate,
    SemanticJoin,
    SemanticSimilarityJoin,
    Sort,
    TableSink,
    TableSource,
    Union,
    Unnest,
)
from langframe._logical_plan.optimizer import (
    LogicalPlanOptimizer,
    MergeFiltersRule,
    NotFilterPushdownRule,
    SemanticFilterRewriteRule,
)
from langframe._backends.local.physical_plan import (
    AggregateExec,
    DropDuplicatesExec,
    DuckDBTableSinkExec,
    DuckDBTableSourceExec,
    ExplodeExec,
    FileSinkExec,
    FileSourceExec,
    FilterExec,
    InMemorySourceExec,
    JoinExec,
    LimitExec,
    PhysicalPlan,
    ProjectionExec,
    SemanticAggregateExec,
    SemanticJoinExec,
    SemanticSimilarityJoinExec,
    SortExec,
    UnionExec,
    UnnestExec,
)

if TYPE_CHECKING:
    from langframe._backends import LocalSessionState

from langframe._backends.local.transpiler.expr_converter import convert_logical_expr_to_physical_expr


def convert_logical_plan_to_physical_plan(
    logical: LogicalPlan,
    session_state: "LocalSessionState",
) -> PhysicalPlan:
    # Note the order of the rules is important here.
    # NotFilterPushdownRule() and MergeFiltersRule() can be applied
    # in any order, but both must be applied before SemanticFilterRewriteRule()
    # for SemanticFilterRewriteRule() to produce optimal plans.
    logical = (
        LogicalPlanOptimizer(
            [NotFilterPushdownRule(), MergeFiltersRule(), SemanticFilterRewriteRule()]
        )
        .optimize(logical)
        .plan
    )
    if isinstance(logical, Projection):
        child_physical = convert_logical_plan_to_physical_plan(
            logical.children()[0], session_state
        )
        physical_exprs = [
            convert_logical_expr_to_physical_expr(log_expr, session_state.app_name)
            for log_expr in logical.exprs()
        ]
        return ProjectionExec(
            child_physical,
            physical_exprs,
            cache_info=logical.cache_info,
            session_state=session_state,
        )

    elif isinstance(logical, Filter):
        child_physical = convert_logical_plan_to_physical_plan(
            logical.children()[0], session_state
        )
        physical_expr = convert_logical_expr_to_physical_expr(
            logical.predicate(), session_state.app_name
        )

        return FilterExec(
            child_physical,
            physical_expr,
            cache_info=logical.cache_info,
            session_state=session_state,
        )

    elif isinstance(logical, Union):
        children_physical = [
            convert_logical_plan_to_physical_plan(child, session_state)
            for child in logical.children()
        ]
        return UnionExec(
            children_physical,
            cache_info=logical.cache_info,
            session_state=session_state,
        )

    elif isinstance(logical, FileSource):
        return FileSourceExec(
            paths=logical._paths,
            file_format=logical._file_format,
            session_state=session_state,
            options=logical._options,
        )
    elif isinstance(logical, InMemorySource):
        return InMemorySourceExec(
            df=logical._source,
            session_state=session_state,
        )
    elif isinstance(logical, TableSource):
        return DuckDBTableSourceExec(
            table_name=logical._table_name,
            session_state=session_state,
        )
    elif isinstance(logical, Limit):
        child_physical = convert_logical_plan_to_physical_plan(
            logical.children()[0], session_state
        )
        return LimitExec(
            child_physical,
            logical.n,
            cache_info=logical.cache_info,
            session_state=session_state,
        )

    elif isinstance(logical, Aggregate):
        child_physical = convert_logical_plan_to_physical_plan(
            logical.children()[0], session_state
        )
        physical_group_exprs = [
            convert_logical_expr_to_physical_expr(log_expr, session_state.app_name)
            for log_expr in logical.group_exprs()
        ]
        physical_agg_exprs = [
            convert_logical_expr_to_physical_expr(log_expr, session_state.app_name)
            for log_expr in logical.agg_exprs()
        ]
        return AggregateExec(
            child_physical,
            physical_group_exprs,
            physical_agg_exprs,
            cache_info=logical.cache_info,
            session_state=session_state,
        )

    elif isinstance(logical, Join):
        left_logical = logical.children()[0]
        right_logical = logical.children()[1]
        query_str = _build_join_query_str(logical, left_logical, right_logical)

        left_physical = convert_logical_plan_to_physical_plan(
            left_logical, session_state
        )
        right_physical = convert_logical_plan_to_physical_plan(
            right_logical, session_state
        )
        return JoinExec(
            left_physical,
            right_physical,
            query_str,
            cache_info=logical.cache_info,
            session_state=session_state,
        )

    elif isinstance(logical, SemanticJoin):
        left_physical = convert_logical_plan_to_physical_plan(
            logical.children()[0], session_state
        )
        right_physical = convert_logical_plan_to_physical_plan(
            logical.children()[1], session_state
        )
        return SemanticJoinExec(
            left_physical,
            right_physical,
            logical.left_on().name,
            logical.right_on().name,
            logical.join_instruction(),
            cache_info=logical.cache_info,
            session_state=session_state,
            examples=logical.examples(),
        )

    elif isinstance(logical, SemanticSimilarityJoin):
        left_physical = convert_logical_plan_to_physical_plan(
            logical.children()[0], session_state
        )
        right_physical = convert_logical_plan_to_physical_plan(
            logical.children()[1], session_state
        )
        return SemanticSimilarityJoinExec(
            left_physical,
            right_physical,
            (
                logical.left_on().name
                if isinstance(logical.left_on(), ColumnExpr)
                else convert_logical_expr_to_physical_expr(
                    logical.left_on(), session_state.app_name
                )
            ),
            (
                logical.right_on().name
                if isinstance(logical.right_on(), ColumnExpr)
                else convert_logical_expr_to_physical_expr(
                    logical.right_on(), session_state.app_name
                )
            ),
            logical.k(),
            cache_info=logical.cache_info,
            session_state=session_state,
            return_similarity_scores=logical.return_similarity_scores(),
        )

    elif isinstance(logical, SemanticAggregate):
        child_physical = convert_logical_plan_to_physical_plan(
            logical.children()[0], session_state
        )
        physical_group_expr = convert_logical_expr_to_physical_expr(
            logical.group_expr(), session_state.app_name
        )
        physical_agg_exprs = [
            convert_logical_expr_to_physical_expr(log_expr, session_state.app_name)
            for log_expr in logical.agg_exprs()
        ]
        return SemanticAggregateExec(
            child_physical,
            physical_group_expr,
            str(logical.group_expr()),
            physical_agg_exprs,
            logical.num_clusters(),
            cache_info=logical.cache_info,
            session_state=session_state,
        )

    elif isinstance(logical, Explode):
        child_logical = logical.children()[0]
        physical_expr = convert_logical_expr_to_physical_expr(
            logical._expr, session_state.app_name
        )
        child_physical = convert_logical_plan_to_physical_plan(
            child_logical, session_state
        )
        target_field = logical._expr.to_column_field(child_logical)
        return ExplodeExec(
            child_physical,
            physical_expr,
            target_field.name,
            cache_info=logical.cache_info,
            session_state=session_state,
        )

    elif isinstance(logical, DropDuplicates):
        child_logical = logical.children()[0]
        child_physical = convert_logical_plan_to_physical_plan(
            child_logical, session_state
        )

        return DropDuplicatesExec(
            child_physical,
            logical._subset(),
            cache_info=logical.cache_info,
            session_state=session_state,
        )

    elif isinstance(logical, Sort):
        child_logical = logical.children()[0]
        child_physical = convert_logical_plan_to_physical_plan(
            child_logical, session_state
        )

        descending_list = []
        physical_col_exprs = []
        nulls_last_list = []

        for sort_expr in logical.sort_exprs():
            # sort dataframe op will convert all columns to SortExprs
            # read the sort orders and nulls_last info from the sort_expr
            # and convert the underlying column expression to a physical expression
            descending_list.append(not sort_expr.ascending)
            nulls_last_list.append(sort_expr.nulls_last)
            physical_col_exprs.append(
                convert_logical_expr_to_physical_expr(
                    sort_expr.column_expr(), session_state.app_name
                )
            )

        return SortExec(
            child_physical,
            physical_col_exprs,
            descending_list,
            nulls_last_list,
            cache_info=logical.cache_info,
            session_state=session_state,
        )

    elif isinstance(logical, Unnest):
        child_logical = logical.children()[0]
        child_physical = convert_logical_plan_to_physical_plan(
            child_logical, session_state
        )
        return UnnestExec(
            child_physical,
            logical.col_names(),
            cache_info=logical.cache_info,
            session_state=session_state,
        )

    elif isinstance(logical, FileSink):
        child_physical = convert_logical_plan_to_physical_plan(
            logical.child, session_state
        )
        return FileSinkExec(
            child=child_physical,
            path=logical.path,
            file_type=logical.sink_type,
            mode=logical.mode,
            cache_info=logical.cache_info,
            session_state=session_state,
        )

    elif isinstance(logical, TableSink):
        child_physical = convert_logical_plan_to_physical_plan(
            logical.child, session_state
        )
        return DuckDBTableSinkExec(
            child=child_physical,
            table_name=logical.table_name,
            mode=logical.mode,
            cache_info=logical.cache_info,
            session_state=session_state,
            schema=logical.schema(),
        )


def _build_join_query_str(
    logical: Join, left_logical: LogicalPlan, right_logical: LogicalPlan
) -> str:
    left_fields = left_logical.schema().column_fields
    right_fields = right_logical.schema().column_fields
    select_clause = _build_select_clause(
        logical.on(),
        [field.name for field in left_fields],
        [field.name for field in right_fields],
    )
    # trunk-ignore-begin(bandit/B608)
    if logical.how() == "cross":
        return f"SELECT {select_clause} FROM left_df CROSS JOIN right_df"
    else:
        on_clause = _build_on_clause(logical.on())
        return f"SELECT {select_clause} FROM left_df {logical.how()} JOIN right_df ON {on_clause}"
    # trunk-ignore-end(bandit/B608)


def _build_select_clause(
    on: List[LogicalExpr], left_col_names: List[str], right_col_names: List[str]
) -> str:
    coalesce_columns = []
    projections = []

    for expr in on:
        if isinstance(expr, ColumnExpr):
            coalesce_columns.append(expr.name)
    for column in coalesce_columns:
        projections.append(f"COALESCE(left_df.{column}, right_df.{column}) AS {column}")

    for col_name in left_col_names:
        if col_name in coalesce_columns:
            continue
        projections.append(f"left_df.{col_name} AS {col_name}")

    for col_name in right_col_names:
        if col_name in coalesce_columns:
            continue
        elif col_name in left_col_names:
            projections.append(f"right_df.{col_name} AS {col_name}_right")
        else:
            projections.append(f"right_df.{col_name} AS {col_name}")
    return ", ".join(projections)


def _build_on_clause(on: List[LogicalExpr]) -> str:
    conditions = []
    for expr in on:
        if isinstance(expr, ColumnExpr):
            conditions.append(f"left_df.{expr.name} = right_df.{expr.name}")
        elif isinstance(expr, EqualityComparisonExpr) or isinstance(
            expr, NumericComparisonExpr
        ):
            return f"left_df.{expr.left.name} {expr.op} right_df.{expr.right.name}"
        else:
            raise NotImplementedError(f"Unsupported on clause: {type(expr)}")
    return " AND ".join(conditions)
