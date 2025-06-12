"""Core coder interface defining the contract for all code editing implementations."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class ChangeType(Enum):
    """Types of code changes that can be applied."""
    CREATE = "create"
    MODIFY = "modify"
    DELETE = "delete"
    RENAME = "rename"


@dataclass
class CodeChange:
    """Represents a single code change to be applied."""
    file_path: str
    change_type: ChangeType
    content: Optional[str] = None
    old_content: Optional[str] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ValidationResult:
    """Result of validating proposed changes."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]


class ICoder(ABC):
    """Interface for all code editing implementations."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this coder implementation."""
        pass
    
    @property
    @abstractmethod
    def supported_languages(self) -> List[str]:
        """Return list of programming languages this coder supports."""
        pass
    
    @abstractmethod
    def parse_response(self, llm_response: str) -> List[CodeChange]:
        """Parse LLM response and extract code changes."""
        pass
    
    @abstractmethod
    def validate_changes(self, changes: List[CodeChange]) -> ValidationResult:
        """Validate proposed changes before applying them."""
        pass
    
    @abstractmethod
    def apply_changes(self, changes: List[CodeChange]) -> bool:
        """Apply validated changes to the codebase."""
        pass
    
    @abstractmethod
    def generate_prompt(self, context: Dict[str, Any]) -> str:
        """Generate the prompt template for this coder format."""
        pass
    
    @abstractmethod
    def can_handle_file(self, file_path: str) -> bool:
        """Check if this coder can handle the given file type."""
        pass


class ParseError(Exception):
    """Raised when a coder cannot parse an LLM response."""
    pass


class ApplyError(Exception):
    """Raised when a coder cannot apply changes."""
    pass