# Project Structure

Understanding Aider v2's modular architecture and design principles.

## Overview

Aider v2 is built with a clean, modular architecture that separates concerns and makes the codebase maintainable, testable, and extensible.

## Directory Structure

```
aider_v2/
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

## Core Layer

### Interfaces (`core/interfaces/`)
Abstract contracts that define the behavior of different components:

- **`ILLMProvider`** - Contract for AI language model providers
- **`ICoder`** - Contract for code editing implementations
- **`IRepository`** - Contract for version control operations
- **`IUserInterface`** - Contract for user interaction

### Domain Models (`core/domain/`)
Core business entities and value objects:

- **Session** - Represents a conversation session
- **FileInfo** - Information about files in context
- **CommitInfo** - Git commit information
- **Message** - Chat message structure

### Services (`core/services/`)
Business logic and orchestration:

- **`ChatService`** - Main service orchestrating AI conversations
- **`SessionManager`** - Manages conversation sessions
- **`ContextManager`** - Handles file context

### Dependency Injection (`core/container.py`)
Simple container for managing service dependencies:

```python
from aider_v2.core.container import container

# Register services
container.register(ILLMProvider, OpenAIProvider)
container.register(ICoder, EditBlockCoder)

# Get services with automatic dependency resolution
chat_service = container.get(ChatService)
```

## Infrastructure Layer

### LLM Providers (`infrastructure/llm/`)
Implementations of different AI providers:

- **`OpenAIProvider`** - OpenAI API integration
- **`AnthropicProvider`** - Anthropic API integration

### Coders (`infrastructure/coders/`)
Code editing implementations:

- **`EditBlockCoder`** - Search-and-replace code editing

### Repository (`infrastructure/repository/`)
Version control implementations:

- **`GitRepository`** - Git integration for tracking changes

## UI Layer

### CLI (`ui/cli/`)
Command-line interface:

- **`main.py`** - Entry point and argument parsing
- **`commands.py`** - Command handlers for slash commands

### Terminal (`ui/terminal/`)
Terminal user interface:

- **`TerminalInterface`** - Rich terminal UI with colors and formatting

## Configuration (`config/`)

### Settings Management
- **`settings.py`** - Configuration data classes and loading logic

## Design Principles

### Separation of Concerns
Each layer has a specific responsibility:
- **Core**: Business logic and domain models
- **Infrastructure**: External system integrations
- **UI**: User interaction and presentation

### Dependency Inversion
High-level modules don't depend on low-level modules. Both depend on abstractions:

```python
# ChatService depends on interfaces, not concrete implementations
class ChatService:
    def __init__(
        self,
        llm_provider: ILLMProvider,  # Interface, not OpenAIProvider
        coder: ICoder,               # Interface, not EditBlockCoder
        repository: IRepository      # Interface, not GitRepository
    ):
        self.llm_provider = llm_provider
        self.coder = coder
        self.repository = repository
```

### Single Responsibility
Each class has one reason to change:
- `OpenAIProvider` only handles OpenAI API communication
- `EditBlockCoder` only handles code editing logic
- `GitRepository` only handles git operations

### Open/Closed Principle
Open for extension, closed for modification:

```python
# Add new LLM provider without modifying existing code
class CustomLLMProvider(ILLMProvider):
    def generate_response(self, messages, model, config=None):
        # Custom implementation
        pass

# Register the new provider
container.register(ILLMProvider, CustomLLMProvider)
```

## Key Interfaces

### ILLMProvider
```python
class ILLMProvider(ABC):
    @abstractmethod
    def generate_response(
        self, 
        messages: List[Dict], 
        model: str, 
        config: Optional[Dict] = None
    ) -> str:
        pass
    
    @abstractmethod
    def validate_api_key(self) -> bool:
        pass
```

### ICoder
```python
class ICoder(ABC):
    @abstractmethod
    def apply_changes(
        self, 
        file_path: str, 
        changes: str
    ) -> bool:
        pass
    
    @abstractmethod
    def preview_changes(
        self, 
        file_path: str, 
        changes: str
    ) -> str:
        pass
```

### IRepository
```python
class IRepository(ABC):
    @abstractmethod
    def get_status(self) -> List[FileInfo]:
        pass
    
    @abstractmethod
    def commit_changes(
        self, 
        message: str, 
        files: List[str]
    ) -> str:
        pass
```

## Data Flow

### Request Processing
1. **UI Layer** receives user input
2. **CLI Commands** parse and validate input
3. **ChatService** orchestrates the request
4. **LLM Provider** generates AI response
5. **Coder** applies code changes
6. **Repository** commits changes
7. **UI Layer** displays results

### Dependency Flow
```
UI Layer
    ↓
Core Services
    ↓
Core Interfaces
    ↑
Infrastructure Implementations
```

## Benefits of This Architecture

### Testability
- Easy to mock dependencies for unit testing
- Each component can be tested in isolation
- Clear interfaces make testing contracts explicit

### Maintainability
- Small, focused files (typically under 300 lines)
- Clear separation of concerns
- Easy to locate and modify specific functionality

### Extensibility
- Add new LLM providers by implementing `ILLMProvider`
- Add new code editors by implementing `ICoder`
- Add new UI implementations by implementing `IUserInterface`

### Flexibility
- Swap implementations without changing business logic
- Configure different combinations of providers and coders
- Easy to add new features without breaking existing code

## Comparison with Original Aider

| Aspect | Original Aider | Aider v2 |
|--------|---------------|----------|
| Architecture | Monolithic | Modular/Layered |
| File Size | 2,485 lines (base_coder.py) | ~300 lines max per file |
| Testing | Difficult (tight coupling) | Easy (dependency injection) |
| Extensibility | Hard to extend | Plugin system |
| Type Safety | Partial | Full type hints |
| Error Handling | Basic | Comprehensive |

## Extension Points

### Adding New LLM Provider
1. Implement `ILLMProvider` interface
2. Add provider-specific configuration
3. Register in dependency container
4. Add CLI option for selection

### Adding New Coder
1. Implement `ICoder` interface
2. Handle your specific edit format
3. Register in dependency container
4. Add configuration options

### Adding New UI
1. Implement `IUserInterface` interface
2. Create UI-specific components
3. Register in dependency container
4. Add startup option

This architecture makes Aider v2 a solid foundation for future development and customization.