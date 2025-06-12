"""Anthropic LLM provider implementation."""

from typing import List, Optional, AsyncIterator
import anthropic
from ...core.interfaces.llm_provider import (
    ILLMProvider, ChatMessage, ModelInfo, GenerationConfig, GenerationResult,
    MessageRole, ModelNotFoundError, GenerationError, AuthenticationError
)


class AnthropicProvider(ILLMProvider):
    """Anthropic LLM provider implementation."""
    
    def __init__(self, api_key: str) -> None:
        self.client = anthropic.Anthropic(api_key=api_key)
        self._models_cache: Optional[List[ModelInfo]] = None
    
    @property
    def name(self) -> str:
        return "anthropic"
    
    @property
    def available_models(self) -> List[ModelInfo]:
        if self._models_cache is None:
            self._models_cache = self._get_default_models()
        return self._models_cache
    
    def get_model_info(self, model_name: str) -> ModelInfo:
        """Get information about a specific model."""
        for model in self.available_models:
            if model.name == model_name:
                return model
        raise ModelNotFoundError(f"Model {model_name} not found")
    
    def generate_response(
        self,
        messages: List[ChatMessage],
        model_name: str,
        config: Optional[GenerationConfig] = None
    ) -> GenerationResult:
        """Generate response using Anthropic API."""
        config = config or GenerationConfig()
        
        # Separate system message from conversation
        system_message = ""
        conversation_messages = []
        
        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                system_message = msg.content
            else:
                conversation_messages.append({
                    "role": msg.role.value,
                    "content": msg.content
                })
        
        try:
            response = self.client.messages.create(
                model=model_name,
                max_tokens=config.max_tokens or 4096,
                temperature=config.temperature,
                top_p=config.top_p,
                system=system_message,
                messages=conversation_messages,
                stop_sequences=config.stop_sequences
            )
            
            return GenerationResult(
                message=ChatMessage(
                    role=MessageRole.ASSISTANT,
                    content=response.content[0].text if response.content else ""
                ),
                usage={
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                },
                finish_reason=response.stop_reason or "unknown",
                model_used=response.model
            )
        except anthropic.AuthenticationError as e:
            raise AuthenticationError(f"Anthropic authentication failed: {str(e)}")
        except Exception as e:
            raise GenerationError(f"Anthropic API error: {str(e)}")
    
    async def generate_response_stream(
        self,
        messages: List[ChatMessage],
        model_name: str,
        config: Optional[GenerationConfig] = None
    ) -> AsyncIterator[str]:
        """Generate a streaming response from Anthropic."""
        config = config or GenerationConfig()
        
        # Separate system message from conversation
        system_message = ""
        conversation_messages = []
        
        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                system_message = msg.content
            else:
                conversation_messages.append({
                    "role": msg.role.value,
                    "content": msg.content
                })
        
        try:
            stream = self.client.messages.create(
                model=model_name,
                max_tokens=config.max_tokens or 4096,
                temperature=config.temperature,
                top_p=config.top_p,
                system=system_message,
                messages=conversation_messages,
                stop_sequences=config.stop_sequences,
                stream=True
            )
            
            for chunk in stream:
                if chunk.type == "content_block_delta" and hasattr(chunk.delta, 'text'):
                    yield chunk.delta.text
                    
        except Exception as e:
            raise GenerationError(f"Anthropic streaming error: {str(e)}")
    
    def validate_api_key(self) -> bool:
        """Validate that the API key is valid and working."""
        try:
            # Try a simple API call to validate
            self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1,
                messages=[{"role": "user", "content": "Hi"}]
            )
            return True
        except Exception:
            return False
    
    def estimate_cost(
        self,
        messages: List[ChatMessage],
        model_name: str
    ) -> Optional[float]:
        """Estimate the cost of generating a response."""
        total_chars = sum(len(msg.content) for msg in messages)
        estimated_tokens = total_chars // 4  # Rough estimate
        
        # Anthropic pricing (simplified)
        pricing = {
            "claude-3-opus": 0.015 / 1000,  # $0.015 per 1K tokens
            "claude-3-sonnet": 0.003 / 1000,  # $0.003 per 1K tokens
            "claude-3-haiku": 0.00025 / 1000,  # $0.00025 per 1K tokens
        }
        
        base_model = model_name.split("-")[0] + "-" + model_name.split("-")[1] + "-" + model_name.split("-")[2]
        rate = pricing.get(base_model, 0.003 / 1000)  # Default to sonnet rate
        
        return estimated_tokens * rate
    
    def _get_default_models(self) -> List[ModelInfo]:
        """Get default Anthropic models."""
        return [
            ModelInfo(
                name="claude-3-5-sonnet-20241022",
                provider="anthropic",
                max_tokens=8192,
                supports_streaming=True,
                supports_function_calling=True,
                supports_vision=True,
                context_window=200000
            ),
            ModelInfo(
                name="claude-3-opus-20240229",
                provider="anthropic",
                max_tokens=4096,
                supports_streaming=True,
                supports_function_calling=True,
                supports_vision=True,
                context_window=200000
            ),
            ModelInfo(
                name="claude-3-haiku-20240307",
                provider="anthropic",
                max_tokens=4096,
                supports_streaming=True,
                supports_function_calling=True,
                supports_vision=True,
                context_window=200000
            )
        ]