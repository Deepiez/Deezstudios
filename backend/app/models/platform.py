import uuid
from datetime import datetime
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base
import enum


class PlatformType(str, enum.Enum):
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    X = "x"
    BLOG = "blog"


class PlatformAccount(Base):
    __tablename__ = "platform_accounts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    brand_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("brands.id"), nullable=False
    )
    platform: Mapped[PlatformType] = mapped_column(SAEnum(PlatformType), nullable=False)
    account_name: Mapped[str] = mapped_column(String(200), nullable=False)
    account_id: Mapped[str | None] = mapped_column(String(200), nullable=True)  # platform-specific ID
    is_connected: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    connected_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    brand = relationship("Brand", back_populates="platform_accounts")
    oauth_tokens = relationship("OAuthToken", back_populates="platform_account", lazy="selectin")
    publish_jobs = relationship("PublishJob", back_populates="platform_account", lazy="selectin")


class OAuthToken(Base):
    __tablename__ = "oauth_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    platform_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("platform_accounts.id"), nullable=False
    )
    access_token: Mapped[str] = mapped_column(Text, nullable=False)  # encrypted
    refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)  # encrypted
    token_type: Mapped[str] = mapped_column(String(50), default="Bearer")
    scope: Mapped[str | None] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    platform_account = relationship("PlatformAccount", back_populates="oauth_tokens")
