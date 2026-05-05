import time
from typing import Optional
from anthropic import AsyncAnthropic
from app.core.config import settings
from app.services.ai_providers.base import BaseAIProvider, GenerationRequest, GenerationResponse


class AnthropicProvider(BaseAIProvider):
    """Anthropic API provider (Claude models)."""

    def __init__(self):
        self.client: Optional[AsyncAnthropic] = None
        if self.is_configured():
            self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    @property
    def provider_name(self) -> str:
        return "anthropic"

    @property
    def available_models(self) -> list[str]:
        return [
            "claude-sonnet-4-20250514",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
        ]

    def is_configured(self) -> bool:
        return bool(settings.ANTHROPIC_API_KEY)

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        if not self.client:
            return GenerationResponse(
                success=False,
                error="Anthropic provider is not configured. Set ANTHROPIC_API_KEY.",
            )

        start_time = time.time()

        try:
            kwargs = {
                "model": request.model or "claude-sonnet-4-20250514",
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "messages": [{"role": "user", "content": request.user_prompt}],
            }

            if request.system_prompt:
                kwargs["system"] = request.system_prompt

            response = await self.client.messages.create(**kwargs)

            latency_ms = int((time.time() - start_time) * 1000)

            content = ""
            for block in response.content:
                if block.type == "text":
                    content += block.text

            cost = self._calculate_cost(
                request.model or "claude-sonnet-4-20250514",
                response.usage.input_tokens,
                response.usage.output_tokens,
            )

            return GenerationResponse(
                content=content,
                model=response.model,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                latency_ms=latency_ms,
                cost_usd=cost,
                raw_response=response.model_dump(),
                success=True,
            )

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            return GenerationResponse(
                success=False,
                error=str(e),
                latency_ms=latency_ms,
                model=request.model or "claude-sonnet-4-20250514",
            )

    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Approximate cost calculation based on model pricing."""
        pricing = {
            "claude-sonnet-4-20250514": (0.003, 0.015),
            "claude-3-5-haiku-20241022": (0.001, 0.005),
            "claude-3-opus-20240229": (0.015, 0.075),
        }
        rates = pricing.get(model, (0.003, 0.015))
        return (input_tokens / 1000 * rates[0]) + (output_tokens / 1000 * rates[1])
