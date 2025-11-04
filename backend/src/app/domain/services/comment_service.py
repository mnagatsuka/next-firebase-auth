"""Domain service for comment business logic and repository protocol."""

from typing import List, Optional, Protocol

from app.domain.entities import Comment
from app.domain.exceptions import (
    PostNotFoundError,
    CommentNotFoundError,
    UnauthorizedCommentAccessError,
)
from .post_service import PostRepository


class CommentRepository(Protocol):
    """Repository interface for comments."""

    async def save(self, comment: Comment) -> Comment: ...

    async def find_by_id(self, comment_id: str) -> Optional[Comment]: ...

    async def find_by_post_id(self, post_id: str, limit: int = 10) -> List[Comment]: ...

    async def find_by_author(self, author: str) -> List[Comment]: ...

    async def delete(self, comment_id: str) -> None: ...

    async def exists_by_id(self, comment_id: str) -> bool: ...


class CommentService:
    """Domain service for comment business logic."""

    def __init__(self, comment_repository: CommentRepository, post_repository: PostRepository):
        self._comment_repository = comment_repository
        self._post_repository = post_repository

    async def create_comment(self, content: str, user_id: str, post_id: str) -> Comment:
        """Create a new comment with business validation."""
        # Verify the post exists
        post_exists = await self._post_repository.exists_by_id(post_id)
        if not post_exists:
            raise PostNotFoundError(f"Post with ID {post_id} not found")

        # Create the comment using the factory method
        comment = Comment.create_new(content=content, user_id=user_id, post_id=post_id)

        # Save and return
        return await self._comment_repository.save(comment)

    async def update_comment(self, comment_id: str, user_id: str, content: str) -> Comment:
        """Update an existing comment."""
        # Find the comment
        comment = await self._comment_repository.find_by_id(comment_id)
        if not comment:
            raise CommentNotFoundError(f"Comment with ID {comment_id} not found")

        # Check permissions
        if not comment.can_be_updated_by(user_id):
            raise UnauthorizedCommentAccessError(
                "User not authorized to update this comment"
            )

        # Update content
        comment.update_content(content)

        # Save and return
        return await self._comment_repository.save(comment)

    async def delete_comment(self, comment_id: str, user_id: str) -> None:
        """Delete a comment."""
        comment = await self._comment_repository.find_by_id(comment_id)
        if not comment:
            raise CommentNotFoundError(f"Comment with ID {comment_id} not found")

        if not comment.can_be_deleted_by(user_id):
            raise UnauthorizedCommentAccessError(
                "User not authorized to delete this comment"
            )

        await self._comment_repository.delete(comment_id)

    async def get_comments_by_post(self, post_id: str, limit: int = 10) -> List[Comment]:
        """Get comments for a specific post."""
        # Verify the post exists
        post_exists = await self._post_repository.exists_by_id(post_id)
        if not post_exists:
            raise PostNotFoundError(f"Post with ID {post_id} not found")

        if limit < 1 or limit > 100:
            limit = 10

        return await self._comment_repository.find_by_post_id(post_id, limit)

    async def get_comments_by_author(self, author: str) -> List[Comment]:
        """Get comments by author."""
        return await self._comment_repository.find_by_author(author)

