from functools import singledispatch
from io import StringIO
from typing import TYPE_CHECKING, Any, Callable, Dict, List

if TYPE_CHECKING:
    from langframe._backends import LocalSessionState

import polars as pl
from langframe._backends.local.template import TemplateFormatReader
from langframe._logical_plan.expressions import (
    AggregateExpr,
    AliasExpr,
    AnalyzeSentimentExpr,
    ArithmeticExpr,
    ArrayContainsExpr,
    ArrayExpr,
    ArrayJoinExpr,
    ArrayLengthExpr,
    AvgExpr,
    BooleanExpr,
    ByteLengthExpr,
    CastExpr,
    CoalesceExpr,
    ColumnExpr,
    ConcatExpr,
    ContainsAnyExpr,
    ContainsExpr,
    CountExpr,
    CountTokensExpr,
    EmbeddingsExpr,
    EndsWithExpr,
    EqualityComparisonExpr,
    ILikeExpr,
    IndexExpr,
    IsNullExpr,
    LikeExpr,
    ListExpr,
    LiteralExpr,
    LogicalExpr,
    MaxExpr,
    MdApplySchemaExpr,
    MdExistsExpr,
    MdExtractExpr,
    MdGroupSchemaExpr,
    MdStructureExpr,
    MdTransformExpr,
    MinExpr,
    NotExpr,
    NumericComparisonExpr,
    Operator,
    OtherwiseExpr,
    RecursiveTextChunkExpr,
    RegexpSplitExpr,
    ReplaceExpr,
    RLikeExpr,
    SemanticClassifyExpr,
    SemanticExtractExpr,
    SemanticMapExpr,
    SemanticPredExpr,
    SemanticReduceExpr,
    SortExpr,
    SplitPartExpr,
    StartsWithExpr,
    StringCasingExpr,
    StripCharsExpr,
    StrLengthExpr,
    StructExpr,
    SumExpr,
    TextChunkExpr,
    TextractExpr,
    TsFormatExpr,
    TsTransformExpr,
    UDFExpr,
    WhenExpr,
)
from langframe._backends.local.semantic_operators import (
    AnalyzeSentiment,
)
from langframe._backends.local.semantic_operators import Classify as SemanticClassify
from langframe._backends.local.semantic_operators import Extract as SemanticExtract
from langframe._backends.local.semantic_operators import Map as SemanticMap
from langframe._backends.local.semantic_operators import Predicate as SemanticPredicate
from langframe._backends.local.semantic_operators import Reduce as SemanticReduce
from langframe.api.types import (
    ArrayType,
    StringType,
    StructField,
    StructType,
)
from langframe._utils.schema import (
    convert_custom_dtype_to_polars,
    convert_pydantic_type_to_custom_struct_type,
)
from langframe._logical_plan.expressions import ChunkLengthFunction


@singledispatch
def _convert_expr(logical: LogicalExpr, app_name: str) -> pl.Expr:
    """Convert a logical expression to a Polars physical expression without aliasing."""
    raise NotImplementedError(f"Conversion not implemented for {type(logical)}")


def _with_alias(expr: pl.Expr, logical: Any) -> pl.Expr:
    """Add an alias to a Polars expression based on the string representation of the logical expression."""
    return expr.alias(str(logical))


def convert_logical_expr_to_physical_expr(
    logical: LogicalExpr, app_name: str
) -> pl.Expr:
    """Convert a logical expression to a Polars physical expression with aliasing."""
    result = _convert_expr(logical, app_name)
    if isinstance(logical, AliasExpr) or isinstance(logical, ColumnExpr):
        return result
    return _with_alias(result, logical)


@_convert_expr.register
def _convert_column_expr(logical: ColumnExpr, app_name: str) -> pl.Expr:
    return pl.col(logical.name)


@_convert_expr.register
def _convert_literal_expr(logical: LiteralExpr, app_name: str) -> pl.Expr:
    return pl.lit(logical.literal)


@_convert_expr.register
def _convert_alias_expr(logical: AliasExpr, app_name: str) -> pl.Expr:
    base_expr = convert_logical_expr_to_physical_expr(logical.expr, app_name)
    return base_expr.alias(logical.name)


