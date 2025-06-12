# Extending Aider v2

Guide for developers who want to extend Aider v2 with new providers, coders, or features.

## Overview

Aider v2's modular architecture makes it easy to extend with new functionality. The plugin system is based on interfaces and dependency injection.

## Adding a New LLM Provider

### 1. Implement the Interface

Create a new provider by implementing `ILLMProvider`:

```python
# infrastructure/llm/custom_provider.py
from typing import Dict, List, Optional
from ...core.interfaces.llm_provider import ILLMProvider

class CustomLLMProvider(ILLMProvider):
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url or "https://api.custom-llm.com/v1"
        
    def generate_response(
        self, 
        messages: List[Dict], 
        model: str, 
        config: Optional[Dict] = None
    ) -> str:
        """Generate response from custom LLM API."""
        import requests
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": config.get("temperature", 0.7) if config else 0.7,
            "max_tokens": config.get("max_tokens", 4000) if config else 4000
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=config.get("timeout", 600) if config else 600
        )
        
        if response.status_code != 200:
            raise Exception(f"API error: {response.status_code} - {response.text}")
            
        return response.json()["choices"][0]["message"]["content"]
    
    def validate_api_key(self) -> bool:
        """Validate the API key."""
        try:
            # Test with a simple request
            self.generate_response(
                [{"role": "user", "content": "test"}],
                "default-model",
                {"max_tokens": 1}
            )
            return True
        except Exception:
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        import requests
        
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.get(f"{self.base_url}/models", headers=headers)
        
        if response.status_code == 200:
            return [model["id"] for model in response.json()["data"]]
        return []
```

### 2. Register the Provider

Add the provider to the CLI options:

```python
# cli/main.py
class ProviderChoice(str, Enum):
    openai = "openai"
    anthropic = "anthropic"
    custom = "custom"  # Add new provider

def setup_container(
    workspace: str,
    provider: str,
    api_key: str,
    model: str,
    coder_type: str,
    base_url: Optional[str] = None
) -> None:
    # ... existing code ...
    
    # Register LLM Provider
    if provider == "openai":
        llm_provider = OpenAIProvider(api_key, base_url=base_url)
    elif provider == "anthropic":
        if base_url:
            raise ValueError("Custom base URL is not supported for Anthropic provider")
        llm_provider = AnthropicProvider(api_key)
    elif provider == "custom":
        llm_provider = CustomLLMProvider(api_key, base_url=base_url)
    else:
        raise ValueError(f"Unsupported provider: {provider}")
```

### 3. Add Configuration Support

Update configuration to support the new provider:

```python
# config/settings.py
@dataclass
class LLMSettings:
    provider: str = "openai"
    model: str = "gpt-4o"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    timeout: int = 600
    
    # Add provider-specific settings
    custom_settings: Dict[str, Any] = field(default_factory=dict)
```

### 4. Update Documentation

Add provider documentation:

```toml
# .aider.toml example
[llm]
provider = "custom"
model = "custom-model-name"
base_url = "https://api.custom-llm.com/v1"
temperature = 0.7

[llm.custom_settings]
special_parameter = "value"
```

## Adding a New Coder

### 1. Implement the Interface

Create a new coder by implementing `ICoder`:

```python
# infrastructure/coders/diff_coder/diff_coder.py
from typing import List, Optional
from pathlib import Path
from ...core.interfaces.coder import ICoder

class DiffCoder(ICoder):
    def __init__(self, workspace: str):
        self.workspace = Path(workspace)
    
    def apply_changes(self, file_path: str, changes: str) -> bool:
        """Apply diff-style changes to a file."""
        try:
            # Parse diff format changes
            patches = self._parse_diff(changes)
            
            for patch in patches:
                self._apply_patch(file_path, patch)
            
            return True
        except Exception as e:
            print(f"Error applying changes: {e}")
            return False
    
    def preview_changes(self, file_path: str, changes: str) -> str:
        """Preview what changes would be applied."""
        try:
            patches = self._parse_diff(changes)
            preview = []
            
            for patch in patches:
                preview.append(self._format_patch_preview(file_path, patch))
            
            return "\n".join(preview)
        except Exception as e:
            return f"Error previewing changes: {e}"
    
    def _parse_diff(self, diff_text: str) -> List[Dict]:
        """Parse diff format into structured patches."""
        # Implementation for parsing diff format
        # This would handle unified diff format
        patches = []
        # ... parsing logic ...
        return patches
    
    def _apply_patch(self, file_path: str, patch: Dict) -> None:
        """Apply a single patch to a file."""
        # Implementation for applying patch
        # ... patching logic ...
        pass
    
    def _format_patch_preview(self, file_path: str, patch: Dict) -> str:
        """Format patch for preview display."""
        # Implementation for formatting preview
        # ... formatting logic ...
        return f"Patch preview for {file_path}"
```

