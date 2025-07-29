from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from langframe.api.io.writer import DataFrameWriter
    from langframe._backends import BaseExecution

import logging
import uuid
from typing import Any, Dict, List, Optional, Tuple, Union

import polars as pl
from langframe._logical_plan.expressions import (
    EqualityComparisonExpr,
    NumericComparisonExpr,
    SortExpr,
)
from langframe._logical_plan.plans import (
    CacheInfo,
    DropDuplicates,
    Explode,
    Filter,
    Join,
    Limit,
    LogicalPlan,
    Projection,
    Sort,
    Union as UnionLogicalPlan,
    Unnest,
)
from langframe.api.metrics import QueryMetrics
from langframe.api.column import Column, ColumnOrName
from langframe.api.dataframe._join_utils import (
    normalize_join_type,
    process_column_list_join,
    process_single_column_string_join,
)
from langframe.api.dataframe.grouped_data import GroupedData
from langframe.api.dataframe.semantic_extensions import SemanticExtensions
from langframe.api.functions import col, lit
from langframe.api.lineage import Lineage
from langframe.api.types import Schema
from pydantic import ConfigDict, validate_call

logger = logging.getLogger(__name__)


class DataFrame:
    """A data collection organized into named columns.

    The DataFrame class represents a lazily evaluated computation on data. Operations on
    DataFrame build up a logical query plan that is only executed when an action like
    show(), collect() or count() is called.

    The DataFrame supports method chaining for building complex transformations.

    Examples:
        >>> # Create a DataFrame from a dictionary
        >>> df = session.create_dataframe({"id": [1, 2, 3], "value": ["a", "b", "c"]})
        >>>
        >>> # Chain transformations
        >>> result = df.filter(col("id") > 1).select("id", "value")
        >>>
        >>> # Show results
        >>> result.show()
    """

    _logical_plan: LogicalPlan
    _execution: BaseExecution

    def __new__(cls):
        if cls is DataFrame:
            raise TypeError(
                "Direct construction of DataFrame is not allowed. Use Session.create_dataframe() to create a DataFrame."
            )
        return super().__new__(cls)

    @classmethod
    def _from_logical_plan(
        cls, logical_plan: LogicalPlan, execution: BaseExecution
    ) -> DataFrame:
        """
        Factory method to create DataFrame instances.

        This method is intended for internal use by the Session class and other
        DataFrame methods that need to create new DataFrame instances.

        Args:
            logical_plan: The logical plan for this DataFrame
            session: The session

        Returns:
            A new DataFrame instance
        """
        if not isinstance(logical_plan, LogicalPlan):
            raise TypeError(f"Expected LogicalPlan, got {type(logical_plan)}")
        df = super().__new__(cls)
        df._logical_plan = logical_plan
        df._execution = execution
        return df

    @property
    def semantic(self) -> SemanticExtensions:
        """Interface for semantic operations on the DataFrame"""
        return SemanticExtensions(self)

    @property
    def write(self) -> DataFrameWriter:
        """
        Interface for saving the content of the DataFrame
        Returns:
            DataFrameWriter: Writer interface to write DataFrame
        """
        from langframe.api.io.writer import DataFrameWriter

        return DataFrameWriter(self)

    @property
    def schema(self) -> Schema:
        """Get the schema of this DataFrame.

        Returns:
            Schema: Schema containing field names and data types

        Examples:
            >>> df.schema
            Schema([
                ColumnField('name', StringType),
                ColumnField('age', IntegerType)
            ])
        """
        return self._logical_plan.schema()

    @property
    def columns(self) -> List[str]:
        """Get list of column names.

        Returns:
            List[str]: List of all column names in the DataFrame

        Examples:
            >>> df.columns
            ['name', 'age', 'city']
        """
        return self.schema.column_names()

    def __getitem__(self, col_name: str) -> Column:
        """Enable DataFrame[column_name] syntax for column access.

        Args:
            col_name: Name of the column to access

        Returns:
            Column: Column object for the specified column

        Raises:
            TypeError: If item is not a string

        Examples:
            >>> df["age"]  # Returns Column object for "age"
            >>> df.filter(df["age"] > 25)  # Use in expressions
        """
        if not isinstance(col_name, str):
            raise TypeError(
                f"Column name must be a string, got {type(col_name).__name__}. "
                "Example: df['column_name']"
            )
        if col_name not in self.columns:
            raise KeyError(
                f"Column '{col_name}' does not exist in DataFrame. "
                f"Available columns: {', '.join(self.columns)}\n"
                "Check for typos or case sensitivity issues."
            )

        return col(col_name)

    def __getattr__(self, col_name: str) -> Column:
        """Enable DataFrame.column_name syntax for column access.

        Args:
            col_name: Name of the column to access

        Returns:
            Column: Column object for the specified column

        Raises:
            TypeError: If col_name is not a string

        Examples:
            >>> df.age  # Returns Column object for "age"
            >>> df.filter(df.age > 25)  # Use in expressions
        """
        if not isinstance(col_name, str):
            raise TypeError(
                f"Column name must be a string, got {type(col_name).__name__}. "
                "Example: df.column_name"
            )
        if col_name not in self.columns:
            raise KeyError(
                f"Column '{col_name}' does not exist in DataFrame. "
                f"Available columns: {', '.join(self.columns)}\n"
                "Check for typos or case sensitivity issues."
            )
        return col(col_name)

    def explain(self) -> None:
        """Display the logical plan of the DataFrame"""
        print(str(self._logical_plan))

    def show(self, n: int = 10, explain_analyze: bool = False) -> None:
        """Display the DataFrame content in a tabular form.

        This is an action that triggers computation of the DataFrame.
        The output is printed to stdout in a formatted table.

        Args:
            n: Number of rows to display
            explain_analyze: Whether to print the explain analyze plan
        """
        output, metrics = self._execution.show(self._logical_plan, n)
        logger.info(metrics.get_summary())
        print(output)
        if explain_analyze:
            print(metrics.get_execution_plan_details())

    def collect(self) -> Tuple[pl.DataFrame, QueryMetrics]:
        """Collect the DataFrame content into a Polars DataFrame.

        This is an action that triggers computation of the DataFrame.
        The output is returned as a Polars DataFrame.

        Returns:
            Tuple[pl.DataFrame, QueryMetrics]: A tuple containing the collected Polars DataFrame and the query metrics
        """
        df, metrics = self._execution.collect(self._logical_plan)
        logger.info(metrics.get_summary())
        return df, metrics

    def count(self) -> Tuple[int, QueryMetrics]:
        """Count the number of rows in the DataFrame.

        This is an action that triggers computation of the DataFrame.
        The output is an integer representing the number of rows.

        Returns:
            Tuple[int, QueryMetrics]: A tuple containing the count and the query metrics
        """
        count, metrics = self._execution.count(self._logical_plan)
        logger.info(metrics.get_summary())
        return count, metrics

    def lineage(self) -> Lineage:
        """Create a Lineage object to trace data through transformations.

        The Lineage interface allows you to trace how specific rows are transformed
        through your DataFrame operations, both forwards and backwards through the
        computation graph.

        Returns:
            Lineage: Interface for querying data lineage

        Example:
            ```python
            # Create lineage query
            lineage = df.lineage()

            # Trace specific rows backwards through transformations
            source_rows = lineage.backward(["result_uuid1", "result_uuid2"])

            # Or trace forwards to see outputs
            result_rows = lineage.forward(["source_uuid1"])
            ```

        See Also:
            LineageQuery: Full documentation of lineage querying capabilities
        """
        return Lineage(self._execution.build_lineage(self._logical_plan))

    def persist(self) -> DataFrame:
        """Mark this DataFrame to be persisted after first computation.

        The persisted DataFrame will be cached after its first computation,
        avoiding recomputation in subsequent operations. This is useful for DataFrames
        that are reused multiple times in your workflow.

        Returns:
            DataFrame: Same DataFrame, but marked for persistence

        Example:
            ```python
            # Cache intermediate results for reuse
            filtered_df = (df
                .filter(col("age") > 25)
                .persist()  # Cache these results
            )

            # Both operations will use cached results
            result1 = filtered_df.group_by("department").count()
            result2 = filtered_df.select("name", "salary")
            ```
        """
        table_name = f"cache_{uuid.uuid4().hex}"
        cache_info = CacheInfo(duckdb_table_name=table_name)
        self._logical_plan.set_cache_info(cache_info)
        return self._from_logical_plan(self._logical_plan, self._execution)

    def cache(self) -> DataFrame:
        """Alias for persist(). Mark DataFrame for caching after first computation.

        Returns:
            DataFrame: Same DataFrame, but marked for caching

        See Also:
            persist(): Full documentation of caching behavior
        """
        return self.persist()

    def select(self, *cols: ColumnOrName) -> DataFrame:
        """Projects a set of Column expressions or column names.

        Args:
            *cols: Column expressions to select. Can be:
                - String column names (e.g., "id", "name")
                - Column objects (e.g., col("id"), col("age") + 1)

        Returns:
            DataFrame: A new DataFrame with selected columns

        Examples:
            >>> # Select by column names
            >>> df.select("name", "age")
            >>>
            >>> # Select with expressions
            >>> df.select(col("name"), col("age") + 1)
            >>>
            >>> # Mix strings and expressions
            >>> df.select("name", col("age") * 2)
        """
        exprs = []
        if not cols:
            return self
        for c in cols:
            if isinstance(c, str):
                if c == "*":
                    exprs.extend(col(field)._logical_expr for field in self.columns)
                else:
                    exprs.append(col(c)._logical_expr)
            else:
                exprs.append(c._logical_expr)

        return self._from_logical_plan(
            Projection(self._logical_plan, exprs), self._execution
        )

    def where(self, condition: Column) -> DataFrame:
        """Filters rows using the given condition (alias for filter()).

        Args:
            condition: A Column expression that evaluates to a boolean

        Returns:
            DataFrame: Filtered DataFrame

        See Also:
            filter(): Full documentation of filtering behavior
        """
        return self.filter(condition)

    def filter(self, condition: Column) -> DataFrame:
        """Filters rows using the given condition.

        Args:
            condition:
                - A Column expression

        Returns:
            DataFrame: Filtered DataFrame

        Examples:
            >>> from typedef.sql.functions import col, semantic
            >>> df.filter(col("age") > 25)
            >>> df.filter((col("age") > 25) & semantic.predicate("This {feedback} mentions problems with the user interface or navigation"))
            >>> df.filter((col("age") > 25) & (col("salary") <= 100000))
        """
        return self._from_logical_plan(
            Filter(self._logical_plan, condition._logical_expr),
            self._execution,
        )

    def with_column(self, col_name: str, col: Union[Any, Column]) -> DataFrame:
        """Add a new column or replace an existing column.

        Args:
            col_name: Name of the new column
            col: Column expression or value to assign to the column. If not a Column,
                it will be treated as a literal value.

        Returns:
            DataFrame: New DataFrame with added/replaced column

        Examples:
            >>> # Add literal column
            >>> df.with_column("constant", 1)
            >>>
            >>> # Add computed column
            >>> df.with_column("double_age", col("age") * 2)
            >>>
            >>> # Replace existing column
            >>> df.with_column("age", col("age") + 1)
        """
        exprs = []
        if not isinstance(col, Column):
            col = lit(col)

        for field in self.columns:
            if field != col_name:
                exprs.append(Column._from_column_name(field)._logical_expr)

        # Add the new column with alias
        exprs.append(col.alias(col_name)._logical_expr)

        return self._from_logical_plan(
            Projection(self._logical_plan, exprs), self._execution
        )

    def with_column_renamed(self, col_name: str, new_col_name: str) -> DataFrame:
        """Rename a column. No-op if the column does not exist.

        Args:
            col_name: Name of the column to rename.
            new_col_name: New name for the column.

        Returns:
            DataFrame: New DataFrame with the column renamed.

        Examples:
            >>> df.with_column_renamed("age", "age_in_years")
        """
        exprs = []
        renamed = False

        for field in self.schema.column_fields:
            name = field.name
            if name == col_name:
                exprs.append(col(name).alias(new_col_name)._logical_expr)
                renamed = True
            else:
                exprs.append(col(name)._logical_expr)

        if not renamed:
            return self

        return self._from_logical_plan(
            Projection(self._logical_plan, exprs), self._execution
        )


    def drop(self, *col_names: str) -> DataFrame:
        """Remove one or more columns from this DataFrame.

        Args:
            *col_names: Names of columns to drop.

        Returns:
            DataFrame: New DataFrame without specified columns

        Raises:
            ValueError: If any specified column doesn't exist in the DataFrame
            ValueError: If dropping the columns would result in an empty DataFrame

        Examples:
            >>> # Drop by column names
            >>> df.drop("col1", "col2")
        """
        if not col_names:
            return self

        current_cols = set(self.columns)
        to_drop = set(col_names)
        missing = to_drop - current_cols

        if missing:
            missing_str = (
                f"Column '{next(iter(missing))}'"
                if len(missing) == 1
                else f"Columns {sorted(missing)}"
            )
            raise ValueError(f"{missing_str} not found in DataFrame")

        remaining_cols = [
            col(c)._logical_expr for c in self.columns if c not in to_drop
        ]

        if not remaining_cols:
            raise ValueError("Cannot drop all columns from DataFrame")

        return self._from_logical_plan(
            Projection(self._logical_plan, remaining_cols), self._execution
        )

    def union(self, other: DataFrame) -> DataFrame:
        """
        Return a new DataFrame containing the union of rows in this and another DataFrame.
        This is equivalent to UNION ALL in SQL. To remove duplicates, use drop_duplicates() after union().

        Args:
            other: Another DataFrame with the same schema

        Returns:
            DataFrame: A new DataFrame containing rows from both DataFrames

        Raises:
            ValueError: If the DataFrames have different schemas
            TypeError: If other is not a DataFrame

        Examples:
            >>> df1 = session.create_dataframe({"id": [1, 2], "value": ["a", "b"]})
            >>> df2 = session.create_dataframe({"id": [3, 4], "value": ["c", "d"]})
            >>> df3 = df1.union(df2)
        """
        return self._from_logical_plan(
            UnionLogicalPlan([self._logical_plan, other._logical_plan]),
            self._execution,
        )

    def limit(self, n: int) -> DataFrame:
        """Limits the number of rows to the specified number.

        Args:
            n: Maximum number of rows to return

        Returns:
            DataFrame: DataFrame with at most n rows

        Raises:
            TypeError: If n is not an integer

        Examples:
            >>> # Get first 10 rows
            >>> df.limit(10).show()
        """
        return self._from_logical_plan(Limit(self._logical_plan, n), self._execution)

    def join(
        self,
        other: DataFrame,
        on: Union[str, List[str], Column, List[Column], None] = None,
        how: Optional[str] = "inner",
    ) -> DataFrame:
        """
        Joins this DataFrame with another DataFrame. The Dataframes must have
        no duplicate column names between them.

        Args:
            other: DataFrame to join with
            on: Join condition(s). Can be a column name, list of column names, Column expression, or list of Column expressions
            how: Type of join to perform (inner, outer, left, right, cross, semi, anti)

        Returns:
            DataFrame: Joined DataFrame
        """
        # Handle cross join special case
        if on and how == "cross":
            raise ValueError(
                "CROSS JOIN cannot be used with an ON clause. "
                "For a CROSS JOIN, omit the 'on' parameter entirely since it performs a cartesian product. "
                "If you need to join with specific conditions, use a different join type like 'inner' or 'left'."
            )
        if not how and not on:
            how = "cross"

        # Normalize join type
        how = normalize_join_type(how)

        # Process join conditions
        if not on:
            on = []
        elif isinstance(on, str):
            on = process_single_column_string_join(self, other, on, how)
        elif isinstance(on, Column):
            if not isinstance(
                on._logical_expr, EqualityComparisonExpr
            ) or not isinstance(on._logical_expr, NumericComparisonExpr):
                raise ValueError(
                    "The ON clause must be a boolean expression comparing columns from both DataFrames, "
                    "for example: col('df1.id') == col('df2.id')."
                )
        elif isinstance(on, list):
            on = process_column_list_join(self, other, on, how)
        else:
            raise TypeError(
                f"Invalid join condition type: {type(on)}. The 'on' argument must be one of:\n"
                "  - A string column name (e.g., 'id')\n"
                "  - A Column expression (e.g., col('a') == col('b'))\n"
                "  - A list of string column names (e.g., ['id', 'type'])\n"
                "  - A list of Column expressions\n"
                "  - None for cross joins"
            )

        return self._from_logical_plan(
            Join(self._logical_plan, other._logical_plan, on, how),
            self._execution,
        )

    def explode(self, column: ColumnOrName) -> DataFrame:
        """Create a new row for each element in an array column.

        This operation is useful for flattening nested data structures. For each row in the
        input DataFrame that contains an array/list in the specified column, this method will:
        1. Create N new rows, where N is the length of the array
        2. Each new row will be identical to the original row, except the array column will
           contain just a single element from the original array
        3. Rows with NULL values or empty arrays in the specified column are filtered out

        Args:
            column: Name of array column to explode (as string) or Column expression

        Returns:
            DataFrame: New DataFrame with the array column exploded into multiple rows

        Raises:
            TypeError: If column argument is not a string or Column

        Examples:
            ```python
            # Input DataFrame:
            # | id | tags            | name  |
            # |----|-----------------|-------|
            # | 1  | ["red", "blue"] | Alice |
            # | 2  | ["green"]       | Bob   |
            # | 3  | []              | Carol |
            # | 4  | None            | Dave  |

            df.explode("tags")

            # Result:
            # | id | tags   | name  |
            # |----|--------|-------|
            # | 1  | "red"  | Alice |
            # | 1  | "blue" | Alice |
            # | 2  | "green"| Bob   |
            ```

            # Using column expression:
            df.explode(col("tags"))
        """
        return self._from_logical_plan(
            Explode(self._logical_plan, Column._from_col_or_name(column)._logical_expr),
            self._execution,
        )

    def group_by(self, *cols: ColumnOrName) -> GroupedData:
        """Groups the DataFrame using the specified columns.

        Args:
            *cols: Columns to group by. Can be column names as strings or Column expressions.

        Returns:
            GroupedData: Object for performing aggregations on the grouped data

        Examples:
            >>> # Group by single column
            >>> df.group_by("department").count()
            >>>
            >>> # Group by multiple columns
            >>> df.group_by("department", "location").agg({"salary": "avg"})
            >>>
            >>> # Group by expression
            >>> df.group_by(col("age").cast("int").alias("age_group")).count()
        """
        return GroupedData(self, list(cols) if cols else None)

    def agg(self, *exprs: Union[Column, Dict[str, str]]) -> DataFrame:
        """Aggregate on the entire DataFrame without groups.

        This is equivalent to group_by() without any grouping columns.

        Args:
            *exprs: Aggregation expressions or dictionary of aggregations

        Returns:
            DataFrame: Aggregation results

        Examples:
            >>> # Multiple aggregations
            >>> df.agg(
            ...     count("*").alias("total_rows"),
            ...     avg("salary").alias("avg_salary")
            ... )
            >>>
            >>> # Dictionary style
            >>> df.agg({"salary": "avg", "age": "max"})
        """
        return self.group_by().agg(*exprs)

    def drop_duplicates(
        self,
        subset: Optional[List[str]] = None,
    ) -> DataFrame:
        """Return a DataFrame with duplicate rows removed.

        Args:
            subset (optional): Column names to consider when identifying duplicates. If not provided, all columns are considered.

        Returns:
            DataFrame: A new DataFrame with duplicate rows removed.

        Raises:
            ValueError: If a specified column is not present in the current DataFrame schema.

        Example:
            >>> df = session.create_dataframe(
            ...     {
            ...         "c1": [1, 2, 3, 1],
            ...         "c2": ["a", "a", "a", "a"],
            ...         "c3": ["b", "b", "b", "b"],
            ...     })
            >>>
            >>> # Remove duplicates considering all columns
            >>> df.drop_duplicates(["c1", "c2", "c3"]).show()
            # Result:
            # | c1  | c2  | c3  |
            # |-----|-----|-----|
            # | 1   | a   | b   |
            # | 2   | a   | b   |
            # | 3   | a   | b   |
        """
        exprs = []
        if subset:
            for c in subset:
                if c not in self.columns:
                    raise TypeError(f"Column {c} not found in DataFrame.")
                exprs.append(col(c)._logical_expr)

        return self._from_logical_plan(
            DropDuplicates(self._logical_plan, exprs),
            self._execution,
        )

    def sort(
        self,
        cols: Union[ColumnOrName, List[ColumnOrName], None] = None,
        ascending: Optional[Union[bool, List[bool]]] = None,
    ) -> DataFrame:
        """
        Sort the DataFrame by the specified columns.

        Args:
            cols: Columns to sort by. This can be:
                - A single column name (str)
                - A Column expression (e.g., `col("name")`)
                - A list of column names or Column expressions
                - Column expressions may include sorting directives such as `asc("col")`, `desc("col")`,
                `asc_nulls_last("col")`, etc.
                - If no columns are provided, the operation is a no-op.

            ascending (optional): A boolean or list of booleans indicating sort order.
                - If `True`, sorts in ascending order; if `False`, descending.
                - If a list is provided, its length must match the number of columns.
                - Cannot be used if any of the columns use `asc()`/`desc()` expressions.
                - If not specified and no sort expressions are used, columns will be sorted in ascending order by default.

        Returns:
            DataFrame: A new DataFrame sorted by the specified columns.

        Raises:
            ValueError:
                - If `ascending` is provided and its length does not match `cols`
                - If both `ascending` and column expressions like `asc()`/`desc()` are used
            TypeError:
                - If `cols` is not a column name, Column, or list of column names/Columns
                - If `ascending` is not a boolean or list of booleans

        >>> ### Sort the DataFrame in ascending order.
        >>> df = session.create_dataframe([(2, "Alice"), (5, "Bob")], schema=["age", "name"])
        >>> df.sort(asc("age")).show()
            +---+-----+
            |age| name|
            +---+-----+
            |  2|Alice|
            |  5|  Bob|
            +---+-----+
        >>> ### Sort the DataFrame in descending order.
        >>> df.sort(df.age.desc()).show()
            +---+-----+
            |age| name|
            +---+-----+
            |  5|  Bob|
            |  2|Alice|
            +---+-----+
        >>> df.sort(df.age.desc()).show()
            +---+-----+
            |age| name|
            +---+-----+
            |  5|  Bob|
            |  2|Alice|
            +---+-----+
        >>> df.sort("age", ascending=False).show()
            +---+-----+
            |age| name|
            +---+-----+
            |  5|  Bob|
            |  2|Alice|
            +---+-----+

        >>> ### Specify multiple columns and ascending strategies
        >>> df = session.create_dataframe([(2, "Alice"), (2, "Bob"), (5, "Bob")], schema=["age", "name"])
        >>> df.sort(desc("age"), "name").show()
            +---+-----+
            |age| name|
            +---+-----+
            |  5|  Bob|
            |  2|Alice|
            |  2|  Bob|
            +---+-----+
        >>> df.sort(["age", "name"], ascending=[False, False]).show()
            +---+-----+
            |age| name|
            +---+-----+
            |  5|  Bob|
            |  2|  Bob|
            |  2|Alice|
            +---+-----+
        """
        col_args = cols
        if cols is None:
            return self._from_logical_plan(
                Sort(self._logical_plan, []),
                self._execution,
            )
        elif not isinstance(cols, List):
            col_args = [cols]

        # parse the ascending arguments
        bool_ascending = []
        using_default_ascending = False
        if ascending is None:
            using_default_ascending = True
            bool_ascending = [True] * len(col_args)
        elif isinstance(ascending, bool):
            bool_ascending = [ascending] * len(col_args)
        elif isinstance(ascending, List):
            bool_ascending = ascending
            if len(bool_ascending) != len(cols):
                raise ValueError(
                    f"the list length of ascending sort strategies must match the specified sort columns"
                    f"Got {len(cols)} column expressions and {len(bool_ascending)} ascending strategies. "
                )
        else:
            raise TypeError(
                f"Invalid ascending strategy type: {type(ascending)}.  Must be a boolean or list of booleans."
            )

        # create our list of sort expressions, for each column expression
        # that isn't already provided as a asc()/desc() SortExpr
        sort_exprs = []
        for c, asc_bool in zip(col_args, bool_ascending, strict=True):
            if isinstance(c, ColumnOrName):
                c_expr = Column._from_col_or_name(c)._logical_expr
            else:
                raise TypeError(
                    f"Invalid column type: {type(c).__name__}.  Must be a string or Column Expression."
                )
            if not isinstance(asc_bool, bool):
                raise TypeError(
                    f"Invalid ascending strategy type: {type(asc_bool).__name__}.  Must be a boolean."
                )
            if isinstance(c_expr, SortExpr):
                if not using_default_ascending:
                    raise TypeError(
                        "Cannot specify both asc()/desc() expressions and boolean ascending strategies."
                        f"Got expression: {c_expr} and ascending argument: {bool_ascending}"
                    )
                sort_exprs.append(c_expr)
            else:
                sort_exprs.append(SortExpr(c_expr, ascending=asc_bool))

        return self._from_logical_plan(
            Sort(self._logical_plan, sort_exprs),
            self._execution,
        )

    def order_by(
        self,
        cols: Union[ColumnOrName, List[ColumnOrName], None] = None,
        ascending: Optional[Union[bool, List[bool]]] = None,
    ) -> "DataFrame":
        """Sort the DataFrame by the specified columns.  Alias for sort().

        Returns:
            DataFrame: sorted Dataframe

        See Also:
            sort(): Full documentation of sorting behavior and parameters
        """
        return self.sort(cols, ascending)

    def unnest(self, *col_names: str) -> DataFrame:
        """
        Unnest the specified struct columns into separate columns.

        This operation flattens nested struct data by expanding each field of a struct
        into its own top-level column.

        For each specified column containing a struct:
        1. Each field in the struct becomes a separate column.
        2. New columns are named after the corresponding struct fields.
        3. The new columns are inserted into the DataFrame in place of the original struct column.
        4. The overall column order is preserved.

        Args:
            cols: One or more struct columns to unnest. Each can be a string (column name)
                or a Column expression.

        Returns:
            DataFrame: A new DataFrame with the specified struct columns expanded.

        Raises:
            TypeError: If any argument is not a string or Column.
            ValueError: If a specified column does not contain struct data.

        Examples:
            ```python
            # Input DataFrame:
            # | id | tags                  | name  |
            # |----|-----------------------|-------|
            # | 1  | {"red": 1, "blue": 2} | Alice |
            # | 2  | {"red": 3}            | Bob   |

            df.unnest("tags")

            # Resulting DataFrame:
            # | id | red | blue | name  |
            # |----|-----|------|------|
            # | 1  | 1   | 2    | Alice |
            # | 2  | 3   | None | Bob   |
            ```
        """
        if not col_names:
            return self
        exprs = []
        for c in col_names:
            if c not in self.columns:
                raise TypeError(f"Column {c} not found in DataFrame.")
            exprs.append(col(c)._logical_expr)
        return self._from_logical_plan(
            Unnest(self._logical_plan, exprs),
            self._execution,
        )


