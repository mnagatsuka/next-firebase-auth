"""FastAPI dependency injection configuration following DDD principles.

Adds environment-driven DI switching between in-memory and DynamoDB repositories.
"""

from functools import lru_cache
from fastapi import Depends

from app.shared.config import get_settings
from app.infra.repositories.posts_repository import (
    InMemoryPostRepository,
    DynamoDBPostRepository,
)
from app.infra.repositories.comments_repository import (
    InMemoryCommentRepository,
    DynamoDBCommentRepository,
)
from app.application.services.posts_service import PostApplicationService
from app.application.services.comments_service import CommentApplicationService
from app.application.services.favorites_service import FavoriteApplicationService
from app.application.services.apigateway_websocket_service import get_apigateway_websocket_service_instance
from app.infra.repositories.favorites_repository import InMemoryFavoriteRepository, DynamoDBFavoriteRepository


# Repository layer dependencies
@lru_cache()
def get_post_repository():
    """Get singleton post repository instance (in-memory or DynamoDB)."""
    settings = get_settings()
    provider = (settings.REPOSITORY_PROVIDER or "memory").lower()
    if provider == "dynamodb":
        return DynamoDBPostRepository(
            table_name=settings.DYNAMODB_TABLE_POSTS,
            endpoint_url=settings.AWS_ENDPOINT_URL,
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
    return InMemoryPostRepository()


@lru_cache()
def get_comment_repository():
    """Get singleton comment repository instance (in-memory or DynamoDB)."""
    settings = get_settings()
    provider = (settings.REPOSITORY_PROVIDER or "memory").lower()
    if provider == "dynamodb":
        return DynamoDBCommentRepository(
            table_name=settings.DYNAMODB_TABLE_COMMENTS,
            endpoint_url=settings.AWS_ENDPOINT_URL,
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
    return InMemoryCommentRepository()


# Application layer dependencies  
def get_post_application_service(
    post_repository=Depends(get_post_repository),
    comment_repository=Depends(get_comment_repository),
) -> PostApplicationService:
    """FastAPI dependency for post application service."""
    return PostApplicationService(post_repository, comment_repository)


def get_comment_application_service(
    comment_repository=Depends(get_comment_repository),
    post_repository=Depends(get_post_repository),
) -> CommentApplicationService:
    """FastAPI dependency for comment application service."""
    return CommentApplicationService(comment_repository, post_repository)


# Favorites dependencies (in-memory only for now)
@lru_cache()
def get_favorite_repository():
    settings = get_settings()
    provider = (settings.REPOSITORY_PROVIDER or "memory").lower()
    if provider == "dynamodb":
        return DynamoDBFavoriteRepository(
            table_name=settings.DYNAMODB_TABLE_FAVORITES,
            endpoint_url=settings.AWS_ENDPOINT_URL,
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
    return InMemoryFavoriteRepository()


def get_favorite_application_service(
    favorite_repository=Depends(get_favorite_repository),
    post_repository=Depends(get_post_repository),
) -> FavoriteApplicationService:
    return FavoriteApplicationService(favorite_repository, post_repository)


# WebSocket service dependency
def get_apigateway_websocket_service():
    """FastAPI dependency for API Gateway WebSocket service."""
    return get_apigateway_websocket_service_instance()