### 2. Register the Coder

Add the coder to CLI options:

```python
# cli/main.py
class CoderChoice(str, Enum):
    editblock = "editblock"
    diff = "diff"  # Add new coder

def setup_container(...):
    # ... existing code ...
    
    # Register Coder
    if coder_type == "editblock":
        coder = EditBlockCoder(workspace)
    elif coder_type == "diff":
        coder = DiffCoder(workspace)
    else:
        raise ValueError(f"Unsupported coder type: {coder_type}")
```

### 3. Add Configuration

```toml
# .aider.toml
[coder]
type = "diff"
auto_apply = false
show_diffs = true
backup_files = true

# Coder-specific settings
[coder.diff_settings]
context_lines = 3
ignore_whitespace = false
```

## Adding New Commands

### 1. Add Command Handler

```python
# cli/commands.py
class CommandHandler:
    def handle_command(self, command: str) -> None:
        # ... existing code ...
        
        command_map = {
            'help': self._help,
            'add': self._add_files,
            'files': self._show_files,
            # ... existing commands ...
            'search': self._search_files,  # New command
            'refactor': self._refactor_code,  # New command
        }
    
    def _search_files(self, args: List[str]) -> None:
        """Search for text in project files."""
        if not args:
            self.ui.show_error("Usage: /search <pattern>")
            return
        
        pattern = " ".join(args)
        # Implementation for searching files
        # ... search logic ...
    
    def _refactor_code(self, args: List[str]) -> None:
        """Start a refactoring session."""
        if not args:
            self.ui.show_error("Usage: /refactor <description>")
            return
        
        description = " ".join(args)
        # Implementation for refactoring workflow
        # ... refactoring logic ...
```

### 2. Update Help Text

```python
def _help(self, args: List[str]) -> None:
    """Show help information."""
    help_text = """
Available commands:
  /add <file>      - Add files to context
  /files           - Show files in context
  /clear           - Clear context
  /status          - Show git status
  /diff <file>     - Show file diff
  /history         - Show commit history
  /search <pattern> - Search for text in files
  /refactor <desc> - Start refactoring session
  /help            - Show this help
  /exit            - Exit application
"""
    self.ui.show_message(help_text)
```

## Adding New UI Components

### 1. Implement UI Interface

```python
# ui/web/web_interface.py
from typing import Optional
from ...core.interfaces.ui import IUserInterface

class WebInterface(IUserInterface):
    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.app = self._create_app()
    
    def show_welcome(self) -> None:
        """Show welcome message."""
        # Web-specific welcome implementation
        pass
    
    def get_user_input(self) -> str:
        """Get user input via web interface."""
        # Implementation for web input
        pass
    
    def show_message(self, message: str) -> None:
        """Display message in web interface."""
        # Implementation for web display
        pass
    
    def _create_app(self):
        """Create web application."""
        from flask import Flask, render_template, request
        
        app = Flask(__name__)
        
        @app.route('/')
        def index():
            return render_template('index.html')
        
        @app.route('/api/chat', methods=['POST'])
        def chat():
            message = request.json.get('message')
            # Process message and return response
            return {'response': 'AI response here'}
        
        return app
    
    def start_server(self):
        """Start the web server."""
        self.app.run(host=self.host, port=self.port)
```

### 2. Register UI Component

