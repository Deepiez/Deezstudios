"""Brand CRUD API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from uuid import UUID

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.brand import Brand
from app.schemas.brand import BrandCreate, BrandUpdate, BrandResponse

router = APIRouter()


@router.get("/", response_model=list[BrandResponse])
async def list_brands(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all brands for the current user."""
    result = await db.execute(
        select(Brand)
        .where(Brand.user_id == current_user.id)
        .order_by(desc(Brand.updated_at))
    )
    brands = result.scalars().all()
    return [BrandResponse.model_validate(b) for b in brands]


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=BrandResponse)
async def create_brand(
    data: BrandCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new brand."""
    brand = Brand(
        user_id=current_user.id,
        name=data.name,
        description=data.description,
        niche=data.niche,
        target_audience=data.target_audience,
    )
    db.add(brand)
    await db.commit()
    await db.refresh(brand)
    return BrandResponse.model_validate(brand)


@router.get("/{brand_id}", response_model=BrandResponse)
async def get_brand(
    brand_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get brand by ID."""
    result = await db.execute(
        select(Brand).where(Brand.id == brand_id, Brand.user_id == current_user.id)
    )
    brand = result.scalar_one_or_none()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return BrandResponse.model_validate(brand)


@router.put("/{brand_id}", response_model=BrandResponse)
async def update_brand(
    brand_id: UUID,
    data: BrandUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update brand."""
    result = await db.execute(
        select(Brand).where(Brand.id == brand_id, Brand.user_id == current_user.id)
    )
    brand = result.scalar_one_or_none()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(brand, field, value)

    await db.commit()
    await db.refresh(brand)
    return BrandResponse.model_validate(brand)


@router.delete("/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_brand(
    brand_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete brand."""
    result = await db.execute(
        select(Brand).where(Brand.id == brand_id, Brand.user_id == current_user.id)
    )
    brand = result.scalar_one_or_none()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    await db.delete(brand)
    await db.commit()
