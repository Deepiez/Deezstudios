import time
from typing import Optional
from openai import AsyncOpenAI
from app.core.config import settings
from app.services.ai_providers.base import BaseAIProvider, GenerationRequest, GenerationResponse


class OpenAIProvider(BaseAIProvider):
    """OpenAI API provider (GPT-4, GPT-4o, etc.)."""

    def __init__(self):
        self.client: Optional[AsyncOpenAI] = None
        if self.is_configured():
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def available_models(self) -> list[str]:
        return [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
        ]

    def is_configured(self) -> bool:
        return bool(settings.OPENAI_API_KEY)

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        if not self.client:
            return GenerationResponse(
                success=False,
                error="OpenAI provider is not configured. Set OPENAI_API_KEY.",
            )

        start_time = time.time()

        try:
            messages = []
            if request.system_prompt:
                messages.append({"role": "system", "content": request.system_prompt})
            messages.append({"role": "user", "content": request.user_prompt})

            response = await self.client.chat.completions.create(
                model=request.model or "gpt-4o",
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                top_p=request.top_p,
                frequency_penalty=request.frequency_penalty,
                presence_penalty=request.presence_penalty,
            )

            latency_ms = int((time.time() - start_time) * 1000)

            usage = response.usage
            # Approximate cost calculation (prices may change)
            cost = self._calculate_cost(
                request.model or "gpt-4o",
                usage.prompt_tokens,
                usage.completion_tokens,
            )

            return GenerationResponse(
                content=response.choices[0].message.content or "",
                model=response.model,
                input_tokens=usage.prompt_tokens,
                output_tokens=usage.completion_tokens,
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
                model=request.model or "gpt-4o",
            )

    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Approximate cost calculation based on model pricing."""
        pricing = {
            "gpt-4o": (0.005, 0.015),  # per 1K tokens (input, output)
            "gpt-4o-mini": (0.00015, 0.0006),
            "gpt-4-turbo": (0.01, 0.03),
            "gpt-4": (0.03, 0.06),
            "gpt-3.5-turbo": (0.0005, 0.0015),
        }
        rates = pricing.get(model, (0.005, 0.015))
        return (input_tokens / 1000 * rates[0]) + (output_tokens / 1000 * rates[1])
