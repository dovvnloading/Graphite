# OpenAI-Compatible API Support

This fork adds support for OpenAI-compatible API endpoints as an alternative to Ollama.

## What This Adds

- **Mode Toggle**: Switch between Ollama (local) and API endpoint
- **Universal Compatibility**: Works with any OpenAI-compatible API
- **Per-Task Models**: Configure different models for different tasks (title generation, chat, chart creation)
- **Dynamic Model Selection**: Automatically fetches available models from the endpoint
- **Fully Backward Compatible**: Original Ollama functionality remains unchanged

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Launch Graphite

```bash
python Graphite.py
```

### 3. Configure API Endpoint

1. Click **"API Settings"** button in the toolbar
2. Enter your **Base URL** (e.g., `https://api.openai.com/v1`)
3. Enter your **API Key**
4. Click **"Load Models from Endpoint"**
5. Select a model for each task:
   - **Title Generation**: Fast, cheap model for generating conversation titles
   - **Chat/Explain/Takeaways**: Your main conversational model
   - **Chart Generation**: Code-capable model for extracting chart data
6. Click **"Save Configuration"**

### 4. Switch to API Mode

1. Find the **"Mode:"** dropdown in the toolbar
2. Select **"API Endpoint"**
3. Start chatting!

## Compatible Services

Any service with an OpenAI-compatible `/v1` endpoint:

| Service | Base URL | Notes |
|---------|----------|-------|
| **OpenAI** | `https://api.openai.com/v1` | GPT-4, GPT-3.5, etc. |
| **Groq** | `https://api.groq.com/openai/v1` | Free tier, extremely fast |
| **OpenRouter** | `https://openrouter.ai/api/v1` | 100+ models, pay-as-you-go |
| **LiteLLM Proxy** | `http://localhost:4000` | Self-hosted proxy to any LLM |
| **Anthropic** | Via OpenAI-compatible endpoint | Claude models |
| **Local Services** | Your custom URL | Any OpenAI-compatible server |

## Why Per-Task Models?

Different tasks have different requirements:

- **Title Generation**: Needs speed and low cost → Use smaller/faster models
- **Main Chat**: Needs quality responses → Use your best model
- **Chart Generation**: Needs structured output → Use code-capable models

This matches how Ollama works (different models for different tasks) and gives you cost/performance optimization.

## Environment Variables

Settings are stored temporarily. For persistence across sessions:

```bash
# Windows (PowerShell)
$env:GRAPHITE_API_BASE = "https://api.openai.com/v1"
$env:GRAPHITE_API_KEY = "your-api-key"

# Linux/macOS
export GRAPHITE_API_BASE="https://api.openai.com/v1"
export GRAPHITE_API_KEY="your-api-key"
```

## Switching Back to Ollama

Simply select **"Ollama (Local)"** from the Mode dropdown. All original Ollama functionality works exactly as before.

## Troubleshooting

### "API client not initialized"
- Open API Settings and configure your endpoint first
- Make sure you clicked "Load Models" and "Save Configuration"

### "No models found"
- Verify Base URL ends with `/v1`
- Check your API key is valid
- Ensure the endpoint is reachable

### "No model configured for task"
- You must select a model for all three tasks (title, chat, chart)
- Re-open API Settings and ensure all dropdowns have a selection

### Connection errors
- Check firewall settings for local services
- Verify API key has proper permissions
- Test the endpoint with curl:
  ```bash
  curl https://your-endpoint/v1/models \
    -H "Authorization: Bearer your-api-key"
  ```

## How It Works

The implementation uses a simple routing system:

1. **Ollama Mode**: Calls `ollama.chat()` directly with original models
2. **API Mode**: Routes through OpenAI client to your configured endpoint

All 5 LLM calls in Graphite (title, chat, explain, takeaway, chart) go through the same router, ensuring consistent behavior.

## Files Modified

- `api_provider.py` - New module for API routing and model management
- `Graphite.py` - Updated to route LLM calls through `api_provider`
- `requirements.txt` - Added `openai` package

## Technical Details

- Uses standard `openai` Python package
- Compatible with any service implementing OpenAI's `/v1/chat/completions` endpoint
- Model discovery via `/v1/models` endpoint
- Maintains same response format as Ollama for seamless integration

## License

MIT License - same as original Graphite project
