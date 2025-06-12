# Troubleshooting

Common issues and solutions for Aider v2.

## Installation Issues

### Python Version Compatibility
```bash
# Check Python version
python --version  # Should be 3.10+

# If using older Python
pyenv install 3.11
pyenv local 3.11
```

### Package Installation Errors
```bash
# Update pip first
pip install --upgrade pip

# Install with verbose output
pip install -e . -v

# Clear pip cache if needed
pip cache purge
```

### Permission Errors
```bash
# Use user installation
pip install --user -e .

# Or use virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
pip install -e .
```

## API Key Issues

### OpenAI API Key Problems
```bash
# Verify key format
echo $OPENAI_API_KEY  # Should start with "sk-"

# Test key validity
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models

# Common issues
export OPENAI_API_KEY="sk-..."  # Remove extra quotes/spaces
```

### Anthropic API Key Problems
```bash
# Verify key format
echo $ANTHROPIC_API_KEY  # Should start with "sk-ant-"

# Test key validity
curl -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "Content-Type: application/json" \
     https://api.anthropic.com/v1/messages
```

### API Key Not Found
```bash
# Check environment variables
env | grep API_KEY

# Set in current session
export OPENAI_API_KEY="your-key"

# Add to shell profile
echo 'export OPENAI_API_KEY="your-key"' >> ~/.bashrc
source ~/.bashrc
```

## Connection Issues

### Network Connectivity
```bash
# Test basic connectivity
ping api.openai.com
ping api.anthropic.com

# Test HTTPS
curl -I https://api.openai.com/v1/models
```

### Proxy Configuration
```bash
# Set proxy environment variables
export HTTPS_PROXY="http://proxy:8080"
export HTTP_PROXY="http://proxy:8080"

# Test with proxy
curl --proxy http://proxy:8080 https://api.openai.com/v1/models
```

### Firewall Issues
```bash
# Check if ports are blocked
telnet api.openai.com 443
telnet api.anthropic.com 443

# Common corporate firewall ports
# 80 (HTTP), 443 (HTTPS), 8080 (proxy)
```

## Model and Provider Issues

### Invalid Model Names
```bash
# Check available models
aider-v2 --provider openai --model gpt-4o --verbose

# Common model name errors
# Wrong: "gpt4", "claude3"
# Correct: "gpt-4o", "claude-3-5-sonnet-20241022"
```

### Provider Compatibility
```bash
# Base URL only works with OpenAI provider
aider-v2 --provider openai --base-url https://openrouter.ai/api/v1

# This will fail:
# aider-v2 --provider anthropic --base-url https://example.com
```

### Rate Limiting
```bash
# OpenAI rate limits
# Free tier: 3 RPM, 200 RPD
# Paid tier: Higher limits

# Anthropic rate limits
# Vary by plan and model

# Check rate limit headers in verbose mode
aider-v2 --verbose
```

## File and Repository Issues

### File Permission Errors
```bash
# Check file permissions
ls -la file.py

# Fix permissions
chmod 644 file.py

# Check directory permissions
ls -la .

# Fix directory permissions
chmod 755 .
```

### Git Repository Issues
```bash
# Not a git repository
git init
git add .
git commit -m "Initial commit"

# Uncommitted changes
git status
git add .
git commit -m "Save current work"

# Repository corruption
git fsck
git gc
```

### File Not Found Errors
```bash
# Check file exists
ls -la src/file.py

# Use absolute paths
/add /full/path/to/file.py

# Check current directory
pwd
ls -la
```

## Configuration Issues

### Invalid Configuration File
```bash
# Check TOML syntax
python -c "import toml; print(toml.load('.aider.toml'))"

# Common TOML errors
# Missing quotes: provider = openai (wrong)
# Correct: provider = "openai"

# Invalid boolean: auto_apply = True (wrong)
# Correct: auto_apply = true
```

### Environment Variable Conflicts
```bash
# Check all Aider variables
env | grep AIDER

# Unset conflicting variables
unset AIDER_MODEL

# Start fresh
aider-v2 --provider openai --model gpt-4o
```

### Configuration Not Loading
```bash
# Check file location
ls -la .aider.toml
ls -la ~/.config/aider/config.toml

# Use verbose mode to see what's loaded
aider-v2 --verbose
```

