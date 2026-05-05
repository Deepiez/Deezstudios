"""
YouTube Integration Service
Handles OAuth 2.0 flow, token management, video upload, and scheduled publishing.
Uses YouTube Data API v3.
"""

import uuid
import json
import time
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import urlencode

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.models.platform import PlatformAccount, OAuthToken, PlatformType
from app.models.publish import PublishJob, PublishJobStatus, PublishLog
from app.models.content import ContentItem, ContentVersion, ContentStatus

# YouTube OAuth 2.0 endpoints
YOUTUBE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
YOUTUBE_TOKEN_URL = "https://oauth2.googleapis.com/token"
YOUTUBE_REVOKE_URL = "https://oauth2.googleapis.com/revoke"
YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"
YOUTUBE_UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos"

# Required scopes for upload and publish
YOUTUBE_SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.readonly",
]


class YouTubeService:
    """Service for YouTube OAuth and API operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.client_id = settings.YOUTUBE_CLIENT_ID
        self.client_secret = settings.YOUTUBE_CLIENT_SECRET
        self.redirect_uri = settings.YOUTUBE_REDIRECT_URI

    def is_configured(self) -> bool:
        """Check if YouTube OAuth credentials are configured."""
        return bool(self.client_id and self.client_secret)

    # =========================================================================
    # OAuth 2.0 Flow
    # =========================================================================

    def get_auth_url(self, brand_id: str) -> str:
        """
        Generate YouTube OAuth 2.0 authorization URL.
        State parameter contains brand_id for callback routing.
        """
        if not self.is_configured():
            raise ValueError("YouTube OAuth not configured. Set YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET.")

        state = json.dumps({"brand_id": brand_id})

        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(YOUTUBE_SCOPES),
            "access_type": "offline",  # Get refresh token
            "prompt": "consent",  # Always show consent to get refresh token
            "state": state,
        }

        return f"{YOUTUBE_AUTH_URL}?{urlencode(params)}"

    async def handle_callback(self, code: str, state: str) -> dict:
        """
        Handle OAuth callback - exchange code for tokens and save.

        Returns:
            dict with platform_account info
        """
        # Parse state
        try:
            state_data = json.loads(state)
            brand_id = state_data["brand_id"]
        except (json.JSONDecodeError, KeyError):
            raise ValueError("Invalid state parameter")

        # Exchange code for tokens
        token_data = await self._exchange_code(code)

        if "error" in token_data:
            raise ValueError(f"Token exchange failed: {token_data.get('error_description', token_data['error'])}")

        access_token = token_data["access_token"]
        refresh_token = token_data.get("refresh_token")
        expires_in = token_data.get("expires_in", 3600)
        scope = token_data.get("scope", "")

        # Get channel info
        channel_info = await self._get_channel_info(access_token)

        # Create or update platform account
        platform_account = await self._upsert_platform_account(
            brand_id=uuid.UUID(brand_id),
            channel_info=channel_info,
        )

        # Save tokens
        await self._save_tokens(
            platform_account_id=platform_account.id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
            scope=scope,
        )

        await self.db.commit()

        return {
            "platform_account_id": str(platform_account.id),
            "account_name": platform_account.account_name,
            "channel_id": platform_account.account_id,
            "connected": True,
        }

    async def disconnect(self, platform_account_id: uuid.UUID) -> bool:
        """Disconnect YouTube account and revoke tokens."""
        result = await self.db.execute(
            select(PlatformAccount).where(PlatformAccount.id == platform_account_id)
        )
        account = result.scalar_one_or_none()
        if not account:
            return False

        # Revoke token if possible
        token_result = await self.db.execute(
            select(OAuthToken)
            .where(OAuthToken.platform_account_id == platform_account_id)
            .order_by(OAuthToken.created_at.desc())
            .limit(1)
        )
        token = token_result.scalar_one_or_none()
        if token:
            await self._revoke_token(token.access_token)

        # Mark as disconnected
        account.is_connected = False
        await self.db.commit()
        return True

    # =========================================================================
    # Token Management
    # =========================================================================

    async def get_valid_token(self, platform_account_id: uuid.UUID) -> Optional[str]:
        """Get a valid access token (decrypted), refreshing if expired."""
        from app.core.encryption import decrypt_token, encrypt_token

        result = await self.db.execute(
            select(OAuthToken)
            .where(OAuthToken.platform_account_id == platform_account_id)
            .order_by(OAuthToken.created_at.desc())
            .limit(1)
        )
        token = result.scalar_one_or_none()
        if not token:
            return None

        # Check if expired
        if token.expires_at and token.expires_at <= datetime.utcnow():
            # Refresh using decrypted refresh token
            if token.refresh_token:
                decrypted_refresh = decrypt_token(token.refresh_token)
                new_token_data = await self._refresh_access_token(decrypted_refresh)
                if "access_token" in new_token_data:
                    new_access = new_token_data["access_token"]
                    token.access_token = encrypt_token(new_access)
                    token.expires_at = datetime.utcnow() + timedelta(
                        seconds=new_token_data.get("expires_in", 3600)
                    )
                    token.updated_at = datetime.utcnow()
                    await self.db.commit()
                    return new_access
                else:
                    return None
            return None

        return decrypt_token(token.access_token)

    # =========================================================================
    # Video Upload & Publish
    # =========================================================================

    async def upload_video(
        self,
        platform_account_id: uuid.UUID,
        video_path: str,
        title: str,
        description: str,
        tags: list[str] = None,
        privacy_status: str = "private",
        publish_at: Optional[datetime] = None,
        category_id: str = "22",  # People & Blogs
    ) -> dict:
        """
        Upload a video to YouTube.

        Args:
            platform_account_id: Platform account with valid OAuth
            video_path: Path to video file
            title: Video title
            description: Video description
            tags: List of tags
            privacy_status: 'private', 'public', 'unlisted'
            publish_at: If set with privacy='private', schedules the video
            category_id: YouTube category ID

        Returns:
            dict with video_id, url, status
        """
        access_token = await self.get_valid_token(platform_account_id)
        if not access_token:
            return {"success": False, "error": "No valid access token. Reconnect YouTube."}

        # Build video metadata
        body = {
            "snippet": {
                "title": title[:100],  # YouTube max 100 chars
                "description": description[:5000],  # YouTube max 5000 chars
                "tags": (tags or [])[:500],
                "categoryId": category_id,
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": False,
            },
        }

        # Scheduled publish: set to private with publishAt
        if publish_at and privacy_status == "private":
            body["status"]["publishAt"] = publish_at.strftime("%Y-%m-%dT%H:%M:%S.000Z")

        try:
            async with httpx.AsyncClient(timeout=300) as client:
                # Step 1: Initialize resumable upload
                init_response = await client.post(
                    f"{YOUTUBE_UPLOAD_URL}?uploadType=resumable&part=snippet,status",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                    },
                    json=body,
                )

                if init_response.status_code != 200:
                    return {
                        "success": False,
                        "error": f"Upload init failed: {init_response.status_code} - {init_response.text}",
                    }

                upload_url = init_response.headers.get("Location")
                if not upload_url:
                    return {"success": False, "error": "No upload URL returned"}

                # Step 2: Upload video file
                with open(video_path, "rb") as video_file:
                    video_data = video_file.read()

                upload_response = await client.put(
                    upload_url,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "video/*",
                        "Content-Length": str(len(video_data)),
                    },
                    content=video_data,
                )

                if upload_response.status_code in [200, 201]:
                    video_data = upload_response.json()
                    video_id = video_data.get("id")
                    return {
                        "success": True,
                        "video_id": video_id,
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                        "status": video_data.get("status", {}).get("uploadStatus"),
                        "privacy": video_data.get("status", {}).get("privacyStatus"),
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Upload failed: {upload_response.status_code} - {upload_response.text}",
                    }

        except Exception as e:
            return {"success": False, "error": f"Upload exception: {str(e)}"}

    async def set_video_metadata(
        self,
        platform_account_id: uuid.UUID,
        video_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[list[str]] = None,
        privacy_status: Optional[str] = None,
        publish_at: Optional[datetime] = None,
    ) -> dict:
        """Update metadata for an existing video."""
        access_token = await self.get_valid_token(platform_account_id)
        if not access_token:
            return {"success": False, "error": "No valid access token"}

        # Get current video data
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{YOUTUBE_API_BASE}/videos",
                params={"part": "snippet,status", "id": video_id},
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if response.status_code != 200:
                return {"success": False, "error": f"Failed to get video: {response.text}"}

            items = response.json().get("items", [])
            if not items:
                return {"success": False, "error": "Video not found"}

            video = items[0]

            # Update fields
            if title:
                video["snippet"]["title"] = title[:100]
            if description:
                video["snippet"]["description"] = description[:5000]
            if tags:
                video["snippet"]["tags"] = tags[:500]
            if privacy_status:
                video["status"]["privacyStatus"] = privacy_status
            if publish_at:
                video["status"]["publishAt"] = publish_at.strftime("%Y-%m-%dT%H:%M:%S.000Z")

            # Update
            update_response = await client.put(
                f"{YOUTUBE_API_BASE}/videos",
                params={"part": "snippet,status"},
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                json=video,
            )

            if update_response.status_code == 200:
                return {"success": True, "video_id": video_id}
            else:
                return {"success": False, "error": f"Update failed: {update_response.text}"}

    async def get_channel_details(self, platform_account_id: uuid.UUID) -> Optional[dict]:
        """Get channel details for a connected account."""
        access_token = await self.get_valid_token(platform_account_id)
        if not access_token:
            return None
        return await self._get_channel_info(access_token)

    # =========================================================================
    # Private Helpers
    # =========================================================================

    async def _exchange_code(self, code: str) -> dict:
        """Exchange authorization code for tokens."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                YOUTUBE_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uri": self.redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            return response.json()

    async def _refresh_access_token(self, refresh_token: str) -> dict:
        """Refresh an expired access token."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                YOUTUBE_TOKEN_URL,
                data={
                    "refresh_token": refresh_token,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "refresh_token",
                },
            )
            return response.json()

    async def _revoke_token(self, token: str):
        """Revoke an OAuth token."""
        try:
            async with httpx.AsyncClient() as client:
                await client.post(YOUTUBE_REVOKE_URL, params={"token": token})
        except Exception:
            pass  # Best effort revocation

    async def _get_channel_info(self, access_token: str) -> dict:
        """Get YouTube channel info for the authenticated user."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{YOUTUBE_API_BASE}/channels",
                params={"part": "snippet,statistics", "mine": "true"},
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if response.status_code != 200:
                return {"error": f"Failed to get channel: {response.text}"}

            data = response.json()
            items = data.get("items", [])
            if not items:
                return {"error": "No channel found"}

            channel = items[0]
            return {
                "channel_id": channel["id"],
                "title": channel["snippet"]["title"],
                "description": channel["snippet"].get("description", ""),
                "thumbnail": channel["snippet"].get("thumbnails", {}).get("default", {}).get("url"),
                "subscriber_count": channel.get("statistics", {}).get("subscriberCount"),
                "video_count": channel.get("statistics", {}).get("videoCount"),
            }

    async def _upsert_platform_account(self, brand_id: uuid.UUID, channel_info: dict) -> PlatformAccount:
        """Create or update platform account for YouTube channel."""
        channel_id = channel_info.get("channel_id", "")

        # Check if account already exists
        result = await self.db.execute(
            select(PlatformAccount).where(
                PlatformAccount.brand_id == brand_id,
                PlatformAccount.platform == PlatformType.YOUTUBE,
                PlatformAccount.account_id == channel_id,
            )
        )
        account = result.scalar_one_or_none()

        if account:
            account.is_connected = True
            account.connected_at = datetime.utcnow()
            account.account_name = channel_info.get("title", account.account_name)
            account.metadata_json = channel_info
        else:
            account = PlatformAccount(
                brand_id=brand_id,
                platform=PlatformType.YOUTUBE,
                account_name=channel_info.get("title", "YouTube Channel"),
                account_id=channel_id,
                is_connected=True,
                is_active=True,
                connected_at=datetime.utcnow(),
                metadata_json=channel_info,
            )
            self.db.add(account)

        await self.db.flush()
        return account

    async def _save_tokens(
        self,
        platform_account_id: uuid.UUID,
        access_token: str,
        refresh_token: Optional[str],
        expires_in: int,
        scope: str,
    ):
        """Save OAuth tokens to database (encrypted at rest)."""
        from app.core.encryption import encrypt_token

        token = OAuthToken(
            platform_account_id=platform_account_id,
            access_token=encrypt_token(access_token),
            refresh_token=encrypt_token(refresh_token) if refresh_token else None,
            token_type="Bearer",
            scope=scope,
            expires_at=datetime.utcnow() + timedelta(seconds=expires_in),
        )
        self.db.add(token)
