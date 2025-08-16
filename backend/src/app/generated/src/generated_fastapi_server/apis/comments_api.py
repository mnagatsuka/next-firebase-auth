# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from generated_fastapi_server.apis.comments_api_base import BaseCommentsApi
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
from pydantic import Field, StrictStr
from typing import Optional
from typing_extensions import Annotated
from generated_fastapi_server.models.comment import Comment
from generated_fastapi_server.models.comments_response import CommentsResponse
from generated_fastapi_server.models.create_comment_request import CreateCommentRequest
from generated_fastapi_server.models.error import Error
from generated_fastapi_server.security_api import get_token_firebaseAuth

router = APIRouter()

ns_pkg = generated_fastapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.post(
    "/posts/{id}/comments",
    responses={
        201: {"model": Comment, "description": "Comment created successfully"},
        400: {"model": Error, "description": "Bad Request. The request data is invalid."},
        401: {"model": Error, "description": "Unauthorized. Authentication is required."},
        404: {"model": Error, "description": "Resource not found."},
        422: {"model": Error, "description": "Validation error"},
        500: {"model": Error, "description": "Internal server error"},
    },
    tags=["comments"],
    summary="Create Comment",
    response_model_by_alias=True,
)
async def create_comment(
    id: Annotated[StrictStr, Field(description="Unique identifier for the blog post")] = Path(..., description="Unique identifier for the blog post"),
    create_comment_request: Annotated[CreateCommentRequest, Field(description="Comment data")] = Body(None, description="Comment data"),
    token_firebaseAuth: TokenModel = Security(
        get_token_firebaseAuth
    ),
) -> Comment:
    """Creates a new comment on a specific blog post. Requires authentication.  The author field will be automatically set based on the authenticated user. Comments are moderated and may not appear immediately. """
    if not BaseCommentsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseCommentsApi.subclasses[0]().create_comment(id, create_comment_request)


@router.get(
    "/posts/{id}/comments",
    responses={
        200: {"model": CommentsResponse, "description": "Successfully retrieved post comments"},
        404: {"model": Error, "description": "Resource not found."},
        500: {"model": Error, "description": "Internal server error"},
    },
    tags=["comments"],
    summary="Get Post Comments",
    response_model_by_alias=True,
)
async def get_post_comments(
    id: Annotated[StrictStr, Field(description="Unique identifier for the blog post")] = Path(..., description="Unique identifier for the blog post"),
    limit: Annotated[Optional[Annotated[int, Field(le=100, strict=True, ge=1)]], Field(description="Maximum number of comments to return")] = Query(50, description="Maximum number of comments to return", alias="limit", ge=1, le=100),
) -> CommentsResponse:
    """Retrieves all comments for a specific blog post.  Comments are returned in chronological order (oldest first). This endpoint is public and does not require authentication. """
    if not BaseCommentsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseCommentsApi.subclasses[0]().get_post_comments(id, limit)
