from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional, Union

from langframe.api.types import (
    JoinExampleCollection,
)

if TYPE_CHECKING:
    from langframe.api.dataframe import DataFrame

import langframe._utils.misc as utils
from langframe._logical_plan.expressions import LiteralExpr
from langframe._logical_plan.plans import (
    SemanticAggregate,
    SemanticJoin,
    SemanticSimilarityJoin,
)
from langframe.api.column import Column, ColumnOrName
from langframe.api.dataframe._base_grouped_data import BaseGroupedData
from langframe.api.functions import col
from langframe.api.types.datatypes import ArrayType, FloatType


class SemGroupedData(BaseGroupedData):
    """Methods for aggregations on a semantically clustered DataFrame."""

    def __init__(self, df: DataFrame, by: ColumnOrName, num_clusters: int):
        super().__init__(df)
        if not isinstance(num_clusters, int) or num_clusters <= 0:
            raise ValueError("num_clusters must be an integer greater than 0")
        if not isinstance(by, ColumnOrName):
            raise TypeError(f"by argument must be a Column or string, got {type(by)}")

        self._num_clusters = num_clusters
        self._by_expr = Column._from_col_or_name(by)._logical_expr

        if isinstance(self._by_expr, LiteralExpr):
            raise ValueError(f"Cannot group by literal value: {by}")

        if self._by_expr.to_column_field(self._df._logical_plan).data_type != ArrayType(
            element_type=FloatType
        ):
            raise ValueError(
                f"Type mismatch: semantic group_by expression must be an embedding column type (List[float])"
                f"got: {self._by_expr.to_column_field(self._df._logical_plan).data_type}"
            )

    def agg(self, *exprs: Union[Column, Dict[str, str]]) -> DataFrame:
        """Compute aggregations on semantically clustered data and return the result as a DataFrame.

        This method applies aggregate functions to data that has been grouped by semantic similarity,
        allowing you to discover patterns and insights across natural language clusters.

        Args:
            *exprs: Aggregation expressions. Can be:
                - Column expressions with aggregate functions (e.g., `count("*")`, `avg("sentiment")`)
                - A dictionary mapping column names to aggregate function names (e.g., {"sentiment": "avg", "count": "sum"})

        Returns:
            DataFrame: A new DataFrame with one row per semantic cluster and columns for aggregated values

        Raises:
            ValueError: If arguments are not Column expressions or a dictionary
            ValueError: If dictionary values are not valid aggregate function names

        Examples:
            >>> # Group customer feedback into 5 clusters and count items per cluster
            >>> df.semantic.group_by("feedback_embeddings", 5).agg(count("*").alias("feedback_count"))
            >>>
            >>> # Analyze multiple metrics across semantic clusters
            >>> df.semantic.group_by("product_review_embeddings", 3).agg(
            ...     count("*").alias("review_count"),
            ...     avg("rating").alias("avg_rating"),
            ...     avg("sentiment_score").alias("avg_sentiment")
            ... )
            >>>
            >>> # Dictionary style for simple aggregations
            >>> df.semantic.group_by("support_ticket_embeddings", 4).agg({"priority": "avg", "resolution_time": "max"})
        """
        self._validate_agg_exprs(*exprs)
        if len(exprs) == 1 and isinstance(exprs[0], dict):
            return self.agg(*self._process_agg_dict(exprs[0]))
        agg_exprs = self._process_agg_exprs(exprs)
        return self._df._from_logical_plan(
            SemanticAggregate(
                self._df._logical_plan, self._by_expr, agg_exprs, self._num_clusters
            ),
            self._df._execution,
        )


