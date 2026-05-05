"""Pydantic schemas for authentication."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class UserResponse(BaseModel):
    id: str
    username: str
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)
