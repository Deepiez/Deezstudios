import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Integer, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base
import enum


class PublishJobStatus(str, enum.Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    UPLOADED = "uploaded"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PublishJob(Base):
    __tablename__ = "publish_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    content_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("content_items.id"), nullable=False
    )
    platform_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("platform_accounts.id"), nullable=False
    )
    status: Mapped[PublishJobStatus] = mapped_column(
        SAEnum(PublishJobStatus), default=PublishJobStatus.QUEUED
    )
    # Scheduling
    scheduled_publish_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # Platform response
    platform_post_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    platform_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Publish data sent to platform
    publish_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # Error handling
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    # Timestamps
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    content_item = relationship("ContentItem", back_populates="publish_jobs")
    platform_account = relationship("PlatformAccount", back_populates="publish_jobs")
    logs = relationship("PublishLog", back_populates="publish_job", lazy="selectin")


class PublishLog(Base):
    __tablename__ = "publish_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    publish_job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("publish_jobs.id"), nullable=False
    )
    level: Mapped[str] = mapped_column(String(20), nullable=False)  # info, warning, error
    message: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    # Relationships
    publish_job = relationship("PublishJob", back_populates="logs")
