"""Analytics API endpoints - Operational dashboard data."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_, case
from datetime import date, datetime, timedelta
from typing import Optional

from app.core.database import get_db
from app.models.content import ContentItem, ContentStatus, ContentType
from app.models.generation import GenerationRun, GenerationStatus, AIProvider
from app.models.publish import PublishJob, PublishJobStatus, PublishLog
from app.models.analytics import AnalyticsDailySnapshot
from app.models.audit import AuditLog

router = APIRouter()


@router.get("/overview")
async def get_analytics_overview(db: AsyncSession = Depends(get_db)):
    """
    Get analytics overview - all key metrics in one call.
    Used for the main dashboard stats cards.
    """
    # Content counts by status
    content_counts = {}
    for status_val in ContentStatus:
        result = await db.execute(
            select(func.count(ContentItem.id)).where(ContentItem.status == status_val)
        )
        content_counts[status_val.value] = result.scalar() or 0

    total_content = sum(content_counts.values())

    # Generation stats
    gen_total = await db.execute(
        select(func.count(GenerationRun.id))
    )
    gen_completed = await db.execute(
        select(func.count(GenerationRun.id)).where(
            GenerationRun.status == GenerationStatus.COMPLETED
        )
    )
    gen_failed = await db.execute(
        select(func.count(GenerationRun.id)).where(
            GenerationRun.status == GenerationStatus.FAILED
        )
    )
    avg_latency = await db.execute(
        select(func.avg(GenerationRun.latency_ms)).where(
            GenerationRun.status == GenerationStatus.COMPLETED
        )
    )
    total_cost = await db.execute(
        select(func.coalesce(func.sum(GenerationRun.cost_usd), 0)).where(
            GenerationRun.status == GenerationStatus.COMPLETED
        )
    )
    total_tokens = await db.execute(
        select(
            func.coalesce(func.sum(GenerationRun.input_tokens), 0) +
            func.coalesce(func.sum(GenerationRun.output_tokens), 0)
        ).where(GenerationRun.status == GenerationStatus.COMPLETED)
    )

    # Publish stats
    publish_success = await db.execute(
        select(func.count(PublishJob.id)).where(PublishJob.status == PublishJobStatus.PUBLISHED)
    )
    publish_failed = await db.execute(
        select(func.count(PublishJob.id)).where(PublishJob.status == PublishJobStatus.FAILED)
    )
    publish_queued = await db.execute(
        select(func.count(PublishJob.id)).where(
            PublishJob.status.in_([PublishJobStatus.QUEUED, PublishJobStatus.SCHEDULED])
        )
    )

    return {
        "content": {
            "total": total_content,
            "by_status": content_counts,
            "drafts": content_counts.get("draft", 0),
            "in_review": content_counts.get("in_review", 0),
            "approved": content_counts.get("approved", 0),
            "scheduled": content_counts.get("scheduled", 0),
            "published": content_counts.get("published", 0),
            "failed": content_counts.get("failed", 0),
        },
        "generation": {
            "total_runs": gen_total.scalar() or 0,
            "completed": gen_completed.scalar() or 0,
            "failed": gen_failed.scalar() or 0,
            "avg_latency_ms": round(avg_latency.scalar() or 0, 0),
            "total_cost_usd": round(float(total_cost.scalar() or 0), 4),
            "total_tokens": total_tokens.scalar() or 0,
        },
        "publishing": {
            "published": publish_success.scalar() or 0,
            "failed": publish_failed.scalar() or 0,
            "queued": publish_queued.scalar() or 0,
        },
    }


@router.get("/content-stats")
async def get_content_stats(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get content statistics by type and status over time."""
    # Content by type
    type_counts = {}
    for ct in ContentType:
        result = await db.execute(
            select(func.count(ContentItem.id)).where(ContentItem.content_type == ct)
        )
        type_counts[ct.value] = result.scalar() or 0

    # Content created per day (last 30 days)
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()

    daily_created = await db.execute(
        select(
            func.date(ContentItem.created_at).label("day"),
            func.count(ContentItem.id).label("count"),
        )
        .where(func.date(ContentItem.created_at) >= start_date)
        .where(func.date(ContentItem.created_at) <= end_date)
        .group_by(func.date(ContentItem.created_at))
        .order_by(func.date(ContentItem.created_at))
    )
    daily_data = [{"date": str(row.day), "count": row.count} for row in daily_created]

    # Approval rate
    total_reviewed = await db.execute(
        select(func.count(ContentItem.id)).where(
            ContentItem.status.in_([
                ContentStatus.APPROVED, ContentStatus.SCHEDULED,
                ContentStatus.PUBLISHED, ContentStatus.PUBLISHED,
            ])
        )
    )
    total_created = await db.execute(select(func.count(ContentItem.id)))

    created_count = total_created.scalar() or 0
    reviewed_count = total_reviewed.scalar() or 0
    approval_rate = (reviewed_count / created_count * 100) if created_count > 0 else 0

    return {
        "by_type": type_counts,
        "daily_created": daily_data,
        "approval_rate": round(approval_rate, 1),
        "total_created": created_count,
        "period": {"start": str(start_date), "end": str(end_date)},
    }


