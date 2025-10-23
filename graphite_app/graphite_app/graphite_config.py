# This file holds the global configuration for the application,
# such as the currently selected Ollama model.

# Default model to use on startup
CURRENT_MODEL = 'qwen2.5:7b-instruct'

def set_current_model(model_name: str):
    """
    Sets the global model to be used by all agents.
    """
    global CURRENT_MODEL
    if model_name:
        CURRENT_MODEL = model_name