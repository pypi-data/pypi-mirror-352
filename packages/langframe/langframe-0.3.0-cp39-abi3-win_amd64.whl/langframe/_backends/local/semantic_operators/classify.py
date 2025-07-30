import json
import logging
from enum import Enum
from typing import List, Optional, Type

import polars as pl
from langframe._constants import TOKEN_OVERHEAD_JSON, TOKEN_OVERHEAD_MISC
from langframe._backends.local.semantic_operators.base import (
    BaseSingleColumnInputOperator,
    CompletionOnlyRequestSender,
)
from langframe._backends.local.semantic_operators.utils import (
    create_classification_pydantic_model,
    stringify_enum_type,
)
from langframe.api.types import ClassifyExample, ClassifyExampleCollection
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class Classify(BaseSingleColumnInputOperator[str, str]):
    SYSTEM_PROMPT = (
        "You are a text classification expert. "
        "Classify the following document into one of the following labels: {labels}. "
        "Respond with *only* the predicted label."
    )

    def __init__(
        self,
        input: pl.Series,
        labels: Type[Enum],
        app_name: str,
        examples: Optional[ClassifyExampleCollection] = None,
    ):
        self.output_model = create_classification_pydantic_model(labels)
        self.labels = labels
        super().__init__(
            input,
            CompletionOnlyRequestSender(
                operator_name="semantic.classify",
                app_name=app_name,
                max_tokens=self.get_max_tokens(),
                response_format=self.output_model,
            ),
            examples,
        )

    def build_system_message(self) -> str:
        return self.SYSTEM_PROMPT.format(labels=stringify_enum_type(self.labels))

    def postprocess(self, responses: List[Optional[str]]) -> List[Optional[str]]:
        predictions = []
        for response in responses:
            if not response:
                predictions.append(None)
            else:
                try:
                    data = json.loads(response)["output"]
                    predictions.append(data)
                except Exception as e:
                    logger.warning(
                        f"Invalid model output: {response} for semantic.classify: {e}"
                    )
                    predictions.append(None)
        return predictions

    def get_response_format(self) -> Optional[Type[BaseModel]]:
        return self.output_model

    def convert_example_to_assistant_message(self, example: ClassifyExample) -> str:
        return self.output_model(output=example.output).model_dump_json()

    def get_max_tokens(self) -> int:
        max_label_length = max(len(str(label.value)) for label in self.labels)
        return TOKEN_OVERHEAD_JSON + TOKEN_OVERHEAD_MISC + max_label_length
