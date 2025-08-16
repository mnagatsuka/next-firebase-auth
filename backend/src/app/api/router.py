from fastapi import APIRouter

from . import health, posts


api_router = APIRouter()

# Mount feature routers
api_router.include_router(health.router, tags=["health"])
api_router.include_router(posts.router)
