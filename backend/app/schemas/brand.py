"""Pydantic schemas for brands and campaigns."""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime, date


# === Brand ===

class BrandCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    niche: Optional[str] = Field(default=None, max_length=100)
    target_audience: Optional[str] = None


class BrandUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    description: Optional[str] = None
    niche: Optional[str] = None
    target_audience: Optional[str] = None


class BrandResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    niche: Optional[str] = None
    target_audience: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# === Campaign ===

class CampaignCreate(BaseModel):
    brand_id: UUID
    name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    objective: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class CampaignUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=200)
    description: Optional[str] = None
    objective: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class CampaignResponse(BaseModel):
    id: UUID
    brand_id: UUID
    name: str
    description: Optional[str] = None
    objective: Optional[str] = None
    status: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