@router.get("/publish-stats")
async def get_publish_stats(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get publish job statistics."""
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()

    # Publish jobs by status
    status_counts = {}
    for s in PublishJobStatus:
        result = await db.execute(
            select(func.count(PublishJob.id)).where(PublishJob.status == s)
        )
        status_counts[s.value] = result.scalar() or 0

    # Daily publish activity
    daily_published = await db.execute(
        select(
            func.date(PublishJob.completed_at).label("day"),
            func.count(PublishJob.id).label("count"),
        )
        .where(PublishJob.status == PublishJobStatus.PUBLISHED)
        .where(func.date(PublishJob.completed_at) >= start_date)
        .where(func.date(PublishJob.completed_at) <= end_date)
        .group_by(func.date(PublishJob.completed_at))
        .order_by(func.date(PublishJob.completed_at))
    )
    daily_data = [{"date": str(row.day), "count": row.count} for row in daily_published]

    # Success rate
    total_attempted = status_counts.get("published", 0) + status_counts.get("failed", 0)
    success_rate = (
        (status_counts.get("published", 0) / total_attempted * 100)
        if total_attempted > 0
        else 0
    )

    # Average retry count for failed jobs
    avg_retries = await db.execute(
        select(func.avg(PublishJob.retry_count)).where(
            PublishJob.status == PublishJobStatus.FAILED
        )
    )

    return {
        "by_status": status_counts,
        "daily_published": daily_data,
        "success_rate": round(success_rate, 1),
        "total_attempted": total_attempted,
        "avg_retries_on_failure": round(float(avg_retries.scalar() or 0), 1),
        "period": {"start": str(start_date), "end": str(end_date)},
    }


@router.get("/provider-usage")
async def get_provider_usage(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get AI provider usage statistics - cost, tokens, latency breakdown."""
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()

    providers_data = []

    for provider_val in AIProvider:
        # Base query for this provider in date range
        base_filter = and_(
            GenerationRun.provider == provider_val,
            GenerationRun.status == GenerationStatus.COMPLETED,
            func.date(GenerationRun.created_at) >= start_date,
            func.date(GenerationRun.created_at) <= end_date,
        )

        run_count = await db.execute(
            select(func.count(GenerationRun.id)).where(base_filter)
        )
        total_input_tokens = await db.execute(
            select(func.coalesce(func.sum(GenerationRun.input_tokens), 0)).where(base_filter)
        )
        total_output_tokens = await db.execute(
            select(func.coalesce(func.sum(GenerationRun.output_tokens), 0)).where(base_filter)
        )
        total_cost = await db.execute(
            select(func.coalesce(func.sum(GenerationRun.cost_usd), 0)).where(base_filter)
        )
        avg_latency = await db.execute(
            select(func.avg(GenerationRun.latency_ms)).where(base_filter)
        )

        count = run_count.scalar() or 0
        if count > 0:
            providers_data.append({
                "provider": provider_val.value,
                "total_runs": count,
                "input_tokens": total_input_tokens.scalar() or 0,
                "output_tokens": total_output_tokens.scalar() or 0,
                "total_tokens": (total_input_tokens.scalar() or 0) + (total_output_tokens.scalar() or 0),
                "total_cost_usd": round(float(total_cost.scalar() or 0), 4),
                "avg_latency_ms": round(float(avg_latency.scalar() or 0), 0),
            })

    # Model breakdown (top 10 models by usage)
    model_usage = await db.execute(
        select(
            GenerationRun.model,
            GenerationRun.provider,
            func.count(GenerationRun.id).label("runs"),
            func.coalesce(func.sum(GenerationRun.cost_usd), 0).label("cost"),
            func.avg(GenerationRun.latency_ms).label("avg_latency"),
        )
        .where(
            GenerationRun.status == GenerationStatus.COMPLETED,
            func.date(GenerationRun.created_at) >= start_date,
            func.date(GenerationRun.created_at) <= end_date,
        )
        .group_by(GenerationRun.model, GenerationRun.provider)
        .order_by(desc("runs"))
        .limit(10)
    )

    models_data = [
        {
            "model": row.model,
            "provider": row.provider.value if hasattr(row.provider, 'value') else row.provider,
            "runs": row.runs,
            "cost_usd": round(float(row.cost), 4),
            "avg_latency_ms": round(float(row.avg_latency or 0), 0),
        }
        for row in model_usage
    ]

    # Total across all providers
    grand_total_cost = sum(p["total_cost_usd"] for p in providers_data)
    grand_total_runs = sum(p["total_runs"] for p in providers_data)

    return {
        "providers": providers_data,
        "models": models_data,
        "totals": {
            "total_runs": grand_total_runs,
            "total_cost_usd": round(grand_total_cost, 4),
        },
        "period": {"start": str(start_date), "end": str(end_date)},
    }


@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """Get recent generation and publish activity feed."""
    activities = []

    # Recent generation runs
    gen_runs = await db.execute(
        select(GenerationRun, ContentItem)
        .join(ContentItem, GenerationRun.content_item_id == ContentItem.id)
        .order_by(desc(GenerationRun.created_at))
        .limit(limit)
    )

    for run, content in gen_runs:
        activities.append({
            "type": "generation",
            "id": str(run.id),
            "title": content.title,
            "content_type": content.content_type.value,
            "status": run.status.value,
            "provider": run.provider.value,
            "model": run.model,
            "cost_usd": run.cost_usd,
            "latency_ms": run.latency_ms,
            "error": run.error_message,
            "timestamp": run.created_at.isoformat(),
        })

    # Recent publish jobs
    pub_jobs = await db.execute(
        select(PublishJob, ContentItem)
        .join(ContentItem, PublishJob.content_item_id == ContentItem.id)
        .order_by(desc(PublishJob.created_at))
        .limit(limit)
    )

    for job, content in pub_jobs:
        activities.append({
            "type": "publish",
            "id": str(job.id),
            "title": content.title,
            "content_type": content.content_type.value,
            "status": job.status.value,
            "platform_url": job.platform_url,
            "error": job.error_message,
            "scheduled_at": job.scheduled_publish_at.isoformat() if job.scheduled_publish_at else None,
            "timestamp": job.created_at.isoformat(),
        })

    # Sort by timestamp descending
    activities.sort(key=lambda x: x["timestamp"], reverse=True)

    return {"activities": activities[:limit]}


@router.get("/daily-snapshots")
async def get_daily_snapshots(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
):
    """Get daily analytics snapshots for trend charts."""
    start = date.today() - timedelta(days=days)

    result = await db.execute(
        select(AnalyticsDailySnapshot)
        .where(AnalyticsDailySnapshot.snapshot_date >= start)
        .order_by(AnalyticsDailySnapshot.snapshot_date)
    )
    snapshots = result.scalars().all()

    return {
        "snapshots": [
            {
                "date": str(s.snapshot_date),
                "drafts": s.total_drafts,
                "in_review": s.total_in_review,
                "approved": s.total_approved,
                "scheduled": s.total_scheduled,
                "published": s.total_published,
                "failed": s.total_failed,
                "generation_runs": s.generation_runs_count,
                "avg_latency_ms": s.avg_generation_latency_ms,
                "total_tokens": s.total_tokens_used,
                "total_cost_usd": s.total_cost_usd,
                "provider_usage": s.provider_usage,
            }
            for s in snapshots
        ],
        "period_days": days,
    }
