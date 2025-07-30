from __future__ import annotations

from typing import Any, List, Union

from langframe._logical_plan.expressions import (
    AliasExpr,
    ArithmeticExpr,
    BooleanExpr,
    CastExpr,
    ColumnExpr,
    ContainsAnyExpr,
    ContainsExpr,
    EndsWithExpr,
    EqualityComparisonExpr,
    ILikeExpr,
    IndexExpr,
    IsNullExpr,
    LikeExpr,
    LiteralExpr,
    LogicalExpr,
    NotExpr,
    NumericComparisonExpr,
    Operator,
    OtherwiseExpr,
    RLikeExpr,
    SortExpr,
    StartsWithExpr,
    WhenExpr,
)
from langframe.api.types.datatypes import (
    BooleanType,
    DataType,
    FloatType,
    IntegerType,
    StringType,
)
from pydantic import ConfigDict, validate_call


class Column:
    """
    A column expression in a DataFrame.
    """

    _logical_expr: LogicalExpr

    def __new__(cls):
        if cls is Column:
            raise TypeError("Direct construction of Column is not allowed")
        return super().__new__(cls)

    def get_item(self, key: Union[str, int]) -> Column:
        """Access an item in a struct or array column.

        This method allows accessing elements in complex data types:
        - For array columns, the key should be an integer index
        - For struct columns, the key should be a field name

        Args:
            key: The index (for arrays) or field name (for structs) to access

        Returns:
            A Column representing the accessed item

        Examples:
            # Access an array element
            df.select(df["array_column"].get_item(0))

            # Access a struct field
            df.select(df["struct_column"].get_item("field_name"))
        """
        return Column._from_logical_expr(IndexExpr(self._logical_expr, key))

    def __getitem__(self, key: Union[str, int]) -> Column:
        """Access an item in a struct or array column using [] syntax.

        This method provides a convenient syntax for accessing elements in complex data types:
        - For array columns: df["array_column"][0]
        - For struct columns: df["struct_column"]["field_name"]

        Args:
            key: The index (for arrays) or field name (for structs) to access

        Returns:
            A Column representing the accessed item

        Examples:
            # Access an array element
            df.select(df["array_column"][0])

            # Access a struct field
            df.select(df["struct_column"]["field_name"])
        """
        return self.get_item(key)

    def __getattr__(self, name: str) -> Column:
        """Access an attribute of a struct column.

        This method allows accessing fields in struct columns using dot notation.

        Args:
            name: The name of the field to access

        Returns:
            A Column representing the accessed field

        Examples:
            df.select(df["struct_column"].field_name)
        """
        if not isinstance(name, str):
            raise TypeError(
                f"Column attribute access requires a string name, got {type(name).__name__}"
            )
        return self.get_item(name)

    def alias(self, name: str) -> Column:
        """Create an alias for this column.

        This method assigns a new name to the column expression, which is useful
        for renaming columns or providing names for complex expressions.

        Args:
            name: The alias name to assign

        Returns:
            Column with the specified alias

        Examples:
            # Rename a column
            df.select(df["original_name"].alias("new_name"))

            # Name a complex expression
            df.select((df["price"] * df["quantity"]).alias("total_value"))
        """
        return Column._from_logical_expr(AliasExpr(self._logical_expr, name))

    def cast(self, data_type: DataType) -> Column:
        """Cast the column to a new data type.

        This method creates an expression that casts the column to a specified data type.
        The casting behavior depends on the source and target types:

        Primitive type casting:
        - Numeric types (IntegerType, FloatType, DoubleType) can be cast between each other
        - Numeric types can be cast to/from StringType
        - BooleanType can be cast to/from numeric types and StringType
        - StringType cannot be directly cast to BooleanType (will raise TypeError)

        Complex type casting:
        - ArrayType can only be cast to another ArrayType (with castable element types)
        - StructType can only be cast to another StructType (with matching/castable fields)
        - Primitive types cannot be cast to/from complex types

        Args:
            data_type: The target DataType to cast the column to

        Returns:
            A Column representing the casted expression

        Examples:
            # Cast integer to string
            df.select(df["int_col"].cast(StringType))

            # Cast array of integers to array of strings
            df.select(df["int_array"].cast(ArrayType(element_type=StringType)))

            # Cast struct fields to different types
            new_type = StructType([
                StructField("id", StringType),
                StructField("value", FloatType)
            ])
            df.select(df["data_struct"].cast(new_type))

        Raises:
            TypeError: If the requested cast operation is not supported
        """
        return Column._from_logical_expr(CastExpr(self._logical_expr, data_type))

    def desc(self) -> Column:
        """Apply descending order to this column during a dataframe sort or order_by.

        This method creates an expression that provides a column and sort order to the sort function

        Returns:
            A Column expression that provides a column and sort order to the sort function

        Examples:
            df.sort(desc("age")).show()
            df.sort(df.age.desc()).show()
        """
        return Column._from_logical_expr(SortExpr(self._logical_expr, ascending=False))

    def desc_nulls_first(self) -> Column:
        """Apply descending order putting nulls first to this column during a dataframe sort or order_by.

        This method creates an expression that provides a column and sort order to the sort function

        Returns:
            A Column expression that provides a column and sort order to the sort function

        Examples:
            df.sort(desc_nulls_first("age")).show()
            df.sort(df.age.desc_nulls_first()).show()
        """
        return Column._from_logical_expr(
            SortExpr(self._logical_expr, ascending=False, nulls_last=False)
        )

    def desc_nulls_last(self) -> Column:
        """Apply descending order putting nulls last to this column during a dataframe sort or order_by.

        This method creates an expression that provides a column and sort order to the sort function

        Returns:
            A Column expression that provides a column and sort order to the sort function

        Examples:
            df.sort(desc_nulls_last("age")).show()
            df.sort(df.age.desc_nulls_last()).show()
        """
        return Column._from_logical_expr(
            SortExpr(self._logical_expr, ascending=False, nulls_last=True)
        )

    def asc(self) -> Column:
        """Apply ascending order to this column during a dataframe sort or order_by.

        This method creates an expression that provides a column and sort order to the sort function

        Returns:
            A Column expression that provides a column and sort order to the sort function

        Examples:
            df.sort(asc("age")).show()
            df.sort(df.age.asc()).show()
        """
        return Column._from_logical_expr(SortExpr(self._logical_expr, ascending=True))

    def asc_nulls_first(self) -> Column:
        """Apply ascending order putting nulls first to this column during a dataframe sort or order_by.

        This method creates an expression that provides a column and sort order to the sort function

        Returns:
            A Column expression that provides a column and sort order to the sort function

        Examples:
            df.sort(asc_nulls_first("age")).show()
            df.sort(df.age.asc_nulls_first()).show()
        """
        return Column._from_logical_expr(
            SortExpr(self._logical_expr, ascending=True, nulls_last=False)
        )

    def asc_nulls_last(self) -> Column:
        """Apply ascending order putting nulls last to this column during a dataframe sort or order_by.

        This method creates an expression that provides a column and sort order to the sort function

        Returns:
            A Column expression that provides a column and sort order to the sort function

        Examples:
            df.sort(asc_nulls_last("age")).show()
            df.sort(df.age.asc_nulls_last()).show()
        """
        return Column._from_logical_expr(
            SortExpr(self._logical_expr, ascending=True, nulls_last=True)
        )

    def contains(self, other: Union[str, Column]) -> Column:
        """Check if the column contains a substring.

        This method creates a boolean expression that checks if each value in the column
        contains the specified substring. The substring can be either a literal string
        or a column expression.

        Args:
            other: The substring to search for (can be a string or column expression)

        Returns:
            Column: A boolean column indicating whether each value contains the substring

        Examples:
            >>> # Find rows where name contains "john"
            >>> df.filter(df["name"].contains("john"))
            >>> # Find rows where text contains a dynamic pattern
            >>> df.filter(df["text"].contains(col("pattern")))
        """
        if isinstance(other, str):
            return Column._from_logical_expr(ContainsExpr(self._logical_expr, other))
        else:
            return Column._from_logical_expr(
                ContainsExpr(self._logical_expr, other._logical_expr)
            )

    def contains_any(self, others: List[str], case_insensitive: bool = True) -> Column:
        """Check if the column contains any of the specified substrings.

        This method creates a boolean expression that checks if each value in the column
        contains any of the specified substrings. The matching can be case-sensitive or
        case-insensitive.

        Args:
            others: List of substrings to search for
            case_insensitive: Whether to perform case-insensitive matching (default: True)

        Returns:
            Column: A boolean column indicating whether each value contains any substring

        Examples:
            >>> # Find rows where name contains "john" or "jane" (case-insensitive)
            >>> df.filter(df["name"].contains_any(["john", "jane"]))
            >>> # Case-sensitive matching
            >>> df.filter(df["name"].contains_any(["John", "Jane"], case_insensitive=False))
        """
        return Column._from_logical_expr(
            ContainsAnyExpr(self._logical_expr, others, case_insensitive)
        )

    def starts_with(self, other: Union[str, Column]) -> Column:
        """Check if the column starts with a substring.

        This method creates a boolean expression that checks if each value in the column
        starts with the specified substring. The substring can be either a literal string
        or a column expression.

        Args:
            other: The substring to check for at the start (can be a string or column expression)

        Returns:
            Column: A boolean column indicating whether each value starts with the substring

        Examples:
            >>> # Find rows where name starts with "Mr"
            >>> df.filter(df["name"].starts_with("Mr"))
            >>> # Find rows where text starts with a dynamic pattern
            >>> df.filter(df["text"].starts_with(col("prefix")))

        Raises:
            ValueError: If the substring starts with a regular expression anchor (^)
        """
        if isinstance(other, str):
            return Column._from_logical_expr(StartsWithExpr(self._logical_expr, other))
        else:
            return Column._from_logical_expr(
                StartsWithExpr(self._logical_expr, other._logical_expr)
            )

    def ends_with(self, other: Union[str, Column]) -> Column:
        """Check if the column ends with a substring.

        This method creates a boolean expression that checks if each value in the column
        ends with the specified substring. The substring can be either a literal string
        or a column expression.

        Args:
            other: The substring to check for at the end (can be a string or column expression)

        Returns:
            Column: A boolean column indicating whether each value ends with the substring

        Examples:
            >>> # Find rows where email ends with "@gmail.com"
            >>> df.filter(df["email"].ends_with("@gmail.com"))
            >>> # Find rows where text ends with a dynamic pattern
            >>> df.filter(df["text"].ends_with(col("suffix")))

        Raises:
            ValueError: If the substring ends with a regular expression anchor ($)
        """
        if isinstance(other, str):
            return Column._from_logical_expr(EndsWithExpr(self._logical_expr, other))
        else:
            return Column._from_logical_expr(
                EndsWithExpr(self._logical_expr, other._logical_expr)
            )

    def rlike(self, other: str) -> Column:
        r"""Check if the column matches a regular expression pattern.

        This method creates a boolean expression that checks if each value in the column
        matches the specified regular expression pattern. The pattern must be a literal string
        and cannot be a column expression.

        Args:
            other: The regular expression pattern to match against

        Returns:
            Column: A boolean column indicating whether each value matches the pattern

        Examples:
            >>> # Find rows where phone number matches pattern
            >>> df.filter(df["phone"].rlike(r"^\d{3}-\d{3}-\d{4}$"))
            >>> # Find rows where text contains word boundaries
            >>> df.filter(df["text"].rlike(r"\bhello\b"))
        """
        return Column._from_logical_expr(RLikeExpr(self._logical_expr, other))

    def like(self, other: str) -> Column:
        r"""Check if the column matches a SQL LIKE pattern.

        This method creates a boolean expression that checks if each value in the column
        matches the specified SQL LIKE pattern. The pattern must be a literal string
        and cannot be a column expression.

        SQL LIKE pattern syntax:
        - % matches any sequence of characters
        - _ matches any single character

        Args:
            other: The SQL LIKE pattern to match against

        Returns:
            Column: A boolean column indicating whether each value matches the pattern

        Examples:
            >>> # Find rows where name starts with "J" and ends with "n"
            >>> df.filter(df["name"].like("J%n"))
            >>> # Find rows where code matches specific pattern
            >>> df.filter(df["code"].like("A_B%"))
        """
        return Column._from_logical_expr(LikeExpr(self._logical_expr, other))

    def ilike(self, other: str) -> Column:
        r"""Check if the column matches a SQL LIKE pattern (case-insensitive).

        This method creates a boolean expression that checks if each value in the column
        matches the specified SQL LIKE pattern, ignoring case. The pattern must be a literal string
        and cannot be a column expression.

        SQL LIKE pattern syntax:
        - % matches any sequence of characters
        - _ matches any single character

        Args:
            other: The SQL LIKE pattern to match against

        Returns:
            Column: A boolean column indicating whether each value matches the pattern

        Examples:
            >>> # Find rows where name starts with "j" and ends with "n" (case-insensitive)
            >>> df.filter(df["name"].ilike("j%n"))

            >>> # Find rows where code matches pattern (case-insensitive)
            >>> df.filter(df["code"].ilike("a_b%"))
        """
        return Column._from_logical_expr(ILikeExpr(self._logical_expr, other))

    def is_null(self) -> Column:
        """Check if the column contains NULL values.

        This method creates an expression that evaluates to TRUE when the column value is NULL.

        Returns:
            A Column representing a boolean expression that is TRUE when this column is NULL

        Examples:
            >>> # Filter rows where a column is NULL
            >>> df.filter(df["some_column"].is_null())

            >>> # Use in a complex condition
            >>> df.filter(df["col1"].is_null() | (df["col2"] > 100))
        """
        return Column._from_logical_expr(IsNullExpr(self._logical_expr, True))

    def is_not_null(self) -> Column:
        """Check if the column contains non-NULL values.

        This method creates an expression that evaluates to TRUE when the column value is not NULL.

        Returns:
            A Column representing a boolean expression that is TRUE when this column is not NULL

        Examples:
            >>> # Filter rows where a column is not NULL
            >>> df.filter(df["some_column"].is_not_null())

            >>> # Use in a complex condition
            >>> df.filter(df["col1"].is_not_null() & (df["col2"] <= 50))
        """
        return Column._from_logical_expr(IsNullExpr(self._logical_expr, False))

    def when(self, condition: Column, value: Column) -> Column:
        """
        Evaluates a list of conditions and returns one of multiple possible result expressions. If Column.otherwise() is not invoked, None is returned for unmatched conditions.  Otherwise() will return for rows with None inputs.

        Args:
            condition: A boolean Column expression
            value: A literal value or Column expression to return if the condition is true

        Returns:
            A Column expression representing whether each element of Column matches the condition

        Raises:
            TypeError: If the condition is not a boolean Column expression

        Examples:
            >>> df = session.createDataFrame(
                {"age": [2,5] }, {"name": ["Alice", "Bob"]})
            >>> df.select(df.name, when(col("age") > 3, 1).otherwise(0).alias("case_result")).show()
            +-----+-----------+
            | name|case_result|
            +-----+-----------+
            |Alice|          0|
            |  Bob|          1|
            +-----+-----------+
        """
        return Column._from_logical_expr(
            WhenExpr(self._logical_expr, condition._logical_expr, value._logical_expr)
        )

    def otherwise(self, value: Column) -> Column:
        """
        Evaluates a list of conditions and returns one of multiple possible result expressions. If Column.otherwise() is not invoked, None is returned for unmatched conditions.  Otherwise() will return for rows with None inputs.

        Args:
            value: A literal value or Column expression to return

        Returns:
            A Column expression representing whether each element of Column is not matched by any previous conditions

        Examples:
            >>> df = session.createDataFrame(
                {"age": [2,5] }, {"name": ["Alice", "Bob"]})
            >>> df.select(df.name, when(col("age") > 3, 1).otherwise(0).alias("case_result")).show()
            +-----+-----------+
            | name|case_result|
            +-----+-----------+
            |Alice|          0|
            |  Bob|          1|
            +-----+-----------+
        """
        return Column._from_logical_expr(
            OtherwiseExpr(self._logical_expr, value._logical_expr)
        )

    @classmethod
    def _from_logical_expr(cls, logical_expr: LogicalExpr) -> Column:
        if not isinstance(logical_expr, LogicalExpr):
            raise TypeError(f"Expected LogicalExpr, got {type(logical_expr)}")
        column = super().__new__(cls)
        column._logical_expr = logical_expr
        return column

    @classmethod
    def _from_column_name(cls, col_name: str):
        if not isinstance(col_name, str):
            raise TypeError(f"Expected str, got {type(col_name)}")
        column = super().__new__(cls)
        column._logical_expr = ColumnExpr(col_name)
        return column

    @classmethod
    def _from_col_or_name(cls, col_or_name: ColumnOrName) -> Column:
        if isinstance(col_or_name, Column):
            return col_or_name
        else:
            return cls._from_column_name(col_or_name)

    @classmethod
    def _infer_literal_type(self, value: Any) -> DataType:
        if isinstance(value, bool):
            return BooleanType
        elif isinstance(value, int):
            return IntegerType
        elif isinstance(value, float):
            return FloatType
        elif isinstance(value, str):
            return StringType
        else:
            raise TypeError(f"Unsupported literal type: {type(value)}")

    def _create_binary_expr(
        self, other: Any, op: Operator, expr_class, reverse=False
    ) -> Column:
        if isinstance(other, Column):
            right_expr = other._logical_expr
        else:
            right_expr = LiteralExpr(other, self._infer_literal_type(other))
        if reverse:
            return Column._from_logical_expr(
                expr_class(right_expr, self._logical_expr, op)
            )
        else:
            return Column._from_logical_expr(
                expr_class(self._logical_expr, right_expr, op)
            )

    def __invert__(self) -> Column:
        return Column._from_logical_expr(NotExpr(self._logical_expr))

    def __gt__(self, other: Any) -> Column:
        return self._create_binary_expr(other, Operator.GT, NumericComparisonExpr)

    def __ge__(self, other: Any) -> Column:
        return self._create_binary_expr(other, Operator.GTEQ, NumericComparisonExpr)

    def __lt__(self, other: Any) -> Column:
        return self._create_binary_expr(other, Operator.LT, NumericComparisonExpr)

    def __le__(self, other: Any) -> Column:
        return self._create_binary_expr(other, Operator.LTEQ, NumericComparisonExpr)

    def __eq__(self, other: Any) -> Column:
        return self._create_binary_expr(other, Operator.EQ, EqualityComparisonExpr)

    def __ne__(self, other: Any) -> Column:
        return self._create_binary_expr(other, Operator.NOT_EQ, EqualityComparisonExpr)

    def __and__(self, other: Column) -> Column:
        return self._create_binary_expr(other, Operator.AND, BooleanExpr)

    def __rand__(self, other: Column) -> Column:
        return self & other

    def __or__(self, other: Column) -> Column:
        return self._create_binary_expr(other, Operator.OR, BooleanExpr)

    def __ror__(self, other: Column) -> Column:
        return self | other

    def __add__(self, other: Any) -> Column:
        return self._create_binary_expr(other, Operator.PLUS, ArithmeticExpr)

    def __radd__(self, other: Any) -> Column:
        return self._create_binary_expr(
            other, Operator.PLUS, ArithmeticExpr, reverse=True
        )

    def __sub__(self, other: Any) -> Column:
        return self._create_binary_expr(other, Operator.MINUS, ArithmeticExpr)

    def __rsub__(self, other: Any) -> Column:
        return self._create_binary_expr(
            other, Operator.MINUS, ArithmeticExpr, reverse=True
        )

    def __mul__(self, other: Any) -> Column:
        return self._create_binary_expr(other, Operator.MULTIPLY, ArithmeticExpr)

    def __rmul__(self, other) -> Column:
        return self * other

    def __truediv__(self, other: Any) -> Column:
        return self._create_binary_expr(other, Operator.DIVIDE, ArithmeticExpr)

    def __rtruediv__(self, other: Any) -> Column:
        return self._create_binary_expr(
            other, Operator.DIVIDE, ArithmeticExpr, reverse=True
        )

    def __bool__(self):
        raise TypeError(
            "Cannot use Column in boolean context. Use '&', '|', or '~', not 'and', 'or', or 'not'."
        )


