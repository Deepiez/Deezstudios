"""Generation API endpoints - Content generation using AI providers."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from uuid import UUID
from typing import Optional

from app.core.database import get_db
from app.models.generation import GenerationRun
from app.models.content import ContentItem
from app.schemas.generation import (
    GenerationRunRequest,
    RegenerationRequest,
    GenerationRunResponse,
    GenerationRunDetail,
    GenerationRunListItem,
    ProvidersListResponse,
    ProviderInfo,
)
from app.services.generation.generation_service import GenerationService
from app.services.ai_providers.provider_manager import provider_manager

router = APIRouter()


@router.post("/run", response_model=GenerationRunResponse)
async def run_generation(
    request: GenerationRunRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Run AI content generation for a content item.

    This endpoint:
    1. Loads the content item and its brief
    2. Fetches relevant style guides and CTA patterns
    3. Builds optimized prompts for the content type
    4. Calls the specified AI provider
    5. Parses the structured JSON output
    6. Creates a new content version

    The content item must have a brief attached before generation can run.
    """
    # Validate content item exists
    result = await db.execute(
        select(ContentItem).where(ContentItem.id == request.content_item_id)
    )
    content_item = result.scalar_one_or_none()
    if not content_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content item not found",
        )

    # Validate provider is available
    if request.provider.value not in provider_manager.get_available_providers():
        available = provider_manager.get_available_providers()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Provider '{request.provider.value}' is not configured. "
                   f"Available providers: {available}",
        )

    if request.provider.value == "custom":
        if not request.custom_endpoint or not request.custom_api_key or not request.model:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Custom provider requires custom_endpoint, custom_api_key, and model.",
            )

    # Run generation
    service = GenerationService(db)
    result = await service.generate_content(
        content_item_id=request.content_item_id,
        provider=request.provider.value,
        model=request.model,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        fallback_provider=request.fallback_provider.value if request.fallback_provider else None,
        custom_instructions=request.custom_instructions,
        custom_endpoint=request.custom_endpoint,
        custom_api_key=request.custom_api_key,
    )

    if not result["success"]:
        # Return error response (not HTTP error, since the request was valid)
        return GenerationRunResponse(
            success=False,
            generation_run_id=result.get("generation_run_id", ""),
            error=result.get("error"),
            raw_content=result.get("raw_content"),
        )

    return GenerationRunResponse(
        success=True,
        generation_run_id=result["generation_run_id"],
        content_version_id=result.get("content_version_id"),
        version_number=result.get("version_number"),
        content_data=result.get("content_data"),
        parse_warning=result.get("parse_warning"),
        metrics=result.get("metrics"),
    )


