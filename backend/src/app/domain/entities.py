"""Domain entities for the blog application."""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
import uuid


class PostStatus(Enum):
    """Blog post status enumeration."""
    DRAFT = "draft"
    PUBLISHED = "published"


@dataclass
class BlogPost:
    """Blog post domain entity with business logic."""
    
    id: str
    title: str
    content: str
    excerpt: str
    author: str
    published_at: Optional[datetime] = None
    status: PostStatus = PostStatus.DRAFT
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Basic validation and data cleaning."""
        if not self.title.strip():
            raise ValueError("Title cannot be empty")
        if not self.content.strip():
            raise ValueError("Content cannot be empty")
        if not self.excerpt.strip():
            raise ValueError("Excerpt cannot be empty")
        if not self.author.strip():
            raise ValueError("Author cannot be empty")
        
        # Clean up data
        self.title = self.title.strip()
        self.content = self.content.strip()
        self.excerpt = self.excerpt.strip()
        self.author = self.author.strip()
        
        # Set timestamps if not provided
        now = datetime.now(timezone.utc)
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now
    
    def publish(self) -> None:
        """Publish the blog post."""
        if self.status == PostStatus.PUBLISHED:
            raise ValueError("Post is already published")
        
        self.status = PostStatus.PUBLISHED
        self.published_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def unpublish(self) -> None:
        """Unpublish the blog post (set to draft)."""
        if self.status == PostStatus.DRAFT:
            raise ValueError("Post is already a draft")
        
        self.status = PostStatus.DRAFT
        self.published_at = None
        self.updated_at = datetime.now(timezone.utc)
    
    def update_content(self, title: str = None, content: str = None, excerpt: str = None) -> None:
        """Update post content fields."""
        if title is not None:
            if not title.strip():
                raise ValueError("Title cannot be empty")
            self.title = title.strip()
        
        if content is not None:
            if not content.strip():
                raise ValueError("Content cannot be empty")
            self.content = content.strip()
        
        if excerpt is not None:
            if not excerpt.strip():
                raise ValueError("Excerpt cannot be empty")
            self.excerpt = excerpt.strip()
        
        self.updated_at = datetime.now(timezone.utc)
    
    def is_published(self) -> bool:
        """Check if the post is published."""
        return self.status == PostStatus.PUBLISHED
    
    def can_be_updated_by(self, user_id: str) -> bool:
        """Check if the post can be updated by the given user."""
        # For now, only the author can update
        # In the future, this could include admin roles
        return self.author == user_id
    
    def can_be_deleted_by(self, user_id: str) -> bool:
        """Check if the post can be deleted by the given user."""
        # For now, only the author can delete
        # In the future, this could include admin roles
        return self.author == user_id
    
    @classmethod
    def create_new(cls, title: str, content: str, excerpt: str, author: str) -> 'BlogPost':
        """Factory method to create a new blog post."""
        post_id = str(uuid.uuid4())
        return cls(
            id=post_id,
            title=title,
            content=content,
            excerpt=excerpt,
            author=author,
            status=PostStatus.DRAFT
        )


@dataclass
class Comment:
    """Comment domain entity with business logic."""
    
    id: str
    content: str
    author: str
    post_id: str
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Basic validation and data cleaning."""
        if not self.content.strip():
            raise ValueError("Comment content cannot be empty")
        if not self.author.strip():
            raise ValueError("Author cannot be empty")
        if not self.post_id.strip():
            raise ValueError("Post ID cannot be empty")
        
        # Clean up data
        self.content = self.content.strip()
        self.author = self.author.strip()
        self.post_id = self.post_id.strip()
        
        # Set timestamp if not provided
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
    
    def update_content(self, content: str) -> None:
        """Update comment content."""
        if not content.strip():
            raise ValueError("Comment content cannot be empty")
        
        self.content = content.strip()
    
    def can_be_updated_by(self, user_id: str) -> bool:
        """Check if the comment can be updated by the given user."""
        # For now, only the author can update
        return self.author == user_id
    
    def can_be_deleted_by(self, user_id: str) -> bool:
        """Check if the comment can be deleted by the given user."""
        # For now, only the author can delete
        return self.author == user_id
    
    @classmethod
    def create_new(cls, content: str, author: str, post_id: str) -> 'Comment':
        """Factory method to create a new comment."""
        comment_id = str(uuid.uuid4())
        return cls(
            id=comment_id,
            content=content,
            author=author,
            post_id=post_id
        )