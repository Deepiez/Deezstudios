import time
from openai import AsyncOpenAI

from app.services.ai_providers.base import BaseAIProvider, GenerationRequest, GenerationResponse


class CustomProvider(BaseAIProvider):
    """User-defined OpenAI-compatible provider via custom endpoint/API key/model."""

    @property
    def provider_name(self) -> str:
        return "custom"

    @property
    def available_models(self) -> list[str]:
        return []

    def is_configured(self) -> bool:
        return True

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        if not request.custom_endpoint:
            return GenerationResponse(success=False, error="Custom endpoint is required.")
        if not request.custom_api_key:
            return GenerationResponse(success=False, error="Custom API key is required.")
        if not request.model:
            return GenerationResponse(success=False, error="Custom model is required.")

        start_time = time.time()

        try:
            base_url = request.custom_endpoint.rstrip("/")
            client = AsyncOpenAI(api_key=request.custom_api_key, base_url=base_url)

            messages = []
            if request.system_prompt:
                messages.append({"role": "system", "content": request.system_prompt})
            messages.append({"role": "user", "content": request.user_prompt})

            response = await client.chat.completions.create(
                model=request.model,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                top_p=request.top_p,
                frequency_penalty=request.frequency_penalty,
                presence_penalty=request.presence_penalty,
            )

            latency_ms = int((time.time() - start_time) * 1000)
            usage = response.usage

            return GenerationResponse(
                content=response.choices[0].message.content or "",
                model=response.model,
                input_tokens=getattr(usage, "prompt_tokens", 0) if usage else 0,
                output_tokens=getattr(usage, "completion_tokens", 0) if usage else 0,
                latency_ms=latency_ms,
                cost_usd=0.0,
                raw_response=response.model_dump(),
                success=True,
            )
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            return GenerationResponse(
                success=False,
                error=str(e),
                latency_ms=latency_ms,
                model=request.model,
            )
