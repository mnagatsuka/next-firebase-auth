"""Unit tests for PostService domain service."""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timezone

# Add backend to Python path
backend_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(backend_path))

from app.domain.services import PostService
from app.domain.entities import BlogPost, PostStatus
from app.domain.exceptions import PostNotFoundError, UnauthorizedPostAccessError

# Import test factory
tests_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(tests_path))
from factories.post_factory import PostFactory


class TestPostService:
    """Test suite for PostService domain service."""
    
    def setup_method(self):
        """Set up test dependencies."""
        self.post_repository = Mock()
        self.post_service = PostService(self.post_repository)
    
    @pytest.mark.asyncio
    async def test_create_post_with_valid_data_returns_post(self):
        """Test creating a post through the service."""
        # Arrange
        expected_post = PostFactory.create()
        self.post_repository.save = AsyncMock(return_value=expected_post)
        
        # Act
        result = await self.post_service.create_post(
            title="Test Post",
            content="Test content",
            excerpt="Test excerpt",
            author="test-author"
        )
        
        # Assert
        assert result.title == "Test Blog Post"
        assert result.content == "This is a test blog post content with lots of interesting information."
        assert result.excerpt == "This is a test excerpt for the blog post."
        assert result.author == "test-author"
        assert result.status == PostStatus.DRAFT
        self.post_repository.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_post_with_valid_data_returns_updated_post(self):
        """Test updating a post through the service."""
        # Arrange
        existing_post = PostFactory.create(author="test-author")
        updated_post = PostFactory.create(
            id=existing_post.id,
            title="Updated Title",
            author="test-author"
        )
        
        self.post_repository.find_by_id = AsyncMock(return_value=existing_post)
        self.post_repository.save = AsyncMock(return_value=updated_post)
        
        # Act
        result = await self.post_service.update_post(
            post_id="post-123",
            user_id="test-author",
            title="Updated Title"
        )
        
        # Assert
        assert result.title == "Updated Title"
        self.post_repository.find_by_id.assert_called_once_with("post-123")
        self.post_repository.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_nonexistent_post_raises_not_found_error(self):
        """Test that updating non-existent post raises error."""
        # Arrange
        self.post_repository.find_by_id = AsyncMock(return_value=None)
        
        # Act & Assert
        with pytest.raises(PostNotFoundError, match="Post with ID post-123 not found"):
            await self.post_service.update_post(
                post_id="post-123",
                user_id="test-author",
                title="Updated Title"
            )
    
    @pytest.mark.asyncio
    async def test_update_post_by_unauthorized_user_raises_error(self):
        """Test that updating post by unauthorized user raises error."""
        # Arrange
        existing_post = PostFactory.create(author="original-author")
        self.post_repository.find_by_id = AsyncMock(return_value=existing_post)
        
        # Act & Assert
        with pytest.raises(UnauthorizedPostAccessError, match="User not authorized to update this post"):
            await self.post_service.update_post(
                post_id="post-123",
                user_id="different-author",
                title="Updated Title"
            )
    
    @pytest.mark.asyncio
    async def test_publish_post_changes_status_to_published(self):
        """Test publishing a post through the service."""
        # Arrange
        draft_post = PostFactory.create_draft()
        published_post = PostFactory.create_published()
        
        self.post_repository.find_by_id = AsyncMock(return_value=draft_post)
        self.post_repository.save = AsyncMock(return_value=published_post)
        
        # Act
        result = await self.post_service.publish_post("post-123", "test-author")
        
        # Assert
        assert result.status == PostStatus.PUBLISHED
        self.post_repository.find_by_id.assert_called_once_with("post-123")
        self.post_repository.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_unpublish_post_changes_status_to_draft(self):
        """Test unpublishing a post through the service."""
        # Arrange
        published_post = PostFactory.create_published()
        draft_post = PostFactory.create_draft()
        
        self.post_repository.find_by_id = AsyncMock(return_value=published_post)
        self.post_repository.save = AsyncMock(return_value=draft_post)
        
        # Act
        result = await self.post_service.unpublish_post("post-123", "test-author")
        
        # Assert
        assert result.status == PostStatus.DRAFT
        self.post_repository.find_by_id.assert_called_once_with("post-123")
        self.post_repository.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_post_calls_repository_delete(self):
        """Test deleting a post through the service."""
        # Arrange
        existing_post = PostFactory.create(author="test-author")
        self.post_repository.find_by_id = AsyncMock(return_value=existing_post)
        self.post_repository.delete = AsyncMock()
        
        # Act
        await self.post_service.delete_post("post-123", "test-author")
        
        # Assert
        self.post_repository.find_by_id.assert_called_once_with("post-123")
        self.post_repository.delete.assert_called_once_with("post-123")
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_post_raises_not_found_error(self):
        """Test that deleting non-existent post raises error."""
        # Arrange
        self.post_repository.find_by_id = AsyncMock(return_value=None)
        
        # Act & Assert
        with pytest.raises(PostNotFoundError, match="Post with ID post-123 not found"):
            await self.post_service.delete_post("post-123", "test-author")
    
    @pytest.mark.asyncio
    async def test_delete_post_by_unauthorized_user_raises_error(self):
        """Test that deleting post by unauthorized user raises error."""
        # Arrange
        existing_post = PostFactory.create(author="original-author")
        self.post_repository.find_by_id = AsyncMock(return_value=existing_post)
        
        # Act & Assert
        with pytest.raises(UnauthorizedPostAccessError, match="User not authorized to delete this post"):
            await self.post_service.delete_post("post-123", "different-author")
    
    @pytest.mark.asyncio
    async def test_get_post_by_id_returns_post_when_exists(self):
        """Test getting a post by ID when it exists."""
        # Arrange
        expected_post = PostFactory.create()
        self.post_repository.find_by_id = AsyncMock(return_value=expected_post)
        
        # Act
        result = await self.post_service.get_post_by_id("post-123")
        
        # Assert
        assert result.id == expected_post.id
        assert result.title == expected_post.title
        self.post_repository.find_by_id.assert_called_once_with("post-123")
    
    @pytest.mark.asyncio
    async def test_get_post_by_id_raises_error_when_not_found(self):
        """Test that getting non-existent post raises error."""
        # Arrange
        self.post_repository.find_by_id = AsyncMock(return_value=None)
        
        # Act & Assert
        with pytest.raises(PostNotFoundError, match="Post with ID post-123 not found"):
            await self.post_service.get_post_by_id("post-123")
    
    @pytest.mark.asyncio
    async def test_get_published_posts_returns_published_posts(self):
        """Test getting published posts with pagination."""
        # Arrange
        published_posts = [
            PostFactory.create_published(),
            PostFactory.create_published()
        ]
        self.post_repository.find_published = AsyncMock(return_value=published_posts)
        
        # Act
        result = await self.post_service.get_published_posts(page=1, limit=10)
        
        # Assert
        assert len(result) == 2
        assert all(post.status == PostStatus.PUBLISHED for post in result)
        self.post_repository.find_published.assert_called_once_with(
            page=1, limit=10, author=None
        )
    
    @pytest.mark.asyncio
    async def test_get_published_posts_with_invalid_page_uses_default(self):
        """Test that invalid page number defaults to 1."""
        # Arrange
        self.post_repository.find_published = AsyncMock(return_value=[])
        
        # Act
        await self.post_service.get_published_posts(page=0, limit=10)
        
        # Assert
        self.post_repository.find_published.assert_called_once_with(
            page=1, limit=10, author=None
        )
    
    @pytest.mark.asyncio
    async def test_get_published_posts_with_invalid_limit_uses_default(self):
        """Test that invalid limit defaults to 10."""
        # Arrange
        self.post_repository.find_published = AsyncMock(return_value=[])
        
        # Act
        await self.post_service.get_published_posts(page=1, limit=100)
        
        # Assert
        self.post_repository.find_published.assert_called_once_with(
            page=1, limit=10, author=None
        )
    
    @pytest.mark.asyncio
    async def test_get_posts_by_author_returns_author_posts(self):
        """Test getting posts by specific author."""
        # Arrange
        author_posts = [
            PostFactory.create_with_author("specific-author"),
            PostFactory.create_with_author("specific-author")
        ]
        self.post_repository.find_by_author = AsyncMock(return_value=author_posts)
        
        # Act
        result = await self.post_service.get_posts_by_author("specific-author")
        
        # Assert
        assert len(result) == 2
        assert all(post.author == "specific-author" for post in result)
        self.post_repository.find_by_author.assert_called_once_with(
            "specific-author", None
        )