@_convert_expr.register
def _convert_arithmetic_expr(logical: ArithmeticExpr, app_name: str) -> pl.Expr:
    left = convert_logical_expr_to_physical_expr(logical.left, app_name)
    right = convert_logical_expr_to_physical_expr(logical.right, app_name)

    op_handlers = {
        Operator.PLUS: lambda left, right: left + right,
        Operator.MINUS: lambda left, right: left - right,
        Operator.MULTIPLY: lambda left, right: left * right,
        Operator.DIVIDE: lambda left, right: left / right,
    }

    if logical.op in op_handlers:
        return _with_alias(op_handlers[logical.op](left, right), logical)
    else:
        raise NotImplementedError(f"Unsupported arithmetic operator: {logical.op}")


@_convert_expr.register
def _convert_sort_expr(logical: SortExpr, app_name: str) -> pl.Expr:
    raise ValueError(
        "asc and desc() expressions can only be used in sort or order_by operations."
    )


def _handle_comparison_expr(logical, app_name: str) -> pl.Expr:
    left = convert_logical_expr_to_physical_expr(logical.left, app_name)
    right = convert_logical_expr_to_physical_expr(logical.right, app_name)

    op_handlers = {
        Operator.EQ: lambda left, right: left == right,
        Operator.NOT_EQ: lambda left, right: left != right,
        Operator.GT: lambda left, right: left > right,
        Operator.GTEQ: lambda left, right: left >= right,
        Operator.LT: lambda left, right: left < right,
        Operator.LTEQ: lambda left, right: left <= right,
        Operator.AND: lambda left, right: left & right,
        Operator.OR: lambda left, right: left | right,
    }

    if logical.op in op_handlers:
        return _with_alias(op_handlers[logical.op](left, right), logical)
    else:
        raise NotImplementedError(f"Unsupported comparison operator: {logical.op}")


@_convert_expr.register(BooleanExpr)
@_convert_expr.register(EqualityComparisonExpr)
@_convert_expr.register(NumericComparisonExpr)
def _convert_comparison_expr(logical, app_name: str) -> pl.Expr:
    result = _handle_comparison_expr(logical, app_name)
    return result


@_convert_expr.register(AggregateExpr)
def _convert_aggregate_expr(logical: AggregateExpr, app_name: str) -> pl.Expr:
    agg_handlers = {
        SumExpr: lambda expr: convert_logical_expr_to_physical_expr(
            expr.expr, app_name
        ).sum(),
        AvgExpr: lambda expr: convert_logical_expr_to_physical_expr(
            expr.expr, app_name
        ).mean(),
        MinExpr: lambda expr: convert_logical_expr_to_physical_expr(
            expr.expr, app_name
        ).min(),
        MaxExpr: lambda expr: convert_logical_expr_to_physical_expr(
            expr.expr, app_name
        ).max(),
        CountExpr: lambda expr: (
            pl.len()
            if isinstance(expr.expr, LiteralExpr)
            else convert_logical_expr_to_physical_expr(expr.expr, app_name).count()
        ),
        ListExpr: lambda expr: convert_logical_expr_to_physical_expr(
            expr.expr, app_name
        ),
        MdGroupSchemaExpr: lambda expr: convert_logical_expr_to_physical_expr(
            expr.expr, app_name
        ).markdown.group_schema(),
    }

    for expr_type, handler in agg_handlers.items():
        if isinstance(logical, expr_type):
            return handler(logical)

    if isinstance(logical, SemanticReduceExpr):

        def sem_reduce_fn(batch: pl.Series) -> str:
            return SemanticReduce(
                input=batch,
                user_instruction=logical.instruction,
                app_name=app_name,
            ).execute()

        struct = pl.struct(
            [
                convert_logical_expr_to_physical_expr(expr, app_name)
                for expr in logical.exprs
            ]
        )
        return struct.map_batches(
            sem_reduce_fn, return_dtype=pl.Utf8, agg_list=True, returns_scalar=True
        )

    raise NotImplementedError(f"Unsupported aggregate function: {type(logical)}")


