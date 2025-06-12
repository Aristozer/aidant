# Configuration

Aider v2 can be configured through command-line options, environment variables, and configuration files.

## Configuration Priority

1. **Command-line options** (highest priority)
2. **Environment variables**
3. **Configuration files**
4. **Default values** (lowest priority)

## Configuration File

Create `.aider.toml` in your project directory or `~/.config/aider/config.toml` for global settings.

### Example Configuration
```toml
[llm]
provider = "openai"
model = "gpt-4o"
temperature = 0.7
max_tokens = 4000
timeout = 600

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
    "dist/*",
    "build/*"
]

[ui]
theme = "monokai"
show_line_numbers = true
syntax_highlighting = true
confirm_changes = true
verbose = false
```

## Configuration Sections

### LLM Settings
```toml
[llm]
provider = "openai"           # openai, anthropic
model = "gpt-4o"             # Model name
temperature = 0.7            # Response randomness (0.0-1.0)
max_tokens = 4000            # Maximum response length
timeout = 600                # Request timeout in seconds
```

### Coder Settings
```toml
[coder]
type = "editblock"           # Coder implementation
auto_apply = false           # Auto-apply changes without confirmation
show_diffs = true            # Show diffs before applying
backup_files = true          # Create backups before editing
```

### Repository Settings
```toml
[repository]
auto_commit = true           # Automatically commit changes
commit_message_template = "AI: {description}"  # Commit message format
ignore_patterns = [         # Files to ignore
    ".git/*",
    "__pycache__/*",
    "*.pyc"
]
```

### UI Settings
```toml
[ui]
theme = "monokai"            # Syntax highlighting theme
show_line_numbers = true     # Show line numbers in code
syntax_highlighting = true   # Enable syntax highlighting
confirm_changes = true       # Confirm before applying changes
verbose = false              # Enable verbose output
```

## Environment Variables

### LLM Configuration
```bash
export AIDER_PROVIDER="openai"
export AIDER_MODEL="gpt-4o"
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
```

### Coder Configuration
```bash
export AIDER_CODER="editblock"
export AIDER_AUTO_APPLY="false"
```

### Repository Configuration
```bash
export AIDER_AUTO_COMMIT="true"
```

### UI Configuration
```bash
export AIDER_THEME="monokai"
export AIDER_VERBOSE="false"
```

## Command-Line Options

### Basic Options
```bash
aider-v2 --provider openai \
         --model gpt-4o \
         --api-key your-key \
         --workspace /path/to/project \
         --verbose
```

### File Options
```bash
aider-v2 --files src/main.py src/utils.py
```

### Custom API Options
```bash
aider-v2 --provider openai \
         --base-url https://openrouter.ai/api/v1 \
         --api-key your-openrouter-key \
         --model anthropic/claude-3.5-sonnet
```

## Configuration Examples

### OpenAI Setup
```toml
[llm]
provider = "openai"
model = "gpt-4o"
temperature = 0.7
```

### Anthropic Setup
```toml
[llm]
provider = "anthropic"
model = "claude-3-5-sonnet-20241022"
temperature = 0.7
```

### OpenRouter Setup
```bash
# Environment variables
export OPENROUTER_API_KEY="your-key"

# Command line
aider-v2 --provider openai \
         --base-url https://openrouter.ai/api/v1 \
         --api-key $OPENROUTER_API_KEY \
         --model anthropic/claude-3.5-sonnet
```

### Local Development
```toml
[llm]
provider = "openai"
model = "llama3.1:8b"

[coder]
auto_apply = true
show_diffs = false

[repository]
auto_commit = false

[ui]
verbose = true
```

## Configuration Locations

### Project-Specific
- `.aider.toml` in project root
- Takes precedence over global config

### Global Configuration
- `~/.config/aider/config.toml` (Linux/macOS)
- `%APPDATA%\aider\config.toml` (Windows)

### Creating Configuration
```bash
# Create project config
cat > .aider.toml << EOF
[llm]
provider = "openai"
model = "gpt-4o"

[coder]
auto_apply = false
show_diffs = true
EOF

# Create global config directory
mkdir -p ~/.config/aider
```

## Validation

Aider v2 validates configuration on startup:
- Invalid provider names are rejected
- Missing API keys are detected
- Incompatible options (like base-url with anthropic) are caught

## Tips

### Development vs Production
```toml
# Development
[coder]
auto_apply = true
show_diffs = false

[ui]
verbose = true

# Production
[coder]
auto_apply = false
show_diffs = true

[ui]
verbose = false
```

### Multiple Projects
Use project-specific `.aider.toml` files for different configurations per project.

### Security
- Never commit API keys to version control
- Use environment variables for sensitive data
- Consider using `.env` files (not committed) for local development