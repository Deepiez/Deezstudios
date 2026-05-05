import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Integer, Float, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base
import enum


class GenerationStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AIProvider(str, enum.Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE_GEMINI = "google_gemini"
    LOCAL = "local"


class GenerationRun(Base):
    __tablename__ = "generation_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    content_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("content_items.id"), nullable=False
    )
    # AI Provider details
    provider: Mapped[AIProvider] = mapped_column(SAEnum(AIProvider), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    # Prompt and parameters
    system_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    parameters: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # temperature, max_tokens, etc.
    # Result
    status: Mapped[GenerationStatus] = mapped_column(
        SAEnum(GenerationStatus), default=GenerationStatus.PENDING
    )
    output_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Usage metrics
    input_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cost_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
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

    # Relationships
    content_item = relationship("ContentItem", back_populates="generation_runs")
    content_version = relationship("ContentVersion", back_populates="generation_run", uselist=False)
