"""
Session state management for query execution.
"""

import logging
from typing import Optional, Tuple
from pathlib import Path
import duckdb

from langframe._inference import (
    EmbeddingModel,
    LanguageModel,
    OpenAIBatchChatCompletionsClient,
    OpenAIBatchEmbeddingsClient,
)
from langframe.api.metrics import LMMetrics, RMMetrics
from langframe._backends import BaseSessionState
from langframe.api.session.config import ModelConfig, SemanticConfig, SessionConfig
from langframe._backends.local.catalog import LocalCatalog
from langframe._backends.local.execution import LocalExecution
from langframe._backends.local.temp_df_db_client import TempDFDBClient
logger = logging.getLogger(__name__)


class LocalSessionState(BaseSessionState):
    """
    Maintains the state for a query session, including database connections and cached dataframes
    and indices.
    """

    language_model: LanguageModel
    embedding_model: Optional[EmbeddingModel]

    def __init__(
        self,
        config: SessionConfig,
    ):
        self.app_name = config.app_name
        if config.db_path:
            db_path = Path(config.db_path) / f"{config.app_name}.duckdb"
        else:
            db_path = Path(f"{config.app_name}.duckdb")
        self.duckdb_conn = self._configure_duckdb_conn(db_path)
        self.language_model, self.embedding_model = self._configure_models(
            config.semantic
        )
        self.intermediate_df_client = TempDFDBClient(self.app_name)
        self._execution = LocalExecution(self)
        self._catalog = LocalCatalog(self.duckdb_conn)


    def _configure_duckdb_conn(self, db_path: Path | None
    ) -> duckdb.DuckDBPyConnection:
        db_conn = duckdb.connect(str(db_path))
        db_conn.execute("PRAGMA arrow_large_buffer_size = true;")
        return db_conn


    def _configure_models(
        self, semantic_config: SemanticConfig
    ) -> Tuple[LanguageModel, Optional[EmbeddingModel]]:
        """
        Configure semantic settings on the session.

        Args:
            semantic_config: Semantic configuration
        """
        # Create the language model clients
        # TODO (TD-1199): API for updating semantic_config in live session, maybe via Dataframe operation
        language_model: LanguageModel = self._configure_language_model(
            semantic_config.language_model
        )
        embeddings_model: Optional[EmbeddingModel] = None
        if semantic_config.embedding_model:
            embeddings_model = self._configure_embedding_model(
                semantic_config.embedding_model
            )

        return language_model, embeddings_model

    def _configure_embedding_model(self, model_config: ModelConfig) -> EmbeddingModel:
        model_name = model_config.model_name
        try:
            client = OpenAIBatchEmbeddingsClient(
                requests_per_minute=model_config.rpm,
                tokens_per_minute=model_config.tpm,
                model=model_name,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to create retrieval model client: {e}") from e

        return EmbeddingModel(model=model_name, client=client)

    def _configure_language_model(self, model_config: ModelConfig) -> LanguageModel:
        model_name = model_config.model_name
        try:
            client = OpenAIBatchChatCompletionsClient(
                requests_per_minute=model_config.rpm,
                tokens_per_minute=model_config.tpm,
                model=model_name,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to create language model client: {e}") from e

        return LanguageModel(model=model_name, client=client)

    @property
    def execution(self) -> LocalExecution:
        """Get the execution object"""
        return self._execution

    @property
    def catalog(self) -> LocalCatalog:
        """Get the catalog object"""
        return self._catalog

    def get_model_metrics(self) -> tuple[LMMetrics, RMMetrics]:
        """Get the language model and retriever model metrics"""
        return self.language_model.get_metrics(), (
            self.embedding_model.get_metrics() if self.embedding_model else RMMetrics()
        )

    def reset_model_metrics(self):
        """Reset the language model and retriever model metrics"""
        self.language_model.reset_metrics()
        if self.embedding_model:
            self.embedding_model.reset_metrics()

    def stop(self):
        """
        Clean up the session state.
        """
        from langframe._backends import LocalSessionManager

        LocalSessionManager().remove_session(self.app_name)

    def _check_active(self):
        """
        Check if the session is active, raise an error if it's stopped.

        Raises:
            RuntimeError: If the session has been stopped
        """
        from langframe._backends import LocalSessionManager

        if not LocalSessionManager().check_session_active(self.app_name):
            raise RuntimeError(
                f"This session '{self.app_name}' has been stopped. Create a new session using Session.get_or_create()."
            )
