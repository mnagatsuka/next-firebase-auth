"""Users API routes with proper FastAPI dependency injection."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import Field

# Ensure generated imports are available
from app.shared.generated_imports import setup_generated_imports
setup_generated_imports()

from generated_fastapi_server.models.blog_post_list_response import BlogPostListResponse
from generated_fastapi_server.models.error import Error
from generated_fastapi_server.models.blog_post_summary import BlogPostSummary
from generated_fastapi_server.models.blog_post_list_data import BlogPostListData
from generated_fastapi_server.models.pagination import Pagination
from generated_fastapi_server.models.api_response_status import ApiResponseStatus

from app.application.services.posts_service import PostApplicationService
from app.shared.dependencies import get_post_application_service, get_favorite_application_service
from app.shared.auth import AuthenticatedUser, require_authenticated_user
from app.shared.response_utils import normalize_published_at
from app.application.exceptions import ApplicationError, ForbiddenError

users_router = APIRouter(prefix="/users", tags=["users"])

@users_router.get(
    "/{uid}/posts",
    responses={
        200: {"model": BlogPostListResponse, "description": "User posts retrieved successfully"},
        401: {"model": Error, "description": "Unauthorized. Authentication is required."},
        403: {"model": Error, "description": "Forbidden. User cannot access this resource."},
        500: {"model": Error, "description": "Internal server error"},
    },
    summary="Get Posts For User",
    response_model_by_alias=True,
)
async def get_user_posts(
    uid: str,
    page: int = 1,
    limit: int = 10,
    status: Optional[str] = None,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    post_service: PostApplicationService = Depends(get_post_application_service)
) -> BlogPostListResponse:
    """Get a list of blog posts for a specific user with filtering and pagination.
    
    Args:
        uid: Firebase User ID (stable across anonymous -> authenticated transitions)
        page: Page number for pagination (default: 1)
        limit: Number of posts per page (default: 10, max: 50)
        status: Filter by post status ('published' or 'draft')
    
    The caller must be the same user as {uid} or have admin permissions.
    Supports filtering by status (published, draft). When status is omitted, returns all posts.
    
    Note: Using Firebase UID ensures data continuity when anonymous users become authenticated.
    """
    try:
        # Check if user can access this resource
        current_user_id = current_user.get_identity()
        if current_user_id != uid:
            # In the future, we could add admin role checking here
            raise ForbiddenError("You can only access your own posts")
        
        # Validate query parameters
        page = max(1, page or 1)
        limit = max(1, min(50, limit or 10))  # Cap at 50 posts per page
        
        # Validate status parameter
        if status and status not in ["published", "draft"]:
            raise HTTPException(status_code=400, detail="Invalid status. Must be 'published' or 'draft'")
        
        response_data = await post_service.get_user_posts(
            user_id=uid,
            page=page,
            limit=limit,
            status=status
        )
        
        post_summaries = []
        for post in response_data["data"]:
            post_summaries.append(BlogPostSummary(
                id=post["id"],
                title=post["title"],
                excerpt=post["excerpt"],
                author=post["author"],
                publishedAt=normalize_published_at(post["publishedAt"]),
                status=post["status"]
            ))
        
        # Calculate has_next for pagination
        total = response_data["pagination"]["total"]
        current_page = response_data["pagination"]["page"]
        limit = response_data["pagination"]["limit"]
        has_next = (current_page * limit) < total
        
        data = BlogPostListData(
            posts=post_summaries,
            pagination=Pagination(
                page=current_page,
                limit=limit,
                total=total,
                hasNext=has_next
            )
        )
        
        return BlogPostListResponse(
            status=ApiResponseStatus.SUCCESS,
            data=data
        )
        
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=e.message)
    except ApplicationError as e:
        raise HTTPException(status_code=500, detail=e.message)


@users_router.get(
    "/{uid}/favorites",
    responses={
        200: {"model": BlogPostListResponse, "description": "User favorites retrieved successfully"},
        401: {"model": Error, "description": "Unauthorized. Authentication is required."},
        403: {"model": Error, "description": "Forbidden. User cannot access this resource."},
        500: {"model": Error, "description": "Internal server error"},
    },
    summary="Get Favorite Posts For User",
    response_model_by_alias=True,
)
async def get_user_favorites(
    uid: str,
    page: int = 1,
    limit: int = 10,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    favorite_service = Depends(get_favorite_application_service),
):
    """Get a list of favorited posts for the specified user with pagination.

    Caller must be the same user.
    """
    try:
        current_user_id = current_user.get_identity()
        if current_user_id != uid:
            raise ForbiddenError("You can only access your own favorites")

        page = max(1, page or 1)
        limit = max(1, min(50, limit or 10))

        response_data = await favorite_service.get_user_favorites(uid, page=page, limit=limit)

        # Convert domain posts to summaries
        post_summaries = []
        for post in response_data["data"]:
            post_summaries.append(BlogPostSummary(
                id=post.id,
                title=post.title,
                excerpt=post.excerpt,
                author=post.author,
                publishedAt=normalize_published_at(post.published_at.isoformat() if post.published_at else None),
                status=post.status.value,
            ))

        total = response_data["pagination"]["total"]
        current_page = response_data["pagination"]["page"]
        limit_val = response_data["pagination"]["limit"]
        has_next = (current_page * limit_val) < total

        data = BlogPostListData(
            posts=post_summaries,
            pagination=Pagination(
                page=current_page,
                limit=limit_val,
                total=total,
                hasNext=has_next,
            ),
        )

        return BlogPostListResponse(status=ApiResponseStatus.SUCCESS, data=data)

    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=e.message)
    except ApplicationError as e:
        raise HTTPException(status_code=500, detail=e.message)
