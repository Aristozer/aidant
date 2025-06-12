# Base URL Support for OpenAI-Compatible APIs

## Overview

Aider v2 now supports using OpenAI-compatible APIs through the `--base-url` option. This allows you to use services like OpenRouter, local LLM servers, or any other API that implements the OpenAI chat completions format.

## Usage

### Basic Syntax

```bash
aider-v2 --provider openai --base-url <CUSTOM_URL> --api-key <API_KEY> --model <MODEL_NAME>
```

### Examples

#### 1. Using OpenRouter

OpenRouter provides access to multiple LLM models through a unified OpenAI-compatible API:

```bash
# Using OpenRouter with Claude
aider-v2 --provider openai \
         --base-url https://openrouter.ai/api/v1 \
         --api-key $OPENROUTER_API_KEY \
         --model anthropic/claude-3.5-sonnet

# Using OpenRouter with GPT-4
aider-v2 --provider openai \
         --base-url https://openrouter.ai/api/v1 \
         --api-key $OPENROUTER_API_KEY \
         --model openai/gpt-4o
```

#### 2. Using Local LLM Servers

For local servers running OpenAI-compatible APIs (like Ollama, LocalAI, etc.):

```bash
# Local server example
aider-v2 --provider openai \
         --base-url http://localhost:11434/v1 \
         --api-key local-key \
         --model llama3.1:8b

# Another local server example
aider-v2 --provider openai \
         --base-url http://localhost:8000/v1 \
         --api-key your-local-key \
         --model custom-model
```

#### 3. Using Standard OpenAI (No Base URL Needed)

```bash
# Standard OpenAI usage (base-url not required)
aider-v2 --provider openai \
         --api-key $OPENAI_API_KEY \
         --model gpt-4o
```

## Features

### ✅ Supported
- **Full OpenAI API Compatibility**: Any service implementing the OpenAI chat completions API
- **Streaming Support**: Real-time response streaming if supported by the endpoint
- **Model Selection**: Use any model name supported by your chosen service
- **Error Handling**: Proper error messages for authentication and API issues
- **Cost Estimation**: Basic cost estimation (may not be accurate for non-OpenAI services)

### ⚠️ Limitations
- **Provider Restriction**: `--base-url` only works with `--provider openai`
- **Anthropic Incompatible**: Cannot use `--base-url` with `--provider anthropic`
- **Model Validation**: Model availability depends on the target service
- **Pricing**: Cost estimates may not reflect actual pricing for third-party services

## Configuration

### Environment Variables

You can set environment variables for convenience:

```bash
# For OpenRouter
export OPENROUTER_API_KEY="your-openrouter-key"
export OPENROUTER_BASE_URL="https://openrouter.ai/api/v1"

# Then use:
aider-v2 --provider openai --base-url $OPENROUTER_BASE_URL --api-key $OPENROUTER_API_KEY --model anthropic/claude-3.5-sonnet
```

### Validation

The CLI includes validation to ensure proper usage:

```bash
# ❌ This will fail - base-url not supported with anthropic
aider-v2 --provider anthropic --base-url https://example.com --api-key key

# ✅ This works - base-url with openai provider
aider-v2 --provider openai --base-url https://openrouter.ai/api/v1 --api-key key
```

## Popular OpenAI-Compatible Services

### OpenRouter
- **URL**: `https://openrouter.ai/api/v1`
- **Models**: Access to Claude, GPT, Llama, and many others
- **API Key**: Get from [OpenRouter Dashboard](https://openrouter.ai/keys)

### Ollama
- **URL**: `http://localhost:11434/v1` (default local)
- **Models**: Local models like Llama, Mistral, CodeLlama
- **Setup**: Install Ollama and pull models locally

### LocalAI
- **URL**: `http://localhost:8080/v1` (configurable)
- **Models**: Various open-source models
- **Setup**: Self-hosted OpenAI-compatible API

### Together AI
- **URL**: `https://api.together.xyz/v1`
- **Models**: Open-source models with fast inference
- **API Key**: Get from Together AI platform

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   ```bash
   # Make sure your API key is correct for the service
   aider-v2 --provider openai --base-url https://openrouter.ai/api/v1 --api-key $CORRECT_KEY
   ```

2. **Model Not Found**
   ```bash
   # Check the service's documentation for available model names
   # OpenRouter uses format: provider/model-name
   # Local servers may use different naming conventions
   ```

3. **Connection Issues**
   ```bash
   # For local servers, ensure they're running and accessible
   curl http://localhost:11434/v1/models  # Test Ollama
   ```

### Debug Mode

Use verbose logging to troubleshoot issues:

```bash
aider-v2 --provider openai \
         --base-url https://openrouter.ai/api/v1 \
         --api-key $OPENROUTER_API_KEY \
         --model anthropic/claude-3.5-sonnet \
         --verbose
```

## Implementation Details

The base URL feature works by:

1. **Passing Custom URL**: The `--base-url` parameter is passed to the OpenAI client
2. **API Compatibility**: Uses the same OpenAI Python client with a different endpoint
3. **Request Format**: Maintains OpenAI's request/response format for compatibility
4. **Error Handling**: Preserves error handling and retry logic

This approach ensures maximum compatibility with OpenAI-compatible services while maintaining the same user experience and feature set.