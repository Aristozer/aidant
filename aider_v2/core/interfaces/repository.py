"""Repository interface for abstracting version control and file system operations."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class FileStatus(Enum):
    """Git file status."""
    UNTRACKED = "untracked"
    MODIFIED = "modified"
    ADDED = "added"
    DELETED = "deleted"
    RENAMED = "renamed"
    COPIED = "copied"


@dataclass
class FileInfo:
    """Information about a file in the repository."""
    path: str
    status: FileStatus
    size: int
    last_modified: str
    content_type: str


@dataclass
class CommitInfo:
    """Information about a commit."""
    hash: str
    message: str
    author: str
    timestamp: str
    files_changed: List[str]


class IRepository(ABC):
    """Interface for repository operations."""
    
    @property
    @abstractmethod
    def root_path(self) -> str:
        """Return the root path of the repository."""
        pass
    
    @property
    @abstractmethod
    def is_git_repo(self) -> bool:
        """Return True if this is a Git repository."""
        pass
    
    @abstractmethod
    def get_files(self, patterns: Optional[List[str]] = None) -> List[FileInfo]:
        """Get files in the repository matching optional patterns."""
        pass
    
    @abstractmethod
    def get_file_content(self, file_path: str) -> str:
        """Get the content of a specific file."""
        pass
    
    @abstractmethod
    def get_context(self, file_paths: List[str]) -> Dict[str, Any]:
        """Get repository context for the given files."""
        pass
    
    @abstractmethod
    def get_status(self) -> List[FileInfo]:
        """Get the status of all files in the repository."""
        pass
    
    @abstractmethod
    def commit_changes(self, changes: List[Any], message: str) -> str:
        """Commit changes to the repository."""
        pass
    
    @abstractmethod
    def get_commit_history(self, limit: int = 10) -> List[CommitInfo]:
        """Get recent commit history."""
        pass
    
    @abstractmethod
    def get_diff(self, file_path: str, commit_hash: Optional[str] = None) -> str:
        """Get diff for a file."""
        pass
    
    @abstractmethod
    def is_clean(self) -> bool:
        """Check if the repository has no uncommitted changes."""
        pass


class CommitError(Exception):
    """Raised when a commit operation fails."""
    pass