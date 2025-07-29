import hashlib
import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

import tiktoken
from langframe._inference.model_client import (
    FatalException,
    ModelClient,
    TransientException,
)
from langframe._inference.model_config import OPEN_AI_COMPLETIONS_MODEL_CONFIG
from langframe._constants import PREFIX_TOKENS_PER_MESSAGE
from langframe.api.metrics import LMMetrics
from openai import (
    APIConnectionError,
    APITimeoutError,
    AsyncOpenAI,
    OpenAIError,
    RateLimitError,
)
from openai.types import CompletionUsage
from openai.types.chat.chat_completion_token_logprob import ChatCompletionTokenLogprob
from pydantic import BaseModel


@dataclass
class OpenAICompletionsRequest:
    messages: List[Dict[str, str]]
    max_completion_tokens: int
    top_logprobs: Optional[int]
    structured_output: Optional[BaseModel]


@dataclass
class OpenAICompletionsResponse:
    completion: str
    logprobs: Optional[List[ChatCompletionTokenLogprob]]


class OpenAIBatchChatCompletionsClient(
    ModelClient[OpenAICompletionsRequest, OpenAICompletionsResponse]
):
    def __init__(
        self,
        requests_per_minute: int,
        tokens_per_minute: int,
        queue_size: int = 100,
        model: str = "gpt-4.1-nano",
        max_backoffs: int = 10,
    ):
        super().__init__(
            model=model,
            requests_per_minute=requests_per_minute,
            tokens_per_minute=tokens_per_minute,
            queue_size=queue_size,
            max_backoffs=max_backoffs,
        )
        self.model = model
        try:
            self.tokenizer = tiktoken.encoding_for_model(model)
        except KeyError:
            # Set default encoding to o200k_base if model-specific encoding isn't available (for 4.1 models)
            self.tokenizer = tiktoken.get_encoding("o200k_base")
        self.client = AsyncOpenAI()
        self.tokens_per_minute = tokens_per_minute
        self.metrics = LMMetrics()

    async def make_single_request(
        self, request: OpenAICompletionsRequest
    ) -> Union[None, OpenAICompletionsResponse, TransientException, FatalException]:
        """Make a single request to the OpenAI API."""
        try:
            common_params = {
                "model": self.model,
                "messages": request.messages,
                "max_completion_tokens": request.max_completion_tokens,
                "temperature": 0.0,
                "n": 1,
            }

            # Determine if we need logprobs
            if request.top_logprobs:
                common_params.update(
                    {
                        "logprobs": True,
                        "top_logprobs": request.top_logprobs,
                    }
                )

            # Choose between parse and create based on structured_output
            if request.structured_output:
                common_params["response_format"] = request.structured_output
                response = await self.client.beta.chat.completions.parse(
                    **common_params
                )
                if response.choices[0].message.refusal:
                    return None
            else:
                response = await self.client.chat.completions.create(**common_params)

            usage: CompletionUsage = response.usage

            input_tokens = (
                usage.prompt_tokens_details.cached_tokens
                if usage.prompt_tokens_details
                else 0
            )
            uncached_input_tokens = usage.prompt_tokens - input_tokens
            output_tokens = usage.completion_tokens

            self.metrics.num_cached_input_tokens += input_tokens
            self.metrics.num_input_tokens += uncached_input_tokens
            self.metrics.num_output_tokens += output_tokens
            self.metrics.num_requests += 1

            config = OPEN_AI_COMPLETIONS_MODEL_CONFIG[self.model]
            self.metrics.cost += (
                uncached_input_tokens * config["input_token_cost"]
                + input_tokens * config["cached_input_token_cost"]
                + output_tokens * config["output_token_cost"]
            )
            return OpenAICompletionsResponse(
                completion=response.choices[0].message.content,
                logprobs=response.choices[0].logprobs,
            )
        except (RateLimitError, APITimeoutError, APIConnectionError) as e:
            return TransientException(e)
        except OpenAIError as e:
            return FatalException(e)

    def estimate_tokens_for_request(self, request: OpenAICompletionsRequest) -> int:
        tokens = self.count_tokens(request.messages) + request.max_completion_tokens
        return tokens

    def count_tokens(self, messages: list[dict[str, str]]) -> int:
        tokens_per_name = 1

        num_tokens = 0
        for message in messages:
            num_tokens += PREFIX_TOKENS_PER_MESSAGE  # Every message starts with <im_start>{role/name}\n{content}<im_end>\n
            for key, value in message.items():
                num_tokens += len(self.tokenizer.encode(value))
                if key == "name":
                    num_tokens -= tokens_per_name  # Subtract one token if the 'name' field is present

        num_tokens += 2  # Every assistant reply is primed with <im_start>assistant

        return num_tokens

    def get_request_key(self, request: OpenAICompletionsRequest) -> str:
        return hashlib.sha256(json.dumps(request.messages).encode()).hexdigest()[:10]

    def reset_metrics(self):
        self.metrics = LMMetrics()

    def get_metrics(self) -> LMMetrics:
        return self.metrics