@_convert_expr.register(UDFExpr)
def _convert_udf_expr(logical: UDFExpr, app_name: str) -> pl.Expr:
    struct = pl.struct(
        [convert_logical_expr_to_physical_expr(arg, app_name) for arg in logical.args]
    )
    converted_udf = _convert_udf_to_map_elements(
        logical.func, [str(arg) for arg in logical.args]
    )
    return struct.map_elements(
        converted_udf,
        return_dtype=convert_custom_dtype_to_polars(logical.return_type),
    )


@_convert_expr.register(StructExpr)
def _convert_struct_expr(logical: StructExpr, app_name: str) -> pl.Expr:
    return pl.struct(
        [convert_logical_expr_to_physical_expr(arg, app_name) for arg in logical.args]
    )


@_convert_expr.register(ArrayExpr)
def _convert_array_expr(logical: ArrayExpr, app_name: str) -> pl.Expr:
    return pl.concat_list(
        [convert_logical_expr_to_physical_expr(arg, app_name) for arg in logical.args]
    )


@_convert_expr.register(IndexExpr)
def _convert_index_expr(logical: IndexExpr, app_name: str) -> pl.Expr:
    base_expr = convert_logical_expr_to_physical_expr(logical.expr, app_name)
    if isinstance(logical.index, int):
        return base_expr.list.get(logical.index, null_on_oob=True)
    elif isinstance(logical.index, str):
        return base_expr.struct.field(str(logical.index))
    else:
        raise NotImplementedError(f"Unsupported index key type: {type(logical.index)}")


@_convert_expr.register(TsFormatExpr)
def _convert_ts_format_expr(logical: TsFormatExpr, app_name: str) -> pl.Expr:
    physical_expr = convert_logical_expr_to_physical_expr(logical.expr, app_name)
    return physical_expr.transcript.format()


@_convert_expr.register(TsTransformExpr)
def _convert_ts_transform_expr(logical: TsTransformExpr, app_name: str) -> pl.Expr:
    physical_expr = convert_logical_expr_to_physical_expr(logical.expr, app_name)
    return physical_expr.transcript.transform(logical.format)


@_convert_expr.register(TextractExpr)
def _convert_textract_expr(logical: TextractExpr, app_name: str) -> pl.Expr:
    col_expr = convert_logical_expr_to_physical_expr(logical.input_expr, app_name)
    struct_expr = pl.struct([col_expr])

    def extract_fields(row: Any) -> Dict[str, any]:
        text = str(row[str(logical.input_expr)])
        if not text:
            return {col: None for col in logical.parsed_template.columns}
        reader = TemplateFormatReader(logical.parsed_template, StringIO(text))
        result_dict = reader.read_row() or {
            col: None for col in logical.parsed_template.columns
        }
        return {
            col: result_dict.get(col, None) for col in logical.parsed_template.columns
        }

    return_struct_type = StructType(
        struct_fields=[
            StructField(name=col, data_type=StringType)
            for col in logical.parsed_template.columns
        ]
    )

    return struct_expr.map_elements(
        extract_fields,
        return_dtype=convert_custom_dtype_to_polars(return_struct_type),
    )


@_convert_expr.register(SemanticMapExpr)
def _convert_semantic_map_expr(logical: SemanticMapExpr, app_name: str) -> pl.Expr:
    def sem_map_fn(batch: pl.Series) -> pl.Series:
        expanded_df = pl.DataFrame(
            {field: batch.struct.field(field) for field in batch.struct.fields}
        )

        return SemanticMap(
            input=expanded_df,
            user_instruction=logical.instruction,
            app_name=app_name,
            examples=logical.examples,
        ).execute()

    struct = pl.struct(
        [
            convert_logical_expr_to_physical_expr(expr, app_name)
            for expr in logical.exprs
        ]
    )
    return struct.map_batches(sem_map_fn, return_dtype=pl.String)


@_convert_expr.register(RecursiveTextChunkExpr)
def _convert_text_chunk_expr(logical: RecursiveTextChunkExpr, app_name: str) -> pl.Expr:
    text_col = convert_logical_expr_to_physical_expr(logical.input_expr, app_name)
    kwargs = dict(logical.chunking_configuration)
    return text_col.chunking.recursive(**kwargs)


