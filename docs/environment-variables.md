# Environment Variables

Complete reference for all environment variables supported by Aidant.

## API Keys

### OpenAI
```bash
export OPENAI_API_KEY="sk-..."
```
Required for OpenAI provider.

### Anthropic
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```
Required for Anthropic provider.

### Third-party Services
```bash
export OPENROUTER_API_KEY="sk-or-..."
export TOGETHER_API_KEY="..."
export GROQ_API_KEY="gsk_..."
```
For use with `--base-url` option.

## LLM Configuration

### Provider Selection
```bash
export AIDER_PROVIDER="openai"        # openai, anthropic
export AIDER_MODEL="gpt-4o"           # Model name
```

### Model Parameters
```bash
export AIDER_TEMPERATURE="0.7"        # Response randomness (0.0-1.0)
export AIDER_MAX_TOKENS="4000"        # Maximum response length
export AIDER_TIMEOUT="600"            # Request timeout in seconds
```

### Custom APIs
```bash
export AIDER_BASE_URL="https://api.openrouter.ai/v1"
```
For OpenAI-compatible APIs.

## Coder Configuration

### Coder Type
```bash
export AIDER_CODER="editblock"         # Currently only editblock
```

### Behavior Settings
```bash
export AIDER_AUTO_APPLY="false"       # Skip confirmation prompts
export AIDER_SHOW_DIFFS="true"        # Show diffs before applying
export AIDER_BACKUP_FILES="true"      # Create backups before editing
```

## Repository Settings

### Git Integration
```bash
export AIDER_AUTO_COMMIT="true"       # Automatically commit changes
export AIDER_COMMIT_TEMPLATE="AI: {description}"  # Commit message format
```

### Workspace
```bash
export AIDER_WORKSPACE="/path/to/project"  # Default workspace directory
```

## UI Configuration

### Display Settings
```bash
export AIDER_THEME="monokai"           # Syntax highlighting theme
export AIDER_VERBOSE="false"          # Enable verbose output
export AIDER_SHOW_LINE_NUMBERS="true" # Show line numbers in code
export AIDER_SYNTAX_HIGHLIGHTING="true"  # Enable syntax highlighting
export AIDER_CONFIRM_CHANGES="true"   # Confirm before applying changes
```

### Color and Formatting
```bash
export NO_COLOR="1"                    # Disable all colors
export FORCE_COLOR="1"                 # Force colors even in non-TTY
```

## System Configuration

### Logging
```bash
export AIDER_LOG_LEVEL="INFO"         # DEBUG, INFO, WARNING, ERROR
export AIDER_LOG_FILE="aider.log"     # Log file path
```

### Cache and Temporary Files
```bash
export AIDER_CACHE_DIR="~/.cache/aider"     # Cache directory
export AIDER_TEMP_DIR="/tmp/aider"          # Temporary files
```

### Network Settings
```bash
export HTTPS_PROXY="http://proxy:8080"      # HTTPS proxy
export HTTP_PROXY="http://proxy:8080"       # HTTP proxy
export NO_PROXY="localhost,127.0.0.1"      # Proxy exceptions
```

## Development Settings

### Debug Mode
```bash
export AIDER_DEBUG="true"              # Enable debug mode
export AIDER_TRACE="true"              # Enable request tracing
```

### Testing
```bash
export AIDER_TEST_MODE="true"          # Enable test mode
export AIDER_MOCK_API="true"           # Use mock API responses
```

## Configuration Examples

### OpenAI Setup
```bash
export OPENAI_API_KEY="sk-..."
export AIDER_PROVIDER="openai"
export AIDER_MODEL="gpt-4o"
export AIDER_TEMPERATURE="0.7"
```

### Anthropic Setup
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export AIDER_PROVIDER="anthropic"
export AIDER_MODEL="claude-3-5-sonnet-20241022"
export AIDER_TEMPERATURE="0.7"
```

### OpenRouter Setup
```bash
export OPENROUTER_API_KEY="sk-or-..."
export AIDER_PROVIDER="openai"
export AIDER_BASE_URL="https://openrouter.ai/api/v1"
export AIDER_MODEL="anthropic/claude-3.5-sonnet"
```

### Local Development
```bash
export OPENAI_API_KEY="local-key"
export AIDER_PROVIDER="openai"
export AIDER_BASE_URL="http://localhost:11434/v1"
export AIDER_MODEL="llama3.1:8b"
export AIDER_AUTO_APPLY="true"
export AIDER_VERBOSE="true"
```

### Production Environment
```bash
export OPENAI_API_KEY="sk-..."
export AIDER_PROVIDER="openai"
export AIDER_MODEL="gpt-4o"
export AIDER_AUTO_APPLY="false"
export AIDER_AUTO_COMMIT="true"
export AIDER_VERBOSE="false"
```

## Environment Files

### .env File Support
Create a `.env` file in your project:
```bash
# .env
OPENAI_API_KEY=sk-...
AIDER_PROVIDER=openai
AIDER_MODEL=gpt-4o
AIDER_AUTO_APPLY=false
```

Load with:
```bash
# Install python-dotenv if not already installed
pip install python-dotenv

# Load .env file
set -a; source .env; set +a
aidant
```

### Multiple Environments
```bash
# Development
cp .env.development .env

# Production
cp .env.production .env

# Testing
cp .env.testing .env
```

## Shell Integration

### Bash/Zsh Profile
Add to `~/.bashrc` or `~/.zshrc`:
```bash
# Aidant configuration
export OPENAI_API_KEY="sk-..."
export AIDER_PROVIDER="openai"
export AIDER_MODEL="gpt-4o"
export AIDER_THEME="monokai"

# Aliases
alias ai='aidant'
alias aid='aidant --verbose'
alias aif='aidant --files'
```

### Fish Shell
Add to `~/.config/fish/config.fish`:
```fish
# Aidant configuration
set -x OPENAI_API_KEY "sk-..."
set -x AIDER_PROVIDER "openai"
set -x AIDER_MODEL "gpt-4o"

# Aliases
alias ai='aidant'
alias aid='aidant --verbose'
```

## Security Considerations

### API Key Protection
```bash
# Use restricted permissions
chmod 600 ~/.env

# Don't commit to version control
echo ".env" >> .gitignore

# Use environment-specific files
.env.local      # Local development (not committed)
.env.production # Production (deployed separately)
```

### Proxy Settings
```bash
# Corporate environments
export HTTPS_PROXY="http://corporate-proxy:8080"
export HTTP_PROXY="http://corporate-proxy:8080"
export NO_PROXY="localhost,127.0.0.1,internal.company.com"
```

## Validation

### Check Current Settings
```bash
# Show all Aider-related environment variables
env | grep AIDER

# Test configuration
aidant --help
```

### Verify API Keys
```bash
# Test OpenAI key
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models

# Test Anthropic key
curl -H "x-api-key: $ANTHROPIC_API_KEY" \
     https://api.anthropic.com/v1/messages
```

## Troubleshooting

### Common Issues
```bash
# API key not found
echo $OPENAI_API_KEY  # Should show your key

# Wrong provider
echo $AIDER_PROVIDER  # Should match your API key

# Permission denied
ls -la ~/.env         # Check file permissions
```

### Debug Environment
```bash
# Show all environment variables
printenv | sort

# Show Aider-specific variables
printenv | grep -i aider

# Test with verbose mode
AIDER_VERBOSE=true aidant
```

### Reset Configuration
```bash
# Unset all Aider variables
unset $(env | grep AIDER | cut -d= -f1)

# Start fresh
aidant --provider openai --api-key $OPENAI_API_KEY
```