ColumnOrName = Union[Column, str]

Column.get_item = validate_call(config=ConfigDict(strict=True))(Column.get_item)
Column.getItem = Column.get_item
Column.alias = validate_call(config=ConfigDict(strict=True))(Column.alias)
Column.cast = validate_call(
    config=ConfigDict(strict=True, arbitrary_types_allowed=True)
)(Column.cast)
Column.contains = validate_call(
    config=ConfigDict(strict=True, arbitrary_types_allowed=True)
)(Column.contains)
Column.contains_any = validate_call(config=ConfigDict(strict=True))(Column.contains_any)
Column.starts_with = validate_call(
    config=ConfigDict(strict=True, arbitrary_types_allowed=True)
)(Column.starts_with)
Column.ends_with = validate_call(
    config=ConfigDict(strict=True, arbitrary_types_allowed=True)
)(Column.ends_with)
Column.rlike = validate_call(config=ConfigDict(strict=True))(Column.rlike)
Column.like = validate_call(config=ConfigDict(strict=True))(Column.like)
Column.ilike = validate_call(config=ConfigDict(strict=True))(Column.ilike)
Column.when = validate_call(
    config=ConfigDict(strict=True, arbitrary_types_allowed=True)
)(Column.when)
Column.otherwise = validate_call(
    config=ConfigDict(strict=True, arbitrary_types_allowed=True)
)(Column.otherwise)
