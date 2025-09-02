"""Application service for blog post operations."""

from typing import List, Optional
from datetime import datetime

from app.domain.entities import BlogPost, PostStatus
from app.domain.services import PostService
from app.domain.exceptions import (
    PostNotFoundError, 
    UnauthorizedPostAccessError, 
    PostValidationError
)
from app.application.exceptions import (
    ApplicationError, 
    ValidationError, 
    NotFoundError, 
    ForbiddenError
)
from app.shared.constants import (
    POST_STATUS_PUBLISHED, POST_STATUS_DRAFT, VALID_POST_STATUSES,
    DEFAULT_PAGE, DEFAULT_LIMIT
)


class PostApplicationService:
    """Application service for blog post operations."""
    
    def __init__(self, post_repository, comment_repository):
        self.post_service = PostService(post_repository)
        self.post_repository = post_repository
        self.comment_repository = comment_repository
    
    async def create_post(self, title: str, content: str, excerpt: str, author: str, status: str = "draft") -> dict:
        """Create a new blog post."""
        try:
            post = await self.post_service.create_post(
                title=title,
                content=content,
                excerpt=excerpt,
                author=author,
                status=status
            )
            return self._post_to_dict(post)
        except (ValueError, PostValidationError) as e:
            raise ValidationError(str(e))
        except Exception as e:
            raise ApplicationError(f"Failed to create post: {str(e)}")
    
    async def update_post(self, post_id: str, user_id: str, title: str = None, 
                         content: str = None, excerpt: str = None) -> dict:
        """Update an existing blog post."""
        try:
            post = await self.post_service.update_post(
                post_id=post_id,
                user_id=user_id,
                title=title,
                content=content,
                excerpt=excerpt
            )
            return self._post_to_dict(post)
        except PostNotFoundError:
            raise NotFoundError(f"Post with ID {post_id} not found")
        except UnauthorizedPostAccessError:
            raise ForbiddenError("You don't have permission to update this post")
        except (ValueError, PostValidationError) as e:
            raise ValidationError(str(e))
        except Exception as e:
            raise ApplicationError(f"Failed to update post: {str(e)}")
    
    async def delete_post(self, post_id: str, user_id: str) -> None:
        """Delete a blog post."""
        try:
            await self.post_service.delete_post(post_id, user_id)
        except PostNotFoundError:
            raise NotFoundError(f"Post with ID {post_id} not found")
        except UnauthorizedPostAccessError:
            raise ForbiddenError("You don't have permission to delete this post")
        except Exception as e:
            raise ApplicationError(f"Failed to delete post: {str(e)}")
    
    async def get_post_by_id(self, post_id: str) -> Optional[dict]:
        """Get a blog post by ID."""
        try:
            post = await self.post_service.get_post_by_id(post_id)
            return self._post_to_dict(post)
        except PostNotFoundError:
            raise NotFoundError(f"Post with ID {post_id} not found")
        except Exception as e:
            raise ApplicationError(f"Failed to get post: {str(e)}")
    
    async def get_posts(self, page: int = 1, limit: int = 10, status: str = "published", 
                       author: Optional[str] = None) -> dict:
        """Get blog posts with pagination and filtering."""
        try:
            
            # Validate status
            if status not in VALID_POST_STATUSES:
                status = POST_STATUS_PUBLISHED
            
            # For now, only return published posts for public API
            # In the future, add authorization to allow authors to see their drafts
            if status == POST_STATUS_PUBLISHED:
                posts = await self.post_service.get_published_posts(
                    page=page,
                    limit=limit,
                    author=author
                )
            else:
                # This would require additional authorization logic
                posts = []
            
            # Convert to response format
            post_summaries = [self._post_to_summary_dict(post) for post in posts]
            
            # Get total count for pagination (using existing posts for now)
            if status == POST_STATUS_PUBLISHED:
                # For now, use current implementation - optimize later when repository supports count
                total_count = len(post_summaries) if len(post_summaries) < limit else limit * page
            else:
                total_count = 0
            
            response = {
                "data": post_summaries,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_count
                }
            }
            return response
        except Exception as e:
            raise ApplicationError(f"Failed to get posts: {str(e)}")
    
    async def get_user_posts(self, user_id: str, page: int = 1, limit: int = 10, status: Optional[str] = None) -> dict:
        """Get blog posts for a specific user with pagination and filtering."""
        try:
            # Parse status filter
            status_filter = None
            if status == POST_STATUS_PUBLISHED:
                status_filter = PostStatus.PUBLISHED
            elif status == POST_STATUS_DRAFT:
                status_filter = PostStatus.DRAFT
            # If status is None or invalid, return all posts for the user
            
            # Get posts from domain service
            posts = await self.post_service.get_posts_by_author_with_pagination(
                author=user_id,
                page=page,
                limit=limit,
                status=status_filter
            )
            
            # Convert to response format
            post_summaries = [self._post_to_summary_dict(post) for post in posts]
            
            # Get total count for pagination (using existing posts for now)
            # TODO: Implement count_by_author in repository for efficiency
            total_count = len(post_summaries) if len(post_summaries) < limit else limit * page
            
            return {
                "data": post_summaries,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_count
                }
            }
        except Exception as e:
            raise ApplicationError(f"Failed to get user posts: {str(e)}")
    
    async def publish_post(self, post_id: str, user_id: str) -> dict:
        """Publish a blog post."""
        try:
            post = await self.post_service.publish_post(post_id, user_id)
            return self._post_to_dict(post)
        except PostNotFoundError:
            raise NotFoundError(f"Post with ID {post_id} not found")
        except UnauthorizedPostAccessError:
            raise ForbiddenError("You don't have permission to publish this post")
        except ValueError as e:
            raise ValidationError(str(e))
        except Exception as e:
            raise ApplicationError(f"Failed to publish post: {str(e)}")
    
    def _post_to_dict(self, post: BlogPost) -> dict:
        """Convert domain post entity to API response format."""
        return {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "excerpt": post.excerpt,
            "author": post.author,
            "publishedAt": post.published_at.isoformat() if post.published_at else None,
            "status": post.status.value,
            "createdAt": post.created_at.isoformat() if post.created_at else None,
            "updatedAt": post.updated_at.isoformat() if post.updated_at else None
        }
    
    def _post_to_summary_dict(self, post: BlogPost) -> dict:
        """Convert domain post entity to summary format for list views."""
        return {
            "id": post.id,
            "title": post.title,
            "excerpt": post.excerpt,
            "author": post.author,
            "publishedAt": post.published_at.isoformat() if post.published_at else None,
            "status": post.status.value
        }