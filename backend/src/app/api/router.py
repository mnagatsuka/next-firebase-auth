"""Main API router."""

from fastapi import APIRouter
from app.api.routes import posts_router
from app.api.routes.comments import comments_router

api_router = APIRouter()

# Health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "API is running"}

# Include route modules
api_router.include_router(posts_router)
api_router.include_router(comments_router)