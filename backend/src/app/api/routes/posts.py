"""Posts API routes with proper FastAPI dependency injection."""

from typing import Optional
from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import Field
from typing_extensions import Annotated

# Ensure generated imports are available
from app.shared.generated_imports import setup_generated_imports
setup_generated_imports()

from generated_fastapi_server.models.blog_post_response import BlogPostResponse
from generated_fastapi_server.models.blog_post_list_response import BlogPostListResponse
from generated_fastapi_server.models.create_post_request import CreatePostRequest
from generated_fastapi_server.models.error import Error
from generated_fastapi_server.models.blog_post import BlogPost as ApiBlogPost
from generated_fastapi_server.models.blog_post_summary import BlogPostSummary
from generated_fastapi_server.models.blog_post_list_data import BlogPostListData
from generated_fastapi_server.models.pagination import Pagination
from generated_fastapi_server.models.api_response_status import ApiResponseStatus

from app.application.services.posts_service import PostApplicationService
from app.shared.dependencies import get_post_application_service
from app.shared.auth import AuthenticatedUser, get_current_user_optional, require_authenticated_user, require_non_anonymous_user
from app.shared.response_utils import normalize_published_at
from app.application.exceptions import ValidationError, NotFoundError, ForbiddenError, ApplicationError, AuthenticationError

posts_router = APIRouter(prefix="/posts", tags=["posts"])

@posts_router.post(
    "",
    status_code=201,
    responses={
        201: {"model": BlogPostResponse, "description": "Blog post created successfully"},
        400: {"model": Error, "description": "Bad Request. The request data is invalid."},
        401: {"model": Error, "description": "Unauthorized. Authentication is required."},
        403: {"model": Error, "description": "Forbidden. Anonymous users cannot create posts."},
        422: {"model": Error, "description": "Validation error"},
        500: {"model": Error, "description": "Internal server error"},
    },
    summary="Create Blog Post",
    response_model_by_alias=True,
)
async def create_blog_post(
    create_post_request: Annotated[CreatePostRequest, Field(description="Blog post data")] = Body(None, description="Blog post data"),
    current_user: AuthenticatedUser = Depends(require_non_anonymous_user),
    post_service: PostApplicationService = Depends(get_post_application_service)
) -> BlogPostResponse:
    """Create a new blog post. Requires authenticated non-anonymous user."""
    try:
        # Use authenticated user's information
        author = current_user.get_identity()
        
        post_data = await post_service.create_post(
            title=create_post_request.title,
            content=create_post_request.content,
            excerpt=create_post_request.excerpt,
            author=author,
            status=create_post_request.status
        )
        
        api_post = ApiBlogPost(
            id=post_data["id"],
            title=post_data["title"],
            content=post_data["content"],
            excerpt=post_data["excerpt"],
            author=post_data["author"],
            publishedAt=normalize_published_at(post_data["publishedAt"]),
            status=post_data["status"]
        )
        
        return BlogPostResponse(
            status=ApiResponseStatus.SUCCESS,
            data=api_post
        )
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=e.message)
    except ApplicationError as e:
        raise HTTPException(status_code=500, detail=e.message)

@posts_router.get(
    "/{id}",
    responses={
        200: {"model": BlogPostResponse, "description": "Blog post retrieved successfully"},
        404: {"model": Error, "description": "Blog post not found"},
        500: {"model": Error, "description": "Internal server error"},
    },
    summary="Get Blog Post by ID",
    response_model_by_alias=True,
)
async def get_blog_post_by_id(
    id: str,
    post_service: PostApplicationService = Depends(get_post_application_service)
) -> BlogPostResponse:
    """Get a blog post by its ID."""
    try:
        post_data = await post_service.get_post_by_id(id)
        
        api_post = ApiBlogPost(
            id=post_data["id"],
            title=post_data["title"],
            content=post_data["content"],
            excerpt=post_data["excerpt"],
            author=post_data["author"],
            publishedAt=normalize_published_at(post_data["publishedAt"]),
            status=post_data["status"]
        )
        
        return BlogPostResponse(
            status=ApiResponseStatus.SUCCESS,
            data=api_post
        )
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Blog post not found")
    except ApplicationError as e:
        raise HTTPException(status_code=500, detail=e.message)

@posts_router.get(
    "",
    responses={
        200: {"model": BlogPostListResponse, "description": "Blog posts retrieved successfully"},
        500: {"model": Error, "description": "Internal server error"},
    },
    summary="Get Blog Posts",
    response_model_by_alias=True,
)
async def get_blog_posts(
    page: int = 1,
    limit: int = 10,
    status: Optional[str] = None,
    author: Optional[str] = None,
    current_user: Optional[AuthenticatedUser] = Depends(get_current_user_optional),
    post_service: PostApplicationService = Depends(get_post_application_service)
) -> BlogPostListResponse:
    """Get a list of blog posts with filtering and pagination."""
    try:
        page = page or 1
        limit = limit or 10
        status = status or "published"
        
        response_data = await post_service.get_posts(
            page=page,
            limit=limit,
            status=status,
            author=author
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
        
    except ApplicationError as e:
        raise HTTPException(status_code=500, detail=e.message)

@posts_router.put(
    "/{id}",
    responses={
        200: {"model": BlogPostResponse, "description": "Blog post updated successfully"},
        401: {"model": Error, "description": "Unauthorized. Authentication is required."},
        403: {"model": Error, "description": "Forbidden. User cannot update this post."},
        404: {"model": Error, "description": "Blog post not found"},
        500: {"model": Error, "description": "Internal server error"},
    },
    summary="Update Blog Post",
    response_model_by_alias=True,
)
async def update_blog_post(
    id: str,
    create_post_request: Annotated[CreatePostRequest, Field(description="Updated blog post data")] = Body(None, description="Updated blog post data"),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    post_service: PostApplicationService = Depends(get_post_application_service)
) -> BlogPostResponse:
    """Update an existing blog post. Requires authentication."""
    try:
        # Use authenticated user's information
        user_id = current_user.get_identity()
        
        post_data = await post_service.update_post(
            post_id=id,
            user_id=user_id,
            title=create_post_request.title,
            content=create_post_request.content,
            excerpt=create_post_request.excerpt
        )
        
        api_post = ApiBlogPost(
            id=post_data["id"],
            title=post_data["title"],
            content=post_data["content"],
            excerpt=post_data["excerpt"],
            author=post_data["author"],
            publishedAt=normalize_published_at(post_data["publishedAt"]),
            status=post_data["status"]
        )
        
        return BlogPostResponse(
            status=ApiResponseStatus.SUCCESS,
            data=api_post
        )
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Blog post not found")
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=e.message)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=e.message)
    except ApplicationError as e:
        raise HTTPException(status_code=500, detail=e.message)

@posts_router.delete(
    "/{id}",
    status_code=204,
    responses={
        204: {"description": "Blog post deleted successfully"},
        401: {"model": Error, "description": "Unauthorized. Authentication is required."},
        403: {"model": Error, "description": "Forbidden. User cannot delete this post."},
        404: {"model": Error, "description": "Blog post not found"},
        500: {"model": Error, "description": "Internal server error"},
    },
    summary="Delete Blog Post",
)
async def delete_blog_post(
    id: str,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    post_service: PostApplicationService = Depends(get_post_application_service)
):
    """Delete a blog post. Requires authentication."""
    try:
        # Use authenticated user's information
        user_id = current_user.get_identity()
        await post_service.delete_post(id, user_id)
        return None
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Blog post not found")
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=e.message)
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=e.message)
    except ApplicationError as e:
        raise HTTPException(status_code=500, detail=e.message)