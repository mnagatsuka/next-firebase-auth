"""Infrastructure implementation of post repository."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from app.domain.entities import BlogPost, PostStatus
from app.domain.services import PostRepository


class InMemoryPostRepository(PostRepository):
    """In-memory implementation of post repository for development/testing."""
    
    def __init__(self):
        self._posts: Dict[str, BlogPost] = {}
    
    async def save(self, post: BlogPost) -> BlogPost:
        """Save a blog post."""
        # Update the updated_at timestamp
        post.updated_at = datetime.now(timezone.utc)
        self._posts[post.id] = post
        return post
    
    async def find_by_id(self, post_id: str) -> Optional[BlogPost]:
        """Find a blog post by ID."""
        return self._posts.get(post_id)
    
    async def find_by_author(self, author: str, status: Optional[PostStatus] = None) -> List[BlogPost]:
        """Find blog posts by author."""
        posts = [post for post in self._posts.values() if post.author == author]
        
        if status:
            posts = [post for post in posts if post.status == status]
        
        # Sort by created_at descending
        posts.sort(key=lambda p: p.created_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
        return posts
    
    async def find_published(self, page: int = 1, limit: int = 10, author: Optional[str] = None) -> List[BlogPost]:
        """Find published blog posts with pagination."""
        # Filter for published posts
        posts = [post for post in self._posts.values() if post.status == PostStatus.PUBLISHED]
        
        # Filter by author if specified
        if author:
            posts = [post for post in posts if post.author == author]
        
        # Sort by published_at descending
        posts.sort(key=lambda p: p.published_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
        
        # Apply pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        return posts[start_idx:end_idx]
    
    async def delete(self, post_id: str) -> None:
        """Delete a blog post."""
        if post_id in self._posts:
            del self._posts[post_id]
    
    async def exists_by_id(self, post_id: str) -> bool:
        """Check if a blog post exists."""
        return post_id in self._posts


# Future database implementation would go here
class DatabasePostRepository(PostRepository):
    """Database implementation of post repository (placeholder)."""
    
    def __init__(self, db_connection):
        self._db = db_connection
    
    async def save(self, post: BlogPost) -> BlogPost:
        """Save a blog post to database."""
        # This would implement actual database operations
        # For now, raising NotImplementedError to indicate it's a placeholder
        raise NotImplementedError("Database repository not implemented yet")
    
    async def find_by_id(self, post_id: str) -> Optional[BlogPost]:
        """Find a blog post by ID from database."""
        raise NotImplementedError("Database repository not implemented yet")
    
    async def find_by_author(self, author: str, status: Optional[PostStatus] = None) -> List[BlogPost]:
        """Find blog posts by author from database."""
        raise NotImplementedError("Database repository not implemented yet")
    
    async def find_published(self, page: int = 1, limit: int = 10, author: Optional[str] = None) -> List[BlogPost]:
        """Find published blog posts with pagination from database."""
        raise NotImplementedError("Database repository not implemented yet")
    
    async def delete(self, post_id: str) -> None:
        """Delete a blog post from database."""
        raise NotImplementedError("Database repository not implemented yet")
    
    async def exists_by_id(self, post_id: str) -> bool:
        """Check if a blog post exists in database."""
        raise NotImplementedError("Database repository not implemented yet")