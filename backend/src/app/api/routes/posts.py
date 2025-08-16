"""Posts API routes."""

from fastapi import APIRouter, Body
from pydantic import Field
from typing_extensions import Annotated

# Import generated models
import sys
from pathlib import Path
generated_path = Path(__file__).parent.parent.parent / "generated" / "src"
sys.path.insert(0, str(generated_path))

from generated_fastapi_server.models.blog_post_response import BlogPostResponse
from generated_fastapi_server.models.blog_post_list_response import BlogPostListResponse
from generated_fastapi_server.models.create_post_request import CreatePostRequest
from generated_fastapi_server.models.error import Error

from app.api.posts_implementation import PostsImplementation

posts_router = APIRouter(prefix="/posts", tags=["posts"])

def get_posts_impl():
    """Get PostsImplementation instance - called at request time for proper mocking."""
    return PostsImplementation()

@posts_router.post(
    "",
    status_code=201,
    responses={
        201: {"model": BlogPostResponse, "description": "Blog post created successfully"},
        400: {"model": Error, "description": "Bad Request. The request data is invalid."},
        401: {"model": Error, "description": "Unauthorized. Authentication is required."},
        422: {"model": Error, "description": "Validation error"},
        500: {"model": Error, "description": "Internal server error"},
    },
    summary="Create Blog Post",
    response_model_by_alias=True,
)
async def create_blog_post(
    create_post_request: Annotated[CreatePostRequest, Field(description="Blog post data")] = Body(None, description="Blog post data"),
) -> BlogPostResponse:
    """Create a new blog post."""
    posts_impl = get_posts_impl()
    return await posts_impl.create_blog_post(create_post_request)

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
async def get_blog_post_by_id(id: str) -> BlogPostResponse:
    """Get a blog post by its ID."""
    posts_impl = get_posts_impl()
    return await posts_impl.get_blog_post_by_id(id)

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
    status: str = None,
    author: str = None,
) -> BlogPostListResponse:
    """Get a list of blog posts with filtering and pagination."""
    posts_impl = get_posts_impl()
    return await posts_impl.get_blog_posts(page, limit, status, author)

@posts_router.put(
    "/{id}",
    responses={
        200: {"model": BlogPostResponse, "description": "Blog post updated successfully"},
        404: {"model": Error, "description": "Blog post not found"},
        500: {"model": Error, "description": "Internal server error"},
    },
    summary="Update Blog Post",
    response_model_by_alias=True,
)
async def update_blog_post(
    id: str,
    create_post_request: Annotated[CreatePostRequest, Field(description="Updated blog post data")] = Body(None, description="Updated blog post data"),
) -> BlogPostResponse:
    """Update an existing blog post."""
    posts_impl = get_posts_impl()
    return await posts_impl.update_blog_post(id, create_post_request)

@posts_router.delete(
    "/{id}",
    status_code=204,
    responses={
        204: {"description": "Blog post deleted successfully"},
        404: {"model": Error, "description": "Blog post not found"},
        500: {"model": Error, "description": "Internal server error"},
    },
    summary="Delete Blog Post",
)
async def delete_blog_post(id: str):
    """Delete a blog post."""
    posts_impl = get_posts_impl()
    await posts_impl.delete_blog_post(id)
    return None