@_convert_expr.register(CountTokensExpr)
def _count_tokens(logical: CountTokensExpr, app_name: str) -> pl.Expr:
    text_col = convert_logical_expr_to_physical_expr(logical.input_expr, app_name)
    return text_col.tokenization.count_tokens()


@_convert_expr.register(TextChunkExpr)
def _convert_token_chunk_expr(logical: TextChunkExpr, app_name: str) -> pl.Expr:
    import tiktoken

    model = "cl100k_base"
    encoding = tiktoken.get_encoding(model)
    config = logical.chunk_configuration
    chunk_overlap = round(
        config.chunk_overlap_percentage * (config.desired_chunk_size / 100.0)
    )
    window_size = config.desired_chunk_size - chunk_overlap

    def token_chunk_udf(val: Any) -> List[str]:
        if val is None:
            return []
        tokens = encoding.encode(val)
        chunks = [
            tokens[i : i + config.desired_chunk_size]
            for i in range(0, len(tokens), window_size)
        ]
        return [encoding.decode(chunk) for chunk in chunks]

    def word_chunk_udf(val: Any) -> List[str]:
        if val is None:
            return []
        words = val.split()
        step = config.desired_chunk_size - chunk_overlap
        chunks = [
            words[i : i + config.desired_chunk_size] for i in range(0, len(words), step)
        ]
        return [" ".join(chunk) for chunk in chunks]

    def character_chunk_udf(val: Any) -> List[str]:
        if val is None:
            return []
        characters = list(val)
        step = config.desired_chunk_size - chunk_overlap
        chunks = [
            characters[i : i + config.desired_chunk_size]
            for i in range(0, len(characters), step)
        ]
        return ["".join(chunk) for chunk in chunks]

    chunk_udfs = {
        ChunkLengthFunction.TOKEN: token_chunk_udf,
        ChunkLengthFunction.WORD: word_chunk_udf,
        ChunkLengthFunction.CHARACTER: character_chunk_udf,
    }

    output_dtype = convert_custom_dtype_to_polars(ArrayType(element_type=StringType))
    return convert_logical_expr_to_physical_expr(
        logical.input_expr, app_name
    ).map_elements(
        chunk_udfs[config.chunk_length_function_name], return_dtype=output_dtype
    )


@_convert_expr.register(SemanticExtractExpr)
def _convert_semantic_extract_expr(
    logical: SemanticExtractExpr, app_name: str
) -> pl.Expr:
    def sem_ext_fn(batch: pl.Series) -> pl.Series:
        return SemanticExtract(
            input=batch,
            schema=logical.schema,
            app_name=app_name,
        ).execute()

    return convert_logical_expr_to_physical_expr(logical.expr, app_name).map_batches(
        sem_ext_fn,
        return_dtype=convert_custom_dtype_to_polars(
            convert_pydantic_type_to_custom_struct_type(logical.schema)
        ),
    )


@_convert_expr.register(SemanticPredExpr)
def _convert_semantic_pred_expr(logical: SemanticPredExpr, app_name: str) -> pl.Expr:
    def sem_predicate_fn(batch: pl.Series) -> pl.Series:
        expanded_df = pl.DataFrame(
            {field: batch.struct.field(field) for field in batch.struct.fields}
        )
        return SemanticPredicate(
            input=expanded_df,
            user_instruction=logical.instruction,
            app_name=app_name,
        ).execute()

    struct = pl.struct(
        [
            convert_logical_expr_to_physical_expr(expr, app_name)
            for expr in logical.exprs
        ]
    )
    return struct.map_batches(sem_predicate_fn, return_dtype=pl.Boolean)


@_convert_expr.register(SemanticClassifyExpr)
def _convert_semantic_classify_expr(
    logical: SemanticClassifyExpr, app_name: str
) -> pl.Expr:
    def sem_classify_fn(batch: pl.Series) -> pl.Series:
        return SemanticClassify(
            input=batch,
            labels=logical.labels,
            app_name=app_name,
            examples=logical.examples,
        ).execute()

    return convert_logical_expr_to_physical_expr(logical.expr, app_name).map_batches(
        sem_classify_fn, return_dtype=pl.Utf8
    )


