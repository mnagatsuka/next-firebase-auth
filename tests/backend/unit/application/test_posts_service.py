"""Unit tests for PostApplicationService."""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock

# Add backend to Python path
backend_path = Path(__file__).parent.parent.parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_path))

from app.application.services.posts_service import PostApplicationService
from app.application.exceptions import (
    ValidationError, 
    NotFoundError, 
    ForbiddenError,
    ApplicationError
)
from app.domain.exceptions import (
    PostNotFoundError, 
    UnauthorizedPostAccessError, 
    PostValidationError
)

# Import test factory
tests_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(tests_path))
from factories.post_factory import PostFactory


class TestPostApplicationService:
    """Test suite for PostApplicationService."""
    
    def setup_method(self):
        """Set up test dependencies."""
        self.post_repository = Mock()
        self.post_service = PostApplicationService(self.post_repository)
    
    @pytest.mark.asyncio
    async def test_create_post_with_valid_data_returns_dict(self):
        """Test creating a post through the application service."""
        # Arrange
        created_post = PostFactory.create()
        self.post_service.post_service.create_post = AsyncMock(return_value=created_post)
        
        # Act
        result = await self.post_service.create_post(
            title="Test Post",
            content="Test content",
            excerpt="Test excerpt",
            author="test-author"
        )
        
        # Assert
        assert isinstance(result, dict)
        assert result["title"] == "Test Blog Post"
        assert result["content"] == "This is a test blog post content with lots of interesting information."
        assert result["excerpt"] == "This is a test excerpt for the blog post."
        assert result["author"] == "test-author"
        assert result["status"] == "draft"
        assert "id" in result
        self.post_service.post_service.create_post.assert_called_once_with(
            title="Test Post",
            content="Test content",
            excerpt="Test excerpt",
            author="test-author"
        )
    
    @pytest.mark.asyncio
    async def test_create_post_with_invalid_data_raises_validation_error(self):
        """Test that creating post with invalid data raises validation error."""
        # Arrange
        self.post_service.post_service.create_post = AsyncMock(
            side_effect=ValueError("Title cannot be empty")
        )
        
        # Act & Assert
        with pytest.raises(ValidationError, match="Title cannot be empty"):
            await self.post_service.create_post(
                title="",
                content="Test content",
                excerpt="Test excerpt",
                author="test-author"
            )
    
    @pytest.mark.asyncio
    async def test_create_post_with_service_error_raises_application_error(self):
        """Test that service errors are wrapped in application errors."""
        # Arrange
        self.post_service.post_service.create_post = AsyncMock(
            side_effect=Exception("Database connection failed")
        )
        
        # Act & Assert
        with pytest.raises(ApplicationError, match="Failed to create post"):
            await self.post_service.create_post(
                title="Test Post",
                content="Test content",
                excerpt="Test excerpt",
                author="test-author"
            )
    
    @pytest.mark.asyncio
    async def test_update_post_with_valid_data_returns_dict(self):
        """Test updating a post through the application service."""
        # Arrange
        updated_post = PostFactory.create(title="Updated Title")
        self.post_service.post_service.update_post = AsyncMock(return_value=updated_post)
        
        # Act
        result = await self.post_service.update_post(
            post_id="post-123",
            user_id="test-author",
            title="Updated Title"
        )
        
        # Assert
        assert isinstance(result, dict)
        assert result["title"] == "Updated Title"
        self.post_service.post_service.update_post.assert_called_once_with(
            post_id="post-123",
            user_id="test-author",
            title="Updated Title",
            content=None,
            excerpt=None
        )
    
    @pytest.mark.asyncio
    async def test_update_nonexistent_post_raises_not_found_error(self):
        """Test that updating non-existent post raises not found error."""
        # Arrange
        self.post_service.post_service.update_post = AsyncMock(
            side_effect=PostNotFoundError("Post not found")
        )
        
        # Act & Assert
        with pytest.raises(NotFoundError, match="Post with ID post-123 not found"):
            await self.post_service.update_post(
                post_id="post-123",
                user_id="test-author",
                title="Updated Title"
            )
    
    @pytest.mark.asyncio
    async def test_update_post_with_unauthorized_user_raises_forbidden_error(self):
        """Test that unauthorized update raises forbidden error."""
        # Arrange
        self.post_service.post_service.update_post = AsyncMock(
            side_effect=UnauthorizedPostAccessError("Not authorized")
        )
        
        # Act & Assert
        with pytest.raises(ForbiddenError, match="You don't have permission to update this post"):
            await self.post_service.update_post(
                post_id="post-123",
                user_id="wrong-author",
                title="Updated Title"
            )
    
    @pytest.mark.asyncio
    async def test_delete_post_calls_service_delete(self):
        """Test deleting a post through the application service."""
        # Arrange
        self.post_service.post_service.delete_post = AsyncMock()
        
        # Act
        await self.post_service.delete_post("post-123", "test-author")
        
        # Assert
        self.post_service.post_service.delete_post.assert_called_once_with(
            "post-123", "test-author"
        )
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_post_raises_not_found_error(self):
        """Test that deleting non-existent post raises not found error."""
        # Arrange
        self.post_service.post_service.delete_post = AsyncMock(
            side_effect=PostNotFoundError("Post not found")
        )
        
        # Act & Assert
        with pytest.raises(NotFoundError, match="Post with ID post-123 not found"):
            await self.post_service.delete_post("post-123", "test-author")
    
    @pytest.mark.asyncio
    async def test_delete_post_with_unauthorized_user_raises_forbidden_error(self):
        """Test that unauthorized delete raises forbidden error."""
        # Arrange
        self.post_service.post_service.delete_post = AsyncMock(
            side_effect=UnauthorizedPostAccessError("Not authorized")
        )
        
        # Act & Assert
        with pytest.raises(ForbiddenError, match="You don't have permission to delete this post"):
            await self.post_service.delete_post("post-123", "wrong-author")
    
    @pytest.mark.asyncio
    async def test_get_post_by_id_returns_dict_when_exists(self):
        """Test getting a post by ID returns formatted dict."""
        # Arrange
        post = PostFactory.create()
        self.post_service.post_service.get_post_by_id = AsyncMock(return_value=post)
        
        # Act
        result = await self.post_service.get_post_by_id("post-123")
        
        # Assert
        assert isinstance(result, dict)
        assert result["id"] == post.id
        assert result["title"] == post.title
        self.post_service.post_service.get_post_by_id.assert_called_once_with("post-123")
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_post_raises_not_found_error(self):
        """Test that getting non-existent post raises not found error."""
        # Arrange
        self.post_service.post_service.get_post_by_id = AsyncMock(
            side_effect=PostNotFoundError("Post not found")
        )
        
        # Act & Assert
        with pytest.raises(NotFoundError, match="Post with ID post-123 not found"):
            await self.post_service.get_post_by_id("post-123")
    
    @pytest.mark.asyncio
    async def test_get_posts_returns_paginated_response(self):
        """Test getting posts returns paginated response."""
        # Arrange
        posts = [PostFactory.create_published(), PostFactory.create_published()]
        self.post_service.post_service.get_published_posts = AsyncMock(return_value=posts)
        
        # Act
        result = await self.post_service.get_posts(page=1, limit=10, status="published")
        
        # Assert
        assert isinstance(result, dict)
        assert "data" in result
        assert "pagination" in result
        assert len(result["data"]) == 2
        assert result["pagination"]["page"] == 1
        assert result["pagination"]["limit"] == 10
        self.post_service.post_service.get_published_posts.assert_called_once_with(
            page=1, limit=10, author=None
        )
    
    @pytest.mark.asyncio
    async def test_get_posts_with_invalid_status_defaults_to_published(self):
        """Test that invalid status defaults to published."""
        # Arrange
        self.post_service.post_service.get_published_posts = AsyncMock(return_value=[])
        
        # Act
        await self.post_service.get_posts(status="invalid")
        
        # Assert
        self.post_service.post_service.get_published_posts.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_posts_with_draft_status_returns_empty_for_now(self):
        """Test that draft status returns empty list (authorization not implemented)."""
        # Act
        result = await self.post_service.get_posts(status="draft")
        
        # Assert
        assert result["data"] == []
    
    @pytest.mark.asyncio
    async def test_publish_post_returns_updated_dict(self):
        """Test publishing a post through the application service."""
        # Arrange
        published_post = PostFactory.create_published()
        self.post_service.post_service.publish_post = AsyncMock(return_value=published_post)
        
        # Act
        result = await self.post_service.publish_post("post-123", "test-author")
        
        # Assert
        assert isinstance(result, dict)
        assert result["status"] == "published"
        self.post_service.post_service.publish_post.assert_called_once_with(
            "post-123", "test-author"
        )
    
    @pytest.mark.asyncio
    async def test_publish_nonexistent_post_raises_not_found_error(self):
        """Test that publishing non-existent post raises not found error."""
        # Arrange
        self.post_service.post_service.publish_post = AsyncMock(
            side_effect=PostNotFoundError("Post not found")
        )
        
        # Act & Assert
        with pytest.raises(NotFoundError, match="Post with ID post-123 not found"):
            await self.post_service.publish_post("post-123", "test-author")
    
    @pytest.mark.asyncio
    async def test_publish_post_with_unauthorized_user_raises_forbidden_error(self):
        """Test that unauthorized publish raises forbidden error."""
        # Arrange
        self.post_service.post_service.publish_post = AsyncMock(
            side_effect=UnauthorizedPostAccessError("Not authorized")
        )
        
        # Act & Assert
        with pytest.raises(ForbiddenError, match="You don't have permission to publish this post"):
            await self.post_service.publish_post("post-123", "wrong-author")
    
    def test_post_to_dict_converts_entity_to_api_format(self):
        """Test that _post_to_dict converts domain entity to API format."""
        # Arrange
        post = PostFactory.create()
        
        # Act
        result = self.post_service._post_to_dict(post)
        
        # Assert
        assert isinstance(result, dict)
        assert result["id"] == post.id
        assert result["title"] == post.title
        assert result["content"] == post.content
        assert result["excerpt"] == post.excerpt
        assert result["author"] == post.author
        assert result["status"] == post.status.value
        assert "publishedAt" in result
        assert "createdAt" in result
        assert "updatedAt" in result
    
    def test_post_to_summary_dict_converts_entity_to_summary_format(self):
        """Test that _post_to_summary_dict converts domain entity to summary format."""
        # Arrange
        post = PostFactory.create()
        
        # Act
        result = self.post_service._post_to_summary_dict(post)
        
        # Assert
        assert isinstance(result, dict)
        assert result["id"] == post.id
        assert result["title"] == post.title
        assert result["excerpt"] == post.excerpt
        assert result["author"] == post.author
        assert result["status"] == post.status.value
        assert "publishedAt" in result
        # Summary should not include full content
        assert "content" not in result