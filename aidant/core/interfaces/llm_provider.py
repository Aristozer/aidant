"""LLM provider interface for abstracting different language model implementations."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, AsyncIterator
from dataclasses import dataclass
from enum import Enum


class MessageRole(Enum):
    """Roles for chat messages."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class ChatMessage:
    """Represents a single message in a chat conversation."""
    role: MessageRole
    content: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ModelInfo:
    """Information about an LLM model's capabilities."""
    name: str
    provider: str
    max_tokens: int
    supports_streaming: bool
    supports_function_calling: bool
    supports_vision: bool
    cost_per_token: Optional[float] = None
    context_window: Optional[int] = None


@dataclass
class GenerationConfig:
    """Configuration for LLM generation."""
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: Optional[List[str]] = None


@dataclass
class GenerationResult:
    """Result from LLM generation."""
    message: ChatMessage
    usage: Dict[str, int]  # token usage statistics
    finish_reason: str
    model_used: str


class ILLMProvider(ABC):
    """Interface for all LLM provider implementations."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this LLM provider."""
        pass
    
    @property
    @abstractmethod
    def available_models(self) -> List[ModelInfo]:
        """Return list of available models from this provider."""
        pass
    
    @abstractmethod
    def get_model_info(self, model_name: str) -> ModelInfo:
        """Get information about a specific model."""
        pass
    
    @abstractmethod
    def generate_response(
        self,
        messages: List[ChatMessage],
        model_name: str,
        config: Optional[GenerationConfig] = None
    ) -> GenerationResult:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    async def generate_response_stream(
        self,
        messages: List[ChatMessage],
        model_name: str,
        config: Optional[GenerationConfig] = None
    ) -> AsyncIterator[str]:
        """Generate a streaming response from the LLM."""
        pass
    
    @abstractmethod
    def validate_api_key(self) -> bool:
        """Validate that the API key is valid and working."""
        pass
    
    @abstractmethod
    def estimate_cost(
        self,
        messages: List[ChatMessage],
        model_name: str
    ) -> Optional[float]:
        """Estimate the cost of generating a response."""
        pass


class ModelNotFoundError(Exception):
    """Raised when a requested model is not available."""
    pass


class GenerationError(Exception):
    """Raised when LLM generation fails."""
    pass


class RateLimitError(Exception):
    """Raised when rate limit is exceeded."""
    pass


class AuthenticationError(Exception):
    """Raised when API authentication fails."""
    pass