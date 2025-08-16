"""Comments API routes using generated models."""

from fastapi import APIRouter, Body, HTTPException
from pydantic import Field
from typing_extensions import Annotated

# Import generated models
import sys
from pathlib import Path
generated_path = Path(__file__).parent.parent.parent / "generated" / "src"
sys.path.insert(0, str(generated_path))

from generated_fastapi_server.models.comment import Comment
from generated_fastapi_server.models.create_comment_request import CreateCommentRequest
from generated_fastapi_server.models.comments_response import CommentsResponse

from app.api.comments_implementation import CommentsImplementation

comments_router = APIRouter(prefix="/posts", tags=["comments"])

def get_comments_impl():
    """Get CommentsImplementation instance - called at request time for proper mocking."""
    return CommentsImplementation()

@comments_router.post("/{id}/comments", status_code=201)
async def create_comment(
    id: str,
    create_comment_request: Annotated[CreateCommentRequest, Field(description="Comment data")] = Body(None),
) -> Comment:
    """Create a new comment on a specific blog post."""
    comments_impl = get_comments_impl()
    return await comments_impl.create_comment(id, create_comment_request)

@comments_router.get("/{id}/comments")
async def get_post_comments(
    id: str,
    limit: int = 10
) -> CommentsResponse:
    """Get comments for a specific blog post."""
    comments_impl = get_comments_impl()
    return await comments_impl.get_post_comments(id, limit)