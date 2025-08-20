"""Comments API routes with proper FastAPI dependency injection."""

from typing import Optional
from fastapi import APIRouter, Body, HTTPException, Depends
from pydantic import Field
from typing_extensions import Annotated

# Ensure generated imports are available
from app.shared.generated_imports import setup_generated_imports
setup_generated_imports()

from generated_fastapi_server.models.comment import Comment
from generated_fastapi_server.models.create_comment_request import CreateCommentRequest
from generated_fastapi_server.models.comments_response import CommentsResponse
from generated_fastapi_server.models.api_response_status import ApiResponseStatus

from app.application.services.comments_service import CommentApplicationService
from app.shared.dependencies import get_comment_application_service
from app.shared.auth import AuthenticatedUser, get_current_user_optional, require_authenticated_user
from app.domain.exceptions import CommentNotFoundError, CommentValidationError, PostNotFoundError
from app.application.exceptions import ValidationError, NotFoundError, ApplicationError, AuthenticationError

comments_router = APIRouter(prefix="/posts", tags=["comments"])

@comments_router.post("/{id}/comments", status_code=201)
async def create_comment(
    id: str,
    create_comment_request: Annotated[CreateCommentRequest, Field(description="Comment data")] = Body(None),
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    comment_service: CommentApplicationService = Depends(get_comment_application_service)
) -> Comment:
    """Create a new comment on a specific blog post. Requires authentication."""
    try:
        # Use authenticated user's UID as userId
        user_id = current_user.get_identity()
        
        comment_data = await comment_service.create_comment(
            post_id=id,
            content=create_comment_request.content,
            user_id=user_id
        )
        
        return Comment(
            id=comment_data["id"],
            content=comment_data["content"],
            userId=comment_data["userId"],
            createdAt=comment_data["createdAt"],
            postId=comment_data["postId"]
        )
        
    except (PostNotFoundError, NotFoundError):
        raise HTTPException(status_code=404, detail="Post not found")
    except (CommentValidationError, ValidationError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except ApplicationError as e:
        raise HTTPException(status_code=500, detail=str(e))

@comments_router.get("/{id}/comments")
async def get_post_comments(
    id: str,
    limit: int = 10,
    current_user: Optional[AuthenticatedUser] = Depends(get_current_user_optional),
    comment_service: CommentApplicationService = Depends(get_comment_application_service)
) -> CommentsResponse:
    """Get comments for a specific blog post. Authentication optional."""
    try:
        comments_data = await comment_service.get_comments_by_post(
            post_id=id,
            limit=limit
        )
        
        comments = []
        for comment_data in comments_data:
            comments.append(Comment(
                id=comment_data["id"],
                content=comment_data["content"],
                userId=comment_data["userId"],
                createdAt=comment_data["createdAt"],
                postId=comment_data["postId"]
            ))
        
        return CommentsResponse(
            status=ApiResponseStatus.SUCCESS,
            data=comments
        )
        
    except (PostNotFoundError, NotFoundError):
        raise HTTPException(status_code=404, detail="Post not found")
    except ApplicationError as e:
        raise HTTPException(status_code=500, detail=str(e))
