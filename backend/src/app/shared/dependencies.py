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