```python
# cli/main.py
@app.command()
def web(
    host: str = typer.Option("localhost", help="Web server host"),
    port: int = typer.Option(8080, help="Web server port"),
    # ... other options ...
) -> None:
    """Start Aider v2 with web interface."""
    
    # Setup container with web UI
    container.register_instance(IUserInterface, WebInterface(host, port))
    
    # Start web server
    ui = container.get(IUserInterface)
    ui.start_server()
```

## Plugin System

### 1. Plugin Interface

```python
# core/interfaces/plugin.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class IPlugin(ABC):
    @abstractmethod
    def initialize(self, container: 'Container') -> None:
        """Initialize the plugin with the DI container."""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get plugin name."""
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """Get plugin version."""
        pass
```

### 2. Plugin Loader

```python
# core/plugin_loader.py
import importlib
from pathlib import Path
from typing import List
from .interfaces.plugin import IPlugin

class PluginLoader:
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = Path(plugin_dir)
        self.loaded_plugins: List[IPlugin] = []
    
    def load_plugins(self) -> None:
        """Load all plugins from plugin directory."""
        if not self.plugin_dir.exists():
            return
        
        for plugin_file in self.plugin_dir.glob("*.py"):
            if plugin_file.name.startswith("__"):
                continue
            
            try:
                module_name = plugin_file.stem
                spec = importlib.util.spec_from_file_location(
                    module_name, plugin_file
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Look for plugin class
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, IPlugin) and 
                        attr != IPlugin):
                        plugin = attr()
                        self.loaded_plugins.append(plugin)
                        
            except Exception as e:
                print(f"Failed to load plugin {plugin_file}: {e}")
    
    def initialize_plugins(self, container) -> None:
        """Initialize all loaded plugins."""
        for plugin in self.loaded_plugins:
            try:
                plugin.initialize(container)
            except Exception as e:
                print(f"Failed to initialize plugin {plugin.get_name()}: {e}")
```

### 3. Example Plugin

```python
# plugins/example_plugin.py
from aider_v2.core.interfaces.plugin import IPlugin
from aider_v2.core.interfaces.llm_provider import ILLMProvider

class ExamplePlugin(IPlugin):
    def initialize(self, container) -> None:
        """Initialize the plugin."""
        # Register custom provider
        container.register(ILLMProvider, CustomLLMProvider)
        
        # Add custom commands
        # ... command registration ...
    
    def get_name(self) -> str:
        return "Example Plugin"
    
    def get_version(self) -> str:
        return "1.0.0"
```

## Testing Extensions

### 1. Unit Tests

```python
# tests/test_custom_provider.py
import pytest
from unittest.mock import Mock, patch
from aider_v2.infrastructure.llm.custom_provider import CustomLLMProvider

class TestCustomLLMProvider:
    def test_generate_response(self):
        provider = CustomLLMProvider("test-key")
        
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "test response"}}]
            }
            mock_post.return_value = mock_response
            
            result = provider.generate_response(
                [{"role": "user", "content": "test"}],
                "test-model"
            )
            
            assert result == "test response"
    
    def test_validate_api_key(self):
        provider = CustomLLMProvider("invalid-key")
        
        with patch.object(provider, 'generate_response', side_effect=Exception()):
            assert not provider.validate_api_key()
```

### 2. Integration Tests

```python
# tests/integration/test_custom_integration.py
import pytest
from aider_v2.core.container import container
from aider_v2.infrastructure.llm.custom_provider import CustomLLMProvider

class TestCustomIntegration:
    def test_provider_registration(self):
        # Test that custom provider can be registered and retrieved
        container.register(ILLMProvider, CustomLLMProvider)
        provider = container.get(ILLMProvider)
        
        assert isinstance(provider, CustomLLMProvider)
```

## Best Practices

### 1. Follow Interface Contracts
- Implement all required methods
- Handle errors gracefully
- Return expected types

### 2. Configuration
- Add configuration options for customization
- Use sensible defaults
- Validate configuration values

### 3. Error Handling
- Provide clear error messages
- Handle network failures gracefully
- Log errors for debugging

### 4. Documentation
- Document new features
- Provide usage examples
- Update help text

### 5. Testing
- Write unit tests for new components
- Test integration with existing system
- Test error conditions

This extension system makes Aider v2 highly customizable while maintaining clean architecture and separation of concerns.