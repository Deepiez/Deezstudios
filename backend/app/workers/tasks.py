"""
Celery tasks for background processing.
These tasks handle async operations like content generation,
scheduled publishing, and analytics aggregation.
"""

import asyncio
from datetime import datetime, date, timedelta
from uuid import UUID
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session

from app.workers.celery_app import celery_app
from app.core.config import settings
from app.models.content import ContentItem, ContentStatus
from app.models.generation import GenerationRun, GenerationStatus, AIProvider
from app.models.publish import PublishJob, PublishJobStatus, PublishLog
from app.models.analytics import AnalyticsDailySnapshot

# Sync engine for Celery tasks (Celery doesn't support async natively)
sync_engine = create_engine(settings.DATABASE_URL_SYNC)


@celery_app.task(name="app.workers.tasks.run_content_generation_async")
def run_content_generation_async(
    content_item_id: str,
    provider: str,
    model: str,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    fallback_provider: str = None,
    custom_instructions: str = None,
) -> dict:
    """
    Background task: Run AI content generation.

    Use this for long-running generations or when you want
    non-blocking generation (e.g., batch generation).

    Returns dict with generation result summary.
    """
    from app.services.generation.prompt_builder import build_generation_prompt
    from app.services.generation.output_parser import parse_generation_output
    from app.services.ai_providers.base import GenerationRequest
    from app.services.ai_providers.provider_manager import provider_manager
    from app.models.content import ContentVersion

    with Session(sync_engine) as db:
        # Load content item
        content_item = db.execute(
            select(ContentItem).where(ContentItem.id == UUID(content_item_id))
        ).scalar_one_or_none()

        if not content_item:
            return {"success": False, "error": "Content item not found"}

        if not content_item.brief:
            return {"success": False, "error": "No brief attached"}

        # Build prompts (simplified - no style guide loading in sync context)
        try:
            system_prompt, user_prompt = build_generation_prompt(
                content_type=content_item.content_type.value,
                brief=content_item.brief,
                style_guides=[],
                cta_patterns=[],
            )
        except ValueError as e:
            return {"success": False, "error": str(e)}

        if custom_instructions:
            user_prompt += f"\n\n## INSTRUKSI TAMBAHAN\n{custom_instructions}"

        # Create generation run
        generation_run = GenerationRun(
            content_item_id=UUID(content_item_id),
            provider=AIProvider(provider),
            model=model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            parameters={
                "temperature": temperature,
                "max_tokens": max_tokens,
                "fallback_provider": fallback_provider,
            },
            status=GenerationStatus.RUNNING,
            started_at=datetime.utcnow(),
        )
        db.add(generation_run)
        db.flush()

        # Call AI provider (run async in sync context)
        request = GenerationRequest(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response = loop.run_until_complete(
                provider_manager.generate(
                    provider_name=provider,
                    request=request,
                    fallback_provider=fallback_provider,
                )
            )
        finally:
            loop.close()

        # Update generation run
        generation_run.completed_at = datetime.utcnow()
        generation_run.latency_ms = response.latency_ms
        generation_run.input_tokens = response.input_tokens
        generation_run.output_tokens = response.output_tokens
        generation_run.cost_usd = response.cost_usd

        if not response.success:
            generation_run.status = GenerationStatus.FAILED
            generation_run.error_message = response.error
            db.commit()
            return {
                "success": False,
                "error": response.error,
                "generation_run_id": str(generation_run.id),
            }

        # Parse output
        parsed_content, parse_error = parse_generation_output(
            response.content, content_item.content_type.value
        )

        if parsed_content is None:
            generation_run.status = GenerationStatus.FAILED
            generation_run.error_message = f"Parse failed: {parse_error}"
            db.commit()
            return {
                "success": False,
                "error": f"Output parsing failed: {parse_error}",
                "generation_run_id": str(generation_run.id),
            }

        # Success - create version
        generation_run.status = GenerationStatus.COMPLETED
        generation_run.output_data = parsed_content

        new_version_number = content_item.current_version + 1
        content_version = ContentVersion(
            content_item_id=UUID(content_item_id),
            version_number=new_version_number,
            content_data=parsed_content,
            generation_run_id=generation_run.id,
        )
        db.add(content_version)
        content_item.current_version = new_version_number

        db.commit()

        return {
            "success": True,
            "generation_run_id": str(generation_run.id),
            "content_version_id": str(content_version.id),
            "version_number": new_version_number,
            "metrics": {
                "provider": provider,
                "model": response.model,
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
                "latency_ms": response.latency_ms,
                "cost_usd": response.cost_usd,
            },
        }


@celery_app.task(name="app.workers.tasks.process_scheduled_publishes")
def process_scheduled_publishes():
    """
    Periodic task: Check for publish jobs that are due and process them.
    Runs every minute via Celery Beat.
    """
    with Session(sync_engine) as db:
        now = datetime.utcnow()

        # Find queued jobs that are due
        due_jobs = db.execute(
            select(PublishJob).where(
                PublishJob.status == PublishJobStatus.QUEUED,
                PublishJob.scheduled_publish_at <= now,
            )
        ).scalars().all()

        for job in due_jobs:
            # Mark as processing
            job.status = PublishJobStatus.PROCESSING
            job.started_at = datetime.utcnow()
            db.flush()

            # Log
            log = PublishLog(
                publish_job_id=job.id,
                level="info",
                message=f"Starting publish job for content {job.content_item_id}",
            )
            db.add(log)

            # Dispatch to platform-specific task
            # TODO: Route to youtube/tiktok/x publish tasks
            # For now, just log that it would be processed
            log2 = PublishLog(
                publish_job_id=job.id,
                level="info",
                message="Publish task dispatched (platform integration pending)",
            )
            db.add(log2)

        db.commit()
        return {"processed": len(due_jobs)}


@celery_app.task(name="app.workers.tasks.generate_daily_analytics")
def generate_daily_analytics():
    """
    Periodic task: Generate daily analytics snapshot.
    Aggregates content counts, generation metrics, and publish stats.
    """
    with Session(sync_engine) as db:
        today = date.today()

        # Check if snapshot already exists
        existing = db.execute(
            select(AnalyticsDailySnapshot).where(
                AnalyticsDailySnapshot.snapshot_date == today
            )
        ).scalar_one_or_none()

        if existing:
            snapshot = existing
        else:
            snapshot = AnalyticsDailySnapshot(snapshot_date=today)
            db.add(snapshot)

        # Count content by status
        for status_val in ContentStatus:
            count = db.execute(
                select(func.count(ContentItem.id)).where(
                    ContentItem.status == status_val
                )
            ).scalar() or 0

            field_map = {
                ContentStatus.DRAFT: "total_drafts",
                ContentStatus.IN_REVIEW: "total_in_review",
                ContentStatus.APPROVED: "total_approved",
                ContentStatus.SCHEDULED: "total_scheduled",
                ContentStatus.PUBLISHED: "total_published",
                ContentStatus.FAILED: "total_failed",
            }
            field = field_map.get(status_val)
            if field:
                setattr(snapshot, field, count)

        # Generation metrics
        gen_count = db.execute(
            select(func.count(GenerationRun.id)).where(
                GenerationRun.status == GenerationStatus.COMPLETED
            )
        ).scalar() or 0
        snapshot.generation_runs_count = gen_count

        avg_latency = db.execute(
            select(func.avg(GenerationRun.latency_ms)).where(
                GenerationRun.status == GenerationStatus.COMPLETED
            )
        ).scalar()
        snapshot.avg_generation_latency_ms = float(avg_latency) if avg_latency else None

        total_tokens = db.execute(
            select(
                func.coalesce(func.sum(GenerationRun.input_tokens), 0) +
                func.coalesce(func.sum(GenerationRun.output_tokens), 0)
            ).where(GenerationRun.status == GenerationStatus.COMPLETED)
        ).scalar() or 0
        snapshot.total_tokens_used = total_tokens

        total_cost = db.execute(
            select(func.coalesce(func.sum(GenerationRun.cost_usd), 0)).where(
                GenerationRun.status == GenerationStatus.COMPLETED
            )
        ).scalar() or 0
        snapshot.total_cost_usd = float(total_cost)

        # Provider usage breakdown
        provider_counts = {}
        for provider_val in AIProvider:
            count = db.execute(
                select(func.count(GenerationRun.id)).where(
                    GenerationRun.provider == provider_val,
                    GenerationRun.status == GenerationStatus.COMPLETED,
                )
            ).scalar() or 0
            if count > 0:
                provider_counts[provider_val.value] = count
        snapshot.provider_usage = provider_counts

        # Platform publish counts
        platform_counts = {}
        for status_val in [PublishJobStatus.PUBLISHED, PublishJobStatus.FAILED]:
            count = db.execute(
                select(func.count(PublishJob.id)).where(
                    PublishJob.status == status_val
                )
            ).scalar() or 0
            platform_counts[status_val.value] = count
        snapshot.platform_publish_counts = platform_counts

        db.commit()
        return {"snapshot_date": str(today), "generation_runs": gen_count}


@celery_app.task(name="app.workers.tasks.publish_to_youtube", bind=True, max_retries=3)
def publish_to_youtube(self, publish_job_id: str):
    """
    Task: Publish content to YouTube.

    For video content (Shorts/Long-form):
    - Requires video file to be available in storage
    - Uploads via YouTube Data API v3 resumable upload
    - Sets metadata (title, description, tags, privacy, schedule)

    For metadata-only publish (scheduled publish of already-uploaded video):
    - Updates privacy status and publish schedule
    """
    import asyncio
    from app.models.platform import PlatformAccount, OAuthToken
    from app.models.content import ContentItem, ContentVersion

    with Session(sync_engine) as db:
        # Load publish job
        job = db.execute(
            select(PublishJob).where(PublishJob.id == UUID(publish_job_id))
        ).scalar_one_or_none()

        if not job:
            return {"success": False, "error": "Publish job not found"}

        # Log start
        log = PublishLog(
            publish_job_id=job.id,
            level="info",
            message="YouTube publish task started",
        )
        db.add(log)
        db.flush()

        try:
            # Load content item and current version
            content = db.execute(
                select(ContentItem).where(ContentItem.id == job.content_item_id)
            ).scalar_one_or_none()

            if not content:
                raise ValueError("Content item not found")

            # Get current version content data
            version = db.execute(
                select(ContentVersion)
                .where(ContentVersion.content_item_id == content.id)
                .where(ContentVersion.version_number == content.current_version)
            ).scalar_one_or_none()

            if not version:
                raise ValueError("No content version found")

            content_data = version.content_data

            # Load platform account
            account = db.execute(
                select(PlatformAccount).where(PlatformAccount.id == job.platform_account_id)
            ).scalar_one_or_none()

            if not account or not account.is_connected:
                raise ValueError("Platform account not connected")

            # Get OAuth token
            token = db.execute(
                select(OAuthToken)
                .where(OAuthToken.platform_account_id == account.id)
                .order_by(OAuthToken.created_at.desc())
                .limit(1)
            ).scalar_one_or_none()

            if not token:
                raise ValueError("No OAuth token found. Reconnect YouTube.")

            # Extract metadata from content_data
            # Titles: pick first option
            titles = content_data.get("titles", [])
            title = titles[0] if titles else content.title

            description = content_data.get("description_draft", "")
            tags = content_data.get("tags", [])

            # Determine privacy and schedule
            privacy_status = "private"
            publish_at_str = None

            if job.scheduled_publish_at:
                # Scheduled publish: upload as private, set publishAt
                publish_at_str = job.scheduled_publish_at.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            else:
                # Publish now: set to public
                privacy_status = "public"

            # Log metadata
            log2 = PublishLog(
                publish_job_id=job.id,
                level="info",
                message=f"Publishing: title='{title[:50]}...', privacy={privacy_status}",
                details={"title": title, "tags": tags[:5], "privacy": privacy_status},
            )
            db.add(log2)
            db.flush()

            # Check if video file exists in publish_data
            video_path = (job.publish_data or {}).get("video_path")

            if video_path:
                # Full video upload flow
                # Note: In production, this would use the YouTubeService async method
                # For Celery sync context, we use httpx synchronously
                import httpx

                # Refresh token if needed
                access_token = token.access_token
                if token.expires_at and token.expires_at <= datetime.utcnow():
                    if token.refresh_token:
                        refresh_response = httpx.post(
                            "https://oauth2.googleapis.com/token",
                            data={
                                "refresh_token": token.refresh_token,
                                "client_id": settings.YOUTUBE_CLIENT_ID,
                                "client_secret": settings.YOUTUBE_CLIENT_SECRET,
                                "grant_type": "refresh_token",
                            },
                        )
                        if refresh_response.status_code == 200:
                            new_tokens = refresh_response.json()
                            access_token = new_tokens["access_token"]
                            token.access_token = access_token
                            token.expires_at = datetime.utcnow() + timedelta(
                                seconds=new_tokens.get("expires_in", 3600)
                            )
                        else:
                            raise ValueError("Token refresh failed")
                    else:
                        raise ValueError("Token expired and no refresh token available")

                # Upload video
                body = {
                    "snippet": {
                        "title": title[:100],
                        "description": description[:5000],
                        "tags": tags[:500],
                        "categoryId": "22",
                    },
                    "status": {
                        "privacyStatus": privacy_status,
                        "selfDeclaredMadeForKids": False,
                    },
                }

                if publish_at_str:
                    body["status"]["publishAt"] = publish_at_str

                # Initialize resumable upload
                init_resp = httpx.post(
                    "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                    },
                    json=body,
                    timeout=60,
                )

                if init_resp.status_code != 200:
                    raise ValueError(f"Upload init failed: {init_resp.status_code} - {init_resp.text[:200]}")

                upload_url = init_resp.headers.get("Location")
                if not upload_url:
                    raise ValueError("No upload URL in response")

                # Upload file
                with open(video_path, "rb") as f:
                    video_bytes = f.read()

                upload_resp = httpx.put(
                    upload_url,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "video/*",
                        "Content-Length": str(len(video_bytes)),
                    },
                    content=video_bytes,
                    timeout=600,
                )

                if upload_resp.status_code in [200, 201]:
                    video_data = upload_resp.json()
                    video_id = video_data.get("id")

                    job.status = PublishJobStatus.PUBLISHED if not publish_at_str else PublishJobStatus.SCHEDULED
                    job.platform_post_id = video_id
                    job.platform_url = f"https://www.youtube.com/watch?v={video_id}"
                    job.completed_at = datetime.utcnow()

                    content.status = ContentStatus.PUBLISHED
                    content.published_at = datetime.utcnow()

                    log3 = PublishLog(
                        publish_job_id=job.id,
                        level="info",
                        message=f"Video uploaded successfully: {video_id}",
                        details={"video_id": video_id, "url": job.platform_url},
                    )
                    db.add(log3)
                else:
                    raise ValueError(f"Upload failed: {upload_resp.status_code}")

            else:
                # No video file - this is a metadata-only publish
                # Mark as scheduled (video needs to be uploaded separately)
                job.status = PublishJobStatus.SCHEDULED
                job.completed_at = datetime.utcnow()

                log3 = PublishLog(
                    publish_job_id=job.id,
                    level="info",
                    message="Publish job marked as scheduled (no video file - metadata only)",
                    details={"title": title, "scheduled_at": publish_at_str},
                )
                db.add(log3)

            db.commit()
            return {
                "success": True,
                "publish_job_id": publish_job_id,
                "video_id": job.platform_post_id,
                "url": job.platform_url,
            }

        except Exception as e:
            # Handle failure
            error_msg = str(e)
            job.status = PublishJobStatus.FAILED
            job.error_message = error_msg
            job.retry_count = (job.retry_count or 0) + 1

            log_err = PublishLog(
                publish_job_id=job.id,
                level="error",
                message=f"Publish failed: {error_msg}",
            )
            db.add(log_err)
            db.commit()

            # Retry if under max retries
            if job.retry_count < job.max_retries:
                raise self.retry(exc=e, countdown=60 * job.retry_count)

            return {"success": False, "error": error_msg}


