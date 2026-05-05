"""Campaign CRUD API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from uuid import UUID
from typing import Optional

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.brand import Brand
from app.models.campaign import Campaign, CampaignStatus
from app.schemas.brand import CampaignCreate, CampaignUpdate, CampaignResponse

router = APIRouter()


@router.get("/", response_model=list[CampaignResponse])
async def list_campaigns(
    brand_id: Optional[UUID] = None,
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List campaigns, optionally filtered by brand or status."""
    query = (
        select(Campaign)
        .join(Brand, Campaign.brand_id == Brand.id)
        .where(Brand.user_id == current_user.id)
        .order_by(desc(Campaign.updated_at))
    )

    if brand_id:
        query = query.where(Campaign.brand_id == brand_id)
    if status_filter:
        query = query.where(Campaign.status == status_filter)

    result = await db.execute(query)
    campaigns = result.scalars().all()
    return [CampaignResponse.model_validate(c) for c in campaigns]


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CampaignResponse)
async def create_campaign(
    data: CampaignCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new campaign."""
    # Verify brand belongs to user
    brand_result = await db.execute(
        select(Brand).where(Brand.id == data.brand_id, Brand.user_id == current_user.id)
    )
    if not brand_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Brand not found")

    campaign = Campaign(
        brand_id=data.brand_id,
        name=data.name,
        description=data.description,
        objective=data.objective,
        start_date=data.start_date,
        end_date=data.end_date,
        status=CampaignStatus.PLANNING,
    )
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return CampaignResponse.model_validate(campaign)


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get campaign by ID."""
    result = await db.execute(
        select(Campaign)
        .join(Brand, Campaign.brand_id == Brand.id)
        .where(Campaign.id == campaign_id, Brand.user_id == current_user.id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return CampaignResponse.model_validate(campaign)


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: UUID,
    data: CampaignUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update campaign."""
    result = await db.execute(
        select(Campaign)
        .join(Brand, Campaign.brand_id == Brand.id)
        .where(Campaign.id == campaign_id, Brand.user_id == current_user.id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    update_data = data.model_dump(exclude_unset=True)

    # Handle status enum conversion
    if "status" in update_data and update_data["status"]:
        update_data["status"] = CampaignStatus(update_data["status"])

    for field, value in update_data.items():
        setattr(campaign, field, value)

    await db.commit()
    await db.refresh(campaign)
    return CampaignResponse.model_validate(campaign)


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete campaign."""
    result = await db.execute(
        select(Campaign)
        .join(Brand, Campaign.brand_id == Brand.id)
        .where(Campaign.id == campaign_id, Brand.user_id == current_user.id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    await db.delete(campaign)
    await db.commit()
