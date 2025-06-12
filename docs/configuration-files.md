# Configuration Files

Aidant supports TOML configuration files for persistent settings across sessions.

## Configuration Locations

### Project-Specific Configuration
`.aider.toml` in your project root directory:
```bash
# Create project config
touch .aider.toml
```

### Global Configuration
User-wide configuration:
- Linux/macOS: `~/.config/aider/config.toml`
- Windows: `%APPDATA%\aider\config.toml`

```bash
# Create global config directory
mkdir -p ~/.config/aider
touch ~/.config/aider/config.toml
```

## Configuration Priority

1. Command-line options (highest)
2. Environment variables
3. Project `.aider.toml`
4. Global `config.toml`
5. Default values (lowest)

## Complete Configuration Example

```toml
# .aider.toml

[llm]
provider = "openai"
model = "gpt-4o"
temperature = 0.7
max_tokens = 4000
timeout = 600
base_url = ""  # For custom APIs

[coder]
type = "editblock"
auto_apply = false
show_diffs = true
backup_files = true

[repository]
auto_commit = true
commit_message_template = "AI: {description}"
ignore_patterns = [
    ".git/*",
    "__pycache__/*",
    "*.pyc",
    "node_modules/*",
    ".venv/*",
    "venv/*",
    "dist/*",
    "build/*",
    ".DS_Store",
    "*.log",
    "*.tmp",
    ".pytest_cache/*"
]

[ui]
theme = "monokai"
show_line_numbers = true
syntax_highlighting = true
confirm_changes = true
verbose = false
```

## Section Details

### LLM Configuration
```toml
[llm]
provider = "openai"              # openai, anthropic
model = "gpt-4o"                 # Model name
temperature = 0.7                # Response randomness (0.0-1.0)
max_tokens = 4000                # Maximum response length
timeout = 600                    # Request timeout in seconds
base_url = ""                    # Custom API endpoint (OpenAI only)
```

#### Supported Models
```toml
# OpenAI models
model = "gpt-4o"
model = "gpt-4"
model = "gpt-3.5-turbo"
model = "o1-mini"
model = "o3-mini"

# Anthropic models
model = "claude-3-5-sonnet-20241022"
model = "claude-3-opus-20240229"
model = "claude-3-haiku-20240307"
```

### Coder Configuration
```toml
[coder]
type = "editblock"               # Coder implementation (currently only editblock)
auto_apply = false               # Skip confirmation prompts
show_diffs = true                # Show diffs before applying changes
backup_files = true              # Create backups before editing
```

### Repository Configuration
```toml
[repository]
auto_commit = true               # Automatically commit changes
commit_message_template = "AI: {description}"  # Commit message format

# Files and patterns to ignore
ignore_patterns = [
    ".git/*",                    # Git metadata
    "__pycache__/*",             # Python cache
    "*.pyc",                     # Python bytecode
    "node_modules/*",            # Node.js dependencies
    ".venv/*",                   # Python virtual environment
    "venv/*",                    # Alternative venv location
    "dist/*",                    # Distribution files
    "build/*",                   # Build artifacts
    ".DS_Store",                 # macOS metadata
    "*.log",                     # Log files
    "*.tmp",                     # Temporary files
    ".pytest_cache/*",           # Pytest cache
    "*.backup",                  # Backup files
    ".coverage",                 # Coverage reports
    "htmlcov/*"                  # Coverage HTML reports
]
```

#### Custom Commit Messages
```toml
[repository]
commit_message_template = "feat: {description}"
commit_message_template = "[AI] {description}"
commit_message_template = "🤖 {description}"
commit_message_template = "auto: {description} [skip ci]"
```

### UI Configuration
```toml
[ui]
theme = "monokai"                # Syntax highlighting theme
show_line_numbers = true         # Show line numbers in code
syntax_highlighting = true       # Enable syntax highlighting
confirm_changes = true           # Confirm before applying changes
verbose = false                  # Enable verbose output
```

#### Available Themes
```toml
theme = "monokai"        # Default dark theme
theme = "github"         # GitHub-style light theme
theme = "solarized-dark" # Solarized dark
theme = "solarized-light"# Solarized light
theme = "dracula"        # Dracula theme
theme = "nord"           # Nord theme
theme = "high-contrast"  # High contrast for accessibility
```

## Configuration Examples

### OpenAI Development Setup
```toml
[llm]
provider = "openai"
model = "gpt-4o"
temperature = 0.7

[coder]
auto_apply = false
show_diffs = true

[repository]
auto_commit = true

[ui]
theme = "monokai"
verbose = true
```

