"""Pydantic schemas for content items and briefs."""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum


class ContentTypeEnum(str, Enum):
    YOUTUBE_SHORTS = "youtube_shorts"
    YOUTUBE_LONGFORM = "youtube_longform"
    TIKTOK_SHORT = "tiktok_short"
    BLOG_ARTICLE = "blog_article"
    X_POST = "x_post"


class ContentStatusEnum(str, Enum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    ARCHIVED = "archived"


class LanguageEnum(str, Enum):
    ID = "id"
    EN = "en"


# =============================================================================
# BRIEF SCHEMA
# =============================================================================

class ContentBrief(BaseModel):
    """Brief structure for content generation."""
    topic: str = Field(..., min_length=3, max_length=500)
    audience: str = Field(default="General audience", max_length=300)
    objective: str = Field(default="Inform and engage", max_length=500)
    key_message: str = Field(default="", max_length=1000)
    tone: str = Field(default="Conversational", max_length=100)
    language: LanguageEnum = LanguageEnum.ID
    references: Optional[str] = Field(default=None, max_length=2000)
    # Platform-specific fields
    target_duration: Optional[str] = Field(
        default=None, description="For video content: e.g. '30-60 detik' or '8-12 menit'"
    )
    target_word_count: Optional[str] = Field(
        default=None, description="For blog: e.g. '1500-2000'"
    )
    additional_context: Optional[str] = Field(
        default=None, max_length=2000, description="Any extra context for the AI"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "topic": "5 Tips Produktivitas untuk Developer yang WFH",
                "audience": "Developer Indonesia usia 22-35 yang kerja remote",
                "objective": "Edukasi + engagement, dorong subscribe",
                "key_message": "Produktivitas bukan soal jam kerja, tapi sistem yang tepat",
                "tone": "Casual tapi informatif, seperti ngobrol sama teman",
                "language": "id",
                "references": "Referensi: video Ali Abdaal tentang productivity systems",
                "target_duration": "45-60 detik",
            }
        }


# =============================================================================
# CONTENT ITEM SCHEMAS
# =============================================================================

class ContentItemCreate(BaseModel):
    """Create a new content item."""
    campaign_id: UUID
    title: str = Field(..., min_length=3, max_length=300)
    content_type: ContentTypeEnum
    language: LanguageEnum = LanguageEnum.ID
    brief: ContentBrief
    tags: Optional[list[str]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "campaign_id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "5 Tips Produktivitas Developer WFH",
                "content_type": "youtube_shorts",
                "language": "id",
                "brief": {
                    "topic": "5 Tips Produktivitas untuk Developer yang WFH",
                    "audience": "Developer Indonesia usia 22-35",
                    "objective": "Edukasi + engagement",
                    "key_message": "Produktivitas bukan soal jam kerja",
                    "tone": "Casual informatif",
                    "language": "id",
                    "target_duration": "45-60 detik",
                },
                "tags": ["productivity", "developer", "wfh"],
            }
        }


class ContentItemUpdate(BaseModel):
    """Update a content item."""
    title: Optional[str] = Field(default=None, min_length=3, max_length=300)
    brief: Optional[ContentBrief] = None
    tags: Optional[list[str]] = None
    scheduled_at: Optional[datetime] = None


class ContentItemResponse(BaseModel):
    """Content item response."""
    id: UUID
    campaign_id: UUID
    title: str
    content_type: str
    status: str
    language: str
    brief: Optional[dict] = None
    current_version: int
    scheduled_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    tags: Optional[list[str]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContentVersionResponse(BaseModel):
    """Content version response."""
    id: UUID
    content_item_id: UUID
    version_number: int
    content_data: dict
    generation_run_id: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    approval_notes: Optional[str] = None
    revision_notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