@router.post("/regenerate", response_model=GenerationRunResponse)
async def regenerate_content(
    request: RegenerationRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Regenerate content with optional revision notes.

    Use this when the previous generation wasn't satisfactory.
    Revision notes are injected into the prompt to guide the AI
    toward better output.
    """
    # Validate content item exists
    result = await db.execute(
        select(ContentItem).where(ContentItem.id == request.content_item_id)
    )
    content_item = result.scalar_one_or_none()
    if not content_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content item not found",
        )

    service = GenerationService(db)

    if request.provider.value == "custom":
        if not request.custom_endpoint or not request.custom_api_key or not request.model:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Custom provider requires custom_endpoint, custom_api_key, and model.",
            )

    result = await service.regenerate_content(
        content_item_id=request.content_item_id,
        provider=request.provider.value,
        model=request.model,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        revision_notes=request.revision_notes,
        fallback_provider=request.fallback_provider.value if request.fallback_provider else None,
        custom_endpoint=request.custom_endpoint,
        custom_api_key=request.custom_api_key,
    )

    if not result["success"]:
        return GenerationRunResponse(
            success=False,
            generation_run_id=result.get("generation_run_id", ""),
            error=result.get("error"),
            raw_content=result.get("raw_content"),
        )

    return GenerationRunResponse(
        success=True,
        generation_run_id=result["generation_run_id"],
        content_version_id=result.get("content_version_id"),
        version_number=result.get("version_number"),
        content_data=result.get("content_data"),
        parse_warning=result.get("parse_warning"),
        metrics=result.get("metrics"),
    )


@router.get("/runs", response_model=list[GenerationRunListItem])
async def list_generation_runs(
    content_item_id: Optional[UUID] = None,
    provider: Optional[str] = None,
    status_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List generation runs with optional filters."""
    query = select(GenerationRun).order_by(desc(GenerationRun.created_at))

    if content_item_id:
        query = query.where(GenerationRun.content_item_id == content_item_id)
    if provider:
        query = query.where(GenerationRun.provider == provider)
    if status_filter:
        query = query.where(GenerationRun.status == status_filter)

    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    runs = result.scalars().all()

    return [GenerationRunListItem.model_validate(run) for run in runs]


@router.get("/runs/{run_id}", response_model=GenerationRunDetail)
async def get_generation_run(
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get detailed information about a specific generation run."""
    result = await db.execute(
        select(GenerationRun).where(GenerationRun.id == run_id)
    )
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation run not found",
        )

    return GenerationRunDetail.model_validate(run)


@router.post("/runs/{run_id}/retry", response_model=GenerationRunResponse)
async def retry_generation(
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Retry a failed generation run with the same parameters.
    Creates a new generation run with identical settings.
    """
    # Load the failed run
    result = await db.execute(
        select(GenerationRun).where(GenerationRun.id == run_id)
    )
    original_run = result.scalar_one_or_none()
    if not original_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation run not found",
        )

    if original_run.status.value != "failed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only retry failed generation runs",
        )

    # Re-run with same parameters
    params = original_run.parameters or {}
    service = GenerationService(db)
    result = await service.generate_content(
        content_item_id=original_run.content_item_id,
        provider=original_run.provider.value,
        model=original_run.model,
        temperature=params.get("temperature", 0.7),
        max_tokens=params.get("max_tokens", 4096),
        fallback_provider=params.get("fallback_provider"),
    )

    if not result["success"]:
        return GenerationRunResponse(
            success=False,
            generation_run_id=result.get("generation_run_id", ""),
            error=result.get("error"),
        )

    return GenerationRunResponse(
        success=True,
        generation_run_id=result["generation_run_id"],
        content_version_id=result.get("content_version_id"),
        version_number=result.get("version_number"),
        content_data=result.get("content_data"),
        metrics=result.get("metrics"),
    )


@router.post("/run-async")
async def run_generation_async(
    request: GenerationRunRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Run content generation as a background task (non-blocking).

    Returns immediately with a task ID. Use this for:
    - Batch generation of multiple content items
    - Long-running generations with large max_tokens
    - When you don't need to wait for the result

    Poll /generation/runs/{run_id} to check status.
    """
    from app.workers.tasks import run_content_generation_async

    # Validate content item exists
    result = await db.execute(
        select(ContentItem).where(ContentItem.id == request.content_item_id)
    )
    content_item = result.scalar_one_or_none()
    if not content_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content item not found",
        )

    # Dispatch to Celery
    task = run_content_generation_async.delay(
        content_item_id=str(request.content_item_id),
        provider=request.provider.value,
        model=request.model,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        fallback_provider=request.fallback_provider.value if request.fallback_provider else None,
        custom_instructions=request.custom_instructions,
        custom_endpoint=request.custom_endpoint,
        custom_api_key=request.custom_api_key,
    )

    return {
        "task_id": task.id,
        "status": "queued",
        "message": "Generation task queued. Poll /generation/runs to check results.",
    }


@router.get("/providers", response_model=ProvidersListResponse)
async def list_providers():
    """
    List all available AI providers and their models.
    Shows which providers are configured and ready to use.
    """
    providers_info = provider_manager.get_configured_providers()
    providers = [ProviderInfo(**p) for p in providers_info]
    available_count = len(provider_manager.get_available_providers())

    return ProvidersListResponse(
        providers=providers,
        available_count=available_count,
    )


@router.get("/defaults")
async def get_provider_defaults():
    """
    Get default provider and model recommendations per content type.
    Frontend uses this to pre-select provider/model in the generation panel.
    """
    from app.services.generation.provider_defaults import get_all_defaults
    return get_all_defaults()


@router.get("/defaults/{content_type}")
async def get_provider_default_for_type(content_type: str):
    """Get default provider/model for a specific content type."""
    from app.services.generation.provider_defaults import get_default_provider, get_fallback_provider

    default = get_default_provider(content_type)
    default["fallback_provider"] = get_fallback_provider(default.get("provider", ""))
    return default
