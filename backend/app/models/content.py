import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Integer, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base
import enum


class ContentType(str, enum.Enum):
    YOUTUBE_SHORTS = "youtube_shorts"
    YOUTUBE_LONGFORM = "youtube_longform"
    TIKTOK_SHORT = "tiktok_short"
    BLOG_ARTICLE = "blog_article"
    X_POST = "x_post"


class ContentStatus(str, enum.Enum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    ARCHIVED = "archived"


class ContentLanguage(str, enum.Enum):
    ID = "id"
    EN = "en"


class ContentItem(Base):
    __tablename__ = "content_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    content_type: Mapped[ContentType] = mapped_column(
        SAEnum(ContentType), nullable=False
    )
    status: Mapped[ContentStatus] = mapped_column(
        SAEnum(ContentStatus), default=ContentStatus.DRAFT
    )
    language: Mapped[ContentLanguage] = mapped_column(
        SAEnum(ContentLanguage), default=ContentLanguage.ID
    )
    # Brief data
    brief: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # Current active version number
    current_version: Mapped[int] = mapped_column(Integer, default=1)
    # Scheduling
    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # Metadata
    tags: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # list of tags
    metadata_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    campaign = relationship("Campaign", back_populates="content_items")
    versions = relationship("ContentVersion", back_populates="content_item", lazy="selectin")
    publish_jobs = relationship("PublishJob", back_populates="content_item", lazy="selectin")
    generation_runs = relationship("GenerationRun", back_populates="content_item", lazy="selectin")


class ContentVersion(Base):
    __tablename__ = "content_versions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    content_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("content_items.id"), nullable=False
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    # Content fields stored as structured JSON
    # For YouTube: {title, hook, script, description, thumbnail_prompt, tags}
    # For Blog: {title, outline, body, cta}
    # For X: {post_text, thread_texts, cta}
    # For TikTok: {hook, script, caption, visual_cues}
    content_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    # Which generation run produced this version (null if manually created)
    generation_run_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("generation_runs.id"), nullable=True
    )
    # Approval tracking
    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    approval_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Revision notes
    revision_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    # Relationships
    content_item = relationship("ContentItem", back_populates="versions")
    generation_run = relationship("GenerationRun", back_populates="content_version")
