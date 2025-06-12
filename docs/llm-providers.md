# LLM Providers

Aider v2 supports multiple AI providers with different models and capabilities.

## OpenAI Provider

### Supported Models
- `gpt-4o` (recommended)
- `gpt-4`
- `gpt-3.5-turbo`
- `o1-mini`
- `o3-mini`

### Usage
```bash
# With API key from environment
export OPENAI_API_KEY="your-key"
aider-v2 --provider openai --model gpt-4o

# With API key as argument
aider-v2 --provider openai --api-key your-key --model gpt-4o
```

## Anthropic Provider

### Supported Models
- `claude-3-5-sonnet-20241022` (recommended)
- `claude-3-opus-20240229`
- `claude-3-haiku-20240307`

### Usage
```bash
# With API key from environment
export ANTHROPIC_API_KEY="your-key"
aider-v2 --provider anthropic --model claude-3-5-sonnet-20241022

# With API key as argument
aider-v2 --provider anthropic --api-key your-key --model claude-3-5-sonnet-20241022
```

## OpenAI-Compatible APIs

Use any OpenAI-compatible API with the `--base-url` option.

### OpenRouter
Access multiple models through a unified API:
```bash
aider-v2 --provider openai \
         --base-url https://openrouter.ai/api/v1 \
         --api-key $OPENROUTER_API_KEY \
         --model anthropic/claude-3.5-sonnet
```

### Local Servers (Ollama)
```bash
aider-v2 --provider openai \
         --base-url http://localhost:11434/v1 \
         --api-key local-key \
         --model llama3.1:8b
```

### Together AI
```bash
aider-v2 --provider openai \
         --base-url https://api.together.xyz/v1 \
         --api-key $TOGETHER_API_KEY \
         --model meta-llama/Llama-2-70b-chat-hf
```

## Provider Comparison

| Provider | Strengths | Best For |
|----------|-----------|----------|
| OpenAI GPT-4o | Fast, reliable, good code understanding | General coding tasks |
| Claude 3.5 Sonnet | Excellent reasoning, detailed explanations | Complex refactoring |
| Local Models | Privacy, no API costs | Offline development |
| OpenRouter | Access to many models | Experimenting with different models |

## Configuration

### Environment Variables
```bash
# Set default provider and model
export AIDER_PROVIDER="openai"
export AIDER_MODEL="gpt-4o"

# Provider-specific keys
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export OPENROUTER_API_KEY="your-openrouter-key"
```

### Config File (.aider.toml)
```toml
[llm]
provider = "openai"
model = "gpt-4o"
temperature = 0.7
max_tokens = 4000
timeout = 600
```

## Limitations

### Base URL Support
- Only works with `--provider openai`
- Cannot be used with `--provider anthropic`
- Model availability depends on the service

### Model Validation
- Aider v2 doesn't validate model names
- Check your provider's documentation for available models
- Invalid models will cause API errors

## Troubleshooting

### Authentication Errors
```bash
# Verify your API key is correct
aider-v2 --provider openai --api-key your-key --model gpt-4o --verbose
```

### Model Not Found
- Check the provider's model list
- Ensure correct model name format
- For OpenRouter: use `provider/model-name` format

### Connection Issues
```bash
# Test local server connectivity
curl http://localhost:11434/v1/models

# Use verbose mode for debugging
aider-v2 --verbose --provider openai --base-url http://localhost:11434/v1
```