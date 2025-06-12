# Session Management

Aider v2 manages conversation sessions and file context to provide effective AI assistance.

## Session Lifecycle

### Starting a Session
```bash
# Start with empty context
aider-v2

# Start with initial files
aider-v2 --files src/main.py src/utils.py

# Start with specific configuration
aider-v2 --provider openai --model gpt-4o --verbose
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

### Ending a Session
```
> /exit
Session completed. Messages: 8
```

## File Context Management

### Adding Files
```bash
# Add single file
> /add src/calculator.py

# Add multiple files
> /add src/main.py src/utils.py tests/test_main.py

# Add with wildcards (not supported - use explicit paths)
> /add src/*.py  # This won't work
```

### Viewing Context
```bash
# Show files in context
> /files
Files in context:
  1. src/calculator.py
  2. src/utils.py
  3. tests/test_calculator.py
```

### Managing Context
```bash
# Clear all files from context
> /clear
Clear all files from context? (y/N): y
✅ Context cleared

# Add files back
> /add src/calculator.py
✅ Added 1 files to context
```

## Context Best Practices

### Optimal Context Size
- **Small Projects**: Add all relevant files
- **Large Projects**: Focus on specific modules
- **Refactoring**: Include related files and tests
- **Bug Fixes**: Include failing tests and implementation

### File Selection Strategy
```bash
# For new features
/add src/feature.py tests/test_feature.py

# For bug fixes
/add src/buggy_module.py tests/test_buggy_module.py

# For refactoring
/add src/old_module.py src/new_module.py src/shared.py
```

### Context Limits
- Token limits vary by model
- Large files may be truncated
- Too many files reduce individual file detail
- Monitor context size with `/session`

## Session Types

### Development Session
```bash
# Start with core files
aider-v2 --files src/main.py src/config.py

# Add features incrementally
> /add src/new_feature.py
> Implement the new authentication feature

# Add tests
> /add tests/test_auth.py
> Add comprehensive tests for the auth feature
```

### Debugging Session
```bash
# Start with failing test
aider-v2 --files tests/test_calculator.py

# Add implementation
> /add src/calculator.py
> Fix the failing test in test_divide_by_zero

# Check status
> /status
> /diff src/calculator.py
```

### Refactoring Session
```bash
# Add all related files
aider-v2 --files src/old_module.py src/related.py tests/

# Plan refactoring
> Refactor the old_module to use modern Python patterns

# Apply changes incrementally
> Now update the tests to match the new structure
```

## Context Strategies

### Incremental Context
Start small and add files as needed:
```bash
# Start minimal
> /add src/main.py

# Add dependencies as they come up
> /add src/utils.py
> /add src/config.py
```

### Full Context
Add all relevant files upfront:
```bash
# Add complete module
> /add src/auth/ tests/auth/ config/auth.yaml
```

### Focused Context
Keep context specific to current task:
```bash
# Clear and refocus
> /clear
> /add src/specific_feature.py tests/test_specific.py
```

## Session Persistence

### Session State
- File context persists during session
- Conversation history is maintained
- Configuration remains active
- Repository state is tracked

### Between Sessions
- No automatic persistence between sessions
- Must re-add files when restarting
- Git history preserves all changes
- Configuration files maintain settings

### Session Recovery
```bash
# After restart, check what was changed
git log --oneline -10

# Re-add relevant files
aider-v2 --files $(git diff --name-only HEAD~5)
```

## Advanced Session Management

### Multiple Workspaces
```bash
# Work on different projects
cd project1/
aider-v2 --workspace .

# Switch to another project
cd ../project2/
aider-v2 --workspace .
```

### Session Templates
Create scripts for common session types:
```bash
#!/bin/bash
# start-feature-session.sh
aider-v2 --provider openai \
         --model gpt-4o \
         --files src/main.py src/config.py tests/test_main.py
```

### Context Presets
```bash
# Development preset
alias aider-dev='aider-v2 --files src/ tests/ --verbose'

# Quick fix preset
alias aider-fix='aider-v2 --files src/main.py --auto-apply'
```

## Monitoring and Optimization

### Context Size Monitoring
```bash
# Check context regularly
> /session
Session Information:
  Context size: 15,247 characters  # Monitor this

# If too large, remove unnecessary files
> /clear
> /add essential_file.py
```

### Performance Tips
- Remove large files not directly relevant
- Use `/clear` to reset context when switching tasks
- Add files incrementally rather than all at once
- Monitor token usage with verbose mode

### Memory Management
```bash
# For long sessions, periodically check
> /session

# If context gets too large
> /clear
> /add current_focus_files.py
```

## Troubleshooting

### Context Issues
```bash
# File not found
> /add nonexistent.py
File not found: nonexistent.py

# Permission denied
> /add /etc/passwd
Permission denied: /etc/passwd
```

### Session Problems
```bash
# Session state corruption
# Restart Aider v2
exit
aider-v2

# Re-add files
> /add previous_files.py
```

### Performance Issues
```bash
# Large context causing slowness
> /session
Context size: 50,000 characters  # Too large

# Reduce context
> /clear
> /add core_files_only.py
```

## Integration Tips

### With IDEs
- Keep Aider v2 session focused on current task
- Use IDE for navigation, Aider for changes
- Sync file context with IDE's open files

### With Testing
```bash
# Add tests first
> /add tests/test_feature.py

# Then implementation
> /add src/feature.py

# Request test-driven development
> Implement the feature to make these tests pass
```

### With Documentation
```bash
# Include relevant docs
> /add README.md docs/api.md

# Request documentation updates
> Update the documentation to reflect these changes
```