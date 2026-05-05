"""Pydantic schemas for content generation API."""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum


class AIProviderEnum(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE_GEMINI = "google_gemini"
    CUSTOM = "custom"


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================

class GenerationRunRequest(BaseModel):
    """Request to run content generation."""
    content_item_id: UUID
    provider: AIProviderEnum
    model: str = Field(
        ...,
        description="Model name, e.g. gpt-4o, claude-sonnet-4-20250514, gemini-2.0-flash"
    )
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, ge=256, le=16384)
    fallback_provider: Optional[AIProviderEnum] = None
    custom_instructions: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Additional instructions to append to the generation prompt"
    )
    custom_endpoint: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Custom provider endpoint (OpenAI-compatible base URL)"
    )
    custom_api_key: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Custom provider API key"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "content_item_id": "550e8400-e29b-41d4-a716-446655440000",
                "provider": "openai",
                "model": "gpt-4o",
                "temperature": 0.7,
                "max_tokens": 4096,
                "fallback_provider": "anthropic",
                "custom_instructions": "Fokus pada hook yang sangat engaging untuk audience Gen Z"
            }
        }


class RegenerationRequest(BaseModel):
    """Request to regenerate content with revision notes."""
    content_item_id: UUID
    provider: AIProviderEnum
    model: str
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, ge=256, le=16384)
    revision_notes: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Notes about what to improve in the regeneration"
    )
    fallback_provider: Optional[AIProviderEnum] = None
    custom_endpoint: Optional[str] = Field(default=None, max_length=500)
    custom_api_key: Optional[str] = Field(default=None, max_length=500)

    class Config:
        json_schema_extra = {
            "example": {
                "content_item_id": "550e8400-e29b-41d4-a716-446655440000",
                "provider": "anthropic",
                "model": "claude-sonnet-4-20250514",
                "revision_notes": "Hook kurang kuat, buat lebih provokatif. CTA terlalu generic.",
                "temperature": 0.8,
            }
        }


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================

class GenerationMetrics(BaseModel):
    """Metrics from a generation run."""
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
    cost_usd: float


class GenerationRunResponse(BaseModel):
    """Response from a successful generation run."""
    success: bool
    generation_run_id: str
    content_version_id: Optional[str] = None
    version_number: Optional[int] = None
    content_data: Optional[dict] = None
    parse_warning: Optional[str] = None
    metrics: Optional[GenerationMetrics] = None
    error: Optional[str] = None
    raw_content: Optional[str] = None  # Only on parse failure for debugging


class GenerationRunDetail(BaseModel):
    """Detailed view of a generation run."""
    id: UUID
    content_item_id: UUID
    provider: str
    model: str
    status: str
    system_prompt: Optional[str] = None
    user_prompt: Optional[str] = None
    parameters: Optional[dict] = None
    output_data: Optional[dict] = None
    error_message: Optional[str] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    latency_ms: Optional[int] = None
    cost_usd: Optional[float] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class GenerationRunListItem(BaseModel):
    """Summary view of a generation run for list endpoints."""
    id: UUID
    content_item_id: UUID
    provider: str
    model: str
    status: str
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    latency_ms: Optional[int] = None
    cost_usd: Optional[float] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ProviderInfo(BaseModel):
    """Information about an AI provider."""
    provider: str
    configured: bool
    models: list[str]


class ProvidersListResponse(BaseModel):
    """Response listing all available providers."""
    providers: list[ProviderInfo]
    available_count: int
