# Basic Usage

## Starting Aidant

### Simple Start
```bash
# Start in current directory with default settings
aidant
```

### With Specific Model
```bash
# Use specific model and provider
aidant --provider openai --model gpt-4o
aidant --provider anthropic --model claude-3-5-sonnet-20241022
```

### With Initial Files
```bash
# Add files to context when starting
aidant --files src/main.py src/utils.py
```

## Basic Workflow

1. **Start Aidant**
   ```bash
   aidant --provider openai --model gpt-4o
   ```

2. **Add files to context**
   ```
   /add src/calculator.py
   ```

3. **Make requests**
   ```
   Add error handling to the divide function
   ```

4. **Review and apply changes**
   - Aider will show proposed changes
   - Confirm with `y` or reject with `n`

5. **Continue the conversation**
   ```
   Now add unit tests for the calculator
   ```

## Example Session

```
🤖 Aidant - AI Pair Programming Assistant
Using openai gpt-4o model. Type '/help' for commands or start chatting!

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

> /status
Repository status:
No changes (all committed)

> /exit
Session completed. Messages: 2
```

## Key Concepts

### File Context
- Add files with `/add <file>`
- View current files with `/files`
- Clear context with `/clear`

### Auto-commit
- Changes are automatically committed to git
- Each change gets a descriptive commit message
- Use `/status` to see repository state

### Commands vs Chat
- Commands start with `/` (e.g., `/add`, `/help`)
- Regular messages are sent to the AI
- Type `/help` to see all available commands

## Next Steps

- [CLI Commands](cli-commands.md) - Learn all available commands
- [Configuration](configuration.md) - Customize your setup
- [LLM Providers](llm-providers.md) - Explore different AI models