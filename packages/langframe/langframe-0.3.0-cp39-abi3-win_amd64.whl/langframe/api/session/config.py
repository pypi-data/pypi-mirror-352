from enum import Enum
from pathlib import Path
from typing import Optional

from langframe._inference.model_config import (
    OPEN_AI_COMPLETIONS_MODEL_CONFIG,
    OPEN_AI_EMBEDDING_MODEL_CONFIG,
)
from pydantic import BaseModel, Field, model_validator


class ModelConfig(BaseModel):
    """
    Configuration for a single model, including its name and rate limits.

    Attributes:
        model_name (str): The name of the model to use.
        rpm (int): Requests per minute; must be greater than 0.
        tpm (int): Tokens per minute; must be greater than 0.
    """

    model_name: str
    rpm: int = Field(..., gt=0, description="Requests per minute; must be > 0")
    tpm: int = Field(..., gt=0, description="Tokens per minute; must be > 0")


class SemanticConfig(BaseModel):
    """
    Configuration for semantic language and embedding models.

    Attributes:
        language_model (ModelConfig): Configuration for the language model.
        embedding_model (Optional[ModelConfig]): Configuration for the optional embedding model.
    """

    language_model: ModelConfig
    embedding_model: Optional[ModelConfig] = None

    @model_validator(mode="after")
    def validate_models(self) -> "SemanticConfig":
        """
        Validates that the selected model names are within the allowed set
        of known model configurations.
        """
        if self.language_model.model_name not in OPEN_AI_COMPLETIONS_MODEL_CONFIG:
            raise ValueError(
                f"Invalid language model: '{self.language_model.model_name}'. "
                f"Allowed: {sorted(OPEN_AI_COMPLETIONS_MODEL_CONFIG.keys())}"
            )
        if (
            self.embedding_model
            and self.embedding_model.model_name not in OPEN_AI_EMBEDDING_MODEL_CONFIG
        ):
            raise ValueError(
                f"Invalid embedding model: '{self.embedding_model.model_name}'. "
                f"Allowed: {sorted(OPEN_AI_EMBEDDING_MODEL_CONFIG.keys())}"
            )

        return self


class RemoteExecutorSize(str, Enum):
    SMALL = "INSTANCE_SIZE_S"
    MEDIUM = "INSTANCE_SIZE_M"
    LARGE = "INSTANCE_SIZE_L"
    XLARGE = "INSTANCE_SIZE_XL"


class RemoteConfig(BaseModel):
    size: Optional[RemoteExecutorSize] = None


class SessionConfig(BaseModel):
    """
    Configuration for a user session, including application settings and model usage.

    Attributes:
        app_name (str): Name of the application using this session.
        db_path (Optional[Path]): Optional path to a local database file.
        semantic (SemanticConfig): Semantic model configuration.
        remote_url (Optional[str]): Optional remote backend URL.
    """

    app_name: str = "default_app"
    db_path: Optional[Path] = None
    semantic: SemanticConfig
    remote: Optional[RemoteConfig] = None
