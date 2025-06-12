"""Configuration settings for Aidant."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import os
from pathlib import Path


@dataclass
class LLMSettings:
    """LLM provider settings."""
    provider: str = "openai"
    model: str = "gpt-4o"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    timeout: int = 600


@dataclass
class CoderSettings:
    """Coder settings."""
    type: str = "editblock"
    auto_apply: bool = False
    show_diffs: bool = True
    backup_files: bool = True


@dataclass
class RepositorySettings:
    """Repository settings."""
    auto_commit: bool = True
    commit_message_template: str = "AI: {description}"
    ignore_patterns: List[str] = field(default_factory=lambda: [
        '.git/*', '__pycache__/*', '*.pyc', 'node_modules/*',
        '.venv/*', 'venv/*', 'dist/*', 'build/*', '.DS_Store',
        '*.log', '*.tmp', '.pytest_cache/*'
    ])


@dataclass
class UISettings:
    """UI settings."""
    theme: str = "monokai"
    show_line_numbers: bool = True
    syntax_highlighting: bool = True
    confirm_changes: bool = True
    verbose: bool = False


@dataclass
class AppSettings:
    """Main application settings."""
    workspace: str = "."
    llm: LLMSettings = field(default_factory=LLMSettings)
    coder: CoderSettings = field(default_factory=CoderSettings)
    repository: RepositorySettings = field(default_factory=RepositorySettings)
    ui: UISettings = field(default_factory=UISettings)
    
    @classmethod
    def load_from_env(cls) -> 'AppSettings':
        """Load settings from environment variables."""
        settings = cls()
        
        # LLM settings
        if os.getenv('AIDER_PROVIDER'):
            settings.llm.provider = os.getenv('AIDER_PROVIDER')
        if os.getenv('AIDER_MODEL'):
            settings.llm.model = os.getenv('AIDER_MODEL')
        if os.getenv('OPENAI_API_KEY'):
            settings.llm.api_key = os.getenv('OPENAI_API_KEY')
        elif os.getenv('ANTHROPIC_API_KEY'):
            settings.llm.api_key = os.getenv('ANTHROPIC_API_KEY')
        
        # Coder settings
        if os.getenv('AIDER_CODER'):
            settings.coder.type = os.getenv('AIDER_CODER')
        if os.getenv('AIDER_AUTO_APPLY'):
            settings.coder.auto_apply = os.getenv('AIDER_AUTO_APPLY').lower() == 'true'
        
        # Repository settings
        if os.getenv('AIDER_AUTO_COMMIT'):
            settings.repository.auto_commit = os.getenv('AIDER_AUTO_COMMIT').lower() == 'true'
        
        # UI settings
        if os.getenv('AIDER_THEME'):
            settings.ui.theme = os.getenv('AIDER_THEME')
        if os.getenv('AIDER_VERBOSE'):
            settings.ui.verbose = os.getenv('AIDER_VERBOSE').lower() == 'true'
        
        return settings
    
    @classmethod
    def load_from_file(cls, config_path: Path) -> 'AppSettings':
        """Load settings from a configuration file."""
        import toml
        
        if not config_path.exists():
            return cls()
        
        try:
            config_data = toml.load(config_path)
            
            settings = cls()
            
            # Update LLM settings
            if 'llm' in config_data:
                llm_data = config_data['llm']
                for key, value in llm_data.items():
                    if hasattr(settings.llm, key):
                        setattr(settings.llm, key, value)
            
            # Update coder settings
            if 'coder' in config_data:
                coder_data = config_data['coder']
                for key, value in coder_data.items():
                    if hasattr(settings.coder, key):
                        setattr(settings.coder, key, value)
            
            # Update repository settings
            if 'repository' in config_data:
                repo_data = config_data['repository']
                for key, value in repo_data.items():
                    if hasattr(settings.repository, key):
                        setattr(settings.repository, key, value)
            
            # Update UI settings
            if 'ui' in config_data:
                ui_data = config_data['ui']
                for key, value in ui_data.items():
                    if hasattr(settings.ui, key):
                        setattr(settings.ui, key, value)
            
            return settings
            
        except Exception as e:
            print(f"Warning: Could not load config file {config_path}: {e}")
            return cls()
    
    def save_to_file(self, config_path: Path) -> None:
        """Save settings to a configuration file."""
        import toml
        
        config_data = {
            'llm': {
                'provider': self.llm.provider,
                'model': self.llm.model,
                'temperature': self.llm.temperature,
                'max_tokens': self.llm.max_tokens,
                'timeout': self.llm.timeout
            },
            'coder': {
                'type': self.coder.type,
                'auto_apply': self.coder.auto_apply,
                'show_diffs': self.coder.show_diffs,
                'backup_files': self.coder.backup_files
            },
            'repository': {
                'auto_commit': self.repository.auto_commit,
                'commit_message_template': self.repository.commit_message_template,
                'ignore_patterns': self.repository.ignore_patterns
            },
            'ui': {
                'theme': self.ui.theme,
                'show_line_numbers': self.ui.show_line_numbers,
                'syntax_highlighting': self.ui.syntax_highlighting,
                'confirm_changes': self.ui.confirm_changes,
                'verbose': self.ui.verbose
            }
        }
        
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            toml.dump(config_data, f)


def get_config_path() -> Path:
    """Get the path to the configuration file."""
    # Check for config in current directory first
    local_config = Path('.aider.toml')
    if local_config.exists():
        return local_config
    
    # Check user config directory
    config_dir = Path.home() / '.config' / 'aider'
    return config_dir / 'config.toml'


def load_settings() -> AppSettings:
    """Load settings from file and environment."""
    # Start with file settings
    config_path = get_config_path()
    settings = AppSettings.load_from_file(config_path)
    
    # Override with environment variables
    env_settings = AppSettings.load_from_env()
    
    # Merge settings (env takes precedence)
    if env_settings.llm.provider != "openai":
        settings.llm.provider = env_settings.llm.provider
    if env_settings.llm.model != "gpt-4o":
        settings.llm.model = env_settings.llm.model
    if env_settings.llm.api_key:
        settings.llm.api_key = env_settings.llm.api_key
    
    return settings