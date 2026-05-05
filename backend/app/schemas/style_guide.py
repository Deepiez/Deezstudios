"""Pydantic schemas for style guides and CTA patterns."""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


# === Style Guide ===

class StyleGuideCreate(BaseModel):
    brand_id: Optional[UUID] = None
    campaign_id: Optional[UUID] = None
    name: str = Field(..., min_length=2, max_length=200)
    tone_of_voice: Optional[str] = None
    writing_rules: Optional[list[str]] = None
    preferred_phrases: Optional[list[str]] = None
    banned_phrases: Optional[list[str]] = None
    brand_examples: Optional[list[dict]] = None
    additional_notes: Optional[str] = None


class StyleGuideUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=200)
    is_active: Optional[bool] = None
    tone_of_voice: Optional[str] = None
    writing_rules: Optional[list[str]] = None
    preferred_phrases: Optional[list[str]] = None
    banned_phrases: Optional[list[str]] = None
    brand_examples: Optional[list[dict]] = None
    additional_notes: Optional[str] = None


class StyleGuideResponse(BaseModel):
    id: UUID
    brand_id: Optional[UUID] = None
    campaign_id: Optional[UUID] = None
    name: str
    is_active: bool
    tone_of_voice: Optional[str] = None
    writing_rules: Optional[list[str]] = None
    preferred_phrases: Optional[list[str]] = None
    banned_phrases: Optional[list[str]] = None
    brand_examples: Optional[list[dict]] = None
    additional_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# === CTA Pattern ===

class CTAPatternCreate(BaseModel):
    brand_id: Optional[UUID] = None
    campaign_id: Optional[UUID] = None
    name: str = Field(..., min_length=2, max_length=200)
    cta_text: str = Field(..., min_length=3)
    cta_type: Optional[str] = Field(default=None, max_length=50)
    placement: Optional[str] = Field(default=None, max_length=50)
    platform_target: Optional[str] = Field(default=None, max_length=50)


class CTAPatternUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=200)
    is_active: Optional[bool] = None
    cta_text: Optional[str] = None
    cta_type: Optional[str] = None
    placement: Optional[str] = None
    platform_target: Optional[str] = None


class CTAPatternResponse(BaseModel):
    id: UUID
    brand_id: Optional[UUID] = None
    campaign_id: Optional[UUID] = None
    name: str
    is_active: bool
    cta_text: str
    cta_type: Optional[str] = None
    placement: Optional[str] = None
    platform_target: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