@_convert_expr.register(AnalyzeSentimentExpr)
def _convert_semantic_analyze_sentiment_expr(
    logical: AnalyzeSentimentExpr, app_name: str
) -> pl.Expr:
    def sem_sentiment_fn(batch: pl.Series) -> pl.Series:
        return AnalyzeSentiment(
            input=batch,
            app_name=app_name,
        ).execute()

    return convert_logical_expr_to_physical_expr(logical.expr, app_name).map_batches(
        sem_sentiment_fn, return_dtype=pl.Utf8
    )


@_convert_expr.register(ArrayJoinExpr)
def _convert_array_join_expr(logical: ArrayJoinExpr, app_name: str) -> pl.Expr:
    return convert_logical_expr_to_physical_expr(logical.expr, app_name).list.join(
        logical.delimiter
    )


@_convert_expr.register(ContainsExpr)
def _convert_contains_expr(logical: ContainsExpr, app_name: str) -> pl.Expr:
    physical_expr = convert_logical_expr_to_physical_expr(logical.expr, app_name)
    substr_expr = (
        convert_logical_expr_to_physical_expr(logical.substr, app_name)
        if isinstance(logical.substr, LogicalExpr)
        else pl.lit(logical.substr)
    )
    return physical_expr.str.contains(pattern=substr_expr, literal=True)


@_convert_expr.register(ContainsAnyExpr)
def _convert_contains_any_expr(logical: ContainsAnyExpr, app_name: str) -> pl.Expr:
    physical_expr = convert_logical_expr_to_physical_expr(logical.expr, app_name)
    return physical_expr.str.contains_any(
        patterns=logical.substrs, ascii_case_insensitive=logical.case_insensitive
    )


# Group like/regex expressions together
def _handle_regex_like_expr(
    logical, app_name: str, pattern_field="pattern", literal=False
):
    physical_expr = convert_logical_expr_to_physical_expr(logical.expr, app_name)
    pattern = getattr(logical, pattern_field)
    return physical_expr.str.contains(pattern=pattern, literal=literal)


@_convert_expr.register(RLikeExpr)
@_convert_expr.register(LikeExpr)
@_convert_expr.register(ILikeExpr)
def _convert_like_expr(logical, app_name: str) -> pl.Expr:
    return _handle_regex_like_expr(logical, app_name)


@_convert_expr.register(StartsWithExpr)
def _convert_starts_with_expr(logical: StartsWithExpr, app_name: str) -> pl.Expr:
    physical_expr = convert_logical_expr_to_physical_expr(logical.expr, app_name)
    substr_expr = (
        convert_logical_expr_to_physical_expr(logical.substr, app_name)
        if isinstance(logical.substr, LogicalExpr)
        else pl.lit(logical.substr)
    )
    return physical_expr.str.starts_with(prefix=substr_expr)


@_convert_expr.register(EndsWithExpr)
def _convert_ends_with_expr(logical: EndsWithExpr, app_name: str) -> pl.Expr:
    physical_expr = convert_logical_expr_to_physical_expr(logical.expr, app_name)
    substr_expr = (
        convert_logical_expr_to_physical_expr(logical.substr, app_name)
        if isinstance(logical.substr, LogicalExpr)
        else pl.lit(logical.substr)
    )
    return physical_expr.str.ends_with(suffix=substr_expr)


@_convert_expr.register(EmbeddingsExpr)
def _convert_embeddings_expr(logical: EmbeddingsExpr, app_name: str) -> pl.Expr:
    physical_expr = convert_logical_expr_to_physical_expr(logical.expr, app_name)

    def embeddings_fn(batch: pl.Series) -> pl.Series:
        from langframe._backends import LocalSessionManager

        session_state: LocalSessionState = (
            LocalSessionManager().get_existing_session(app_name)._session_state
        )
        if session_state.embedding_model is None:
            raise ValueError(
                "An embedding model must be configured to use semantic.embed(). "
                "Please configure a valid embedding model in your SessionConfig."
            )
        FILTERED_RESULTS_COLUMN = "filtered_results"
        results = session_state.embedding_model.get_embeddings(batch.to_list())
        df = pl.DataFrame({"results": results})
        return df.with_columns(
            pl.when(pl.col("results").arr.first().is_nan())
            .then(None)
            .otherwise(pl.col("results"))
            .cast(pl.List(pl.Float32))
            .alias(FILTERED_RESULTS_COLUMN)
        )[FILTERED_RESULTS_COLUMN]

    return physical_expr.map_batches(embeddings_fn, return_dtype=pl.List(pl.Float32))


