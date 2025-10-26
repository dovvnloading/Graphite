import os
import ollama
import graphite_config as config

USE_API_MODE = False
API_PROVIDER_TYPE = None
API_CLIENT = None
API_MODELS = {
    config.TASK_TITLE: None,
    config.TASK_CHAT: None,
    config.TASK_CHART: None
}

# Static, hard-coded list of reliable Gemini models. This is now the primary source.
GEMINI_MODELS_STATIC = sorted([
    "gemini-2.5-pro-latest",
    "gemini-2.5-pro",
    "gemini-2.5-flash-latest",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-pro",
])


def _convert_to_gemini_messages(messages: list) -> tuple:
    """
    Converts standard message list to Gemini format and extracts system prompt.
    """
    system_prompt = None
    gemini_history = []
    
    for msg in messages:
        if msg['role'] == 'system':
            system_prompt = msg['content']
            continue
        
        # Gemini roles are 'user' and 'model'
        role = 'model' if msg['role'] == 'assistant' else 'user'
        
        # Ensure alternating roles
        if gemini_history and gemini_history[-1]['role'] == role:
            # If two user messages in a row, combine them.
            if role == 'user':
                gemini_history[-1]['parts'].append(msg['content'])
                continue
            # If two model messages in a row, this is unusual, but we'll add a placeholder user message
            else:
                gemini_history.append({'role': 'user', 'parts': ["(Continuing...)"]})

        gemini_history.append({
            'role': role,
            'parts': [msg['content']]
        })
        
    return system_prompt, gemini_history

def chat(task: str, messages: list, **kwargs) -> dict:
    if not USE_API_MODE:
        model = config.OLLAMA_MODELS.get(task)
        if not model:
            raise ValueError(f"No Ollama model configured for task: {task}")
        return ollama.chat(model=model, messages=messages, **kwargs)
    else:
        if not API_CLIENT:
            raise RuntimeError("API client not initialized. Configure API settings first.")

        api_model = API_MODELS.get(task)
        if not api_model:
            raise RuntimeError(
                f"No API model configured for task '{task}'.\n"
                f"Please configure models in API Settings."
            )

        if API_PROVIDER_TYPE == config.API_PROVIDER_OPENAI:
            response = API_CLIENT.chat.completions.create(
                model=api_model,
                messages=messages,
                **kwargs
            )
            return {
                'message': {
                    'content': response.choices[0].message.content,
                    'role': 'assistant'
                }
            }
        elif API_PROVIDER_TYPE == config.API_PROVIDER_GEMINI:
            system_prompt, gemini_history = _convert_to_gemini_messages(messages)
            
            model_config = {}
            if system_prompt:
                model_config['system_instruction'] = system_prompt

            gemini_model = API_CLIENT.GenerativeModel(api_model, **model_config)
            
            # This was the error. The .pop() method was removing the user's message
            # before sending the request. The generate_content method expects the full
            # conversation history, including the latest message.
            # prompt = gemini_history.pop() # <--- THIS LINE IS THE ROOT CAUSE OF THE FAILURE
            
            response = gemini_model.generate_content(
                contents=gemini_history,
                generation_config=kwargs
            )
            
            return {
                'message': {
                    'content': response.text,
                    'role': 'assistant'
                }
            }
        else:
            raise RuntimeError(f"Unsupported API provider: {API_PROVIDER_TYPE}")


def initialize_api(provider: str, api_key: str, base_url: str = None):
    global API_PROVIDER_TYPE, API_CLIENT
    API_PROVIDER_TYPE = provider

    if provider == config.API_PROVIDER_OPENAI:
        try:
            from openai import OpenAI
        except ImportError:
            raise RuntimeError("openai package required. Install with: pip install openai")
        
        if not base_url:
            base_url = 'https://api.openai.com/v1'

        API_CLIENT = OpenAI(api_key=api_key, base_url=base_url)

    elif provider == config.API_PROVIDER_GEMINI:
        try:
            import google.generativeai as genai
        except ImportError:
            raise RuntimeError("google-generativeai package required. Install with: pip install google-generativeai")
        
        genai.configure(api_key=api_key)
        API_CLIENT = genai # Store the configured module as the client
    else:
        raise ValueError(f"Unknown API provider: {provider}")

    return API_CLIENT


def get_available_models():
    if not API_CLIENT:
        raise RuntimeError("API client not initialized")

    try:
        if API_PROVIDER_TYPE == config.API_PROVIDER_OPENAI:
            models = API_CLIENT.models.list()
            return sorted([model.id for model in models.data])
        elif API_PROVIDER_TYPE == config.API_PROVIDER_GEMINI:
            # The brittle API call has been removed. We now return a reliable, static list.
            return GEMINI_MODELS_STATIC
        else:
            return []
    except Exception as e:
        raise RuntimeError(f"Failed to fetch models from endpoint: {str(e)}")

def set_mode(use_api: bool):
    global USE_API_MODE
    USE_API_MODE = use_api

def set_task_model(task: str, api_model: str):
    if task in API_MODELS:
        API_MODELS[task] = api_model

def get_task_models() -> dict:
    return API_MODELS.copy()

def get_mode() -> str:
    return "API" if USE_API_MODE else "Ollama"

def is_configured() -> bool:
    return API_CLIENT is not None and all(API_MODELS.values())
