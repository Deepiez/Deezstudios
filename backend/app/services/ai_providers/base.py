from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class GenerationRequest:
    """Request object for AI generation."""
    system_prompt: Optional[str] = None
    user_prompt: str = ""
    model: str = ""
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0


@dataclass
class GenerationResponse:
    """Response object from AI generation."""
    content: str = ""
    model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int = 0
    cost_usd: float = 0.0
    raw_response: Optional[dict] = None
    error: Optional[str] = None
    success: bool = True


class BaseAIProvider(ABC):
    """Abstract base class for AI providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name."""
        pass

    @property
    @abstractmethod
    def available_models(self) -> list[str]:
        """Return list of available models."""
        pass

    @abstractmethod
    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        """Generate content using the AI provider."""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if the provider is properly configured with API keys."""
        pass
