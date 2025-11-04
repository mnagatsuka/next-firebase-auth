"""Domain service for blog post business logic and repository protocol."""

from typing import List, Optional, Protocol

from app.domain.entities import BlogPost, PostStatus
from app.domain.exceptions import (
    PostNotFoundError,
    UnauthorizedPostAccessError,
)


class PostRepository(Protocol):
    """Repository interface for blog posts."""

    async def save(self, post: BlogPost) -> BlogPost: ...

    async def find_by_id(self, post_id: str) -> Optional[BlogPost]: ...

    async def find_by_author(
        self, author: str, status: Optional[PostStatus] = None
    ) -> List[BlogPost]: ...

    async def find_published(
        self, page: int = 1, limit: int = 10, author: Optional[str] = None
    ) -> List[BlogPost]: ...

    async def find_by_author_with_pagination(
        self,
        author: str,
        page: int = 1,
        limit: int = 10,
        status: Optional[PostStatus] = None,
    ) -> List[BlogPost]: ...

    async def delete(self, post_id: str) -> None: ...

    async def exists_by_id(self, post_id: str) -> bool: ...

    async def count_published(self, author: Optional[str] = None) -> int: ...

    async def count_by_author(
        self, author: str, status: Optional[PostStatus] = None
    ) -> int: ...


class PostService:
    """Domain service for blog post business logic."""

    def __init__(self, post_repository: PostRepository):
        self._post_repository = post_repository

    async def create_post(
        self, title: str, content: str, excerpt: str, author: str, status: str = "draft"
    ) -> BlogPost:
        """Create a new blog post with business validation."""
        # Create the post using the factory method
        post = BlogPost.create_new(
            title=title, content=content, excerpt=excerpt, author=author, status=status
        )

        # Save and return
        return await self._post_repository.save(post)

    async def update_post(
        self, post_id: str, user_id: str, title: str | None = None, content: str | None = None, excerpt: str | None = None
    ) -> BlogPost:
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

    async def get_published_posts(
        self, page: int = 1, limit: int = 10, author: Optional[str] = None
    ) -> List[BlogPost]:
        """Get published blog posts with pagination."""
        if page < 1:
            page = 1
        if limit < 1 or limit > 50:
            limit = 10

        return await self._post_repository.find_published(
            page=page, limit=limit, author=author
        )

    async def get_posts_by_author(
        self, author: str, status: Optional[PostStatus] = None
    ) -> List[BlogPost]:
        """Get blog posts by author."""
        return await self._post_repository.find_by_author(author, status)

    async def get_posts_by_author_with_pagination(
        self,
        author: str,
        page: int = 1,
        limit: int = 10,
        status: Optional[PostStatus] = None,
    ) -> List[BlogPost]:
        """Get blog posts by author with pagination and status filtering."""
        if page < 1:
            page = 1
        if limit < 1 or limit > 50:
            limit = 10

        return await self._post_repository.find_by_author_with_pagination(
            author=author, page=page, limit=limit, status=status
        )