@_convert_expr.register(SplitPartExpr)
def _convert_split_part_expr(logical: SplitPartExpr, app_name: str) -> pl.Expr:
    physical_expr = convert_logical_expr_to_physical_expr(logical.expr, app_name)
    is_delimiter_column = isinstance(logical.delimiter, LogicalExpr)
    is_part_number_column = isinstance(logical.part_number, LogicalExpr)

    # If neither delimiter nor part_number is a column, use the standard split_part
    if not is_delimiter_column and not is_part_number_column:
        # arr.get is zero indexed, split_part is 1-based per the Spark spec
        if logical.part_number > 0:
            pl_index = logical.part_number - 1
        else:
            pl_index = logical.part_number

        return (
            physical_expr.str.split(logical.delimiter)
            .list.get(index=pl_index, null_on_oob=True)
            .fill_null(
                ""
            )  # spark semantics expect an empty string if part number is out of range
        )

    # Convert expressions for delimiter and part number
    delimiter_expr = (
        convert_logical_expr_to_physical_expr(logical.delimiter, app_name)
        if is_delimiter_column
        else pl.lit(logical.delimiter)
    )
    part_number_expr = (
        convert_logical_expr_to_physical_expr(logical.part_number, app_name)
        if is_part_number_column
        else pl.lit(logical.part_number)
    )

    # If only delimiter is a column, we can pass it directly to split
    if is_delimiter_column and not is_part_number_column:
        # Convert part number from 1-based to 0-based for positive numbers
        pl_index = (
            logical.part_number - 1 if logical.part_number > 0 else logical.part_number
        )
        return (
            physical_expr.str.split(delimiter_expr)
            .list.get(index=pl_index, null_on_oob=True)
            .fill_null("")
        )

    # If part_number is a column, use over expressions
    # First split using the delimiter (either column or literal)
    split_expr = physical_expr.str.split(delimiter_expr)

    # Convert from 1-based to 0-based indexing for positive numbers
    part_expr = (
        pl.when(part_number_expr.first() > 0)
        .then(part_number_expr.first() - 1)
        .otherwise(part_number_expr.first())
    )

    # Get the part and handle out of range with empty string
    return (
        split_expr.list.get(part_expr, null_on_oob=True)
        .fill_null("")
        .over(part_number_expr)
    )


@_convert_expr.register(ArrayContainsExpr)
def _convert_array_contains_expr(logical: ArrayContainsExpr, app_name: str) -> pl.Expr:
    array_expr = convert_logical_expr_to_physical_expr(logical.expr, app_name)
    element_expr = convert_logical_expr_to_physical_expr(logical.other, app_name)

    return array_expr.list.contains(element_expr)


@_convert_expr.register(RegexpSplitExpr)
def _convert_regexp_split_expr(logical: RegexpSplitExpr, app_name: str) -> pl.Expr:
    physical_expr = convert_logical_expr_to_physical_expr(logical.expr, app_name)
    delimiter = "|||SPLIT|||"
    if logical.limit > 0:
        split_ready = physical_expr.str.replace(
            pattern=logical.pattern,
            value=delimiter,
            literal=False,
            n=logical.limit - 1,
        )
        return split_ready.str.split(by=delimiter)
    else:
        split_ready = physical_expr.str.replace_all(
            pattern=logical.pattern, value=delimiter, literal=False
        )
        return split_ready.str.split(by=delimiter)


@_convert_expr.register(StripCharsExpr)
def _convert_strip_chars_expr(logical: StripCharsExpr, app_name: str) -> pl.Expr:
    physical_expr = convert_logical_expr_to_physical_expr(logical.expr, app_name)
    chars_expr = (
        convert_logical_expr_to_physical_expr(logical.chars, app_name)
        if isinstance(logical.chars, LogicalExpr)
        else pl.lit(logical.chars)
    )

    strip_methods = {
        "both": physical_expr.str.strip_chars,
        "left": physical_expr.str.strip_chars_start,
        "right": physical_expr.str.strip_chars_end,
    }

    if logical.side in strip_methods:
        return strip_methods[logical.side](characters=chars_expr)
    else:
        raise NotImplementedError(f"Unsupported side: {logical.side}")


