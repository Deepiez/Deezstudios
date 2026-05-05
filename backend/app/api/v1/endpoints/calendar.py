"""Calendar API endpoints - Content scheduling and publish management."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from uuid import UUID
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.models.content import ContentItem, ContentStatus
from app.models.publish import PublishJob, PublishJobStatus, PublishLog
from app.models.platform import PlatformAccount

router = APIRouter()


# --- Schemas ---

class ScheduleRequest(BaseModel):
    content_item_id: UUID
    platform_account_id: UUID
    scheduled_publish_at: datetime
    publish_data: Optional[dict] = None


class RescheduleRequest(BaseModel):
    scheduled_publish_at: datetime


class CalendarEventResponse(BaseModel):
    id: str
    content_item_id: str
    title: str
    content_type: str
    status: str
    scheduled_at: str
    platform: str
    platform_account_id: str

    class Config:
        from_attributes = True


# --- Endpoints ---

@router.get("/", response_model=list[CalendarEventResponse])
async def get_calendar(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    brand_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Get content calendar view with scheduled and published items.
    Returns events within the date range.
    """
    query = (
        select(PublishJob, ContentItem, PlatformAccount)
        .join(ContentItem, PublishJob.content_item_id == ContentItem.id)
        .join(PlatformAccount, PublishJob.platform_account_id == PlatformAccount.id)
    )

    # Date filters
    if start_date:
        query = query.where(PublishJob.scheduled_publish_at >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.where(PublishJob.scheduled_publish_at <= datetime.combine(end_date, datetime.max.time()))

    # Exclude cancelled
    query = query.where(PublishJob.status != PublishJobStatus.CANCELLED)

    # Order by scheduled time
    query = query.order_by(PublishJob.scheduled_publish_at)

    result = await db.execute(query)
    rows = result.all()

    events = []
    for job, content, account in rows:
        events.append(CalendarEventResponse(
            id=str(job.id),
            content_item_id=str(content.id),
            title=content.title,
            content_type=content.content_type.value,
            status=job.status.value,
            scheduled_at=job.scheduled_publish_at.isoformat() if job.scheduled_publish_at else "",
            platform=account.platform.value,
            platform_account_id=str(account.id),
        ))

    return events


@router.post("/schedule", status_code=status.HTTP_201_CREATED)
async def schedule_item(
    data: ScheduleRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Schedule an approved content item for publishing.
    Content must be in 'approved' status.
    """
    # Validate content item
    content_result = await db.execute(
        select(ContentItem).where(ContentItem.id == data.content_item_id)
    )
    content = content_result.scalar_one_or_none()
    if not content:
        raise HTTPException(status_code=404, detail="Content item not found")

    if content.status != ContentStatus.APPROVED:
        raise HTTPException(
            status_code=400,
            detail=f"Content must be approved before scheduling. Current status: {content.status.value}",
        )

    # Validate platform account
    account_result = await db.execute(
        select(PlatformAccount).where(PlatformAccount.id == data.platform_account_id)
    )
    account = account_result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Platform account not found")

    # Validate schedule is in the future
    if data.scheduled_publish_at <= datetime.utcnow():
        raise HTTPException(status_code=400, detail="Scheduled time must be in the future")

    # Create publish job
    publish_job = PublishJob(
        content_item_id=data.content_item_id,
        platform_account_id=data.platform_account_id,
        status=PublishJobStatus.QUEUED,
        scheduled_publish_at=data.scheduled_publish_at,
        publish_data=data.publish_data,
    )
    db.add(publish_job)

    # Update content status
    content.status = ContentStatus.SCHEDULED
    content.scheduled_at = data.scheduled_publish_at

    # Log
    log = PublishLog(
        publish_job_id=publish_job.id,
        level="info",
        message=f"Content scheduled for {data.scheduled_publish_at.isoformat()} on {account.platform.value}",
    )
    db.add(log)

    await db.commit()
    await db.refresh(publish_job)

    return {
        "id": str(publish_job.id),
        "status": publish_job.status.value,
        "scheduled_publish_at": publish_job.scheduled_publish_at.isoformat(),
        "platform": account.platform.value,
        "message": "Content scheduled successfully",
    }


@router.put("/schedule/{job_id}")
async def reschedule_item(
    job_id: UUID,
    data: RescheduleRequest,
    db: AsyncSession = Depends(get_db),
):
    """Reschedule a publish job to a new time."""
    result = await db.execute(
        select(PublishJob).where(PublishJob.id == job_id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Publish job not found")

    if job.status not in [PublishJobStatus.QUEUED, PublishJobStatus.SCHEDULED]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot reschedule job with status: {job.status.value}",
        )

    if data.scheduled_publish_at <= datetime.utcnow():
        raise HTTPException(status_code=400, detail="New schedule must be in the future")

    old_time = job.scheduled_publish_at
    job.scheduled_publish_at = data.scheduled_publish_at

    # Update content item scheduled_at
    content_result = await db.execute(
        select(ContentItem).where(ContentItem.id == job.content_item_id)
    )
    content = content_result.scalar_one_or_none()
    if content:
        content.scheduled_at = data.scheduled_publish_at

    # Log
    log = PublishLog(
        publish_job_id=job.id,
        level="info",
        message=f"Rescheduled from {old_time.isoformat()} to {data.scheduled_publish_at.isoformat()}",
    )
    db.add(log)

    await db.commit()

    return {
        "id": str(job.id),
        "scheduled_publish_at": job.scheduled_publish_at.isoformat(),
        "message": "Rescheduled successfully",
    }


@router.delete("/schedule/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_schedule(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Cancel a scheduled publish job."""
    result = await db.execute(
        select(PublishJob).where(PublishJob.id == job_id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Publish job not found")

    if job.status not in [PublishJobStatus.QUEUED, PublishJobStatus.SCHEDULED]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel job with status: {job.status.value}",
        )

    job.status = PublishJobStatus.CANCELLED

    # Revert content status to approved
    content_result = await db.execute(
        select(ContentItem).where(ContentItem.id == job.content_item_id)
    )
    content = content_result.scalar_one_or_none()
    if content and content.status == ContentStatus.SCHEDULED:
        content.status = ContentStatus.APPROVED
        content.scheduled_at = None

    # Log
    log = PublishLog(
        publish_job_id=job.id,
        level="info",
        message="Publish job cancelled by user",
    )
    db.add(log)

    await db.commit()


@router.post("/publish/{job_id}/run")
async def run_publish_now(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Immediately trigger a publish job (publish now)."""
    result = await db.execute(
        select(PublishJob).where(PublishJob.id == job_id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Publish job not found")

    if job.status not in [PublishJobStatus.QUEUED, PublishJobStatus.SCHEDULED]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot publish job with status: {job.status.value}",
        )

    # Dispatch to Celery task
    from app.workers.tasks import publish_to_youtube
    # TODO: Route to correct platform task based on platform account

    job.status = PublishJobStatus.PROCESSING
    job.started_at = datetime.utcnow()

    log = PublishLog(
        publish_job_id=job.id,
        level="info",
        message="Publish triggered manually (publish now)",
    )
    db.add(log)

    await db.commit()

    # Dispatch async task
    publish_to_youtube.delay(str(job.id))

    return {
        "id": str(job.id),
        "status": "processing",
        "message": "Publish job triggered. Check status for updates.",
    }
