"""
Default AI provider and model configuration per content type.
Users can override these defaults when running generation.
"""

from typing import Optional

# Default provider + model per content type
# These are the recommended defaults for best quality/cost balance
CONTENT_TYPE_DEFAULTS: dict[str, dict[str, str]] = {
    "youtube_shorts": {
        "provider": "openai",
        "model": "gpt-4o",
        "reason": "Best for short-form creative content with structured output",
    },
    "youtube_longform": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-20250514",
        "reason": "Best for long-form structured content (outlines, full scripts)",
    },
    "tiktok_short": {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "reason": "Fast and cost-effective for short creative content",
    },
    "blog_article": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-20250514",
        "reason": "Best for long-form writing quality and structure",
    },
    "x_post": {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "reason": "Fast, concise output ideal for short posts",
    },
}

# Fallback chain: if primary fails, try these in order
FALLBACK_CHAIN: dict[str, str] = {
    "openai": "anthropic",
    "anthropic": "openai",
    "google_gemini": "openai",
}


def get_default_provider(content_type: str) -> dict[str, str]:
    """Get default provider and model for a content type."""
    return CONTENT_TYPE_DEFAULTS.get(content_type, {
        "provider": "openai",
        "model": "gpt-4o",
        "reason": "General default",
    })


def get_fallback_provider(provider: str) -> Optional[str]:
    """Get fallback provider for a given provider."""
    return FALLBACK_CHAIN.get(provider)


def get_all_defaults() -> dict:
    """Get all default configurations (for API response)."""
    return {
        "content_type_defaults": CONTENT_TYPE_DEFAULTS,
        "fallback_chain": FALLBACK_CHAIN,
    }