@_convert_expr.register(StringCasingExpr)
def _convert_string_casing_expr(logical: StringCasingExpr, app_name: str) -> pl.Expr:
    physical_expr = convert_logical_expr_to_physical_expr(logical.expr, app_name)

    case_methods = {
        "upper": physical_expr.str.to_uppercase,
        "lower": physical_expr.str.to_lowercase,
        "title": physical_expr.str.to_titlecase,
    }

    if logical.case in case_methods:
        return case_methods[logical.case]()
    else:
        raise NotImplementedError(f"Unsupported case: {logical.case}")


@_convert_expr.register(ReplaceExpr)
def _convert_replace_expr(logical: ReplaceExpr, app_name: str) -> pl.Expr:
    physical_expr = convert_logical_expr_to_physical_expr(logical.expr, app_name)
    is_search_column = isinstance(logical.search, LogicalExpr)
    is_replace_column = isinstance(logical.replacement, LogicalExpr)

    # If neither search nor replacement is a column, use the standard string replace
    if not is_search_column and not is_replace_column:
        if logical.replacement_count == -1:
            return physical_expr.str.replace_all(
                pattern=logical.search,
                value=logical.replacement,
                literal=logical.literal,
            )
        else:
            return physical_expr.str.replace(
                pattern=logical.search,
                value=logical.replacement,
                literal=logical.literal,
                n=logical.replacement_count,
            )

    # Handle column-based replacement
    if is_search_column:
        search_expr = convert_logical_expr_to_physical_expr(logical.search, app_name)
        pattern_expr = search_expr.first()
    else:
        search_expr = pl.lit(logical.search)
        pattern_expr = search_expr

    if is_replace_column:
        replacement_expr = convert_logical_expr_to_physical_expr(
            logical.replacement, app_name
        )
    else:
        replacement_expr = pl.lit(logical.replacement)

    if logical.replacement_count == -1:
        result = physical_expr.str.replace_all(
            pattern=pattern_expr,
            value=replacement_expr,
            literal=logical.literal,
        )
    else:
        result = physical_expr.str.replace(
            pattern=pattern_expr,
            value=replacement_expr,
            literal=logical.literal,
            n=logical.replacement_count,
        )

    if is_search_column:
        return result.over(search_expr)
    else:
        return result


@_convert_expr.register(MdExistsExpr)
def _convert_md_exists_expr(logical: MdExistsExpr, app_name: str) -> pl.Expr:
    physical_expr = convert_logical_expr_to_physical_expr(logical.input_expr, app_name)
    return physical_expr.markdown.exists(selector=logical.selector)


@_convert_expr.register(MdExtractExpr)
def _convert_md_extract_expr(logical: MdExtractExpr, app_name: str) -> pl.Expr:
    physical_expr = convert_logical_expr_to_physical_expr(logical.input_expr, app_name)
    return physical_expr.markdown.extract(selector=logical.selector)


@_convert_expr.register(MdStructureExpr)
def _convert_md_structure_expr(logical: MdStructureExpr, app_name: str) -> pl.Expr:
    physical_expr = convert_logical_expr_to_physical_expr(logical.input_expr, app_name)
    return physical_expr.markdown.structure()


@_convert_expr.register(MdApplySchemaExpr)
def _convert_md_apply_schema_expr(logical: MdApplySchemaExpr, app_name: str) -> pl.Expr:
    physical_expr = convert_logical_expr_to_physical_expr(logical.input_expr, app_name)
    return physical_expr.markdown.apply_schema(logical.schema)


@_convert_expr.register(MdTransformExpr)
def _convert_md_transform_expr(logical: MdTransformExpr, app_name: str) -> pl.Expr:
    physical_expr = convert_logical_expr_to_physical_expr(logical.input_expr, app_name)
    return physical_expr.markdown.transform(logical.schema)


