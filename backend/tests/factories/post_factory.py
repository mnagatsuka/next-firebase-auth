"""Test data factory for blog posts."""

import sys
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

# Add backend to Python path
backend_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(backend_path))

from app.domain.entities import BlogPost, PostStatus


@dataclass
class PostFactory:
    """Factory for creating test blog post instances."""
    
    @staticmethod
    def create(
        id: str = "post-123",
        title: str = "Test Blog Post",
        content: str = "This is a test blog post content with lots of interesting information.",
        excerpt: str = "This is a test excerpt for the blog post.",
        author: str = "test-author",
        status: PostStatus = PostStatus.DRAFT,
        published_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ) -> BlogPost:
        """Create a blog post with default or provided values."""
        now = datetime.now(timezone.utc)
        return BlogPost(
            id=id,
            title=title,
            content=content,
            excerpt=excerpt,
            author=author,
            status=status,
            published_at=published_at,
            created_at=created_at or now,
            updated_at=updated_at or now
        )
    
    @staticmethod
    def create_published() -> BlogPost:
        """Create a published blog post."""
        now = datetime.now(timezone.utc)
        return PostFactory.create(
            status=PostStatus.PUBLISHED,
            published_at=now
        )
    
    @staticmethod
    def create_draft() -> BlogPost:
        """Create a draft blog post."""
        return PostFactory.create(status=PostStatus.DRAFT)
    
    @staticmethod
    def create_with_author(author: str) -> BlogPost:
        """Create a blog post with specific author."""
        return PostFactory.create(author=author)
    
    @staticmethod
    def create_minimal() -> BlogPost:
        """Create a blog post with minimal valid data."""
        return PostFactory.create(
            title="Minimal Post",
            content="Minimal content.",
            excerpt="Minimal excerpt."
        )


# Usage examples:
# post = PostFactory.create()
# published_post = PostFactory.create_published()
# author_post = PostFactory.create_with_author("john-doe")