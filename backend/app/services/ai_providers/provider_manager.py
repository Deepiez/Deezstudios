from typing import Optional
from app.models.generation import AIProvider
from app.services.ai_providers.base import BaseAIProvider, GenerationRequest, GenerationResponse
from app.services.ai_providers.openai_provider import OpenAIProvider
from app.services.ai_providers.anthropic_provider import AnthropicProvider
from app.services.ai_providers.gemini_provider import GeminiProvider
from app.services.ai_providers.custom_provider import CustomProvider


class ProviderManager:
    """
    Manages multiple AI providers and routes generation requests.
    Supports provider selection, fallback, and configuration checking.
    """

    def __init__(self):
        self._providers: dict[str, BaseAIProvider] = {}
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize all available providers."""
        providers = [
            OpenAIProvider(),
            AnthropicProvider(),
            GeminiProvider(),
            CustomProvider(),
        ]
        for provider in providers:
            self._providers[provider.provider_name] = provider

    def get_provider(self, provider_name: str) -> Optional[BaseAIProvider]:
        """Get a specific provider by name."""
        return self._providers.get(provider_name)

    def get_configured_providers(self) -> list[dict]:
        """Get list of all configured (ready-to-use) providers with their models."""
        result = []
        for name, provider in self._providers.items():
            result.append({
                "provider": name,
                "configured": provider.is_configured(),
                "models": provider.available_models,
            })
        return result

    def get_available_providers(self) -> list[str]:
        """Get names of providers that are configured and ready."""
        return [
            name for name, provider in self._providers.items()
            if provider.is_configured() or name == "custom"
        ]

    async def generate(
        self,
        provider_name: str,
        request: GenerationRequest,
        fallback_provider: Optional[str] = None,
    ) -> GenerationResponse:
        """
        Generate content using specified provider.
        Optionally falls back to another provider on failure.
        """
        provider = self.get_provider(provider_name)
        if not provider:
            return GenerationResponse(
                success=False,
                error=f"Provider '{provider_name}' not found.",
            )

        if not provider.is_configured() and provider_name != "custom":
            # Try fallback if primary is not configured
            if fallback_provider:
                fallback = self.get_provider(fallback_provider)
                if fallback and fallback.is_configured():
                    return await fallback.generate(request)
            return GenerationResponse(
                success=False,
                error=f"Provider '{provider_name}' is not configured.",
            )

        response = await provider.generate(request)

        # If failed and fallback is available, try fallback
        if not response.success and fallback_provider:
            fallback = self.get_provider(fallback_provider)
            if fallback and fallback.is_configured():
                return await fallback.generate(request)

        return response


# Singleton instance
provider_manager = ProviderManager()
