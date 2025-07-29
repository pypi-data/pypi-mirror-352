from typing import Optional

from langframe._inference.model_config import (
    OPEN_AI_COMPLETIONS_MODEL_CONFIG,
    get_supported_completions_models_as_string,
)
from langframe._inference.openai_batch_chat_completions_client import (
    OpenAIBatchChatCompletionsClient,
    OpenAICompletionsRequest,
    OpenAICompletionsResponse,
)
from langframe.api.metrics import LMMetrics


class LanguageModel:
    def __init__(self, model: str, client: OpenAIBatchChatCompletionsClient):
        if model not in OPEN_AI_COMPLETIONS_MODEL_CONFIG:
            raise ValueError(
                f"Unsupported model: {model}. Supported models: {get_supported_completions_models_as_string()}"
            )
        # Divide by 3 to avoid sending one massive request that would be slow to retry on failure.
        self.max_ctx_len = (
            min(
                client.tokens_per_minute,
                OPEN_AI_COMPLETIONS_MODEL_CONFIG[model]["context_window_length"],
            )
            / 3
        )
        self.max_completion_tokens = 512
        self.client = client

    def get_completions(
        self,
        messages: list[list[dict[str, str]]],
        operation_name: Optional[str] = None,
        max_completion_tokens: Optional[int] = None,
        top_logprobs: Optional[int] = None,
        response_format: Optional[str] = None,
    ) -> list[Optional[OpenAICompletionsResponse]]:
        if max_completion_tokens is None:
            max_completion_tokens = self.max_completion_tokens
        else:
            max_completion_tokens = max_completion_tokens

        # Create batch requests
        requests = []
        for message_list in messages:
            # if there are no messages, set the request as None, so it can be skipped.
            if not message_list:
                requests.append(None)
                continue

            request = OpenAICompletionsRequest(
                messages=message_list,
                max_completion_tokens=max_completion_tokens,
                top_logprobs=top_logprobs,
                structured_output=response_format,
            )
            requests.append(request)

        # Process batch requests
        return self.client.make_batch_requests(
            requests,
            operation_name=operation_name,
        )

    def count_tokens(self, messages: list[dict[str, str]] | str) -> int:
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        return self.client.count_tokens(messages)

    def reset_metrics(self):
        self.client.reset_metrics()

    def get_metrics(self) -> LMMetrics:
        return self.client.get_metrics()