DataFrame.show = validate_call(config=ConfigDict(strict=True))(DataFrame.show)
DataFrame.select = validate_call(
    config=ConfigDict(arbitrary_types_allowed=True, strict=True)
)(DataFrame.select)
DataFrame.where = validate_call(
    config=ConfigDict(arbitrary_types_allowed=True, strict=True)
)(DataFrame.where)
DataFrame.filter = validate_call(
    config=ConfigDict(arbitrary_types_allowed=True, strict=True)
)(DataFrame.filter)
DataFrame.with_column = validate_call(
    config=ConfigDict(arbitrary_types_allowed=True, strict=True)
)(DataFrame.with_column)
DataFrame.with_column_renamed = validate_call(
    config=ConfigDict(strict=True)
)(DataFrame.with_column_renamed)
DataFrame.withColumnRenamed = DataFrame.with_column_renamed
DataFrame.withColumn = DataFrame.with_column
DataFrame.drop = validate_call(
    config=ConfigDict(strict=True)
)(DataFrame.drop)
DataFrame.union = validate_call(
    config=ConfigDict(arbitrary_types_allowed=True, strict=True)
)(DataFrame.union)
DataFrame.unionAll = DataFrame.union
DataFrame.limit = validate_call(
    config=ConfigDict(arbitrary_types_allowed=True, strict=True)
)(DataFrame.limit)
DataFrame.join = validate_call(
    config=ConfigDict(arbitrary_types_allowed=True, strict=True)
)(DataFrame.join)
DataFrame.explode = validate_call(
    config=ConfigDict(arbitrary_types_allowed=True, strict=True)
)(DataFrame.explode)
DataFrame.group_by = validate_call(
    config=ConfigDict(arbitrary_types_allowed=True, strict=True)
)(DataFrame.group_by)
DataFrame.groupBy = DataFrame.group_by
DataFrame.groupby = DataFrame.group_by
DataFrame.agg = validate_call(
    config=ConfigDict(arbitrary_types_allowed=True, strict=True)
)(DataFrame.agg)
DataFrame.drop_duplicates = validate_call(
    config=ConfigDict(arbitrary_types_allowed=True, strict=True)
)(DataFrame.drop_duplicates)
DataFrame.dropDuplicates = DataFrame.drop_duplicates
DataFrame.sort = validate_call(
    config=ConfigDict(arbitrary_types_allowed=True, strict=True)
)(DataFrame.sort)
DataFrame.orderBy = DataFrame.order_by
DataFrame.orderBy = DataFrame.order_by
DataFrame.unnest = validate_call(
    config=ConfigDict(strict=True)
)(DataFrame.unnest)
