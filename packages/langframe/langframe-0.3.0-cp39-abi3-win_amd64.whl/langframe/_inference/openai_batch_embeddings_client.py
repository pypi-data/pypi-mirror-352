import hashlib
from typing import List, Union

import tiktoken
from langframe._inference.model_client import (
    FatalException,
    ModelClient,
    TransientException,
)
from langframe._inference.model_config import OPEN_AI_EMBEDDING_MODEL_CONFIG
from langframe.api.metrics import RMMetrics
from openai import (
    APIConnectionError,
    APITimeoutError,
    AsyncOpenAI,
    OpenAIError,
    RateLimitError,
)


class OpenAIBatchEmbeddingsClient(ModelClient[str, List[float]]):
    def __init__(
        self,
        requests_per_minute: int,
        tokens_per_minute: int,
        queue_size: int = 100,
        model: str = "text-embedding-3-small",
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
        self.tokenizer = tiktoken.encoding_for_model(model)
        self.client = AsyncOpenAI()
        self.metrics = RMMetrics()

    async def make_single_request(
        self, request: str
    ) -> Union[None, List[float], TransientException, FatalException]:
        try:
            # TODO(rohitrastogi): Embeddings API supports multiple inputs per request.
            # We should use this feature if we're RPM constrained instead of TPM constrained.
            response = await self.client.embeddings.create(
                input=request,
                model=self.model,
            )
            usage = response.usage
            total_tokens = usage.total_tokens
            self.metrics.num_input_tokens += total_tokens
            self.metrics.num_requests += 1
            self.metrics.cost += (
                total_tokens
                * OPEN_AI_EMBEDDING_MODEL_CONFIG[self.model]["input_token_cost"]
            )
            return response.data[0].embedding

        except (RateLimitError, APITimeoutError, APIConnectionError) as e:
            return TransientException(e)

        except OpenAIError as e:
            return FatalException(e)

    def get_request_key(self, request: str) -> str:
        return hashlib.sha256(request.encode()).hexdigest()[:10]

    def estimate_tokens_for_request(self, request: str) -> int:
        return len(self.tokenizer.encode(request))

    def reset_metrics(self):
        self.metrics = RMMetrics()

    def get_metrics(self) -> RMMetrics:
        return self.metrics