class SemanticExtensions:
    """A namespace for semantic dataframe operators."""

    def __init__(self, df: DataFrame):
        self._df = df

    def group_by(self, by: ColumnOrName, num_clusters: int) -> SemGroupedData:
        """
        Semantically group rows by clustering an embedding column into the specified number of centroids.

        This method is useful when you want to uncover natural themes, topics, or intent in embedded free-form text—
        without needing predefined categories.

        Args:
            by: Column containing embeddings to cluster
            num_clusters: Number of semantic clusters to create

        Returns:
            SemGroupedData: Object for performing aggregations on the clustered data.

        Examples:
            >>> # Group customer feedback into 5 clusters
            >>> df.semantic.group_by("feedback_embeddings", 5).agg(count("*"))
            >>>
            >>> # Analyze sentiment by semantic group
            >>> df.semantic.group_by("feedback_embeddings", 5).agg(
            ...     count("*").alias("count"),
            ...     avg("sentiment_score").alias("avg_sentiment")
            ... )
        """
        return SemGroupedData(self._df, by, num_clusters)

    def join(
        self,
        other: DataFrame,
        join_instruction: str,
        examples: Optional[JoinExampleCollection] = None,
    ) -> DataFrame:
        """
        Performs a semantic join between two DataFrames using a natural language predicate
        that evaluates to either true or false for each potential row pair.

        The join works by:
        1. Evaluating the provided join_instruction as a boolean predicate for each possible pair of rows
        2. Including ONLY the row pairs where the predicate evaluates to True in the result set
        3. Excluding all row pairs where the predicate evaluates to False

        The instruction must reference **exactly two columns**, one from each DataFrame,
        using the `:left` and `:right` suffixes to indicate column origin.

        This is useful when row pairing decisions require complex reasoning based on a custom predicate rather than simple equality or similarity matching.

        Args:
            other: The DataFrame to join with.
            join_instruction: A natural language description of how to match values.
                Must include one placeholder from the left DataFrame (e.g. `{resume_summary:left}`)
                and one from the right (e.g. `{job_description:right}`).
                This instruction is evaluated as a boolean predicate - pairs where it's TRUE are included,
                pairs where it's FALSE are excluded.
            examples: Optional JoinExampleCollection containing labeled pairs (left, right, output)
                to guide the semantic join behavior.

        Returns:
            DataFrame: A new DataFrame containing only the row pairs where the join_instruction
                      predicate evaluates to True.

        Raises:
            TypeError: If `other` is not a DataFrame or `join_instruction` is not a string.
            ValueError: If the instruction format is invalid or references invalid columns.

        Examples:
            >>> # Match job listings with candidate resumes based on title/skills
            >>> # Only includes pairs where the predicate evaluates to True
            >>> df_jobs.semantic.join(df_resumes,
            ...     join_instruction="Given a candidate's resume_summary: {resume_summary:left} and a job description: {job_description:right}, does the candidate have the appropriate skills for the job?"
            ... )
            >>> # Improve join quality with examples
            >>> examples = JoinExampleCollection()
            >>> examples.create_example(JoinExample(
            ...     left="5 years experience building backend services in Python using asyncio, FastAPI, and PostgreSQL",
            ...     right="Senior Software Engineer - Backend",
            ...     output=True))  # This pair WILL be included in similar cases
            >>> examples.create_example(JoinExample(
            ...     left="5 years experience with growth strategy, private equity due diligence, and M&A",
            ...     right="Product Manager - Hardware",
            ...     output=False))  # This pair will NOT be included in similar cases
            >>> df_jobs.semantic.join(df_resumes,
            ...     join_instruction="Given a candidate's resume_summary: {resume_summary:left} and a job description: {job_description:right}, does the candidate have the appropriate skills for the job?",
            ...     examples=examples)
        """
        from langframe.api.dataframe.dataframe import DataFrame

        if not isinstance(other, DataFrame):
            raise TypeError(f"other argument must be a DataFrame, got {type(other)}")

        if not isinstance(join_instruction, str):
            raise TypeError(
                f"join_instruction argument must be a string, got {type(join_instruction)}"
            )
        join_columns = utils.parse_instruction(join_instruction)
        if len(join_columns) != 2:
            raise ValueError(
                f"join_instruction must contain exactly two columns, got {len(join_columns)}"
            )
        left_on = None
        right_on = None
        for join_col in join_columns:
            if join_col.endswith(":left"):
                if left_on is not None:
                    raise ValueError(
                        "join_instruction cannot contain multiple :left columns"
                    )
                left_on = col(join_col.split(":")[0])
            elif join_col.endswith(":right"):
                if right_on is not None:
                    raise ValueError(
                        "join_instruction cannot contain multiple :right columns"
                    )
                right_on = col(join_col.split(":")[0])
            else:
                raise ValueError(
                    f"Column '{join_col}' must end with either :left or :right"
                )

        if left_on is None or right_on is None:
            raise ValueError(
                "join_instruction must contain exactly one :left and one :right column"
            )

        return self._df._from_logical_plan(
            SemanticJoin(
                self._df._logical_plan,
                other._logical_plan,
                left_on._logical_expr,
                right_on._logical_expr,
                join_instruction,
                examples,
            ),
            self._df._execution,
        )

    def sim_join(
        self,
        other: DataFrame,
        left_on: ColumnOrName,
        right_on: ColumnOrName,
        k: int = 1,
        return_similarity_scores: bool = False,
    ) -> DataFrame:
        """
        Performs a semantic similarity join between two DataFrames using precomputed text embeddings.

        For each row in the left DataFrame, finds the top `k` most semantically similar rows in the right DataFrame
        based on the cosine similarity between their text embeddings. This is useful for fuzzy matching tasks when exact matches aren't possible.

        Args:
            other: The right-hand DataFrame to join with.
            left_on: Column in this DataFrame containing text embeddings to compare.
            right_on: Column in the other DataFrame containing text embeddings to compare.
            k: Number of most similar matches to return per row from the left DataFrame.
            return_similarity_scores: If True, include a `_similarity_score` column in the output DataFrame
                                    representing the match confidence (cosine similarity).

        Returns:
            DataFrame: A new DataFrame containing matched rows from both sides and optionally similarity scores.

        Raises:
            TypeError: If argument types are incorrect.
            ValueError: If `k` is not positive or if the columns are invalid.

        Examples:
            >>> # Match customer queries to FAQ entries
            >>> df_queries.semantic.sim_join(
            ...     df_faqs,
            ...     left_on=embeddings(col("query_text")),
            ...     right_on=embeddings(col("faq_question")),
            ...     k=1
            ... )

            >>> # Link news headlines to full articles
            >>> df_headlines.semantic.sim_join(
            ...     df_articles,
            ...     left_on=embeddings(col("headline")),
            ...     right_on=embeddings(col("content")),
            ...     k=3,
            ...     return_similarity_scores=True
            ... )

            >>> # Find similar job postings across two sources
            >>> df_linkedin.semantic.sim_join(
            ...     df_indeed,
            ...     left_on=embeddings(col("job_title")),
            ...     right_on=embeddings(col("job_description")),
            ...     k=2
            ... )
        """

        # Validate basic inputs
        from langframe.api.dataframe.dataframe import DataFrame

        if not isinstance(right_on, ColumnOrName):
            raise TypeError(
                f"right_on argument must be a Column or string, got {type(right_on)}"
            )
        if not isinstance(other, DataFrame):
            raise TypeError(f"other argument must be a DataFrame, got {type(other)}")
        if not isinstance(k, int) or k <= 0:
            raise ValueError(f"k must be a positive integer, got {k}")

        def _validate_column(column: ColumnOrName, name: str):
            if column is None:
                raise ValueError(f"{name} argument must not be None")
            if not isinstance(left_on, ColumnOrName):
                raise TypeError(
                    f"{name} argument must be a Column or string, got {type(left_on)}"
                )

        _validate_column(left_on, "left_on")
        _validate_column(right_on, "right_on")

        return self._df._from_logical_plan(
            SemanticSimilarityJoin(
                self._df._logical_plan,
                other._logical_plan,
                Column._from_col_or_name(left_on)._logical_expr,
                Column._from_col_or_name(right_on)._logical_expr,
                k,
                return_similarity_scores,
            ),
            self._df._execution,
        )

    # Spark aliases
    groupBy = group_by
    groupby = group_by
    simJoin = sim_join
