import numpy as np
from numpy.typing import NDArray
from langframe._inference.openai_batch_embeddings_client import OpenAIBatchEmbeddingsClient
from langframe.api.metrics import RMMetrics


class EmbeddingModel:
    def __init__(self, model: str, client: OpenAIBatchEmbeddingsClient):
        self.client = client
        self.model = model
        # The length of the embeddings for the text-embedding-3-large model.
        # By default, the length of the embedding vector is 1536 for
        # text-embedding-3-small or 3072 for text-embedding-3-large.
        self.list_length = 1536 if model == "text-embedding-3-small" else 3072

    def get_embeddings(self, docs: list[str | None]) -> NDArray[np.float32]:
        results = self.client.make_batch_requests(docs, operation_name="semantic.embed")

        output = np.full((len(results), self.list_length), np.nan, dtype=np.float32)
        for i, result in enumerate(results):
            if result is not None:
                output[i] = result  # fast bulk assignment
        return output

    def reset_metrics(self):
        self.client.reset_metrics()

    def get_metrics(self) -> RMMetrics:
        return self.client.get_metrics()
