"""Domain services for business logic that doesn't belong in entities."""

from typing import List, Optional, Protocol
from .entities import BlogPost, PostStatus, Comment
from .exceptions import (
    PostNotFoundError, 
    UnauthorizedPostAccessError,
    CommentNotFoundError,
    UnauthorizedCommentAccessError
)


class PostRepository(Protocol):
    """Repository interface for blog posts."""
    
    async def save(self, post: BlogPost) -> BlogPost:
        """Save a blog post."""
        ...
    
    async def find_by_id(self, post_id: str) -> Optional[BlogPost]:
        """Find a blog post by ID."""
        ...
    
    async def find_by_author(self, author: str, status: Optional[PostStatus] = None) -> List[BlogPost]:
        """Find blog posts by author."""
        ...
    
    async def find_published(self, page: int = 1, limit: int = 10, author: Optional[str] = None) -> List[BlogPost]:
        """Find published blog posts with pagination."""
        ...
    
    async def find_by_author_with_pagination(self, author: str, page: int = 1, limit: int = 10, status: Optional[PostStatus] = None) -> List[BlogPost]:
        """Find blog posts by author with pagination and status filtering."""
        ...
    
    async def delete(self, post_id: str) -> None:
        """Delete a blog post."""
        ...
    
    async def exists_by_id(self, post_id: str) -> bool:
        """Check if a blog post exists."""
        ...


class PostService:
    """Domain service for blog post business logic."""
    
    def __init__(self, post_repository: PostRepository):
        self._post_repository = post_repository
    
    async def create_post(self, title: str, content: str, excerpt: str, author: str, status: str = "draft") -> BlogPost:
        """Create a new blog post with business validation."""
        # Create the post using the factory method
        post = BlogPost.create_new(
            title=title,
            content=content,
            excerpt=excerpt,
            author=author,
            status=status
        )
        
        # Save and return
        return await self._post_repository.save(post)
    
    async def update_post(self, post_id: str, user_id: str, title: str = None, 
                         content: str = None, excerpt: str = None) -> BlogPost:
        """Update an existing blog post."""
        # Find the post
        post = await self._post_repository.find_by_id(post_id)
        if not post:
            raise PostNotFoundError(f"Post with ID {post_id} not found")
        
        # Check permissions
        if not post.can_be_updated_by(user_id):
            raise UnauthorizedPostAccessError("User not authorized to update this post")
        
        # Update content
        post.update_content(title=title, content=content, excerpt=excerpt)
        
        # Save and return
        return await self._post_repository.save(post)
    
    async def publish_post(self, post_id: str, user_id: str) -> BlogPost:
        """Publish a blog post."""
        post = await self._post_repository.find_by_id(post_id)
        if not post:
            raise PostNotFoundError(f"Post with ID {post_id} not found")
        
        if not post.can_be_updated_by(user_id):
            raise UnauthorizedPostAccessError("User not authorized to publish this post")
        
        post.publish()
        return await self._post_repository.save(post)
    
    async def unpublish_post(self, post_id: str, user_id: str) -> BlogPost:
        """Unpublish a blog post."""
        post = await self._post_repository.find_by_id(post_id)
        if not post:
            raise PostNotFoundError(f"Post with ID {post_id} not found")
        
        if not post.can_be_updated_by(user_id):
            raise UnauthorizedPostAccessError("User not authorized to unpublish this post")
        
        post.unpublish()
        return await self._post_repository.save(post)
    
    async def delete_post(self, post_id: str, user_id: str) -> None:
        """Delete a blog post."""
        post = await self._post_repository.find_by_id(post_id)
        if not post:
            raise PostNotFoundError(f"Post with ID {post_id} not found")
        
        if not post.can_be_deleted_by(user_id):
            raise UnauthorizedPostAccessError("User not authorized to delete this post")
        
        await self._post_repository.delete(post_id)
    
    async def get_post_by_id(self, post_id: str) -> BlogPost:
        """Get a blog post by ID."""
        post = await self._post_repository.find_by_id(post_id)
        if not post:
            raise PostNotFoundError(f"Post with ID {post_id} not found")
        
        return post
    
    async def get_published_posts(self, page: int = 1, limit: int = 10, 
                                 author: Optional[str] = None) -> List[BlogPost]:
        """Get published blog posts with pagination."""
        if page < 1:
            page = 1
        if limit < 1 or limit > 50:
            limit = 10
        
        return await self._post_repository.find_published(
            page=page, 
            limit=limit, 
            author=author
        )
    
    async def get_posts_by_author(self, author: str, status: Optional[PostStatus] = None) -> List[BlogPost]:
        """Get blog posts by author."""
        return await self._post_repository.find_by_author(author, status)
    
    async def get_posts_by_author_with_pagination(self, author: str, page: int = 1, limit: int = 10, status: Optional[PostStatus] = None) -> List[BlogPost]:
        """Get blog posts by author with pagination and status filtering."""
        if page < 1:
            page = 1
        if limit < 1 or limit > 50:
            limit = 10
        
        return await self._post_repository.find_by_author_with_pagination(
            author=author,
            page=page,
            limit=limit,
            status=status
        )


class CommentRepository(Protocol):
    """Repository interface for comments."""
    
    async def save(self, comment: Comment) -> Comment:
        """Save a comment."""
        ...
    
    async def find_by_id(self, comment_id: str) -> Optional[Comment]:
        """Find a comment by ID."""
        ...
    
    async def find_by_post_id(self, post_id: str, limit: int = 10) -> List[Comment]:
        """Find comments by post ID."""
        ...
    
    async def find_by_author(self, author: str) -> List[Comment]:
        """Find comments by author."""
        ...
    
    async def delete(self, comment_id: str) -> None:
        """Delete a comment."""
        ...
    
    async def exists_by_id(self, comment_id: str) -> bool:
        """Check if a comment exists."""
        ...


class CommentService:
    """Domain service for comment business logic."""
    
    def __init__(self, comment_repository: CommentRepository, post_repository: PostRepository):
        self._comment_repository = comment_repository
        self._post_repository = post_repository
    
    async def create_comment(self, content: str, author: str, post_id: str) -> Comment:
        """Create a new comment with business validation."""
        # Verify the post exists
        post_exists = await self._post_repository.exists_by_id(post_id)
        if not post_exists:
            raise PostNotFoundError(f"Post with ID {post_id} not found")
        
        # Create the comment using the factory method
        comment = Comment.create_new(
            content=content,
            author=author,
            post_id=post_id
        )
        
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
            raise UnauthorizedCommentAccessError("User not authorized to update this comment")
        
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
            raise UnauthorizedCommentAccessError("User not authorized to delete this comment")
        
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