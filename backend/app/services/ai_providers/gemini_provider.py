import time
from typing import Optional
import google.generativeai as genai
from app.core.config import settings
from app.services.ai_providers.base import BaseAIProvider, GenerationRequest, GenerationResponse


class GeminiProvider(BaseAIProvider):
    """Google Gemini API provider."""

    def __init__(self):
        if self.is_configured():
            genai.configure(api_key=settings.GOOGLE_GEMINI_API_KEY)

    @property
    def provider_name(self) -> str:
        return "google_gemini"

    @property
    def available_models(self) -> list[str]:
        return [
            "gemini-2.0-flash",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
        ]

    def is_configured(self) -> bool:
        return bool(settings.GOOGLE_GEMINI_API_KEY)

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        if not self.is_configured():
            return GenerationResponse(
                success=False,
                error="Gemini provider is not configured. Set GOOGLE_GEMINI_API_KEY.",
            )

        start_time = time.time()

        try:
            model_name = request.model or "gemini-2.0-flash"
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=request.system_prompt if request.system_prompt else None,
            )

            generation_config = genai.GenerationConfig(
                temperature=request.temperature,
                max_output_tokens=request.max_tokens,
                top_p=request.top_p,
            )

            response = await model.generate_content_async(
                request.user_prompt,
                generation_config=generation_config,
            )

            latency_ms = int((time.time() - start_time) * 1000)

            # Extract token counts if available
            input_tokens = 0
            output_tokens = 0
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                input_tokens = getattr(response.usage_metadata, "prompt_token_count", 0)
                output_tokens = getattr(response.usage_metadata, "candidates_token_count", 0)

            cost = self._calculate_cost(model_name, input_tokens, output_tokens)

            return GenerationResponse(
                content=response.text or "",
                model=model_name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                latency_ms=latency_ms,
                cost_usd=cost,
                success=True,
            )

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            return GenerationResponse(
                success=False,
                error=str(e),
                latency_ms=latency_ms,
                model=request.model or "gemini-2.0-flash",
            )

    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Approximate cost calculation based on model pricing."""
        pricing = {
            "gemini-2.0-flash": (0.0001, 0.0004),
            "gemini-1.5-pro": (0.00125, 0.005),
            "gemini-1.5-flash": (0.000075, 0.0003),
        }
        rates = pricing.get(model, (0.0001, 0.0004))
        return (input_tokens / 1000 * rates[0]) + (output_tokens / 1000 * rates[1])
