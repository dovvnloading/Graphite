"""
OpenAI-Compatible API Support for Graphite
Supports any OpenAI-compatible endpoint (OpenAI, LiteLLM, Anthropic, OpenRouter, etc.)
"""

import os
import ollama


# Global settings
USE_API_MODE = False
API_CLIENT = None

# Model mappings per task (like Ollama does)
TASK_MODELS = {
    'qwen2.5:3b': None,           # title generation
    'qwen2.5:7b': None,           # chat, explain, takeaway
    'qwen2.5-coder:14b': None     # chart generation
}


def chat(model: str, messages: list, **kwargs) -> dict:
    """
    Route LLM requests to either Ollama or OpenAI-compatible API

    Args:
        model: Model identifier (Ollama model name - used as key for API model mapping)
        messages: Chat messages
        **kwargs: Additional parameters

    Returns:
        Response dict with 'message' key
    """
    if not USE_API_MODE:
        # Original Ollama path - completely unchanged
        return ollama.chat(model=model, messages=messages)

    else:
        # OpenAI-compatible API mode
        if not API_CLIENT:
            raise RuntimeError("API client not initialized. Configure API settings first.")

        # Get the API model mapped to this Ollama model
        api_model = TASK_MODELS.get(model)
        if not api_model:
            raise RuntimeError(
                f"No API model configured for task using '{model}'.\n"
                f"Please configure models in API Settings."
            )

        # Call API using mapped model
        response = API_CLIENT.chat.completions.create(
            model=api_model,
            messages=messages,
            **kwargs
        )

        # Return in Ollama-compatible format
        return {
            'message': {
                'content': response.choices[0].message.content,
                'role': 'assistant'
            }
        }


def initialize_api(api_key: str, base_url: str = 'https://api.openai.com/v1'):
    """
    Initialize OpenAI-compatible API client

    Args:
        api_key: API key for authentication
        base_url: Base URL for the API endpoint

    Returns:
        OpenAI client instance
    """
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError("openai package required. Install with: pip install openai")

    global API_CLIENT
    API_CLIENT = OpenAI(
        api_key=api_key,
        base_url=base_url
    )
    return API_CLIENT


def get_available_models():
    """
    Fetch available models from the API /v1/models endpoint

    Returns:
        List of model IDs
    """
    if not API_CLIENT:
        raise RuntimeError("API client not initialized")

    try:
        models = API_CLIENT.models.list()
        return sorted([model.id for model in models.data])
    except Exception as e:
        raise RuntimeError(f"Failed to fetch models from endpoint: {str(e)}")


def set_mode(use_api: bool):
    """Switch between Ollama and API mode"""
    global USE_API_MODE
    USE_API_MODE = use_api


def set_task_model(ollama_model: str, api_model: str):
    """
    Map an API model to a task (identified by Ollama model name)

    Args:
        ollama_model: Ollama model name (e.g., 'qwen2.5:7b')
        api_model: API model to use for this task (e.g., 'gpt-4o')
    """
    if ollama_model in TASK_MODELS:
        TASK_MODELS[ollama_model] = api_model


def get_task_models() -> dict:
    """Get current task-to-model mappings"""
    return TASK_MODELS.copy()


def get_mode() -> str:
    """Get current mode as string"""
    return "API" if USE_API_MODE else "Ollama"


def is_configured() -> bool:
    """Check if API is properly configured"""
    return API_CLIENT is not None and all(TASK_MODELS.values())
