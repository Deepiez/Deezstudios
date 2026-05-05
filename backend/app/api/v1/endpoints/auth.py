"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.config import settings
from app.core.security import verify_password, hash_password, create_access_token
from app.core.deps import get_current_user
from app.models.user import User
from app.models.audit import AuditLog
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse, ChangePasswordRequest

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate user with username and password.
    Returns JWT access token.
    """
    # Find user
    result = await db.execute(
        select(User).where(User.username == form_data.username)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        # Log failed attempt
        audit = AuditLog(
            action="login_failed",
            entity_type="user",
            details={"username": form_data.username},
        )
        db.add(audit)
        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )

    # Create token
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    # Update last login
    user.last_login = datetime.utcnow()

    # Audit log
    audit = AuditLog(
        user_id=user.id,
        action="login_success",
        entity_type="user",
        entity_id=str(user.id),
    )
    db.add(audit)
    await db.commit()

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/login/json", response_model=TokenResponse)
async def login_json(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    JSON-based login (alternative to form-based).
    Useful for frontend API calls.
    """
    result = await db.execute(
        select(User).where(User.username == data.username)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is disabled")

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    user.last_login = datetime.utcnow()
    await db.commit()

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """Get current authenticated user info."""
    return UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        is_active=current_user.is_active,
        last_login=current_user.last_login,
        created_at=current_user.created_at,
    )


@router.post("/change-password")
async def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Change current user's password."""
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    current_user.hashed_password = hash_password(data.new_password)

    audit = AuditLog(
        user_id=current_user.id,
        action="password_changed",
        entity_type="user",
        entity_id=str(current_user.id),
    )
    db.add(audit)
    await db.commit()

    return {"message": "Password changed successfully"}


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout current user.
    Note: With JWT, logout is handled client-side by removing the token.
    This endpoint exists for audit logging purposes.
    """
    return {"message": "Logged out successfully"}
