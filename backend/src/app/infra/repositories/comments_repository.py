"""In-memory repository implementation for comments."""

from typing import List, Optional, Dict
from app.domain.entities import Comment


class InMemoryCommentRepository:
    """In-memory implementation of comment repository for development/testing."""
    
    def __init__(self):
        self._comments: Dict[str, Comment] = {}
    
    async def save(self, comment: Comment) -> Comment:
        """Save a comment to the in-memory store."""
        self._comments[comment.id] = comment
        return comment
    
    async def find_by_id(self, comment_id: str) -> Optional[Comment]:
        """Find a comment by ID."""
        return self._comments.get(comment_id)
    
    async def find_by_post_id(self, post_id: str, limit: int = 10) -> List[Comment]:
        """Find comments by post ID with limit."""
        comments = [
            comment for comment in self._comments.values() 
            if comment.post_id == post_id
        ]
        # Sort by creation time (oldest first)
        comments.sort(key=lambda c: c.created_at)
        return comments[:limit]
    
    async def find_by_author(self, author: str) -> List[Comment]:
        """Find comments by author."""
        comments = [
            comment for comment in self._comments.values() 
            if comment.author == author
        ]
        # Sort by creation time (newest first)
        comments.sort(key=lambda c: c.created_at, reverse=True)
        return comments
    
    async def delete(self, comment_id: str) -> None:
        """Delete a comment."""
        if comment_id in self._comments:
            del self._comments[comment_id]
    
    async def exists_by_id(self, comment_id: str) -> bool:
        """Check if a comment exists."""
        return comment_id in self._comments
    
    def count_all(self) -> int:
        """Get total count of comments (for testing/debugging)."""
        return len(self._comments)
    
    def clear_all(self) -> None:
        """Clear all comments (for testing)."""
        self._comments.clear()
    
    def count_by_post_id(self, post_id: str) -> int:
        """Count comments for a specific post (for testing/debugging)."""
        return sum(1 for comment in self._comments.values() if comment.post_id == post_id)