# User Interface

Aidant features a rich terminal interface with syntax highlighting, themes, and interactive elements.

## Terminal Interface

### Welcome Screen
```
🤖 Aidant - AI Pair Programming Assistant
Using openai gpt-4o model. Type '/help' for commands or start chatting!
```

### Input Prompt
```
> your message here
```

### Status Messages
```
✅ Added 1 files to context
⚠️  File not found: missing.py
❌ Error: Invalid API key
ℹ️  Session completed. Messages: 5
```

## Syntax Highlighting

### Code Display
Files are displayed with syntax highlighting:
```python
# calculator.py
def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

### Diff Display
Changes are shown with color-coded diffs:
```diff
@@ -1,3 +1,5 @@
 def divide(a, b):
+    if b == 0:
+        raise ValueError("Cannot divide by zero")
     return a / b
```

### EditBlock Display
Proposed changes use clear formatting:
```
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
```

## Interactive Elements

### Confirmation Prompts
```
Apply these changes? (y/N): y
Clear all files from context? (y/N): n
Exit Aider? (y/N): y
```

### Progress Indicators
```
⠋ Thinking...
⠙ Processing request...
⠹ Applying changes...
```

### File Content Display
```
📁 src/calculator.py (45 lines)
───────────────────────────────────────
 1 │ def add(a, b):
 2 │     return a + b
 3 │ 
 4 │ def subtract(a, b):
 5 │     return a - b
───────────────────────────────────────
```

## Configuration

### UI Settings
```toml
[ui]
theme = "monokai"                # Syntax highlighting theme
show_line_numbers = true         # Show line numbers in code
syntax_highlighting = true       # Enable syntax highlighting
confirm_changes = true           # Show confirmation prompts
verbose = false                  # Show detailed output
```

### Available Themes
- `monokai` (default)
- `github`
- `solarized-dark`
- `solarized-light`
- `dracula`
- `nord`

### Environment Variables
```bash
export AIDER_THEME="monokai"
export AIDER_VERBOSE="true"
```

## Features

### Smart Formatting
- Automatic code indentation
- Preserved whitespace
- Language-specific highlighting
- Unicode support

### Responsive Layout
- Adapts to terminal width
- Wraps long lines appropriately
- Truncates very long output
- Scrollable content

### Error Handling
- Clear error messages
- Helpful suggestions
- Graceful degradation
- Recovery options

## Customization

### Theme Selection
```bash
# Set theme via command line
aidant --theme dracula

# Set theme via environment
export AIDER_THEME="github"
aidant

# Set theme via config file
[ui]
theme = "solarized-dark"
```

### Verbosity Levels
```bash
# Quiet mode (minimal output)
aidant --quiet

# Normal mode (default)
aidant

# Verbose mode (detailed output)
aidant --verbose
```

### Line Numbers
```toml
[ui]
show_line_numbers = true    # Show line numbers
show_line_numbers = false   # Hide line numbers
```

## Keyboard Shortcuts

### During Input
- `Ctrl+C` - Interrupt current operation
- `Ctrl+D` - Exit Aidant
- `Tab` - File path completion (where supported)
- `Up/Down` - Command history (where supported)

### During Confirmation
- `y` or `Y` - Yes
- `n` or `N` - No
- `Enter` - Default (usually No)

## Output Types

### Information Messages
```
ℹ️  Using openai gpt-4o model
ℹ️  Added 2 files to context
ℹ️  Session completed. Messages: 5
```

### Success Messages
```
✅ Changes applied and committed: abc123
✅ Added 1 files to context
✅ Context cleared
```

### Warning Messages
```
⚠️  File not found: missing.py
⚠️  Large context size may affect performance
⚠️  No active session
```

### Error Messages
```
❌ Error: Invalid API key
❌ Error: File permission denied
❌ Command error: Unknown command
```

### Debug Output (Verbose Mode)
```
🔍 Loading configuration from .aider.toml
🔍 Initializing OpenAI provider
🔍 Setting up git repository
🔍 Starting chat session
```

## Accessibility

### Screen Reader Support
- Clear text descriptions
- Structured output
- Logical reading order
- Alternative text for symbols

### High Contrast
```toml
[ui]
theme = "high-contrast"
```

### Large Text
Terminal font size is controlled by your terminal emulator settings.

## Performance

### Large Files
- Files over 1000 lines are truncated in display
- Full content is still processed
- Use `/diff` for specific changes

### Long Sessions
- Output is paginated for readability
- History is maintained in memory
- Use `/clear` to reset context

### Network Indicators
```
🌐 Connecting to OpenAI...
📡 Sending request...
⬇️  Receiving response...
```

## Troubleshooting

### Display Issues
```bash
# Check terminal capabilities
echo $TERM

# Test color support
aidant --theme github

# Disable colors if needed
export NO_COLOR=1
aidant
```

### Unicode Problems
```bash
# Set proper locale
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
```

### Terminal Compatibility
```bash
# For older terminals
aidant --no-syntax-highlighting

# For minimal terminals
aidant --theme none
```

## Advanced Features

### Custom Prompts
The interface adapts to different contexts:
```
> /add file.py        # Command mode
> regular message     # Chat mode
Apply changes? (y/N): # Confirmation mode
```

### Rich Content
- Tables for structured data
- Lists for multiple items
- Code blocks for file content
- Diffs for changes

### Session Context
```
📊 Session Stats:
   Messages: 8
   Files: 3
   Commits: 2
   Duration: 15m 32s
```

## Integration

### Terminal Emulators
Tested with:
- iTerm2 (macOS)
- Terminal.app (macOS)
- GNOME Terminal (Linux)
- Windows Terminal
- VS Code integrated terminal

### Shell Integration
```bash
# Add to .bashrc or .zshrc
alias ai='aidant'
alias aid='aidant --verbose'
```

### Tmux/Screen
Works well in terminal multiplexers:
```bash
# In tmux session
tmux new-session -d -s aider
tmux send-keys -t aider 'aidant' Enter
```