import uuid
from datetime import datetime
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base


class StyleGuide(Base):
    __tablename__ = "style_guides"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    brand_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("brands.id"), nullable=True
    )
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # Style guide content
    tone_of_voice: Mapped[str | None] = mapped_column(Text, nullable=True)
    writing_rules: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # list of rules
    preferred_phrases: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # list
    banned_phrases: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # list
    brand_examples: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # list of example outputs
    additional_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    brand = relationship("Brand", back_populates="style_guides")
    campaign = relationship("Campaign", back_populates="style_guides")


class CTAPattern(Base):
    __tablename__ = "cta_patterns"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    brand_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("brands.id"), nullable=True
    )
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # CTA content
    cta_text: Mapped[str] = mapped_column(Text, nullable=False)
    cta_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # subscribe, like, comment, link, etc.
    placement: Mapped[str | None] = mapped_column(String(50), nullable=True)  # intro, mid, outro
    platform_target: Mapped[str | None] = mapped_column(String(50), nullable=True)  # youtube, tiktok, blog, x
    metadata_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    brand = relationship("Brand", back_populates="cta_patterns")
    campaign = relationship("Campaign", back_populates="cta_patterns")