@_convert_expr.register(StrLengthExpr)
def _convert_str_length_expr(logical: StrLengthExpr, app_name: str) -> pl.Expr:
    physical_expr = convert_logical_expr_to_physical_expr(logical.expr, app_name)
    return physical_expr.str.len_chars()


@_convert_expr.register(ByteLengthExpr)
def _convert_byte_length_expr(logical: ByteLengthExpr, app_name: str) -> pl.Expr:
    physical_expr = convert_logical_expr_to_physical_expr(logical.expr, app_name)
    return physical_expr.str.len_bytes()


@_convert_expr.register(ConcatExpr)
def _convert_concat_expr(logical: ConcatExpr, app_name: str) -> pl.Expr:
    return pl.concat_str(
        [
            convert_logical_expr_to_physical_expr(expr, app_name)
            for expr in logical.exprs
        ],
        separator="",
    )


@_convert_expr.register(CoalesceExpr)
def _convert_coalesce_expr(logical: CoalesceExpr, app_name: str) -> pl.Expr:
    return pl.coalesce(
        [
            convert_logical_expr_to_physical_expr(expr, app_name)
            for expr in logical.exprs
        ],
    )


@_convert_expr.register(IsNullExpr)
def _convert_is_null_expr(logical: IsNullExpr, app_name: str) -> pl.Expr:
    if logical.is_null:
        return convert_logical_expr_to_physical_expr(logical.expr, app_name).is_null()
    else:
        return convert_logical_expr_to_physical_expr(
            logical.expr, app_name
        ).is_not_null()


@_convert_expr.register(ArrayLengthExpr)
def _convert_array_length_expr(logical: ArrayLengthExpr, app_name: str) -> pl.Expr:
    return convert_logical_expr_to_physical_expr(logical.expr, app_name).list.len()


@_convert_expr.register(CastExpr)
def _convert_cast_expr(logical: CastExpr, app_name: str) -> pl.Expr:
    return convert_logical_expr_to_physical_expr(logical.expr, app_name).cast(
        convert_custom_dtype_to_polars(logical.dest_type), strict=False
    )


@_convert_expr.register(CastExpr)
def _convert_cast_expr(logical: CastExpr, app_name: str) -> pl.Expr:
    return convert_logical_expr_to_physical_expr(logical.expr, app_name).cast(
        convert_custom_dtype_to_polars(logical.dest_type), strict=False
    )


@_convert_expr.register(NotExpr)
def _convert_not_expr(logical: NotExpr, app_name: str) -> pl.Expr:
    return convert_logical_expr_to_physical_expr(logical.expr, app_name).not_()


@_convert_expr.register(WhenExpr)
def _convert_when_expr(logical: WhenExpr, app_name: str) -> pl.Expr:
    if isinstance(logical.expr, WhenExpr):
        # Evaluate the final when expression
        return (
            _convert_when_expr(logical.expr, app_name)
            .when(convert_logical_expr_to_physical_expr(logical.condition, app_name))
            .then(
                convert_logical_expr_to_physical_expr(logical.value, app_name).alias(
                    str(logical)
                )
            )
        )
    else:
        # head of condition chain
        return pl.when(
            convert_logical_expr_to_physical_expr(logical.condition, app_name)
        ).then(convert_logical_expr_to_physical_expr(logical.value, app_name))


@_convert_expr.register(OtherwiseExpr)
def _convert_otherwise_expr(logical: OtherwiseExpr, app_name: str) -> pl.Expr:
    return _convert_when_expr(logical.expr, app_name).otherwise(
        convert_logical_expr_to_physical_expr(logical.value, app_name).alias(
            str(logical)
        )
    )


def _convert_udf_to_map_elements(udf: Callable, column_names: List[str]) -> Callable:
    """
    Converts a scalar-based UDF into one that works with `map_elements` in Polars.

    Args:
        udf: The original UDF that takes scalar arguments.
        columns: List of column names that the UDF should operate on.

    Returns:
        A function that operates on a row (Struct) and applies the UDF to the unwrapped values.
    """

    def adapted_udf(row):
        # Unpack the row (Struct) by its column names
        return udf(*[row[name] for name in column_names])

    return adapted_udf
