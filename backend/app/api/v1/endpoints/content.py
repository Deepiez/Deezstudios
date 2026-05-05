"""Content API endpoints - Content items, versions, and approval workflow."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from uuid import UUID
from datetime import datetime
from typing import Optional

from app.core.database import get_db
from app.models.content import ContentItem, ContentVersion, ContentStatus, ContentType, ContentLanguage
from app.models.campaign import Campaign
from app.models.audit import AuditLog
from app.schemas.content import (
    ContentItemCreate,
    ContentItemUpdate,
    ContentItemResponse,
    ContentVersionResponse,
)

router = APIRouter()


@router.get("/", response_model=list[ContentItemResponse])
async def list_content_items(
    campaign_id: Optional[UUID] = None,
    content_type: Optional[str] = None,
    status_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List content items with optional filters."""
    query = select(ContentItem).order_by(desc(ContentItem.updated_at))

    if campaign_id:
        query = query.where(ContentItem.campaign_id == campaign_id)
    if content_type:
        query = query.where(ContentItem.content_type == content_type)
    if status_filter:
        query = query.where(ContentItem.status == status_filter)

    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    items = result.scalars().all()

    return [ContentItemResponse.model_validate(item) for item in items]


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ContentItemResponse)
async def create_content_item(
    data: ContentItemCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new content item with brief.

    The brief is the starting point for all content generation.
    Once created, you can run generation to produce content versions.
    """
    # Validate campaign exists
    campaign_result = await db.execute(
        select(Campaign).where(Campaign.id == data.campaign_id)
    )
    campaign = campaign_result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )

    # Create content item
    content_item = ContentItem(
        campaign_id=data.campaign_id,
        title=data.title,
        content_type=ContentType(data.content_type.value),
        language=ContentLanguage(data.language.value),
        brief=data.brief.model_dump(),
        tags=data.tags,
        status=ContentStatus.DRAFT,
        current_version=0,
    )
    db.add(content_item)
    await db.commit()
    await db.refresh(content_item)

    return ContentItemResponse.model_validate(content_item)


@router.get("/{content_id}", response_model=ContentItemResponse)
async def get_content_item(
    content_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get content item by ID."""
    result = await db.execute(
        select(ContentItem).where(ContentItem.id == content_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content item not found",
        )

    return ContentItemResponse.model_validate(item)


@router.put("/{content_id}", response_model=ContentItemResponse)
async def update_content_item(
    content_id: UUID,
    data: ContentItemUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update content item (title, brief, tags, schedule)."""
    result = await db.execute(
        select(ContentItem).where(ContentItem.id == content_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content item not found",
        )

    if data.title is not None:
        item.title = data.title
    if data.brief is not None:
        item.brief = data.brief.model_dump()
    if data.tags is not None:
        item.tags = data.tags
    if data.scheduled_at is not None:
        item.scheduled_at = data.scheduled_at

    await db.commit()
    await db.refresh(item)

    return ContentItemResponse.model_validate(item)


@router.post("/{content_id}/submit-review", response_model=ContentItemResponse)
async def submit_for_review(
    content_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Submit content item for review. Requires at least one content version."""
    result = await db.execute(
        select(ContentItem).where(ContentItem.id == content_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Content item not found")

    if item.status != ContentStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot submit for review. Current status: {item.status.value}. Must be 'draft'.",
        )

    if item.current_version < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot submit for review without at least one generated version.",
        )

    item.status = ContentStatus.IN_REVIEW
    await db.commit()
    await db.refresh(item)

    return ContentItemResponse.model_validate(item)


@router.post("/{content_id}/approve", response_model=ContentItemResponse)
async def approve_content(
    content_id: UUID,
    approval_notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Approve content item for scheduling/publishing.
    Content must be in 'in_review' status.
    """
    result = await db.execute(
        select(ContentItem).where(ContentItem.id == content_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Content item not found")

    if item.status != ContentStatus.IN_REVIEW:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve. Current status: {item.status.value}. Must be 'in_review'.",
        )

    # Mark current version as approved
    version_result = await db.execute(
        select(ContentVersion)
        .where(ContentVersion.content_item_id == content_id)
        .where(ContentVersion.version_number == item.current_version)
    )
    current_version = version_result.scalar_one_or_none()
    if current_version:
        current_version.approved_at = datetime.utcnow()
        current_version.approval_notes = approval_notes

    item.status = ContentStatus.APPROVED

    # Audit log
    audit = AuditLog(
        action="content_approved",
        entity_type="content_item",
        entity_id=str(content_id),
        details={"title": item.title, "version": item.current_version, "notes": approval_notes},
    )
    db.add(audit)

    await db.commit()
    await db.refresh(item)

    return ContentItemResponse.model_validate(item)


@router.post("/{content_id}/reject", response_model=ContentItemResponse)
async def reject_content(
    content_id: UUID,
    revision_notes: str = "",
    db: AsyncSession = Depends(get_db),
):
    """
    Reject content and send back to draft for revision.
    Optionally include revision notes for the next generation.
    """
    result = await db.execute(
        select(ContentItem).where(ContentItem.id == content_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Content item not found")

    if item.status != ContentStatus.IN_REVIEW:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reject. Current status: {item.status.value}. Must be 'in_review'.",
        )

    # Store revision notes on current version
    version_result = await db.execute(
        select(ContentVersion)
        .where(ContentVersion.content_item_id == content_id)
        .where(ContentVersion.version_number == item.current_version)
    )
    current_version = version_result.scalar_one_or_none()
    if current_version and revision_notes:
        current_version.revision_notes = revision_notes

    item.status = ContentStatus.DRAFT

    # Audit log
    audit = AuditLog(
        action="content_rejected",
        entity_type="content_item",
        entity_id=str(content_id),
        details={"title": item.title, "version": item.current_version, "revision_notes": revision_notes},
    )
    db.add(audit)

    await db.commit()
    await db.refresh(item)

    return ContentItemResponse.model_validate(item)


@router.get("/{content_id}/versions", response_model=list[ContentVersionResponse])
async def list_content_versions(
    content_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """List all versions of a content item."""
    # Verify content item exists
    item_result = await db.execute(
        select(ContentItem).where(ContentItem.id == content_id)
    )
    if not item_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Content item not found")

    result = await db.execute(
        select(ContentVersion)
        .where(ContentVersion.content_item_id == content_id)
        .order_by(desc(ContentVersion.version_number))
    )
    versions = result.scalars().all()

    return [ContentVersionResponse.model_validate(v) for v in versions]


@router.get("/{content_id}/versions/{version_number}", response_model=ContentVersionResponse)
async def get_content_version(
    content_id: UUID,
    version_number: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific version of a content item."""
    result = await db.execute(
        select(ContentVersion)
        .where(ContentVersion.content_item_id == content_id)
        .where(ContentVersion.version_number == version_number)
    )
    version = result.scalar_one_or_none()
    if not version:
        raise HTTPException(status_code=404, detail="Content version not found")

    return ContentVersionResponse.model_validate(version)


@router.post("/{content_id}/clone", status_code=status.HTTP_201_CREATED, response_model=ContentItemResponse)
async def clone_content(
    content_id: UUID,
    new_title: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Clone/duplicate a content item with its brief.
    Creates a new content item in draft status with the same brief data.
    Useful for creating variations or reusing brief templates.
    """
    # Load source content
    result = await db.execute(
        select(ContentItem).where(ContentItem.id == content_id)
    )
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Content item not found")

    # Create clone
    clone = ContentItem(
        campaign_id=source.campaign_id,
        title=new_title or f"{source.title} (Copy)",
        content_type=source.content_type,
        language=source.language,
        brief=source.brief,  # Clone the brief
        tags=source.tags,
        status=ContentStatus.DRAFT,
        current_version=0,
    )
    db.add(clone)
    await db.commit()
    await db.refresh(clone)

    return ContentItemResponse.model_validate(clone)
