OPEN_AI_COMPLETIONS_MODEL_CONFIG = {
    "gpt-4o-mini": {
        "input_token_cost": 0.300 / 1_000_000,  # $0.300 per 1M tokens
        "cached_input_token_cost": 0.150 / 1_000_000,  # $0.150 per 1M tokens
        "output_token_cost": 1.200 / 1_000_000,  # $1.200 per 1M tokens
        "context_window_length": 128_000,
    },
    "gpt-4o": {
        "input_token_cost": 3.750 / 1_000_000,  # $3.750 per 1M tokens
        "cached_input_token_cost": 1.875 / 1_000_000,  # $1.875 per 1M tokens
        "output_token_cost": 15.00 / 1_000_000,  # $15.00 per 1M tokens
        "context_window_length": 128_000,
    },
    "gpt-4.1-nano": {
        "input_token_cost": 0.100 / 1_000_000,  # $0.100 per 1M tokens
        "cached_input_token_cost": 0.025 / 1_000_000,  # $0.025 per 1M tokens
        "output_token_cost": 0.400 / 1_000_000,  # $0.400 per 1M tokens
        "context_window_length": 1_000_000,
    },
    "gpt-4.1-mini": {
        "input_token_cost": 0.400 / 1_000_000,  # $0.400 per 1M tokens
        "cached_input_token_cost": 0.100 / 1_000_000,  # $0.100 per 1M tokens
        "output_token_cost": 1.600 / 1_000_000,  # $1.600 per 1M tokens
        "context_window_length": 1_000_000,
    },
    "gpt-4.1": {
        "input_token_cost": 2.00 / 1_000_000,  # $2.00 per 1M tokens
        "cached_input_token_cost": 0.500 / 1_000_000,  # $0.500 per 1M tokens
        "output_token_cost": 8.00 / 1_000_000,  # $8.00 per 1M tokens
        "context_window_length": 1_000_000,
    },
}

OPEN_AI_EMBEDDING_MODEL_CONFIG = {
    "text-embedding-3-small": {
        "input_token_cost": 0.02 / 1_000_000,  # $0.02 per 1M tokens
    },
    "text-embedding-3-large": {
        "input_token_cost": 0.13 / 1_000_000,  # $0.13 per 1M tokens
    },
}


def get_supported_completions_models_as_string():
    return ", ".join(OPEN_AI_COMPLETIONS_MODEL_CONFIG.keys())


def get_supported_embeddings_models_as_string():
    return ", ".join(OPEN_AI_EMBEDDING_MODEL_CONFIG.keys())
