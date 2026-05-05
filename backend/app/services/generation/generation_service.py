"""
Generation Service - Orchestrates the full content generation pipeline.

Pipeline:
1. Load content item + brief
2. Load relevant style guides and CTA patterns
3. Build prompts using PromptBuilder
4. Call AI provider via ProviderManager
5. Parse structured output
6. Save generation run + create content version
"""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.content import ContentItem, ContentVersion, ContentStatus
from app.models.generation import GenerationRun, GenerationStatus, AIProvider
from app.models.style_guide import StyleGuide, CTAPattern
from app.models.campaign import Campaign
from app.services.generation.prompt_builder import build_generation_prompt
from app.services.generation.output_parser import parse_generation_output
from app.services.ai_providers.base import GenerationRequest
from app.services.ai_providers.provider_manager import provider_manager


class GenerationService:
    """Main service for content generation orchestration."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_content(
        self,
        content_item_id: uuid.UUID,
        provider: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        fallback_provider: Optional[str] = None,
        custom_instructions: Optional[str] = None,
        custom_endpoint: Optional[str] = None,
        custom_api_key: Optional[str] = None,
    ) -> dict:
        """
        Full generation pipeline for a content item.

        Args:
            content_item_id: ID of the content item to generate for
            provider: AI provider name (openai, anthropic, google_gemini)
            model: Model name (e.g., gpt-4o, claude-sonnet-4-20250514)
            temperature: Generation temperature (0.0 - 1.0)
            max_tokens: Maximum output tokens
            fallback_provider: Optional fallback provider on failure
            custom_instructions: Additional instructions to append to prompt

        Returns:
            dict with generation_run info and parsed content
        """
        # 1. Load content item with brief
        content_item = await self._load_content_item(content_item_id)
        if not content_item:
            return {"success": False, "error": "Content item not found"}

        if not content_item.brief:
            return {"success": False, "error": "Content item has no brief. Create a brief first."}

        # 2. Load style guides and CTA patterns
        style_guides = await self._load_style_guides(content_item)
        cta_patterns = await self._load_cta_patterns(content_item)

        # 3. Build prompts
        try:
            system_prompt, user_prompt = build_generation_prompt(
                content_type=content_item.content_type.value,
                brief=content_item.brief,
                style_guides=style_guides,
                cta_patterns=cta_patterns,
            )
        except ValueError as e:
            return {"success": False, "error": str(e)}

        # Append custom instructions if provided
        if custom_instructions:
            user_prompt += f"\n\n## INSTRUKSI TAMBAHAN\n{custom_instructions}"

        # 4. Create generation run record (status: RUNNING)
        generation_run = GenerationRun(
            content_item_id=content_item_id,
            provider=AIProvider(provider),
            model=model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            parameters={
                "temperature": temperature,
                "max_tokens": max_tokens,
                "fallback_provider": fallback_provider,
                "custom_endpoint": custom_endpoint,
                "has_custom_api_key": bool(custom_api_key),
            },
            status=GenerationStatus.RUNNING,
            started_at=datetime.utcnow(),
        )
        self.db.add(generation_run)
        await self.db.flush()

        # 5. Call AI provider
        request = GenerationRequest(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            custom_endpoint=custom_endpoint,
            custom_api_key=custom_api_key,
        )

        response = await provider_manager.generate(
            provider_name=provider,
            request=request,
            fallback_provider=fallback_provider,
        )

        # 6. Update generation run with results
        generation_run.completed_at = datetime.utcnow()
        generation_run.latency_ms = response.latency_ms
        generation_run.input_tokens = response.input_tokens
        generation_run.output_tokens = response.output_tokens
        generation_run.cost_usd = response.cost_usd

        if not response.success:
            generation_run.status = GenerationStatus.FAILED
            generation_run.error_message = response.error
            await self.db.commit()
            return {
                "success": False,
                "error": response.error,
                "generation_run_id": str(generation_run.id),
                "latency_ms": response.latency_ms,
            }

        # 7. Parse structured output
        parsed_content, parse_error = parse_generation_output(
            response.content, content_item.content_type.value
        )

        if parsed_content is None:
            generation_run.status = GenerationStatus.FAILED
            generation_run.error_message = f"Output parsing failed: {parse_error}"
            await self.db.commit()
            return {
                "success": False,
                "error": f"AI responded but output parsing failed: {parse_error}",
                "raw_content": response.content[:2000],  # Include raw for debugging
                "generation_run_id": str(generation_run.id),
            }

        # 8. Mark generation as completed
        generation_run.status = GenerationStatus.COMPLETED
        generation_run.output_data = parsed_content

        # 9. Create new content version
        new_version_number = content_item.current_version + 1
        content_version = ContentVersion(
            content_item_id=content_item_id,
            version_number=new_version_number,
            content_data=parsed_content,
            generation_run_id=generation_run.id,
        )
        self.db.add(content_version)

        # Update content item version counter
        content_item.current_version = new_version_number

        # If content was in draft, keep it in draft
        # If it was previously rejected, move back to draft
        if content_item.status in [ContentStatus.DRAFT]:
            pass  # Keep as draft
        elif content_item.status == ContentStatus.ARCHIVED:
            content_item.status = ContentStatus.DRAFT

        await self.db.commit()

        return {
            "success": True,
            "generation_run_id": str(generation_run.id),
            "content_version_id": str(content_version.id),
            "version_number": new_version_number,
            "content_data": parsed_content,
            "parse_warning": parse_error,  # May contain validation warnings
            "metrics": {
                "provider": provider,
                "model": response.model,
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
                "latency_ms": response.latency_ms,
                "cost_usd": response.cost_usd,
            },
        }

    async def regenerate_content(
        self,
        content_item_id: uuid.UUID,
        provider: str,
        model: str,
        revision_notes: Optional[str] = None,
        custom_endpoint: Optional[str] = None,
        custom_api_key: Optional[str] = None,
        **kwargs,
    ) -> dict:
        """
        Regenerate content with optional revision notes.
        Adds revision context to the prompt for better results.
        """
        custom_instructions = None
        if revision_notes:
            custom_instructions = (
                f"REVISI: Hasil sebelumnya perlu diperbaiki. "
                f"Catatan revisi: {revision_notes}\n"
                f"Perbaiki output sesuai catatan di atas."
            )

        return await self.generate_content(
            content_item_id=content_item_id,
            provider=provider,
            model=model,
            custom_instructions=custom_instructions,
            custom_endpoint=custom_endpoint,
            custom_api_key=custom_api_key,
            **kwargs,
        )

    async def _load_content_item(self, content_item_id: uuid.UUID) -> Optional[ContentItem]:
        """Load content item from database."""
        result = await self.db.execute(
            select(ContentItem).where(ContentItem.id == content_item_id)
        )
        return result.scalar_one_or_none()

    async def _load_style_guides(self, content_item: ContentItem) -> list[dict]:
        """Load relevant style guides for the content item's brand/campaign."""
        # Get campaign to find brand_id
        campaign_result = await self.db.execute(
            select(Campaign).where(Campaign.id == content_item.campaign_id)
        )
        campaign = campaign_result.scalar_one_or_none()
        if not campaign:
            return []

        # Load style guides for brand or campaign
        result = await self.db.execute(
            select(StyleGuide).where(
                StyleGuide.is_active == True,
                (
                    (StyleGuide.brand_id == campaign.brand_id) |
                    (StyleGuide.campaign_id == campaign.id)
                ),
            )
        )
        guides = result.scalars().all()

        return [
            {
                "name": g.name,
                "is_active": g.is_active,
                "tone_of_voice": g.tone_of_voice,
                "writing_rules": g.writing_rules,
                "preferred_phrases": g.preferred_phrases,
                "banned_phrases": g.banned_phrases,
                "brand_examples": g.brand_examples,
                "additional_notes": g.additional_notes,
            }
            for g in guides
        ]

    async def _load_cta_patterns(self, content_item: ContentItem) -> list[dict]:
        """Load relevant CTA patterns for the content item's brand/campaign."""
        campaign_result = await self.db.execute(
            select(Campaign).where(Campaign.id == content_item.campaign_id)
        )
        campaign = campaign_result.scalar_one_or_none()
        if not campaign:
            return []

        # Load CTA patterns, optionally filtered by platform
        query = select(CTAPattern).where(
            CTAPattern.is_active == True,
            (
                (CTAPattern.brand_id == campaign.brand_id) |
                (CTAPattern.campaign_id == campaign.id)
            ),
        )

        # Filter by platform if CTA has platform_target set
        # Include CTAs with no platform_target (universal) + matching platform
        result = await self.db.execute(query)
        patterns = result.scalars().all()

        platform_map = {
            "youtube_shorts": "youtube",
            "youtube_longform": "youtube",
            "tiktok_short": "tiktok",
            "blog_article": "blog",
            "x_post": "x",
        }
        target_platform = platform_map.get(content_item.content_type.value)

        return [
            {
                "name": p.name,
                "is_active": p.is_active,
                "cta_text": p.cta_text,
                "cta_type": p.cta_type,
                "placement": p.placement,
                "platform_target": p.platform_target,
            }
            for p in patterns
            if p.platform_target is None or p.platform_target == target_platform
        ]
