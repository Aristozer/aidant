"""OpenAI LLM provider implementation."""

from typing import List, Optional, AsyncIterator
import openai
import asyncio
from ...core.interfaces.llm_provider import (
    ILLMProvider, ChatMessage, ModelInfo, GenerationConfig, GenerationResult,
    MessageRole, ModelNotFoundError, GenerationError, AuthenticationError
)


class OpenAIProvider(ILLMProvider):
    """OpenAI LLM provider implementation."""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None) -> None:
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
        self._models_cache: Optional[List[ModelInfo]] = None
    
    @property
    def name(self) -> str:
        return "openai"
    
    @property
    def available_models(self) -> List[ModelInfo]:
        if self._models_cache is None:
            self._models_cache = self._fetch_models()
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
        """Generate response using OpenAI API."""
        config = config or GenerationConfig()
        
        # Convert messages to OpenAI format
        openai_messages = [
            {"role": msg.role.value, "content": msg.content}
            for msg in messages
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=model_name,
                messages=openai_messages,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                top_p=config.top_p,
                frequency_penalty=config.frequency_penalty,
                presence_penalty=config.presence_penalty,
                stop=config.stop_sequences
            )
            
            return GenerationResult(
                message=ChatMessage(
                    role=MessageRole.ASSISTANT,
                    content=response.choices[0].message.content or ""
                ),
                usage={
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                },
                finish_reason=response.choices[0].finish_reason or "unknown",
                model_used=response.model
            )
        except openai.AuthenticationError as e:
            raise AuthenticationError(f"OpenAI authentication failed: {str(e)}")
        except Exception as e:
            raise GenerationError(f"OpenAI API error: {str(e)}")
    
    async def generate_response_stream(
        self,
        messages: List[ChatMessage],
        model_name: str,
        config: Optional[GenerationConfig] = None
    ) -> AsyncIterator[str]:
        """Generate a streaming response from OpenAI."""
        config = config or GenerationConfig()
        
        # Convert messages to OpenAI format
        openai_messages = [
            {"role": msg.role.value, "content": msg.content}
            for msg in messages
        ]
        
        try:
            stream = self.client.chat.completions.create(
                model=model_name,
                messages=openai_messages,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                top_p=config.top_p,
                frequency_penalty=config.frequency_penalty,
                presence_penalty=config.presence_penalty,
                stop=config.stop_sequences,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            raise GenerationError(f"OpenAI streaming error: {str(e)}")
    
    def validate_api_key(self) -> bool:
        """Validate that the API key is valid and working."""
        try:
            # Try to list models as a simple validation
            self.client.models.list()
            return True
        except Exception:
            return False
    
    def estimate_cost(
        self,
        messages: List[ChatMessage],
        model_name: str
    ) -> Optional[float]:
        """Estimate the cost of generating a response."""
        # Simplified cost estimation - in practice, you'd use actual pricing
        total_chars = sum(len(msg.content) for msg in messages)
        estimated_tokens = total_chars // 4  # Rough estimate: 4 chars per token
        
        # Basic pricing (these would be real prices in production)
        pricing = {
            "gpt-4": 0.03 / 1000,  # $0.03 per 1K tokens
            "gpt-4o": 0.005 / 1000,  # $0.005 per 1K tokens
            "gpt-3.5-turbo": 0.001 / 1000,  # $0.001 per 1K tokens
        }
        
        base_model = model_name.split("-")[0] + "-" + model_name.split("-")[1] if "-" in model_name else model_name
        rate = pricing.get(base_model, 0.01 / 1000)  # Default rate
        
        return estimated_tokens * rate
    
    def _fetch_models(self) -> List[ModelInfo]:
        """Fetch available models from OpenAI API."""
        models = []
        try:
            response = self.client.models.list()
            for model in response.data:
                if model.id.startswith(('gpt-', 'o1-', 'o3-')):
                    models.append(ModelInfo(
                        name=model.id,
                        provider="openai",
                        max_tokens=self._get_max_tokens(model.id),
                        supports_streaming=True,
                        supports_function_calling=True,
                        supports_vision='vision' in model.id or 'gpt-4' in model.id,
                        context_window=self._get_context_window(model.id)
                    ))
        except Exception:
            # Return default models if API call fails
            models = self._get_default_models()
        
        return models
    
    def _get_max_tokens(self, model_name: str) -> int:
        """Get max tokens for a model."""
        if "gpt-4" in model_name:
            return 4096
        elif "gpt-3.5" in model_name:
            return 4096
        elif "o1" in model_name or "o3" in model_name:
            return 32768
        return 4096
    
    def _get_context_window(self, model_name: str) -> int:
        """Get context window size for a model."""
        if "gpt-4" in model_name:
            return 128000
        elif "gpt-3.5" in model_name:
            return 16385
        elif "o1" in model_name or "o3" in model_name:
            return 200000
        return 4096
    
    def _get_default_models(self) -> List[ModelInfo]:
        """Get default models when API is not available."""
        return [
            ModelInfo(
                name="gpt-4o",
                provider="openai",
                max_tokens=4096,
                supports_streaming=True,
                supports_function_calling=True,
                supports_vision=True,
                context_window=128000
            ),
            ModelInfo(
                name="gpt-4",
                provider="openai",
                max_tokens=4096,
                supports_streaming=True,
                supports_function_calling=True,
                supports_vision=False,
                context_window=8192
            ),
            ModelInfo(
                name="gpt-3.5-turbo",
                provider="openai",
                max_tokens=4096,
                supports_streaming=True,
                supports_function_calling=True,
                supports_vision=False,
                context_window=16385
            )
        ]