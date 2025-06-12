# Aidant Documentation

Welcome to Aidant, an AI pair programming assistant with improved architecture and enhanced features.

## What is Aidant?

Aidant is a complete architectural rewrite of the original Aider, featuring:
- **Modular Design** - Clean separation of concerns with interfaces and dependency injection
- **Multiple AI Providers** - OpenAI, Anthropic, and custom API support
- **Smart Code Editing** - Precise EditBlock format for safe code modifications
- **Git Integration** - Automatic commits with descriptive messages
- **Rich Terminal UI** - Syntax highlighting, themes, and interactive prompts

## Quick Start

1. **[Installation](installation.md)** - Get Aidant up and running
2. **[Basic Usage](basic-usage.md)** - Your first session with Aidant
3. **[Configuration](configuration.md)** - Customize Aidant to your needs

## Core Features

### AI Providers
- **[LLM Providers](llm-providers.md)** - OpenAI, Anthropic, and custom API support
  - OpenAI: GPT-4o, GPT-4, GPT-3.5-turbo, o1-mini, o3-mini
  - Anthropic: Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku
  - Custom APIs: OpenRouter, local servers (Ollama), Together AI

### Code Editing
- **[Code Editing](code-editing.md)** - How Aidant modifies your code
  - EditBlock format for precise changes
  - Safety features: backups, diffs, confirmations
  - Multi-file refactoring support

### Version Control
- **[Repository Management](repository-management.md)** - Git integration and version control
  - Automatic commits with descriptive messages
  - Repository status and history commands
  - Smart file ignore patterns

### User Interface
- **[CLI Commands](cli-commands.md)** - All available commands and shortcuts
  - File management: `/add`, `/files`, `/clear`
  - Repository: `/status`, `/diff`, `/history`
  - Session: `/session`, `/help`, `/exit`

- **[Session Management](session-management.md)** - Working with files and context
  - File context management
  - Session persistence
  - Context optimization strategies

- **[User Interface](user-interface.md)** - Terminal interface features
  - Syntax highlighting with multiple themes
  - Interactive prompts and confirmations
  - Rich formatting and progress indicators

## Configuration

### Setup Options
- **[Environment Variables](environment-variables.md)** - Complete environment configuration reference
  - API keys: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`
  - Behavior: `AIDER_AUTO_APPLY`, `AIDER_VERBOSE`
  - UI: `AIDER_THEME`, `AIDER_SYNTAX_HIGHLIGHTING`

- **[Configuration Files](configuration-files.md)** - Using .aider.toml for project settings
  - Project-specific: `.aider.toml`
  - Global: `~/.config/aider/config.toml`
  - Complete configuration examples

## Support

- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions
  - Installation problems
  - API key issues
  - Connection and performance problems
  - Configuration troubleshooting

## Architecture & Development

- **[Project Structure](architecture.md)** - Understanding Aidant's modular design
  - Core interfaces and services
  - Infrastructure implementations
  - Dependency injection system

- **[Extending Aider](extending.md)** - Adding new providers and features
  - Creating custom LLM providers
  - Adding new code editors
  - Plugin system development

## Feature Comparison

| Feature | Aider v1 | Aidant |
|---------|----------|----------|
| Architecture | Monolithic | Modular |
| Providers | OpenAI only | OpenAI, Anthropic, Custom APIs |
| Code Editing | Basic | EditBlock with safety features |
| Configuration | Limited | Comprehensive (env vars, config files) |
| UI | Basic terminal | Rich terminal with themes |
| Extensibility | Difficult | Plugin system |
| Testing | Hard to test | Easy with dependency injection |

## Getting Started Examples

### Quick Start
```bash
# Install
pip install -e .

# Set API key
export OPENAI_API_KEY="your-key"

# Start coding
aidant --files src/main.py
```

### With Custom API
```bash
# Use OpenRouter
aidant --provider openai \
         --base-url https://openrouter.ai/api/v1 \
         --api-key $OPENROUTER_API_KEY \
         --model anthropic/claude-3.5-sonnet
```

### With Configuration File
```toml
# .aider.toml
[llm]
provider = "anthropic"
model = "claude-3-5-sonnet-20241022"

[coder]
auto_apply = false
show_diffs = true

[ui]
theme = "dracula"
verbose = true
```

---

**Need help?** Check the [troubleshooting guide](troubleshooting.md) or run `aidant --help` for command-line options.