"""Implementation of Comments API using clean architecture."""

from typing import List, Dict, Any

from app.application.services.comments_service import CommentApplicationService
from app.infra.repositories.comments_repository import InMemoryCommentRepository
from app.domain.exceptions import CommentNotFoundError, CommentValidationError, PostNotFoundError

# Generated models
import sys
from pathlib import Path
generated_path = Path(__file__).parent.parent / "generated" / "src"
sys.path.insert(0, str(generated_path))

from generated_fastapi_server.models.comment import Comment as ApiComment
from generated_fastapi_server.models.create_comment_request import CreateCommentRequest
from generated_fastapi_server.models.comments_response import CommentsResponse
from generated_fastapi_server.models.api_response_status import ApiResponseStatus

from fastapi import HTTPException


class CommentsImplementation:
    """Implementation of the Comments API using layered architecture."""
    
    def __init__(self):
        # Infrastructure layer
        self.comment_repository = InMemoryCommentRepository()
        # Application layer
        self.comment_service = CommentApplicationService(self.comment_repository)
    
    async def create_comment(self, post_id: str, create_comment_request: CreateCommentRequest) -> ApiComment:
        """Create a new comment using clean architecture layers."""
        try:
            # Call application service (use case)
            comment_data = await self.comment_service.create_comment(
                post_id=post_id,
                content=create_comment_request.content,
                author=create_comment_request.author
            )
            
            # Convert domain data to generated API models
            return self._convert_to_api_model(comment_data)
            
        except PostNotFoundError:
            raise HTTPException(status_code=404, detail="Post not found")
        except CommentValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    async def get_post_comments(self, post_id: str, limit: int = 10) -> CommentsResponse:
        """Get comments for a specific post."""
        try:
            comments_data = await self.comment_service.get_comments_by_post(
                post_id=post_id, 
                limit=limit
            )
            
            # Convert domain data to API models
            api_comments = [self._convert_to_api_model(comment) for comment in comments_data]
            
            return CommentsResponse(
                status=ApiResponseStatus.SUCCESS,
                data=api_comments
            )
            
        except PostNotFoundError:
            raise HTTPException(status_code=404, detail="Post not found")
    
    def _convert_to_api_model(self, comment_data: Dict[str, Any]) -> ApiComment:
        """Convert domain data to generated API model."""
        return ApiComment(
            id=comment_data["id"],
            content=comment_data["content"],
            author=comment_data["author"],
            createdAt=comment_data["createdAt"],
            postId=comment_data["postId"]
        )