import json
from typing import Optional, Union

from langframe._logical_plan.expressions import (
    ArrayJoinExpr,
    ConcatExpr,
    TextractExpr,
    ByteLengthExpr,
    CountTokensExpr,
    MdApplySchemaExpr,
    MdExistsExpr,
    MdExtractExpr,
    MdStructureExpr,
    MdGroupSchemaExpr,
    MdTransformExpr,
    RecursiveTextChunkExpr,
    RegexpSplitExpr,
    ReplaceExpr,
    SplitPartExpr,
    StringCasingExpr,
    StripCharsExpr,
    StrLengthExpr,
    TextChunkExpr,
    TsFormatExpr,
    TsTransformExpr,
)
from langframe._logical_plan.expressions.text import (
    RecursiveTextChunkExprConfiguration,
    TextChunkExprConfiguration,
)
from langframe.api.column import Column, ColumnOrName
from langframe.api.functions.core import lit
from langframe._backends.local.polars_plugins import ChunkCharacterSet, ChunkLengthFunction
from pydantic import ConfigDict, validate_call


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def extract(column: ColumnOrName, template: str) -> Column:
    """
    Extracts fields from text using a template pattern.

    Args:
        template: Template string with fields marked as ``${field_name:format}``
        column: Input text column to extract from

    Returns:
        Column: A struct column containing the extracted fields

    Examples:
        >>> # Extract name and age from "Name: John, Age: 30"
        >>> df.select(text.extract("Name: ${name:csv}, Age: ${age:none}", "text"))
    """
    return Column._from_logical_expr(
        TextractExpr(Column._from_col_or_name(column)._logical_expr,template)
    )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def md_exists(column: ColumnOrName, selector: str) -> Column:
    """
    Checks if a markdown structure exists in a string column.

    Args:
        column: The input string column or column name to check
        selector: The selector to check for in the markdown structure

    Returns:
        Column: A column containing the boolean result of the check

    Examples:
        >>> df.select(text.md_exists(col("text"), "#"))
    """
    return Column._from_logical_expr(
        MdExistsExpr(Column._from_col_or_name(column)._logical_expr, selector)
    )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def md_extract(column: ColumnOrName, selector: str) -> Column:
    """
    Extracts a markdown structure from a string column.

    Args:
        column: The input string column or column name to extract from
        selector: The selector to extract from the markdown structure

    Returns:
        Column: A column containing the extracted markdown structure

    Examples:
        >>> df.select(text.md_extract(col("text"), "#"))
    """
    return Column._from_logical_expr(
        MdExtractExpr(Column._from_col_or_name(column)._logical_expr, selector)
    )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def md_structure(column: ColumnOrName) -> Column:
    """
    Extracts the markdown structure from a string column.

    Args:
        column: The input string column or column name to extract the markdown structure from

    Returns:
        Column: A column containing the extracted markdown structure

    Examples:
        >>> df.select(text.md_structure(col("text")))
    """
    return Column._from_logical_expr(
        MdStructureExpr(Column._from_col_or_name(column)._logical_expr)
    )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def md_apply_schema(column: ColumnOrName, schema: str) -> Column:
    """
    Applies a schema to a markdown structure.
    """
    # we should also check if the schema is a valid json document
    try:
        json.loads(schema)
    except json.JSONDecodeError as err:
        raise ValueError(
            f"`md_apply_schema` expects a valid JSON schema, but got {schema}."
        ) from err
    return Column._from_logical_expr(
        MdApplySchemaExpr(Column._from_col_or_name(column)._logical_expr, schema)
    )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def md_group_schema(column: ColumnOrName) -> Column:
    """
    Aggregate function: returns the super-set schema of a column containing markdown documents.
    """
    return Column._from_logical_expr(
        MdGroupSchemaExpr(Column._from_col_or_name(column)._logical_expr)
    )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def md_transform(column: ColumnOrName, schema: str) -> Column:
    """
    Transforms a markdown column into a structured column.
    """
    return Column._from_logical_expr(
        MdTransformExpr(Column._from_col_or_name(column)._logical_expr, schema)
    )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def recursive_character_chunk(
    column: ColumnOrName,
    chunk_size: int,
    chunk_overlap_percentage: int,
    chunking_character_set_custom_characters: Optional[list[str]] = None,
):
    r"""
    Chunks a string column into chunks of a specified size (in characters) with an optional overlap.
    The chunking is performed recursively, attempting to preserve the underlying structure of the text
    by splitting on natural boundaries (paragraph breaks, sentence breaks, etc.) to maintain context.
    By default, these characters are ['\n\n', '\n', '.', ';', ':', ' ', '-', ''], but this can be customized.

    Args:
        column: The input string column or column name to chunk
        chunk_size: The size of each chunk in characters
        chunk_overlap_percentage: The overlap between each chunk as a percentage of the chunk size
        chunking_character_set_custom_characters (Optional): List of alternative characters to split on. Note that the characters should be ordered from coarsest to finest desired granularity -- earlier characters in the list should result in fewer overall splits than later characters.
    Returns:
        Column: A column containing the chunks as an array of strings

    Examples:
        >>> # Default chunking, will create chunks of at most 100 characters with 20% overlap
        >>> df.select(text.recursive_character_chunk(col("text"), 100, 20))
        >>> # Custom chunking
        >>> df.select(text.recursive_character_chunk(col("text"), 100, 20, ['\n\n', '\n', '.', ' ', '']))
    """
    if chunking_character_set_custom_characters is None:
        chunking_character_set_name = ChunkCharacterSet.ASCII
    else:
        chunking_character_set_name = ChunkCharacterSet.CUSTOM

    chunk_configuration = RecursiveTextChunkExprConfiguration(
        desired_chunk_size=chunk_size,
        chunk_overlap_percentage=chunk_overlap_percentage,
        chunk_length_function_name=ChunkLengthFunction.CHARACTER,
        chunking_character_set_name=chunking_character_set_name,
        chunking_character_set_custom_characters=chunking_character_set_custom_characters,
    )
    return Column._from_logical_expr(
        RecursiveTextChunkExpr(
            Column._from_col_or_name(column)._logical_expr, chunk_configuration
        )
    )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def recursive_word_chunk(
    column: ColumnOrName,
    chunk_size: int,
    chunk_overlap_percentage: int,
    chunking_character_set_custom_characters: Optional[list[str]] = None,
):
    r"""
    Chunks a string column into chunks of a specified size (in words) with an optional overlap.
    The chunking is performed recursively, attempting to preserve the underlying structure of the text
    by splitting on natural boundaries (paragraph breaks, sentence breaks, etc.) to maintain context.
    By default, these characters are ['\n\n', '\n', '.', ';', ':', ' ', '-', ''], but this can be customized.

    Args:
        column: The input string column or column name to chunk
        chunk_size: The size of each chunk in words
        chunk_overlap_percentage: The overlap between each chunk as a percentage of the chunk size
        chunking_character_set_custom_characters (Optional): List of alternative characters to split on. Note that the characters should be ordered from coarsest to finest desired granularity -- earlier characters in the list should result in fewer overall splits than later characters.

    Returns:
        Column: A column containing the chunks as an array of strings

    Examples:
        >>> # Default chunking, will create chunks of at most 100 words with 20% overlap
        >>> df.select(text.recursive_word_chunk(col("text"), 100, 20))
        >>> # Custom chunking
        >>> df.select(text.recursive_word_chunk(col("text"), 100, 20, ['\n\n', '\n', '.', ' ', '']))
    """
    if chunking_character_set_custom_characters is None:
        chunking_character_set_name = ChunkCharacterSet.ASCII
    else:
        chunking_character_set_name = ChunkCharacterSet.CUSTOM

    chunk_configuration = RecursiveTextChunkExprConfiguration(
        desired_chunk_size=chunk_size,
        chunk_overlap_percentage=chunk_overlap_percentage,
        chunk_length_function_name=ChunkLengthFunction.WORD,
        chunking_character_set_name=chunking_character_set_name,
        chunking_character_set_custom_characters=chunking_character_set_custom_characters,
    )
    return Column._from_logical_expr(
        RecursiveTextChunkExpr(
            Column._from_col_or_name(column)._logical_expr, chunk_configuration
        )
    )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def recursive_token_chunk(
    column: ColumnOrName,
    chunk_size: int,
    chunk_overlap_percentage: int,
    chunking_character_set_custom_characters: Optional[list[str]] = None,
):
    r"""
    Chunks a string column into chunks of a specified size (in tokens) with an optional overlap.
    The chunking is performed recursively, attempting to preserve the underlying structure of the text
    by splitting on natural boundaries (paragraph breaks, sentence breaks, etc.) to maintain context.
    By default, these characters are ['\n\n', '\n', '.', ';', ':', ' ', '-', ''], but this can be customized.

    Args:
        column: The input string column or column name to chunk
        chunk_size: The size of each chunk in tokens
        chunk_overlap_percentage: The overlap between each chunk as a percentage of the chunk size
        chunking_character_set_custom_characters (Optional): List of alternative characters to split on. Note that the characters should be ordered from coarsest to finest desired granularity -- earlier characters in the list should result in fewer overall splits than later characters.

    Returns:
        Column: A column containing the chunks as an array of strings

    Examples:
        >>> # Default chunking, will create chunks of at most 100 tokens with 20% overlap
        >>> df.select(text.recursive_token_chunk(col("text"), 100, 20))
        >>> # Custom chunking
        >>> df.select(text.recursive_token_chunk(col("text"), 100, 20, ['\n\n', '\n', '.', ' ', '']))
    """
    if chunking_character_set_custom_characters is None:
        chunking_character_set_name = ChunkCharacterSet.ASCII
    else:
        chunking_character_set_name = ChunkCharacterSet.CUSTOM

    chunk_configuration = RecursiveTextChunkExprConfiguration(
        desired_chunk_size=chunk_size,
        chunk_overlap_percentage=chunk_overlap_percentage,
        chunk_length_function_name=ChunkLengthFunction.TOKEN,
        chunking_character_set_name=chunking_character_set_name,
        chunking_character_set_custom_characters=chunking_character_set_custom_characters,
    )
    return Column._from_logical_expr(
        RecursiveTextChunkExpr(
            Column._from_col_or_name(column)._logical_expr, chunk_configuration
        )
    )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def character_chunk(
    column: ColumnOrName, chunk_size: int, chunk_overlap_percentage: int = 0
) -> Column:
    """
    Chunks a string column into chunks of a specified size (in characters) with an optional overlap.
    The chunking is done by applying a simple sliding window across the text to create chunks of equal size.
    This approach does not attempt to preserve the underlying structure of the text.

    Args:
        column: The input string column or column name to chunk
        chunk_size: The size of each chunk in characters
        chunk_overlap_percentage: The overlap between chunks as a percentage of the chunk size (Default: 0)

    Returns:
        Column: A column containing the chunks as an array of strings

    Examples:
        >>> df.select(text.character_chunk(col("text"), 100, 20))
    """
    chunk_configuration = TextChunkExprConfiguration(
        desired_chunk_size=chunk_size,
        chunk_overlap_percentage=chunk_overlap_percentage,
        chunk_length_function_name=ChunkLengthFunction.CHARACTER,
    )
    return Column._from_logical_expr(
        TextChunkExpr(
            Column._from_col_or_name(column)._logical_expr, chunk_configuration
        )
    )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def word_chunk(
    column: ColumnOrName, chunk_size: int, chunk_overlap_percentage: int = 0
) -> Column:
    """
    Chunks a string column into chunks of a specified size (in words) with an optional overlap.
    The chunking is done by applying a simple sliding window across the text to create chunks of equal size.
    This approach does not attempt to preserve the underlying structure of the text.

    Args:
        column: The input string column or column name to chunk
        chunk_size: The size of each chunk in words
        chunk_overlap_percentage: The overlap between chunks as a percentage of the chunk size (Default: 0)

    Returns:
        Column: A column containing the chunks as an array of strings

    Examples:
        >>> df.select(text.word_chunk(col("text"), 100, 20))
    """

    chunk_configuration = TextChunkExprConfiguration(
        desired_chunk_size=chunk_size,
        chunk_overlap_percentage=chunk_overlap_percentage,
        chunk_length_function_name=ChunkLengthFunction.WORD,
    )
    return Column._from_logical_expr(
        TextChunkExpr(
            Column._from_col_or_name(column)._logical_expr, chunk_configuration
        )
    )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def token_chunk(
    column: ColumnOrName, chunk_size: int, chunk_overlap_percentage: int = 0
) -> Column:
    """
    Chunks a string column into chunks of a specified size (in tokens) with an optional overlap.
    The chunking is done by applying a simple sliding window across the text to create chunks of equal size.
    This approach does not attempt to preserve the underlying structure of the text.

    Args:
        column: The input string column or column name to chunk
        chunk_size: The size of each chunk in tokens
        chunk_overlap_percentage: The overlap between chunks as a percentage of the chunk size (Default: 0)

    Returns:
        Column: A column containing the chunks as an array of strings

    Examples:
        >>> df.select(text.token_chunk(col("text"), 100, 20))
    """

    chunk_configuration = TextChunkExprConfiguration(
        desired_chunk_size=chunk_size,
        chunk_overlap_percentage=chunk_overlap_percentage,
        chunk_length_function_name=ChunkLengthFunction.TOKEN,
    )
    return Column._from_logical_expr(
        TextChunkExpr(
            Column._from_col_or_name(column)._logical_expr, chunk_configuration
        )
    )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def count_tokens(
    column: ColumnOrName,
):
    r"""
    Returns the number of tokens in a string using OpenAI's cl100k_base encoding (tiktoken).

    Args:
    column (Column): The input string column.

    Returns:
    Column: A column with the token counts for each input string.

    Example:
        >>> df.select(text.count_tokens(col("text")))
    """
    return Column._from_logical_expr(
        CountTokensExpr(Column._from_col_or_name(column)._logical_expr)
    )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def concat(*cols: ColumnOrName) -> Column:
    """
    Concatenates multiple columns or strings into a single string.

    Args:
        *cols: Columns or strings to concatenate

    Returns:
        Column: A column containing the concatenated strings

    Examples:
        >>> df.select(text.concat(col("col1"), lit(" "), col("col2")))
    """
    if not cols:
        raise ValueError("At least one column must be provided to concat method")

    flattened_args = []
    for arg in cols:
        if isinstance(arg, (list, tuple)):
            flattened_args.extend(arg)
        else:
            flattened_args.append(arg)

    flattened_exprs = [
        Column._from_col_or_name(c)._logical_expr for c in flattened_args
    ]
    return Column._from_logical_expr(ConcatExpr(flattened_exprs))


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def infer_transcript_format(column: ColumnOrName) -> Column:
    """
    Detect the format of a transcript and return a string with the format.

    Args:
        column: The input string column or column name to detect the format of

    Returns:
        Column: A column containing the format of the transcript

    Examples:
        >>> df.select(text.infer_transcript_format(col("transcript")))
    """
    return Column._from_logical_expr(
        TsFormatExpr(Column._from_col_or_name(column)._logical_expr)
    )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def parse_transcript_format(column: ColumnOrName, format: str) -> Column:
    """
    Transforms a transcript from text to a structured format.

    Args:
        column: The input string column or column name to transform
        format: The format to transform the transcript to

    Returns:
        Column: A column containing the transformed transcript

    Examples:
        >>> df.select(text.parse_transcript_format(col("transcript"), "srt"))
    """
    return Column._from_logical_expr(
        TsTransformExpr(Column._from_col_or_name(column)._logical_expr, format)
    )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def concat_ws(separator: str, *cols: ColumnOrName) -> Column:
    """
    Concatenates multiple columns or strings into a single string with a separator.

    Args:
        separator: The separator to use
        *cols: Columns or strings to concatenate

    Returns:
        Column: A column containing the concatenated strings

    Examples:
        >>> df.select(text.concat_ws(",", col("col1"), col("col2")))
    """
    if not cols:
        raise ValueError("At least one column must be provided to concat_ws method")

    flattened_args = []
    for arg in cols:
        if isinstance(arg, (list, tuple)):
            flattened_args.extend(arg)
        else:
            flattened_args.append(arg)

    expr_args = []
    for arg in flattened_args:
        expr_args.append(Column._from_col_or_name(arg)._logical_expr)
        expr_args.append(lit(separator)._logical_expr)
    expr_args.pop()
    return Column._from_logical_expr(ConcatExpr(expr_args))


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def array_join(column: ColumnOrName, delimiter: str) -> Column:
    """
    Joins an array of strings into a single string with a delimiter.

    Args:
        column: The column to join
        delimiter: The delimiter to use
    Returns:
            Column: A column containing the joined strings

    Examples:
        >>> df.select(text.array_join(col("array_column"), ","))
    """
    if not isinstance(delimiter, str):
        raise TypeError(
            f"`array_join` expects a string for the delimiter, but got {type(delimiter).__name__}."
        )
    return Column._from_logical_expr(
        ArrayJoinExpr(Column._from_col_or_name(column)._logical_expr, delimiter)
    )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def replace(
    src: ColumnOrName, search: Union[Column, str], replace: Union[Column, str]
) -> Column:
    """Replace all occurrences of a pattern with a new string, treating pattern as a literal string.

    This method creates a new string column with all occurrences of the specified pattern
    replaced with a new string. The pattern is treated as a literal string, not a regular expression.
    If either search or replace is a column expression, the operation is performed dynamically
    using the values from those columns.

    Args:
        src: The input string column or column name to perform replacements on
        search: The pattern to search for (can be a string or column expression)
        replace: The string to replace with (can be a string or column expression)

    Returns:
        Column: A column containing the strings with replacements applied

    Examples:
        >>> # Replace all occurrences of "foo" with "bar"
        >>> df.select(text.replace(col("name"), "foo", "bar"))
        >>> # Replace using patterns from columns
        >>> df.select(text.replace(col("text"), col("search"), col("replace")))
    """
    if isinstance(search, Column):
        search = search._logical_expr
    if isinstance(replace, Column):
        replace = replace._logical_expr
    return Column._from_logical_expr(
        ReplaceExpr(
            Column._from_col_or_name(src)._logical_expr, search, replace, True, -1
        )
    )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def regexp_replace(
    src: ColumnOrName,
    pattern: Union[Column, str],
    replacement: Union[Column, str],
) -> Column:
    r"""Replace all occurrences of a pattern with a new string, treating pattern as a regular expression.

    This method creates a new string column with all occurrences of the specified pattern
    replaced with a new string. The pattern is treated as a regular expression.
    If either pattern or replacement is a column expression, the operation is performed dynamically
    using the values from those columns.

    Args:
        src: The input string column or column name to perform replacements on
        pattern: The regular expression pattern to search for (can be a string or column expression)
        replacement: The string to replace with (can be a string or column expression)

    Returns:
        Column: A column containing the strings with replacements applied

    Examples:
        >>> # Replace all digits with dashes
        >>> df.select(regexp_replace(col("text"), r"\d+", "--"))
        >>> # Replace using patterns from columns
        >>> df.select(regexp_replace(col("text"), col("pattern"), col("replacement")))
    """
    if isinstance(pattern, Column):
        pattern = pattern._logical_expr
    if isinstance(replacement, Column):
        replacement = replacement._logical_expr
    return Column._from_logical_expr(
        ReplaceExpr(
            Column._from_col_or_name(src)._logical_expr,
            pattern,
            replacement,
            False,
            -1,
        )
    )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def split(src: ColumnOrName, pattern: str, limit: int = -1) -> Column:
    r"""Split a string column into an array using a regular expression pattern.

    This method creates an array column by splitting each value in the input string column
    at matches of the specified regular expression pattern.

    Args:
        src: The input string column or column name to split
        pattern: The regular expression pattern to split on
        limit: Maximum number of splits to perform (Default: -1 for unlimited).
              If > 0, returns at most limit+1 elements, with remainder in last element.

    Returns:
        Column: A column containing arrays of substrings

    Examples:
        >>> # Split on whitespace
        >>> df.select(text.split(col("text"), r"\s+"))
        >>> # Split on whitespace, max 2 splits
        >>> df.select(text.split(col("text"), r"\s+", limit=2))
    """
    return Column._from_logical_expr(
        RegexpSplitExpr(Column._from_col_or_name(src)._logical_expr, pattern, limit)
    )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def split_part(
    src: ColumnOrName, delimiter: Union[Column, str], part_number: Union[int, Column]
) -> Column:
    """Split a string and return a specific part using 1-based indexing.

    Splits each string by a delimiter and returns the specified part.
    If the delimiter is a column expression, the split operation is performed dynamically
    using the delimiter values from that column.

    Behavior:
    - If any input is null, returns null
    - If part_number is out of range of split parts, returns empty string
    - If part_number is 0, throws an error
    - If part_number is negative, counts from the end of the split parts
    - If the delimiter is an empty string, the string is not split

    Args:
        src: The input string column or column name to split
        delimiter: The delimiter to split on (can be a string or column expression)
        part_number: Which part to return (1-based, can be an integer or column expression)

    Returns:
        Column: A column containing the specified part from each split string

    Examples:
        >>> # Get second part of comma-separated values
        >>> df.select(text.split_part(col("text"), ",", 2))
        >>> # Get last part using negative index
        >>> df.select(text.split_part(col("text"), ",", -1))
        >>> # Use dynamic delimiter from column
        >>> df.select(text.split_part(col("text"), col("delimiter"), 1))
    """
    if isinstance(part_number, int) and part_number == 0:
        raise ValueError(
            f"`split_part` expects a non-zero integer for the part_number, but got {part_number}."
        )
    if isinstance(delimiter, Column):
        delimiter = delimiter._logical_expr
    if isinstance(part_number, Column):
        part_number = part_number._logical_expr
    return Column._from_logical_expr(
        SplitPartExpr(
            Column._from_col_or_name(src)._logical_expr, delimiter, part_number
        )
    )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def upper(column: ColumnOrName) -> Column:
    """Convert all characters in a string column to uppercase.

    Args:
        column: The input string column to convert to uppercase

    Returns:
        Column: A column containing the uppercase strings

    Examples:
        >>> df.select(text.upper(col("name")))
    """
    return Column._from_logical_expr(
        StringCasingExpr(Column._from_col_or_name(column)._logical_expr, "upper")
    )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def lower(column: ColumnOrName) -> Column:
    """Convert all characters in a string column to lowercase.

    Args:
        column: The input string column to convert to lowercase

    Returns:
        Column: A column containing the lowercase strings

    Examples:
        >>> df.select(text.lower(col("name")))
    """
    return Column._from_logical_expr(
        StringCasingExpr(Column._from_col_or_name(column)._logical_expr, "lower")
    )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def title_case(column: ColumnOrName) -> Column:
    """Convert the first character of each word in a string column to uppercase.

    Args:
        column: The input string column to convert to title case

    Returns:
        Column: A column containing the title case strings

    Examples:
        >>> df.select(text.title_case(col("name")))
    """
    return Column._from_logical_expr(
        StringCasingExpr(Column._from_col_or_name(column)._logical_expr, "title")
    )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def trim(column: ColumnOrName) -> Column:
    """Remove whitespace from both sides of strings in a column.

    This function removes all whitespace characters (spaces, tabs, newlines) from
    both the beginning and end of each string in the column.

    Args:
        column: The input string column or column name to trim

    Returns:
        Column: A column containing the trimmed strings

    Examples:
        >>> # Remove whitespace from both sides
        >>> df.select(text.trim(col("text")))
    """
    return Column._from_logical_expr(
        StripCharsExpr(Column._from_col_or_name(column)._logical_expr, None, "both")
    )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def btrim(col: ColumnOrName, trim: Optional[Union[Column, str]]) -> Column:
    """Remove specified characters from both sides of strings in a column.

    This function removes all occurrences of the specified characters from
    both the beginning and end of each string in the column.
    If trim is a column expression, the characters to remove are determined dynamically
    from the values in that column.

    Args:
        col: The input string column or column name to trim
        trim: The characters to remove from both sides (Default: whitespace)
              Can be a string or column expression.

    Returns:
        Column: A column containing the trimmed strings

    Examples:
        >>> # Remove brackets from both sides
        >>> df.select(text.btrim(col("text"), "[]"))
        >>> # Remove characters specified in a column
        >>> df.select(text.btrim(col("text"), col("chars")))
    """
    if isinstance(trim, Column):
        trim = trim._logical_expr
    return Column._from_logical_expr(
        StripCharsExpr(Column._from_col_or_name(col)._logical_expr, trim, "both")
    )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def ltrim(col: ColumnOrName) -> Column:
    """Remove whitespace from the start of strings in a column.

    This function removes all whitespace characters (spaces, tabs, newlines) from
    the beginning of each string in the column.

    Args:
        col: The input string column or column name to trim

    Returns:
        Column: A column containing the left-trimmed strings

    Examples:
        >>> # Remove leading whitespace
        >>> df.select(text.ltrim(col("text")))
    """
    return Column._from_logical_expr(
        StripCharsExpr(Column._from_col_or_name(col)._logical_expr, None, "left")
    )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def rtrim(col: ColumnOrName) -> Column:
    """Remove whitespace from the end of strings in a column.

    This function removes all whitespace characters (spaces, tabs, newlines) from
    the end of each string in the column.

    Args:
        col: The input string column or column name to trim

    Returns:
        Column: A column containing the right-trimmed strings

    Examples:
        >>> # Remove trailing whitespace
        >>> df.select(text.rtrim(col("text")))
    """
    return Column._from_logical_expr(
        StripCharsExpr(Column._from_col_or_name(col)._logical_expr, None, "right")
    )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def length(column: ColumnOrName) -> Column:
    """Calculate the character length of each string in the column.

    Args:
        column: The input string column to calculate lengths for

    Returns:
        Column: A column containing the length of each string in characters

    Examples:
        >>> # Get the length of each name
        >>> df.select(text.length(col("name")))
    """
    return Column._from_logical_expr(
        StrLengthExpr(Column._from_col_or_name(column)._logical_expr)
    )


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def byte_length(column: ColumnOrName) -> Column:
    """Calculate the byte length of each string in the column.

    Args:
        column: The input string column to calculate byte lengths for

    Returns:
        Column: A column containing the byte length of each string

    Examples:
        >>> # Get the byte length of each name
        >>> df.select(text.byte_length(col("name")))
    """
    return Column._from_logical_expr(
        ByteLengthExpr(Column._from_col_or_name(column)._logical_expr)
    )
