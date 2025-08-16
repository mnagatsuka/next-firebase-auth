"""Application service for comment-related use cases."""

from typing import Dict, Any, List
from datetime import datetime

from app.domain.entities import Comment
from app.domain.services import CommentService
from app.infra.repositories.comments_repository import InMemoryCommentRepository
from app.infra.repositories.posts_repository import InMemoryPostRepository


class CommentApplicationService:
    """Application service for comment-related use cases."""
    
    def __init__(self, comment_repository: InMemoryCommentRepository):
        # Get post repository instance - in a real app this would be injected
        self.post_repository = InMemoryPostRepository()
        self.comment_repository = comment_repository
        self.comment_service = CommentService(comment_repository, self.post_repository)
    
    async def create_comment(
        self, post_id: str, content: str, author: str
    ) -> Dict[str, Any]:
        """Create a new comment use case."""
        # Create comment through domain service
        comment = await self.comment_service.create_comment(
            content=content,
            author=author,
            post_id=post_id
        )
        
        # Return domain data compatible with generated models
        return self._convert_to_dict(comment)
    
    async def get_comments_by_post(
        self, post_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get comments for a specific post use case."""
        comments = await self.comment_service.get_comments_by_post(post_id, limit)
        
        # Convert to dicts compatible with generated models
        return [self._convert_to_dict(comment) for comment in comments]
    
    async def update_comment(
        self, comment_id: str, user_id: str, content: str
    ) -> Dict[str, Any]:
        """Update comment use case."""
        comment = await self.comment_service.update_comment(comment_id, user_id, content)
        return self._convert_to_dict(comment)
    
    async def delete_comment(self, comment_id: str, user_id: str) -> None:
        """Delete comment use case."""
        await self.comment_service.delete_comment(comment_id, user_id)
    
    async def get_comments_by_author(self, author: str) -> List[Dict[str, Any]]:
        """Get comments by author use case."""
        comments = await self.comment_service.get_comments_by_author(author)
        return [self._convert_to_dict(comment) for comment in comments]
    
    def _convert_to_dict(self, comment: Comment) -> Dict[str, Any]:
        """Convert domain entity to dict compatible with generated models."""
        return {
            "id": comment.id,
            "content": comment.content,
            "author": comment.author,
            "postId": comment.post_id,
            "createdAt": comment.created_at
        }