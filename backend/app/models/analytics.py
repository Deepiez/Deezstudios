import uuid
from datetime import datetime, date
from sqlalchemy import String, DateTime, Date, Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base


class AnalyticsDailySnapshot(Base):
    __tablename__ = "analytics_daily_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False, unique=True)
    # Content counts
    total_drafts: Mapped[int] = mapped_column(Integer, default=0)
    total_in_review: Mapped[int] = mapped_column(Integer, default=0)
    total_approved: Mapped[int] = mapped_column(Integer, default=0)
    total_scheduled: Mapped[int] = mapped_column(Integer, default=0)
    total_published: Mapped[int] = mapped_column(Integer, default=0)
    total_failed: Mapped[int] = mapped_column(Integer, default=0)
    # Generation metrics
    generation_runs_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_generation_latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    total_cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    # Provider breakdown
    provider_usage: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # Platform breakdown
    platform_publish_counts: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
