# Installation

## Requirements

- Python 3.10 or higher
- Git (for repository management)

## Install from Source

```bash
# Clone the repository
git clone <repository-url>
cd aidant

# Install with pip
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

## Verify Installation

```bash
aidant --help
```

## API Keys Setup

### OpenAI
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

### Anthropic
```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

### Multiple Providers
You can set up multiple API keys and switch between them:
```bash
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export OPENROUTER_API_KEY="your-openrouter-key"
```

## Quick Test

```bash
# Test with OpenAI
aidant --provider openai --model gpt-4o

# Test with Anthropic
aidant --provider anthropic --model claude-3-5-sonnet-20241022
```

## Next Steps

- [Basic Usage](basic-usage.md) - Learn how to use Aidant
- [Configuration](configuration.md) - Set up your preferences