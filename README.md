# Aidant - AI Pair Programming Assistant

Aidant is a complete architectural rewrite of the original Aider, featuring a clean, modular design with improved maintainability, testability, and extensibility.

## 🚀 Key Improvements

### Architecture Benefits
- **Modular Design**: Clean separation of concerns with interfaces and dependency injection
- **Testable**: Easy to unit test with mocked dependencies
- **Extensible**: Plugin system for adding new LLM providers and coders
- **Maintainable**: Smaller, focused files with single responsibilities

### Technical Improvements
- **Type Safety**: Full type hints throughout the codebase
- **Error Handling**: Robust error handling with custom exceptions
- **Logging**: Comprehensive logging for debugging and monitoring
- **Configuration**: Flexible configuration system with file and environment support

## 📁 Project Structure

```
aidant/
├── core/                    # Core business logic
│   ├── interfaces/          # Abstract interfaces
│   ├── domain/             # Domain models
│   ├── services/           # Business services
│   └── container.py        # Dependency injection
├── infrastructure/         # External integrations
│   ├── llm/               # LLM provider implementations
│   ├── coders/            # Code editing implementations
│   └── repository/        # Repository implementations
├── ui/                     # User interface layer
│   ├── cli/               # Command-line interface
│   └── terminal/          # Terminal UI implementation
├── utils/                  # Utility functions
└── config/                # Configuration management
```

## 📚 Documentation

**Complete documentation is available in the [docs/](docs/) directory:**

- **[Quick Start Guide](docs/README.md)** - Get started with Aidant
- **[Installation](docs/installation.md)** - Setup and installation instructions
- **[Basic Usage](docs/basic-usage.md)** - Your first session with Aidant
- **[Configuration](docs/configuration.md)** - Customize Aidant to your needs
- **[All Features](docs/README.md#core-features)** - Complete feature documentation

## 🛠 Installation

```bash
# Clone the repository
git clone <repository-url>
cd aidant

# Install dependencies
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

For detailed installation instructions, see [docs/installation.md](docs/installation.md).

## 🔧 Configuration

### Environment Variables
```bash
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export AIDER_MODEL="gpt-4o"
export AIDER_PROVIDER="openai"
```

### Configuration File
Create `.aider.toml` in your project directory:

```toml
[llm]
provider = "openai"
model = "gpt-4o"
temperature = 0.7

[coder]
type = "editblock"
auto_apply = false
show_diffs = true

[repository]
auto_commit = true
commit_message_template = "AI: {description}"

[ui]
theme = "monokai"
syntax_highlighting = true
confirm_changes = true
```

## 🚀 Usage

### Basic Usage
```bash
# Start Aider in current directory
aidant

# Specify model and provider
aidant --model gpt-4o --provider openai

# Add files to initial context
aidant --files src/main.py src/utils.py

# Enable verbose logging
aidant --verbose
```

### Commands
```bash
/add <file>      # Add files to context
/files           # Show files in context
/clear           # Clear context
/status          # Show git status
/diff <file>     # Show file diff
/history         # Show commit history
/help            # Show help
/exit            # Exit application
```

### Example Session
```
🤖 Aidant - AI Pair Programming Assistant

> /add src/calculator.py
✅ Added 1 files to context

> Add error handling to the divide function

I'll add proper error handling to the divide function to handle division by zero.

calculator.py
<<<<<<< SEARCH
def divide(a, b):
    return a / b
=======
def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
>>>>>>> REPLACE

Apply these changes? (y/N): y
✅ Changes applied and committed: a1b2c3d4
```

## 🏗 Architecture Overview

### Core Interfaces
- **ICoder**: Defines contract for code editing implementations
- **ILLMProvider**: Abstracts different LLM providers (OpenAI, Anthropic)
- **IRepository**: Handles version control and file operations
- **IUserInterface**: Abstracts different UI implementations

### Dependency Injection
The application uses a simple dependency injection container to manage service dependencies:

```python
from aidant.core.container import container

# Register services
container.register(ILLMProvider, OpenAIProvider)
container.register(ICoder, EditBlockCoder)

# Get services with automatic dependency resolution
chat_service = container.get(ChatService)
```

### Plugin System
Easy to extend with new providers and coders:

```python
# Add new LLM provider
class CustomLLMProvider(ILLMProvider):
    def generate_response(self, messages, model, config=None):
        # Implementation
        pass

# Register the provider
container.register(ILLMProvider, CustomLLMProvider)
```

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=aidant

# Run specific test file
pytest tests/test_chat_service.py
```

### Test Structure
```
tests/
├── unit/                   # Unit tests
│   ├── test_chat_service.py
│   ├── test_coders.py
│   └── test_llm_providers.py
├── integration/            # Integration tests
│   └── test_full_workflow.py
└── fixtures/              # Test fixtures
```

## 🔌 Extending Aidant

### Adding a New LLM Provider
1. Implement the `ILLMProvider` interface
2. Register it in the container
3. Add configuration options

### Adding a New Coder
1. Implement the `ICoder` interface
2. Handle your specific edit format
3. Register it in the container

### Adding New Commands
1. Add command handler in `cli/commands.py`
2. Update help text
3. Add tests

## 📊 Comparison with Original Aider

| Aspect | Original Aider | Aidant |
|--------|---------------|----------|
| Architecture | Monolithic | Modular/Layered |
| File Size | 2,485 lines (base_coder.py) | ~300 lines max per file |
| Testing | Difficult (tight coupling) | Easy (dependency injection) |
| Extensibility | Hard to extend | Plugin system |
| Type Safety | Partial | Full type hints |
| Error Handling | Basic | Comprehensive |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

[License information]

## 🙏 Acknowledgments

- Original Aider project for inspiration
- Rich library for beautiful terminal output
- Click for CLI framework