from fastapi import APIRouter
from app.api.v1.endpoints import auth, brands, campaigns, content, generation, style_guides, calendar, integrations, analytics

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(brands.router, prefix="/brands", tags=["Brands"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["Campaigns"])
api_router.include_router(content.router, prefix="/content", tags=["Content"])
api_router.include_router(generation.router, prefix="/generation", tags=["Generation"])
api_router.include_router(style_guides.router, prefix="/style-guides", tags=["Style Guides"])
api_router.include_router(calendar.router, prefix="/calendar", tags=["Calendar"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["Integrations"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
