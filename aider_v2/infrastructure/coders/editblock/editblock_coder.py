"""EditBlock coder implementation."""

import re
from typing import List, Dict, Any
from pathlib import Path

from ....core.interfaces.coder import (
    ICoder, CodeChange, ChangeType, ValidationResult, ParseError, ApplyError
)


class EditBlockCoder(ICoder):
    """Coder implementation for the EditBlock format."""
    
    def __init__(self, workspace_path: str) -> None:
        self.workspace_path = Path(workspace_path)
        self._search_replace_pattern = re.compile(
            r'```(?:[\w+]*\n)?(.*?)\n<<<<<<< SEARCH\n(.*?)\n=======\n(.*?)\n>>>>>>> REPLACE\n```',
            re.DOTALL | re.MULTILINE
        )
        self._simple_pattern = re.compile(
            r'(.*?)\n<<<<<<< SEARCH\n(.*?)\n=======\n(.*?)\n>>>>>>> REPLACE',
            re.DOTALL | re.MULTILINE
        )
    
    @property
    def name(self) -> str:
        return "editblock"
    
    @property
    def supported_languages(self) -> List[str]:
        return [
            "python", "javascript", "typescript", "java", "cpp", "c", "go", 
            "rust", "php", "ruby", "swift", "kotlin", "scala", "html", "css",
            "sql", "bash", "shell", "yaml", "json", "xml", "markdown"
        ]
    
    def parse_response(self, llm_response: str) -> List[CodeChange]:
        """Parse LLM response to extract SEARCH/REPLACE blocks."""
        changes = []
        
        # Try the fenced code block pattern first
        matches = self._search_replace_pattern.findall(llm_response)
        
        # If no matches, try the simple pattern
        if not matches:
            matches = self._simple_pattern.findall(llm_response)
        
        if not matches:
            # Look for file creation patterns
            create_pattern = re.compile(
                r'```(?:[\w+]*\n)?(.*?)\n(.*?)```',
                re.DOTALL | re.MULTILINE
            )
            create_matches = create_pattern.findall(llm_response)
            
            for match in create_matches:
                filename, content = match
                filename = filename.strip()
                
                if filename and not any(keyword in filename.lower() for keyword in ['search', 'replace', 'diff']):
                    changes.append(CodeChange(
                        file_path=filename,
                        change_type=ChangeType.CREATE,
                        content=content.strip(),
                        metadata={"format": "editblock", "type": "create"}
                    ))
            
            if not changes:
                raise ParseError("No valid SEARCH/REPLACE blocks or file creation patterns found in response")
        
        for match in matches:
            filename, search_content, replace_content = match
            filename = filename.strip()
            
            # Extract just the filename from the first line
            filename_lines = filename.split('\n')
            if filename_lines:
                filename = filename_lines[-1].strip()  # Take the last line which should be the filename
            
            if not filename:
                raise ParseError("Filename is required for SEARCH/REPLACE blocks")
            
            # Clean up the filename (remove any leading/trailing quotes or whitespace)
            filename = filename.strip('\'"` \t\n')
            
            # If filename still contains spaces or newlines, it's probably not a valid filename
            if '\n' in filename or len(filename.split()) > 1:
                # Try to extract a filename pattern
                import re
                filename_pattern = re.search(r'(\S+\.\w+)', filename)
                if filename_pattern:
                    filename = filename_pattern.group(1)
                else:
                    raise ParseError(f"Could not extract valid filename from: {filename}")
            
            changes.append(CodeChange(
                file_path=filename,
                change_type=ChangeType.MODIFY,
                content=replace_content,
                old_content=search_content,
                metadata={
                    "format": "editblock",
                    "search_content": search_content,
                    "replace_content": replace_content
                }
            ))
        
        return changes
    
    def validate_changes(self, changes: List[CodeChange]) -> ValidationResult:
        """Validate that the proposed changes can be applied."""
        errors = []
        warnings = []
        
        for change in changes:
            file_path = self.workspace_path / change.file_path
            
            # Check if file exists for modifications
            if change.change_type == ChangeType.MODIFY:
                if not file_path.exists():
                    errors.append(f"File {change.file_path} does not exist")
                    continue
                
                # Check if search content exists in file
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    
                    if change.old_content and change.old_content.strip() not in file_content:
                        errors.append(f"Search content not found in {change.file_path}")
                    
                    # Check for multiple matches
                    if change.old_content and file_content.count(change.old_content.strip()) > 1:
                        warnings.append(f"Multiple matches found for search content in {change.file_path}")
                        
                except Exception as e:
                    errors.append(f"Error reading {change.file_path}: {str(e)}")
            
            # Check if parent directory exists for new files
            elif change.change_type == ChangeType.CREATE:
                parent_dir = file_path.parent
                if not parent_dir.exists():
                    warnings.append(f"Parent directory {parent_dir} does not exist, will be created")
                
                # Check if file already exists
                if file_path.exists():
                    warnings.append(f"File {change.file_path} already exists, will be overwritten")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def apply_changes(self, changes: List[CodeChange]) -> bool:
        """Apply the validated changes to the filesystem."""
        try:
            for change in changes:
                file_path = self.workspace_path / change.file_path
                
                if change.change_type == ChangeType.MODIFY:
                    self._apply_modify_change(file_path, change)
                elif change.change_type == ChangeType.CREATE:
                    self._apply_create_change(file_path, change)
                elif change.change_type == ChangeType.DELETE:
                    self._apply_delete_change(file_path)
                
            return True
            
        except Exception as e:
            raise ApplyError(f"Failed to apply changes: {str(e)}")
    
    def _apply_modify_change(self, file_path: Path, change: CodeChange) -> None:
        """Apply a modification change to a file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the search content with replace content
        if change.old_content:
            search_content = change.old_content.strip()
            if search_content not in content:
                raise ApplyError(f"Search content not found in {file_path}")
            
            new_content = content.replace(search_content, change.content or "", 1)
        else:
            # If no search content, append to file
            new_content = content + "\n" + (change.content or "")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
    
    def _apply_create_change(self, file_path: Path, change: CodeChange) -> None:
        """Apply a file creation change."""
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(change.content or "")
    
    def _apply_delete_change(self, file_path: Path) -> None:
        """Apply a file deletion change."""
        if file_path.exists():
            file_path.unlink()
    
    def generate_prompt(self, context: Dict[str, Any]) -> str:
        """Generate the prompt template for EditBlock format."""
        return """