## Performance Issues

### Slow Response Times
```bash
# Check network latency
ping api.openai.com

# Use faster models
aider-v2 --model gpt-3.5-turbo  # Faster than gpt-4

# Reduce context size
/clear
/add essential_files_only.py
```

### Large File Handling
```bash
# Files over 1000 lines are truncated in display
# But full content is still processed

# For very large files, consider:
# 1. Breaking into smaller modules
# 2. Using focused context
# 3. Working on specific functions
```

### Memory Usage
```bash
# Monitor memory usage
top -p $(pgrep -f aider-v2)

# Reduce context if needed
/session  # Check context size
/clear    # Reset context
```

## Terminal and Display Issues

### Unicode/Encoding Problems
```bash
# Set proper locale
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# Check terminal encoding
locale
```

### Color Display Issues
```bash
# Disable colors if needed
export NO_COLOR=1
aider-v2

# Force colors
export FORCE_COLOR=1
aider-v2

# Try different theme
aider-v2 --theme github
```

### Terminal Compatibility
```bash
# For older terminals
aider-v2 --no-syntax-highlighting

# Check terminal capabilities
echo $TERM
tput colors
```

## Command and Usage Issues

### Unknown Command Errors
```bash
# Check command syntax
/help

# Common mistakes
/files file.py  # Wrong - /files takes no arguments
/add file.py    # Correct

/status file.py # Wrong - /status takes no arguments
/diff file.py   # Correct - /diff takes filename
```

### Session State Issues
```bash
# No active session
# Start Aider first, then use commands

# Session corruption
# Exit and restart Aider
/exit
aider-v2
```

### File Context Problems
```bash
# Too many files in context
/session  # Check context size
/clear    # Remove all files
/add essential_files.py  # Add back only needed files

# Files not updating
# Make sure files aren't open in other editors
# Check file permissions
```

## Debugging

### Enable Verbose Mode
```bash
# See detailed output
aider-v2 --verbose

# Check what's happening
export AIDER_VERBOSE=true
aider-v2
```

### Check Logs
```bash
# Default log file
tail -f aider_v2.log

# Custom log file
export AIDER_LOG_FILE="debug.log"
aider-v2 --verbose
tail -f debug.log
```

### Network Debugging
```bash
# Enable request tracing
export AIDER_TRACE=true
aider-v2 --verbose

# Use curl to test API directly
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model":"gpt-3.5-turbo","messages":[{"role":"user","content":"test"}]}' \
     https://api.openai.com/v1/chat/completions
```

## Getting Help

### Built-in Help
```bash
# Command line help
aider-v2 --help

# In-session help
/help

# Check version
aider-v2 --version
```

### Diagnostic Information
```bash
# System information
python --version
pip list | grep aider
git --version

# Environment
env | grep -E "(AIDER|OPENAI|ANTHROPIC)"

# Configuration
cat .aider.toml
```

### Common Error Messages

#### "Invalid API key"
- Check API key format and validity
- Ensure correct provider is selected
- Verify environment variable is set

#### "Model not found"
- Check model name spelling
- Verify model is available for your provider
- Check provider documentation

#### "File not found"
- Verify file path is correct
- Check file permissions
- Use absolute paths if needed

#### "Repository not found"
- Initialize git repository: `git init`
- Check current directory
- Ensure you're in the right project

#### "Connection timeout"
- Check network connectivity
- Verify proxy settings
- Try increasing timeout value

### Recovery Procedures

#### Reset Configuration
```bash
# Remove all configuration
rm .aider.toml
unset $(env | grep AIDER | cut -d= -f1)

# Start with minimal setup
export OPENAI_API_KEY="your-key"
aider-v2 --provider openai --model gpt-4o
```

#### Clean Installation
```bash
# Uninstall
pip uninstall aider-v2

# Clear cache
pip cache purge
rm -rf ~/.cache/aider

# Reinstall
pip install -e .
```

#### Repository Recovery
```bash
# If git repository is corrupted
git fsck
git gc --prune=now

# If that fails, backup and reinitialize
cp -r . ../backup
rm -rf .git
git init
git add .
git commit -m "Recovered repository"
```