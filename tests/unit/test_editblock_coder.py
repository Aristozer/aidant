"""Unit tests for EditBlockCoder."""

import pytest
import tempfile
from pathlib import Path

from aidant.infrastructure.coders.editblock.editblock_coder import EditBlockCoder
from aidant.core.interfaces.coder import ChangeType, ParseError


class TestEditBlockCoder:
    """Test cases for EditBlockCoder."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            
            # Create a test file
            test_file = workspace / "test.py"
            test_file.write_text("""def hello():
    print("Hello, World!")

def goodbye():
    print("Goodbye!")
""")
            yield workspace
    
    @pytest.fixture
    def coder(self, temp_workspace):
        """Create EditBlockCoder instance."""
        return EditBlockCoder(str(temp_workspace))
    
    def test_parse_search_replace_block(self, coder):
        """Test parsing SEARCH/REPLACE blocks."""
        response = """Here's the fix:

test.py
<<<<<<< SEARCH
def hello():
    print("Hello, World!")
=======
def hello(name="World"):
    print(f"Hello, {name}!")
>>>>>>> REPLACE
"""
        
        changes = coder.parse_response(response)
        
        assert len(changes) == 1
        change = changes[0]
        assert change.file_path == "test.py"
        assert change.change_type == ChangeType.MODIFY
        assert 'def hello():' in change.old_content
        assert 'def hello(name="World"):' in change.content
    
    def test_parse_fenced_code_block(self, coder):
        """Test parsing fenced code blocks with SEARCH/REPLACE."""
        response = """```python
test.py
<<<<<<< SEARCH
def goodbye():
    print("Goodbye!")
=======
def goodbye(name="World"):
    print(f"Goodbye, {name}!")
>>>>>>> REPLACE
```"""
        
        changes = coder.parse_response(response)
        
        assert len(changes) == 1
        change = changes[0]
        assert change.file_path == "test.py"
        assert change.change_type == ChangeType.MODIFY
    
    def test_parse_file_creation(self, coder):
        """Test parsing file creation blocks."""
        response = """```python
new_file.py
def new_function():
    return "Hello from new file"
```"""
        
        changes = coder.parse_response(response)
        
        assert len(changes) == 1
        change = changes[0]
        assert change.file_path == "new_file.py"
        assert change.change_type == ChangeType.CREATE
        assert "def new_function():" in change.content
    
    def test_parse_multiple_blocks(self, coder):
        """Test parsing multiple SEARCH/REPLACE blocks."""
        response = """Here are the changes:

test.py
<<<<<<< SEARCH
def hello():
    print("Hello, World!")
=======
def hello(name="World"):
    print(f"Hello, {name}!")
>>>>>>> REPLACE

test.py
<<<<<<< SEARCH
def goodbye():
    print("Goodbye!")
=======
def goodbye(name="World"):
    print(f"Goodbye, {name}!")
>>>>>>> REPLACE
"""
        
        changes = coder.parse_response(response)
        
        assert len(changes) == 2
        assert all(change.file_path == "test.py" for change in changes)
        assert all(change.change_type == ChangeType.MODIFY for change in changes)
    
    def test_parse_no_blocks_raises_error(self, coder):
        """Test that responses without valid blocks raise ParseError."""
        response = "Just a regular response without any code blocks."
        
        with pytest.raises(ParseError):
            coder.parse_response(response)
    
    def test_validate_changes_existing_file(self, coder, temp_workspace):
        """Test validation of changes to existing files."""
        # Create change for existing file
        from aidant.core.interfaces.coder import CodeChange
        
        change = CodeChange(
            file_path="test.py",
            change_type=ChangeType.MODIFY,
            content='def hello(name="World"):\n    print(f"Hello, {name}!")',
            old_content='def hello():\n    print("Hello, World!")'
        )
        
        result = coder.validate_changes([change])
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validate_changes_missing_file(self, coder):
        """Test validation fails for missing files."""
        from aidant.core.interfaces.coder import CodeChange
        
        change = CodeChange(
            file_path="missing.py",
            change_type=ChangeType.MODIFY,
            content="new content",
            old_content="old content"
        )
        
        result = coder.validate_changes([change])
        
        assert not result.is_valid
        assert len(result.errors) > 0
        assert "does not exist" in result.errors[0]
    
    def test_validate_changes_search_not_found(self, coder, temp_workspace):
        """Test validation fails when search content not found."""
        from aidant.core.interfaces.coder import CodeChange
        
        change = CodeChange(
            file_path="test.py",
            change_type=ChangeType.MODIFY,
            content="new content",
            old_content="this content does not exist in the file"
        )
        
        result = coder.validate_changes([change])
        
        assert not result.is_valid
        assert len(result.errors) > 0
        assert "Search content not found" in result.errors[0]
    
    def test_apply_modify_change(self, coder, temp_workspace):
        """Test applying modification changes."""
        from aidant.core.interfaces.coder import CodeChange
        
        change = CodeChange(
            file_path="test.py",
            change_type=ChangeType.MODIFY,
            content='def hello(name="World"):\n    print(f"Hello, {name}!")',
            old_content='def hello():\n    print("Hello, World!")'
        )
        
        success = coder.apply_changes([change])
        
        assert success
        
        # Verify file was modified
        test_file = temp_workspace / "test.py"
        content = test_file.read_text()
        assert 'def hello(name="World"):' in content
        assert 'print(f"Hello, {name}!")' in content
    
    def test_apply_create_change(self, coder, temp_workspace):
        """Test applying file creation changes."""
        from aidant.core.interfaces.coder import CodeChange
        
        change = CodeChange(
            file_path="new_file.py",
            change_type=ChangeType.CREATE,
            content='def new_function():\n    return "Hello from new file"'
        )
        
        success = coder.apply_changes([change])
        
        assert success
        
        # Verify file was created
        new_file = temp_workspace / "new_file.py"
        assert new_file.exists()
        content = new_file.read_text()
        assert "def new_function():" in content
    
    def test_can_handle_file_types(self, coder):
        """Test file type handling."""
        # Text files should be handled
        assert coder.can_handle_file("test.py")
        assert coder.can_handle_file("script.js")
        assert coder.can_handle_file("style.css")
        assert coder.can_handle_file("README.md")
        
        # Binary files should not be handled
        assert not coder.can_handle_file("image.jpg")
        assert not coder.can_handle_file("binary.exe")
        assert not coder.can_handle_file("archive.zip")
    
    def test_generate_prompt(self, coder):
        """Test prompt generation."""
        context = {"files": ["test.py"], "languages": ["python"]}
        
        prompt = coder.generate_prompt(context)
        
        assert "SEARCH" in prompt
        assert "REPLACE" in prompt
        assert "filename.py" in prompt
        assert "exact code to find" in prompt