When editing files, use this format:

```
filename.py
<<<<<<< SEARCH
exact code to find and replace
=======
new code to replace it with
>>>>>>> REPLACE
```

Rules:
1. The SEARCH block must contain the exact code that exists in the file
2. The REPLACE block contains the new code to substitute
3. Include enough context in SEARCH to uniquely identify the location
4. Only show the parts that need to change, not the entire file
5. Multiple SEARCH/REPLACE blocks can be used for the same file

For new files, use:
```
filename.py
new file content here
```

Example:
```
main.py
<<<<<<< SEARCH
def hello():
    print("Hello")
=======
def hello(name="World"):
    print(f"Hello, {name}!")
>>>>>>> REPLACE
```
"""
    
    def can_handle_file(self, file_path: str) -> bool:
        """Check if this coder can handle the given file type."""
        try:
            path = Path(file_path)
            
            # Skip binary files
            binary_extensions = {'.exe', '.bin', '.jpg', '.png', '.gif', '.pdf', '.zip', '.tar', '.gz'}
            if path.suffix.lower() in binary_extensions:
                return False
            
            # Check if it's a text file by trying to read it
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        f.read(1024)  # Try to read first 1KB
                    return True
                except UnicodeDecodeError:
                    return False
            
            # For new files, assume text if extension is known
            text_extensions = {
                '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.go', '.rs',
                '.php', '.rb', '.swift', '.kt', '.scala', '.html', '.css', '.scss', '.sass',
                '.sql', '.sh', '.bash', '.yml', '.yaml', '.json', '.xml', '.md', '.txt',
                '.toml', '.ini', '.cfg', '.conf', '.log'
            }
            return path.suffix.lower() in text_extensions or not path.suffix
            
        except Exception:
            return False