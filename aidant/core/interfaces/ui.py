"""User interface interface for abstracting different UI implementations."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum

from .coder import CodeChange


class MessageType(Enum):
    """Types of messages that can be displayed to the user."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


@dataclass
class UserChoice:
    """Represents a choice presented to the user."""
    key: str
    label: str
    description: Optional[str] = None


class IUserInterface(ABC):
    """Interface for all user interface implementations."""
    
    @abstractmethod
    def show_message(self, message: str, message_type: MessageType = MessageType.INFO) -> None:
        """Display a message to the user."""
        pass
    
    def show_info(self, message: str) -> None:
        """Display an info message."""
        self.show_message(message, MessageType.INFO)
    
    def show_warning(self, message: str) -> None:
        """Display a warning message."""
        self.show_message(message, MessageType.WARNING)
    
    def show_error(self, message: str) -> None:
        """Display an error message."""
        self.show_message(message, MessageType.ERROR)
    
    def show_success(self, message: str) -> None:
        """Display a success message."""
        self.show_message(message, MessageType.SUCCESS)
    
    @abstractmethod
    def get_user_input(self, prompt: str = "> ") -> str:
        """Get input from the user."""
        pass
    
    @abstractmethod
    def confirm(self, message: str, default: bool = False) -> bool:
        """Ask the user for confirmation."""
        pass
    
    @abstractmethod
    def choose_option(self, message: str, choices: List[UserChoice]) -> str:
        """Present multiple choices to the user."""
        pass
    
    @abstractmethod
    def show_changes(self, changes: List[CodeChange]) -> None:
        """Display proposed code changes to the user."""
        pass
    
    @abstractmethod
    def confirm_changes(self, changes: List[CodeChange]) -> bool:
        """Show changes and ask for confirmation."""
        pass
    
    @abstractmethod
    def show_diff(self, old_content: str, new_content: str, file_path: str) -> None:
        """Display a diff between old and new content."""
        pass
    
    @abstractmethod
    def start_spinner(self, message: str) -> None:
        """Start a loading spinner with a message."""
        pass
    
    @abstractmethod
    def stop_spinner(self) -> None:
        """Stop the current loading spinner."""
        pass
    
    @abstractmethod
    def show_welcome(self) -> None:
        """Show welcome message."""
        pass
    
    @abstractmethod
    def show_file_content(self, file_path: str, content: str, language: Optional[str] = None) -> None:
        """Display file content with syntax highlighting."""
        pass
    
    @abstractmethod
    def show_help(self) -> None:
        """Show help information."""
        pass