# Repository Management

Aider v2 integrates seamlessly with Git to track all changes and maintain a clean development workflow.

## Git Integration

### Auto-commit
- All changes are automatically committed
- Each change gets a descriptive commit message
- Commits include only the modified files
- No manual git commands needed

### Commit Messages
Default format: `AI: {description}`

Examples:
- `AI: Add error handling to divide function`
- `AI: Refactor calculator to use class structure`
- `AI: Add unit tests for authentication module`

## Repository Commands

### `/status`
Show current repository status:
```
> /status
Repository status:

Modified:
  src/calculator.py
  tests/test_calculator.py

Untracked:
  new_feature.py
```

### `/diff <file>`
Show changes in a specific file:
```
> /diff src/calculator.py
Diff for src/calculator.py:
@@ -10,6 +10,9 @@ def divide(a, b):
+    if b == 0:
+        raise ValueError("Cannot divide by zero")
     return a / b
```

### `/history [limit]`
View recent commits:
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

## Configuration

### Repository Settings
```toml
[repository]
auto_commit = true                           # Enable auto-commit
commit_message_template = "AI: {description}" # Commit message format
ignore_patterns = [                         # Files to ignore
    ".git/*",
    "__pycache__/*",
    "*.pyc",
    "node_modules/*",
    ".venv/*",
    "dist/*",
    "build/*",
    ".DS_Store",
    "*.log",
    "*.tmp",
    ".pytest_cache/*"
]
```

### Environment Variables
```bash
export AIDER_AUTO_COMMIT="true"
```

### Custom Commit Messages
```toml
[repository]
commit_message_template = "feat: {description}"
commit_message_template = "[AI] {description}"
commit_message_template = "🤖 {description}"
```

## Workflow Examples

### Starting with Clean Repository
```bash
# Check status before starting
git status

# Start Aider v2
aider-v2 --provider openai --model gpt-4o

# Make changes
> Add logging to the main function

# Changes are automatically committed
✅ Changes applied and committed: abc123
```

### Working with Existing Changes
```bash
# If you have uncommitted changes
git add .
git commit -m "Manual changes before AI session"

# Then start Aider v2
aider-v2
```

### Reviewing Changes
```bash
# After Aider session, review commits
git log --oneline -10

# See detailed changes
git show abc123

# Compare with previous state
git diff HEAD~3..HEAD
```

## File Ignore Patterns

### Default Patterns
Aider v2 automatically ignores common files:
- `.git/*` - Git metadata
- `__pycache__/*` - Python cache
- `*.pyc` - Python bytecode
- `node_modules/*` - Node.js dependencies
- `.venv/*`, `venv/*` - Virtual environments
- `dist/*`, `build/*` - Build artifacts
- `.DS_Store` - macOS metadata
- `*.log`, `*.tmp` - Temporary files

### Custom Ignore Patterns
```toml
[repository]
ignore_patterns = [
    ".git/*",
    "*.pyc",
    "custom_cache/*",
    "*.backup",
    "secrets.env"
]
```

### Project-specific Ignores
Use `.gitignore` for standard git ignores:
```gitignore
# .gitignore
__pycache__/
*.pyc
.env
node_modules/
dist/
```

## Best Practices

### Repository Preparation
1. **Clean State**: Start with a clean repository
2. **Backup**: Create a branch before major changes
3. **Small Commits**: Let Aider make focused commits
4. **Review**: Check commits after sessions

### Branching Strategy
```bash
# Create feature branch for AI session
git checkout -b feature/ai-refactoring

# Start Aider v2
aider-v2

# After session, review and merge
git checkout main
git merge feature/ai-refactoring
```

### Commit Management
```bash
# Squash AI commits if needed
git rebase -i HEAD~5

# Amend commit messages if needed
git commit --amend -m "Better commit message"
```

## Advanced Features

### Selective Commits
Aider v2 commits only the files it modifies:
```bash
# If you have other changes
echo "manual change" >> other_file.txt

# Aider commits won't include other_file.txt
> Add function to calculator
✅ Changes applied and committed: abc123

# Your manual changes remain uncommitted
git status
# modified: other_file.txt
```

### Commit Hooks
Git hooks work normally with Aider v2:
```bash
# Pre-commit hooks run on AI commits
# .git/hooks/pre-commit
#!/bin/bash
black --check .
flake8 .
```

### Repository Validation
Aider v2 validates repository state:
- Checks if directory is a git repository
- Warns about uncommitted changes
- Ensures write permissions

## Troubleshooting

### Permission Issues
```bash
# Check repository permissions
ls -la .git/

# Fix permissions if needed
chmod -R u+w .git/
```

### Merge Conflicts
```bash
# Resolve conflicts before starting Aider
git status
git add .
git commit -m "Resolve conflicts"

# Then start Aider v2
aider-v2
```

### Large Repositories
```bash
# For large repos, consider shallow clones
git clone --depth 1 <repo-url>

# Or work in subdirectories
cd specific-module/
aider-v2 --workspace .
```

### Commit History Cleanup
```bash
# Interactive rebase to clean up AI commits
git rebase -i HEAD~10

# Squash related commits
# Edit commit messages
# Remove unnecessary commits
```

## Integration with CI/CD

### GitHub Actions
```yaml
# .github/workflows/ai-review.yml
name: Review AI Changes
on:
  push:
    branches: [ main ]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Check AI commits
      run: |
        git log --oneline -10 | grep "AI:"
```

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```