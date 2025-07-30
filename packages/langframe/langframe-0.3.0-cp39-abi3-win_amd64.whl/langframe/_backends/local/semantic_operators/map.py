from typing import List, Optional

import polars as pl
from langframe._backends.local.semantic_operators.base import (
    BaseMultiColumnInputOperator,
    CompletionOnlyRequestSender,
)
from langframe._backends.local.semantic_operators.utils import (
    convert_row_to_instruction_context,
    uppercase_instruction_placeholder,
)
from langframe._utils.misc import parse_instruction
from langframe.api.types import (
    MapExampleCollection,
)


class Map(BaseMultiColumnInputOperator[str, str]):
    SYSTEM_PROMPT = (
        "You are an AI assistant designed to follow instructions. "
        "Your task is to generate responses based on instructions that reference one or more context fields. "
        "Each input message will have two sections:\n"
        "1. An instruction labeled with the prefix: ###Instruction\n"
        "2. One or more context fields labeled with the prefix: ###Context\n"
        "The instruction will reference the context fields using square brackets [LIKE_THIS]. "
        "Each context field will be labeled with its name in square brackets, matching the references in the instruction. "
        "Your response should fulfill the instruction by appropriately integrating each of the referenced context fields without using any external information. "
    )

    def __init__(
        self,
        input: pl.DataFrame,
        user_instruction: str,
        app_name: str,
        examples: Optional[MapExampleCollection] = None,
    ):
        super().__init__(
            input,
            CompletionOnlyRequestSender(
                app_name=app_name,
                operator_name="semantic.map",
                max_tokens=512,
            ),
            examples,
        )
        self.referenced_cols = parse_instruction(user_instruction)
        self.user_instruction = uppercase_instruction_placeholder(user_instruction)

    def build_system_message(self) -> str:
        return self.SYSTEM_PROMPT

    def build_user_message(self, input: dict[str, str]) -> str:
        prompt = (
            "### Instruction\n"
            f"{self.user_instruction}\n\n"
            "### Context\n"
            f"{convert_row_to_instruction_context(input)}"
        )

        return prompt

    def postprocess(self, responses: List[Optional[str]]) -> List[Optional[str]]:
        return responses
