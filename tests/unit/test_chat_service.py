"""Unit tests for ChatService."""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from aidant.core.services.chat_service import ChatService
from aidant.core.interfaces.llm_provider import (
    ILLMProvider, GenerationResult, ChatMessage, MessageRole
)
from aidant.core.interfaces.coder import ICoder, CodeChange, ChangeType, ValidationResult
from aidant.core.interfaces.repository import IRepository
from aidant.core.interfaces.ui import IUserInterface
from aidant.core.domain.models import SessionStatus


class TestChatService:
    """Test cases for ChatService."""
    
    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for ChatService."""
        return {
            'llm_provider': Mock(spec=ILLMProvider),
            'coder': Mock(spec=ICoder),
            'repository': Mock(spec=IRepository),
            'ui': Mock(spec=IUserInterface)
        }
    
    @pytest.fixture
    def chat_service(self, mock_dependencies):
        """Create ChatService instance with mocked dependencies."""
        return ChatService(**mock_dependencies)
    
    def test_start_session_creates_session(self, chat_service, mock_dependencies):
        """Test that start_session creates a new session."""
        # Arrange
        mock_dependencies['repository'].get_context.return_value = {
            'root_path': '/test',
            'files': [],
            'languages': []
        }
        
        # Act
        session = chat_service.start_session(['test.py'])
        
        # Assert
        assert session is not None
        assert session.status == SessionStatus.ACTIVE
        assert len(session.messages) == 1  # System message
        assert session.messages[0].role == MessageRole.SYSTEM
        assert 'test.py' in session.active_files
        assert chat_service.current_session == session
    
    def test_process_user_message_calls_llm(self, chat_service, mock_dependencies):
        """Test that process_user_message calls LLM provider."""
        # Arrange
        chat_service.start_session([])
        mock_response = GenerationResult(
            message=ChatMessage(role=MessageRole.ASSISTANT, content="Hello!"),
            usage={"total_tokens": 10},
            finish_reason="stop",
            model_used="gpt-4"
        )
        mock_dependencies['llm_provider'].generate_response.return_value = mock_response
        
        # Act
        response = chat_service.process_user_message("Hello", "gpt-4")
        
        # Assert
        assert response == "Hello!"
        mock_dependencies['llm_provider'].generate_response.assert_called_once()
        assert len(chat_service.current_session.messages) == 3  # System + User + Assistant
    
    def test_process_user_message_handles_code_changes(self, chat_service, mock_dependencies):
        """Test that code changes in LLM response are handled."""
        # Arrange
        chat_service.start_session([])
        
        # Mock LLM response with code changes
        llm_response = """Here's the fix:
        
        test.py
        <<<<<<< SEARCH
        def old_function():
            pass
        =======
        def new_function():
            return "fixed"
        >>>>>>> REPLACE
        """
        
        mock_response = GenerationResult(
            message=ChatMessage(role=MessageRole.ASSISTANT, content=llm_response),
            usage={"total_tokens": 50},
            finish_reason="stop",
            model_used="gpt-4"
        )
        mock_dependencies['llm_provider'].generate_response.return_value = mock_response
        
        # Mock coder responses
        mock_change = CodeChange(
            file_path="test.py",
            change_type=ChangeType.MODIFY,
            content="def new_function():\n    return \"fixed\"",
            old_content="def old_function():\n    pass"
        )
        mock_dependencies['coder'].parse_response.return_value = [mock_change]
        mock_dependencies['coder'].validate_changes.return_value = ValidationResult(
            is_valid=True, errors=[], warnings=[]
        )
        mock_dependencies['coder'].apply_changes.return_value = True
        mock_dependencies['ui'].confirm_changes.return_value = True
        mock_dependencies['repository'].commit_changes.return_value = "abc123"
        
        # Act
        response = chat_service.process_user_message("Fix the function", "gpt-4")
        
        # Assert
        mock_dependencies['coder'].parse_response.assert_called_once()
        mock_dependencies['coder'].validate_changes.assert_called_once()
        mock_dependencies['ui'].confirm_changes.assert_called_once()
        mock_dependencies['coder'].apply_changes.assert_called_once()
        mock_dependencies['repository'].commit_changes.assert_called_once()
    
    def test_add_files_to_context(self, chat_service, mock_dependencies):
        """Test adding files to session context."""
        # Arrange
        session = chat_service.start_session([])
        new_context = {
            'file_contents': {'new_file.py': 'print("hello")'},
            'languages': ['python']
        }
        mock_dependencies['repository'].get_context.return_value = new_context
        
        # Act
        chat_service.add_files_to_context(['new_file.py'])
        
        # Assert
        assert 'new_file.py' in session.active_files
        assert 'file_contents' in session.context
    
    def test_get_session_summary(self, chat_service, mock_dependencies):
        """Test getting session summary."""
        # Arrange
        session = chat_service.start_session(['test.py'])
        session.add_message(ChatMessage(role=MessageRole.USER, content="Test"))
        
        # Act
        summary = chat_service.get_session_summary()
        
        # Assert
        assert summary['session_id'] == session.id
        assert summary['status'] == SessionStatus.ACTIVE.value
        assert summary['message_count'] == 2  # System + User
        assert 'test.py' in summary['active_files']
    
    def test_no_active_session_raises_error(self, chat_service):
        """Test that operations without active session raise error."""
        # Act & Assert
        with pytest.raises(ValueError, match="No active chat session"):
            chat_service.process_user_message("Hello", "gpt-4")
        
        with pytest.raises(ValueError, match="No active chat session"):
            chat_service.add_files_to_context(['test.py'])
    
    def test_contains_code_changes_detection(self, chat_service):
        """Test detection of code changes in responses."""
        # Test cases
        test_cases = [
            ("<<<<<<< SEARCH\nold\n=======\nnew\n>>>>>>> REPLACE", True),
            ("```diff\n-old\n+new\n```", True),
            ("Just a regular response", False),
            ("Some code: print('hello')", False)
        ]
        
        for response, expected in test_cases:
            result = chat_service._contains_code_changes(response)
            assert result == expected, f"Failed for: {response}"