# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from generated_fastapi_server.apis.posts_api_base import BasePostsApi
import generated_fastapi_server.impl

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)

from generated_fastapi_server.models.extra_models import TokenModel  # noqa: F401
from pydantic import Field, StrictStr, field_validator
from typing import Any, Optional
from typing_extensions import Annotated
from generated_fastapi_server.models.blog_post_list_response import BlogPostListResponse
from generated_fastapi_server.models.blog_post_response import BlogPostResponse
from generated_fastapi_server.models.create_post_request import CreatePostRequest
from generated_fastapi_server.models.error import Error
from generated_fastapi_server.security_api import get_token_firebaseAuth

router = APIRouter()

ns_pkg = generated_fastapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.post(
    "/posts",
    responses={
        201: {"model": BlogPostResponse, "description": "Blog post created successfully"},
        400: {"model": Error, "description": "Bad Request. The request data is invalid."},
        401: {"model": Error, "description": "Unauthorized. Authentication is required."},
        422: {"model": Error, "description": "Validation error"},
        500: {"model": Error, "description": "Internal server error"},
    },
    tags=["posts"],
    summary="Create Blog Post",
    response_model_by_alias=True,
)
async def create_blog_post(
    create_post_request: Annotated[CreatePostRequest, Field(description="Blog post data")] = Body(None, description="Blog post data"),
    token_firebaseAuth: TokenModel = Security(
        get_token_firebaseAuth
    ),
) -> BlogPostResponse:
    """Creates a new blog post. Requires authentication.  The author field will be automatically set based on the authenticated user. Posts are created in &#39;draft&#39; status by default. """
    if not BasePostsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BasePostsApi.subclasses[0]().create_blog_post(create_post_request)


@router.delete(
    "/posts/{id}",
    responses={
        204: {"description": "Blog post deleted successfully"},
        401: {"model": Error, "description": "Unauthorized. Authentication is required."},
        403: {"model": Error, "description": "Forbidden - insufficient permissions"},
        404: {"model": Error, "description": "Resource not found."},
        500: {"model": Error, "description": "Internal server error"},
    },
    tags=["posts"],
    summary="Delete Blog Post",
    response_model_by_alias=True,
)
async def delete_blog_post(
    id: Annotated[StrictStr, Field(description="Unique identifier for the blog post")] = Path(..., description="Unique identifier for the blog post"),
    token_firebaseAuth: TokenModel = Security(
        get_token_firebaseAuth
    ),
) -> None:
    """Deletes a blog post by its ID. Requires authentication.  Only the author of the post or users with admin privileges can delete a post. This action is irreversible. """
    if not BasePostsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BasePostsApi.subclasses[0]().delete_blog_post(id)


@router.get(
    "/posts/{id}",
    responses={
        200: {"model": BlogPostResponse, "description": "Successfully retrieved blog post details"},
        404: {"model": Error, "description": "Resource not found."},
        500: {"model": Error, "description": "Internal server error"},
    },
    tags=["posts"],
    summary="Get Single Blog Post",
    response_model_by_alias=True,
)
async def get_blog_post_by_id(
    id: Annotated[StrictStr, Field(description="Unique identifier for the blog post")] = Path(..., description="Unique identifier for the blog post"),
) -> BlogPostResponse:
    """Retrieves detailed information about a specific blog post by its ID.  Returns the complete blog post including content, metadata, and author information. """
    if not BasePostsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BasePostsApi.subclasses[0]().get_blog_post_by_id(id)


@router.get(
    "/posts",
    responses={
        200: {"model": BlogPostListResponse, "description": "Successfully retrieved paginated blog posts"},
        400: {"model": Error, "description": "Bad Request. The request data is invalid."},
        500: {"model": Error, "description": "Internal server error"},
    },
    tags=["posts"],
    summary="Get Blog Posts",
    response_model_by_alias=True,
)
async def get_blog_posts(
    page: Annotated[Optional[Annotated[int, Field(strict=True, ge=1)]], Field(description="Page number for pagination")] = Query(1, description="Page number for pagination", alias="page", ge=1),
    limit: Annotated[Optional[Annotated[int, Field(le=50, strict=True, ge=1)]], Field(description="Number of items per page")] = Query(10, description="Number of items per page", alias="limit", ge=1, le=50),
    status: Annotated[Optional[StrictStr], Field(description="Filter posts by status")] = Query(published, description="Filter posts by status", alias="status"),
    author: Annotated[Optional[StrictStr], Field(description="Filter posts by author name")] = Query(None, description="Filter posts by author name", alias="author"),
) -> BlogPostListResponse:
    """Retrieves a paginated list of published blog posts.  This endpoint supports pagination and returns blog post summaries optimized for listing views (homepage, archives, etc.). """
    if not BasePostsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BasePostsApi.subclasses[0]().get_blog_posts(page, limit, status, author)


@router.put(
    "/posts/{id}",
    responses={
        200: {"model": BlogPostResponse, "description": "Blog post updated successfully"},
        400: {"model": Error, "description": "Bad Request. The request data is invalid."},
        401: {"model": Error, "description": "Unauthorized. Authentication is required."},
        403: {"model": Error, "description": "Forbidden - insufficient permissions"},
        404: {"model": Error, "description": "Resource not found."},
        422: {"model": Error, "description": "Validation error"},
        500: {"model": Error, "description": "Internal server error"},
    },
    tags=["posts"],
    summary="Update Blog Post",
    response_model_by_alias=True,
)
async def update_blog_post(
    id: Annotated[StrictStr, Field(description="Unique identifier for the blog post")] = Path(..., description="Unique identifier for the blog post"),
    create_post_request: Annotated[CreatePostRequest, Field(description="Updated blog post data")] = Body(None, description="Updated blog post data"),
    token_firebaseAuth: TokenModel = Security(
        get_token_firebaseAuth
    ),
) -> BlogPostResponse:
    """Updates an existing blog post by its ID. Requires authentication.  Only the author of the post or users with admin privileges can update a post. Partial updates are supported - only provided fields will be updated. """
    if not BasePostsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BasePostsApi.subclasses[0]().update_blog_post(id, create_post_request)
