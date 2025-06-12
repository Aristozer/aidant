"""Domain models for the core business logic."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

from ..interfaces.llm_provider import ChatMessage


class SessionStatus(Enum):
    """Status of a chat session."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class ChatSession:
    """Represents an active chat session."""
    id: str
    created_at: datetime
    status: SessionStatus = SessionStatus.ACTIVE
    messages: List[ChatMessage] = field(default_factory=list)
    active_files: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, message: ChatMessage) -> None:
        """Add a message to the session."""
        self.messages.append(message)
    
    def get_message_count(self) -> int:
        """Get the total number of messages in the session."""
        return len(self.messages)
    
    def get_context_size(self) -> int:
        """Get the size of the context in characters."""
        return len(str(self.context))


@dataclass
class Workspace:
    """Represents a workspace/project."""
    root_path: str
    name: str
    files: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    is_git_repo: bool = False
    git_branch: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_file(self, file_path: str) -> None:
        """Add a file to the workspace."""
        if file_path not in self.files:
            self.files.append(file_path)
    
    def remove_file(self, file_path: str) -> None:
        """Remove a file from the workspace."""
        if file_path in self.files:
            self.files.remove(file_path)


@dataclass
class CodeContext:
    """Represents code context for a conversation."""
    files: Dict[str, str]  # file_path -> content
    functions: List[Dict[str, Any]] = field(default_factory=list)
    classes: List[Dict[str, Any]] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    
    def add_file_content(self, file_path: str, content: str) -> None:
        """Add file content to the context."""
        self.files[file_path] = content
    
    def get_total_lines(self) -> int:
        """Get total lines of code in context."""
        return sum(len(content.splitlines()) for content in self.files.values())


@dataclass
class ChangeSet:
    """Represents a set of related changes."""
    id: str
    description: str
    changes: List[Any]  # CodeChange objects
    created_at: datetime
    applied: bool = False
    commit_hash: Optional[str] = None
    
    def mark_applied(self, commit_hash: str) -> None:
        """Mark the changeset as applied."""
        self.applied = True
        self.commit_hash = commit_hash