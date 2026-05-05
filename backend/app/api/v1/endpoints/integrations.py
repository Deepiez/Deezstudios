"""Platform Integration API endpoints - YouTube OAuth, account management."""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.core.database import get_db
from app.models.platform import PlatformAccount, PlatformType
from app.services.integrations.youtube import YouTubeService

router = APIRouter()


# =============================================================================
# Platform Accounts
# =============================================================================

@router.get("/accounts")
async def list_platform_accounts(
    brand_id: UUID = None,
    db: AsyncSession = Depends(get_db),
):
    """List all connected platform accounts."""
    query = select(PlatformAccount).where(PlatformAccount.is_active == True)
    if brand_id:
        query = query.where(PlatformAccount.brand_id == brand_id)

    result = await db.execute(query)
    accounts = result.scalars().all()

    return [
        {
            "id": str(a.id),
            "brand_id": str(a.brand_id),
            "platform": a.platform.value,
            "account_name": a.account_name,
            "account_id": a.account_id,
            "is_connected": a.is_connected,
            "connected_at": a.connected_at.isoformat() if a.connected_at else None,
            "metadata": a.metadata_json,
        }
        for a in accounts
    ]


# =============================================================================
# YouTube Integration
# =============================================================================

@router.get("/youtube/connect")
async def youtube_connect(
    brand_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Initiate YouTube OAuth 2.0 flow.
    Returns the authorization URL to redirect the user to.
    """
    service = YouTubeService(db)

    if not service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="YouTube OAuth not configured. Set YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET in .env",
        )

    auth_url = service.get_auth_url(str(brand_id))

    return {
        "auth_url": auth_url,
        "message": "Redirect user to auth_url to authorize YouTube access",
    }


@router.get("/youtube/callback")
async def youtube_callback(
    code: str = None,
    error: str = None,
    state: str = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Handle YouTube OAuth 2.0 callback.
    Exchanges authorization code for tokens and saves the connection.
    """
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"YouTube authorization denied: {error}",
        )

    if not code or not state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing code or state parameter",
        )

    service = YouTubeService(db)

    try:
        result = await service.handle_callback(code, state)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return {
        "success": True,
        "platform_account_id": result["platform_account_id"],
        "account_name": result["account_name"],
        "channel_id": result["channel_id"],
        "message": "YouTube connected successfully!",
    }


@router.post("/youtube/disconnect/{account_id}")
async def youtube_disconnect(
    account_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Disconnect YouTube account and revoke tokens."""
    service = YouTubeService(db)
    success = await service.disconnect(account_id)

    if not success:
        raise HTTPException(status_code=404, detail="Platform account not found")

    return {"success": True, "message": "YouTube disconnected"}


@router.get("/youtube/channel/{account_id}")
async def youtube_channel_info(
    account_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get YouTube channel info for a connected account."""
    service = YouTubeService(db)
    info = await service.get_channel_details(account_id)

    if not info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cannot access YouTube. Token may be expired. Try reconnecting.",
        )

    if "error" in info:
        raise HTTPException(status_code=400, detail=info["error"])

    return info


@router.get("/youtube/status")
async def youtube_status(db: AsyncSession = Depends(get_db)):
    """Check YouTube integration status (configured, connected accounts)."""
    service = YouTubeService(db)

    # Get all YouTube accounts
    result = await db.execute(
        select(PlatformAccount).where(
            PlatformAccount.platform == PlatformType.YOUTUBE,
            PlatformAccount.is_active == True,
        )
    )
    accounts = result.scalars().all()

    return {
        "configured": service.is_configured(),
        "connected_accounts": [
            {
                "id": str(a.id),
                "account_name": a.account_name,
                "channel_id": a.account_id,
                "is_connected": a.is_connected,
                "connected_at": a.connected_at.isoformat() if a.connected_at else None,
            }
            for a in accounts
        ],
        "total_connected": sum(1 for a in accounts if a.is_connected),
    }


# =============================================================================
# TikTok (Coming Soon)
# =============================================================================

@router.get("/tiktok/status")
async def tiktok_status():
    """TikTok integration status - coming soon."""
    return {
        "configured": False,
        "status": "coming_soon",
        "message": "TikTok autopost integration akan tersedia setelah validasi API.",
    }


# =============================================================================
# X / Twitter (Coming Soon)
# =============================================================================

@router.get("/x/status")
async def x_status():
    """X integration status - coming soon."""
    return {
        "configured": False,
        "status": "coming_soon",
        "message": "X autopost integration akan tersedia setelah validasi API dan biaya.",
    }
