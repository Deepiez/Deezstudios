from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.rate_limit import RateLimitMiddleware
from app.api.v1.router import api_router

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS
allowed_origins = ["http://localhost:3000"]
if not settings.DEBUG:
    allowed_origins = ["*"]  # In production, Nginx handles CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
app.add_middleware(RateLimitMiddleware)


@app.get("/health")
async def health_check():
    """Basic health check for load balancers and Docker."""
    return {"status": "healthy", "app": settings.APP_NAME, "env": settings.APP_ENV}


@app.get("/health/detailed")
async def health_check_detailed():
    """Detailed health check - tests DB and Redis connectivity."""
    import redis as redis_lib
    from sqlalchemy import text
    from app.core.database import AsyncSessionLocal

    checks = {"app": "healthy", "env": settings.APP_ENV}

    # Database check
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)[:100]}"

    # Redis check
    try:
        r = redis_lib.from_url(settings.REDIS_URL, socket_timeout=3)
        r.ping()
        checks["redis"] = "healthy"
    except Exception as e:
        checks["redis"] = f"unhealthy: {str(e)[:100]}"

    # AI Providers check
    checks["providers"] = {
        "openai": bool(settings.OPENAI_API_KEY),
        "anthropic": bool(settings.ANTHROPIC_API_KEY),
        "gemini": bool(settings.GOOGLE_GEMINI_API_KEY),
    }

    overall = all(
        v == "healthy" for k, v in checks.items()
        if k in ["database", "redis"] and isinstance(v, str)
    )
    checks["status"] = "healthy" if overall else "degraded"

    return checks


# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
