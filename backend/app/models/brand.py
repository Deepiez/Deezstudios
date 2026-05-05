import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base


class Brand(Base):
    __tablename__ = "brands"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    niche: Mapped[str | None] = mapped_column(String(100), nullable=True)
    target_audience: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user = relationship("User", back_populates="brands")
    campaigns = relationship("Campaign", back_populates="brand", lazy="selectin")
    style_guides = relationship("StyleGuide", back_populates="brand", lazy="selectin")
    cta_patterns = relationship("CTAPattern", back_populates="brand", lazy="selectin")
    platform_accounts = relationship("PlatformAccount", back_populates="brand", lazy="selectin")