@celery_app.task(name="app.workers.tasks.refresh_oauth_token")
def refresh_oauth_token(platform_account_id: str):
    """Task: Refresh an expired OAuth token."""
    from app.models.platform import PlatformAccount, OAuthToken

    with Session(sync_engine) as db:
        token = db.execute(
            select(OAuthToken)
            .where(OAuthToken.platform_account_id == UUID(platform_account_id))
            .order_by(OAuthToken.created_at.desc())
            .limit(1)
        ).scalar_one_or_none()

        if not token or not token.refresh_token:
            return {"success": False, "error": "No refresh token available"}

        import httpx
        response = httpx.post(
            "https://oauth2.googleapis.com/token",
            data={
                "refresh_token": token.refresh_token,
                "client_id": settings.YOUTUBE_CLIENT_ID,
                "client_secret": settings.YOUTUBE_CLIENT_SECRET,
                "grant_type": "refresh_token",
            },
        )

        if response.status_code == 200:
            data = response.json()
            token.access_token = data["access_token"]
            token.expires_at = datetime.utcnow() + timedelta(seconds=data.get("expires_in", 3600))
            token.updated_at = datetime.utcnow()
            db.commit()
            return {"success": True, "expires_at": token.expires_at.isoformat()}
        else:
            return {"success": False, "error": f"Refresh failed: {response.text}"}
