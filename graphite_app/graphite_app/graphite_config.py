# This file holds the global configuration for the application,
# such as the currently selected Ollama model.

# Abstract task identifiers
TASK_TITLE = "task_title"
TASK_CHAT = "task_chat"
TASK_CHART = "task_chart"

# API Providers
API_PROVIDER_OPENAI = "OpenAI-Compatible"
API_PROVIDER_GEMINI = "Google Gemini"

# Ollama models per task
OLLAMA_MODELS = {
    TASK_TITLE: 'qwen2.5:3b',
    TASK_CHAT: 'qwen2.5:7b-instruct',
    TASK_CHART: 'deepseek-coder:6.7b'
}

# Default model to use on startup
CURRENT_MODEL = OLLAMA_MODELS[TASK_CHAT]

def set_current_model(model_name: str):
    """
    Sets the global model to be used by all agents.
    NOTE: This now primarily affects the default chat model for Ollama.
    """
    global CURRENT_MODEL
    if model_name:
        CURRENT_MODEL = model_name
        OLLAMA_MODELS[TASK_CHAT] = model_name
