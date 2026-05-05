"""Style Guide and CTA Pattern CRUD API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from uuid import UUID
from typing import Optional

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.style_guide import StyleGuide, CTAPattern
from app.schemas.style_guide import (
    StyleGuideCreate, StyleGuideUpdate, StyleGuideResponse,
    CTAPatternCreate, CTAPatternUpdate, CTAPatternResponse,
)

router = APIRouter()


# =============================================================================
# Style Guides
# =============================================================================

@router.get("/", response_model=list[StyleGuideResponse])
async def list_style_guides(
    brand_id: Optional[UUID] = None,
    campaign_id: Optional[UUID] = None,
    active_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List style guides, optionally filtered by brand or campaign."""
    query = select(StyleGuide).order_by(desc(StyleGuide.updated_at))

    if brand_id:
        query = query.where(StyleGuide.brand_id == brand_id)
    if campaign_id:
        query = query.where(StyleGuide.campaign_id == campaign_id)
    if active_only:
        query = query.where(StyleGuide.is_active == True)

    result = await db.execute(query)
    guides = result.scalars().all()
    return [StyleGuideResponse.model_validate(g) for g in guides]


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=StyleGuideResponse)
async def create_style_guide(
    data: StyleGuideCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new style guide."""
    guide = StyleGuide(
        brand_id=data.brand_id,
        campaign_id=data.campaign_id,
        name=data.name,
        is_active=True,
        tone_of_voice=data.tone_of_voice,
        writing_rules=data.writing_rules,
        preferred_phrases=data.preferred_phrases,
        banned_phrases=data.banned_phrases,
        brand_examples=data.brand_examples,
        additional_notes=data.additional_notes,
    )
    db.add(guide)
    await db.commit()
    await db.refresh(guide)
    return StyleGuideResponse.model_validate(guide)


@router.get("/{guide_id}", response_model=StyleGuideResponse)
async def get_style_guide(
    guide_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get style guide by ID."""
    result = await db.execute(select(StyleGuide).where(StyleGuide.id == guide_id))
    guide = result.scalar_one_or_none()
    if not guide:
        raise HTTPException(status_code=404, detail="Style guide not found")
    return StyleGuideResponse.model_validate(guide)


@router.put("/{guide_id}", response_model=StyleGuideResponse)
async def update_style_guide(
    guide_id: UUID,
    data: StyleGuideUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a style guide."""
    result = await db.execute(select(StyleGuide).where(StyleGuide.id == guide_id))
    guide = result.scalar_one_or_none()
    if not guide:
        raise HTTPException(status_code=404, detail="Style guide not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(guide, field, value)

    await db.commit()
    await db.refresh(guide)
    return StyleGuideResponse.model_validate(guide)


@router.patch("/{guide_id}/toggle")
async def toggle_style_guide(
    guide_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Toggle style guide active/inactive."""
    result = await db.execute(select(StyleGuide).where(StyleGuide.id == guide_id))
    guide = result.scalar_one_or_none()
    if not guide:
        raise HTTPException(status_code=404, detail="Style guide not found")

    guide.is_active = not guide.is_active
    await db.commit()
    return {"id": str(guide.id), "is_active": guide.is_active}


@router.delete("/{guide_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_style_guide(
    guide_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a style guide."""
    result = await db.execute(select(StyleGuide).where(StyleGuide.id == guide_id))
    guide = result.scalar_one_or_none()
    if not guide:
        raise HTTPException(status_code=404, detail="Style guide not found")
    await db.delete(guide)
    await db.commit()


# =============================================================================
# CTA Patterns
# =============================================================================

@router.get("/cta-patterns", response_model=list[CTAPatternResponse])
async def list_cta_patterns(
    brand_id: Optional[UUID] = None,
    campaign_id: Optional[UUID] = None,
    platform: Optional[str] = None,
    active_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List CTA patterns with optional filters."""
    query = select(CTAPattern).order_by(desc(CTAPattern.updated_at))

    if brand_id:
        query = query.where(CTAPattern.brand_id == brand_id)
    if campaign_id:
        query = query.where(CTAPattern.campaign_id == campaign_id)
    if platform:
        query = query.where(
            (CTAPattern.platform_target == platform) | (CTAPattern.platform_target == None)
        )
    if active_only:
        query = query.where(CTAPattern.is_active == True)

    result = await db.execute(query)
    patterns = result.scalars().all()
    return [CTAPatternResponse.model_validate(p) for p in patterns]


@router.post("/cta-patterns", status_code=status.HTTP_201_CREATED, response_model=CTAPatternResponse)
async def create_cta_pattern(
    data: CTAPatternCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new CTA pattern."""
    pattern = CTAPattern(
        brand_id=data.brand_id,
        campaign_id=data.campaign_id,
        name=data.name,
        is_active=True,
        cta_text=data.cta_text,
        cta_type=data.cta_type,
        placement=data.placement,
        platform_target=data.platform_target,
    )
    db.add(pattern)
    await db.commit()
    await db.refresh(pattern)
    return CTAPatternResponse.model_validate(pattern)


@router.get("/cta-patterns/{pattern_id}", response_model=CTAPatternResponse)
async def get_cta_pattern(
    pattern_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get CTA pattern by ID."""
    result = await db.execute(select(CTAPattern).where(CTAPattern.id == pattern_id))
    pattern = result.scalar_one_or_none()
    if not pattern:
        raise HTTPException(status_code=404, detail="CTA pattern not found")
    return CTAPatternResponse.model_validate(pattern)


@router.put("/cta-patterns/{pattern_id}", response_model=CTAPatternResponse)
async def update_cta_pattern(
    pattern_id: UUID,
    data: CTAPatternUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a CTA pattern."""
    result = await db.execute(select(CTAPattern).where(CTAPattern.id == pattern_id))
    pattern = result.scalar_one_or_none()
    if not pattern:
        raise HTTPException(status_code=404, detail="CTA pattern not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(pattern, field, value)

    await db.commit()
    await db.refresh(pattern)
    return CTAPatternResponse.model_validate(pattern)


@router.patch("/cta-patterns/{pattern_id}/toggle")
async def toggle_cta_pattern(
    pattern_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Toggle CTA pattern active/inactive."""
    result = await db.execute(select(CTAPattern).where(CTAPattern.id == pattern_id))
    pattern = result.scalar_one_or_none()
    if not pattern:
        raise HTTPException(status_code=404, detail="CTA pattern not found")

    pattern.is_active = not pattern.is_active
    await db.commit()
    return {"id": str(pattern.id), "is_active": pattern.is_active}


@router.delete("/cta-patterns/{pattern_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cta_pattern(
    pattern_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a CTA pattern."""
    result = await db.execute(select(CTAPattern).where(CTAPattern.id == pattern_id))
    pattern = result.scalar_one_or_none()
    if not pattern:
        raise HTTPException(status_code=404, detail="CTA pattern not found")
    await db.delete(pattern)
    await db.commit()