### Anthropic Production Setup
```toml
[llm]
provider = "anthropic"
model = "claude-3-5-sonnet-20241022"
temperature = 0.5
timeout = 900

[coder]
auto_apply = false
show_diffs = true
backup_files = true

[repository]
auto_commit = true
commit_message_template = "feat: {description}"

[ui]
theme = "github"
verbose = false
confirm_changes = true
```

### OpenRouter Configuration
```toml
[llm]
provider = "openai"
base_url = "https://openrouter.ai/api/v1"
model = "anthropic/claude-3.5-sonnet"
temperature = 0.7

[coder]
auto_apply = false
show_diffs = true

[ui]
theme = "dracula"
verbose = false
```

### Local Development (Ollama)
```toml
[llm]
provider = "openai"
base_url = "http://localhost:11434/v1"
model = "llama3.1:8b"
temperature = 0.8
timeout = 1200

[coder]
auto_apply = true
show_diffs = false

[repository]
auto_commit = false

[ui]
verbose = true
theme = "nord"
```

### Minimal Configuration
```toml
[llm]
provider = "openai"
model = "gpt-4o"

[coder]
auto_apply = false

[repository]
auto_commit = true
```

## Project-Specific Configurations

### Python Project
```toml
# .aider.toml for Python project
[repository]
ignore_patterns = [
    ".git/*",
    "__pycache__/*",
    "*.pyc",
    ".venv/*",
    "dist/*",
    "build/*",
    ".pytest_cache/*",
    ".coverage",
    "htmlcov/*",
    "*.egg-info/*"
]

[coder]
backup_files = true
show_diffs = true
```

### Node.js Project
```toml
# .aider.toml for Node.js project
[repository]
ignore_patterns = [
    ".git/*",
    "node_modules/*",
    "dist/*",
    "build/*",
    ".next/*",
    "coverage/*",
    "*.log"
]

[llm]
model = "gpt-4o"
temperature = 0.6
```

### Documentation Project
```toml
# .aider.toml for documentation
[llm]
provider = "anthropic"
model = "claude-3-5-sonnet-20241022"
temperature = 0.3

[coder]
auto_apply = false
show_diffs = true

[repository]
commit_message_template = "docs: {description}"
```

## Configuration Management

### Creating Configuration
```bash
# Generate default config
cat > .aider.toml << 'EOF'
[llm]
provider = "openai"
model = "gpt-4o"

[coder]
auto_apply = false
show_diffs = true

[repository]
auto_commit = true

[ui]
theme = "monokai"
verbose = false
EOF
```

### Validating Configuration
```bash
# Test configuration
aidant --help

# Verbose mode shows loaded config
aidant --verbose
```

### Sharing Configuration
```bash
# Include in version control (without API keys)
git add .aider.toml

# Create template for team
cp .aider.toml .aider.toml.template
```

## Advanced Configuration

### Conditional Configuration
Use different configs for different environments:
```bash
# Development
ln -sf .aider.dev.toml .aider.toml

# Production
ln -sf .aider.prod.toml .aider.toml
```

### Configuration Inheritance
Global config provides defaults, project config overrides:
```toml
# ~/.config/aider/config.toml (global)
[ui]
theme = "monokai"
verbose = false

# .aider.toml (project)
[ui]
verbose = true  # Overrides global setting
# theme = "monokai" inherited from global
```

### Environment-Specific Sections
```toml
# Base configuration
[llm]
provider = "openai"
temperature = 0.7

# Development overrides (manually switch)
# [llm]
# model = "gpt-3.5-turbo"  # Cheaper for development
# verbose = true

# Production settings
# [llm]
# model = "gpt-4o"
# verbose = false
```

## Troubleshooting

### Configuration Not Loading
```bash
# Check file exists
ls -la .aider.toml

# Check syntax
python -c "import toml; print(toml.load('.aider.toml'))"

# Use verbose mode
aidant --verbose
```

### Invalid Configuration
```bash
# Common TOML syntax errors
# Missing quotes around strings
provider = openai  # Wrong
provider = "openai"  # Correct

# Invalid boolean values
auto_apply = True  # Wrong (Python syntax)
auto_apply = true  # Correct (TOML syntax)

# Invalid array syntax
ignore_patterns = ".git/*", "*.pyc"  # Wrong
ignore_patterns = [".git/*", "*.pyc"]  # Correct
```

### Permission Issues
```bash
# Check file permissions
ls -la .aider.toml

# Fix permissions
chmod 644 .aider.toml
```

### Configuration Conflicts
```bash
# Environment variables override config file
unset AIDER_MODEL  # Remove env var to use config file

# Command line overrides everything
aidant --model gpt-3.5-turbo  # Ignores config file model
```