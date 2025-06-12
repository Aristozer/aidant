# CLI Commands

All commands in Aider v2 start with `/` and can be used during a chat session.

## File Management

### `/add <file1> [file2] ...`
Add files to the conversation context.
```
/add src/main.py
/add src/utils.py src/config.py
```

### `/files`
Show all files currently in context.
```
/files
```

### `/clear`
Remove all files from context (with confirmation).
```
/clear
```

## Repository Commands

### `/status`
Show git repository status.
```
/status
```

### `/diff <file>`
Show changes in a specific file.
```
/diff src/main.py
```

### `/history [limit]`
Show recent commit history.
```
/history        # Show last 10 commits
/history 20     # Show last 20 commits
```

## Session Information

### `/session`
Display current session information.
```
/session
```

### `/models`
Show available models for current provider.
```
/models
```

### `/help`
Show help information and available commands.
```
/help
```

## System Commands

### `/exit`
Exit Aider v2.
```
/exit
```

## Command Examples

### Adding Multiple Files
```
> /add src/calculator.py tests/test_calculator.py
✅ Added 2 files to context
```

### Checking Repository Status
```
> /status
Repository status:

Modified:
  src/calculator.py
  
Untracked:
  new_feature.py
```

### Viewing File Changes
```
> /diff src/calculator.py
Diff for src/calculator.py:
@@ -10,6 +10,9 @@ def divide(a, b):
+    if b == 0:
+        raise ValueError("Cannot divide by zero")
     return a / b
```

### Session Information
```
> /session
Session Information:
  ID: session_abc123
  Status: active
  Messages: 5
  Active files: 2
  Context size: 1,247 characters
```

### Commit History
```
> /history 5
Recent commits (last 5):
  a1b2c3d4 - AI: Add error handling to divide function
    by aider at 2024-01-15 10:30:00
    files: src/calculator.py

  e5f6g7h8 - AI: Implement calculator class
    by aider at 2024-01-15 10:15:00
    files: src/calculator.py, tests/test_calculator.py
```

## Tips

### File Paths
- Use relative paths from your workspace directory
- Tab completion works for file paths
- Wildcards are not supported

### Context Management
- Add related files together for better AI understanding
- Remove unnecessary files with `/clear` to reduce token usage
- Use `/files` to verify your current context

### Repository Integration
- All changes are automatically committed
- Use `/status` to see what's changed since last commit
- Use `/diff` to review changes before they're applied

### Error Handling
- Invalid commands show helpful error messages
- File not found errors are displayed clearly
- Use `/help` if you forget command syntax