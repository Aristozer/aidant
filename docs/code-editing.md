# Code Editing

Aider v2 uses the EditBlock coder to make precise changes to your code files.

## How It Works

### EditBlock Format
Aider v2 shows proposed changes using a search-and-replace format:

```
filename.py
<<<<<<< SEARCH
old code here
=======
new code here
>>>>>>> REPLACE
```

### Example Edit
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

## Edit Process

1. **AI Analysis**: The AI analyzes your request and current code
2. **Change Proposal**: Shows exact changes in EditBlock format
3. **User Confirmation**: You review and approve/reject changes
4. **Application**: Changes are applied to files
5. **Auto-commit**: Changes are automatically committed to git

## Features

### Precise Editing
- Exact line-by-line replacements
- Preserves formatting and indentation
- Handles multiple changes in one file
- Supports changes across multiple files

### Safety Features
- **Backup Creation**: Original files are backed up before changes
- **Diff Display**: See exactly what will change
- **User Confirmation**: Approve each change before application
- **Git Integration**: All changes are tracked in version control

### Smart Context
- Understands file structure and syntax
- Maintains code style consistency
- Preserves imports and dependencies
- Handles complex refactoring operations

## Configuration

### Coder Settings
```toml
[coder]
type = "editblock"           # Coder type (currently only editblock)
auto_apply = false           # Skip confirmation prompts
show_diffs = true            # Show diffs before applying
backup_files = true          # Create backups before editing
```

### Environment Variables
```bash
export AIDER_AUTO_APPLY="false"    # Require confirmation
export AIDER_SHOW_DIFFS="true"     # Show diffs
```

## Usage Examples

### Simple Function Addition
```
> Add a multiply function to the calculator

calculator.py
<<<<<<< SEARCH
def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
=======
def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def multiply(a, b):
    return a * b
>>>>>>> REPLACE

Apply these changes? (y/N): y
✅ Changes applied and committed: abc123
```

### Multiple File Changes
```
> Refactor the calculator to use a class structure

calculator.py
<<<<<<< SEARCH
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b
=======
class Calculator:
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b
>>>>>>> REPLACE

main.py
<<<<<<< SEARCH
from calculator import add, subtract

result = add(5, 3)
=======
from calculator import Calculator

calc = Calculator()
result = calc.add(5, 3)
>>>>>>> REPLACE

Apply these changes? (y/N): y
✅ Changes applied and committed: def456
```

### Complex Refactoring
```
> Add error handling and logging to all calculator methods

calculator.py
<<<<<<< SEARCH
import logging

class Calculator:
    def add(self, a, b):
        return a + b
=======
import logging

logger = logging.getLogger(__name__)

class Calculator:
    def add(self, a, b):
        try:
            logger.info(f"Adding {a} + {b}")
            result = a + b
            logger.info(f"Result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in add: {e}")
            raise
>>>>>>> REPLACE
```

## Best Practices

### File Context
- Add relevant files to context with `/add`
- Include related files (tests, imports, etc.)
- Keep context focused on the task

### Clear Requests
```bash
# Good: Specific and clear
"Add input validation to the login function"

# Better: Include requirements
"Add input validation to the login function - check for empty username/password and valid email format"

# Best: Include context
"Add input validation to the login function in auth.py - check for empty username/password, valid email format, and minimum password length of 8 characters"
```

### Incremental Changes
- Make small, focused changes
- Test changes before requesting more
- Build complexity gradually

## Troubleshooting

### Changes Not Applied
- Check file permissions
- Ensure files are not read-only
- Verify git repository is writable

### Unexpected Results
- Review the proposed changes carefully
- Check if all relevant files are in context
- Use `/diff` to see current file state

### Merge Conflicts
- Aider v2 works on clean repositories
- Commit or stash changes before starting
- Use `/status` to check repository state

## Advanced Features

### Auto-apply Mode
```bash
# Skip confirmation prompts
aider-v2 --auto-apply

# Or set in config
[coder]
auto_apply = true
```

### Backup Management
```bash
# Backups are created in .aider_backup/
ls .aider_backup/

# Restore from backup if needed
cp .aider_backup/filename.py.backup filename.py
```

### Custom Commit Messages
```toml
[repository]
commit_message_template = "feat: {description}"
```

## Limitations

### File Types
- Works best with text files
- Supports most programming languages
- Binary files are not supported

### File Size
- Large files may hit token limits
- Consider breaking large files into smaller modules
- Use focused context for better results

### Concurrent Editing
- Don't edit files manually while Aider is running
- Changes may conflict with AI modifications
- Use git to manage concurrent changes