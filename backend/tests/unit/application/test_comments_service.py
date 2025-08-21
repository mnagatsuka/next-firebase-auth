"""Unit tests for CommentApplicationService."""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timezone

# Add backend to Python path
backend_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(backend_path))

from app.application.services.comments_service import CommentApplicationService
from app.domain.entities import Comment
from app.domain.exceptions import PostNotFoundError, CommentValidationError
from app.application.exceptions import NotFoundError, ValidationError


class TestCommentApplicationService:
    """Test suite for CommentApplicationService."""
    
    def setup_method(self):
        """Set up test dependencies."""
        self.comment_repository = Mock()
        self.post_repository = Mock()
        self.comment_service = CommentApplicationService(self.comment_repository, self.post_repository)
    
    @pytest.mark.asyncio
    async def test_create_comment_with_valid_data_returns_comment_dict(self):
        """Test creating a comment with valid data returns proper dict."""
        # Arrange
        created_comment = Comment(
            id="comment-123",
            content="Test comment",
            user_id="test-user-uid",
            post_id="post-123",
            created_at=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        )
        
        # Mock the domain service method
        self.comment_service.comment_service.create_comment = AsyncMock(return_value=created_comment)
        
        # Act
        result = await self.comment_service.create_comment(
            post_id="post-123",
            content="Test comment",
            user_id="test-user-uid"
        )
        
        # Assert
        assert result["id"] == "comment-123"
        assert result["content"] == "Test comment"
        assert result["userId"] == "test-user-uid"
        assert result["postId"] == "post-123"
        assert result["createdAt"] == datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        
        # Verify domain service was called
        self.comment_service.comment_service.create_comment.assert_called_once_with(
            content="Test comment",
            user_id="test-user-uid",
            post_id="post-123"
        )
    
    @pytest.mark.asyncio
    async def test_create_comment_for_nonexistent_post_raises_error(self):
        """Test creating a comment for nonexistent post raises NotFoundError."""
        # Arrange
        self.comment_service.comment_service.create_comment = AsyncMock(
            side_effect=PostNotFoundError("Post with ID post-123 not found")
        )
        
        # Act & Assert
        with pytest.raises(NotFoundError, match="Post with ID post-123 not found"):
            await self.comment_service.create_comment(
                post_id="post-123",
                content="Test comment",
                user_id="test-user-uid"
            )
    
    @pytest.mark.asyncio
    async def test_get_comments_by_post_returns_comment_list(self):
        """Test getting comments by post returns list of comment dicts."""
        # Arrange
        comments = [
            Comment(
                id="comment-1",
                content="First comment",
                user_id="user-1",
                post_id="post-123",
                created_at=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            ),
            Comment(
                id="comment-2",
                content="Second comment",
                user_id="user-2",
                post_id="post-123",
                created_at=datetime(2024, 1, 1, 13, 0, 0, tzinfo=timezone.utc)
            )
        ]
        
        self.comment_service.comment_service.get_comments_by_post = AsyncMock(return_value=comments)
        
        # Act
        result = await self.comment_service.get_comments_by_post("post-123", limit=10)
        
        # Assert
        assert len(result) == 2
        assert result[0]["id"] == "comment-1"
        assert result[0]["content"] == "First comment"
        assert result[1]["id"] == "comment-2"
        assert result[1]["content"] == "Second comment"
        
        # Verify domain service was called
        self.comment_service.comment_service.get_comments_by_post.assert_called_once_with("post-123", 10)
    
    @pytest.mark.asyncio
    async def test_get_comments_by_nonexistent_post_raises_error(self):
        """Test getting comments for nonexistent post raises PostNotFoundError."""
        # Arrange
        self.comment_service.comment_service.get_comments_by_post = AsyncMock(
            side_effect=PostNotFoundError("Post with ID post-123 not found")
        )
        
        # Act & Assert
        with pytest.raises(PostNotFoundError, match="Post with ID post-123 not found"):
            await self.comment_service.get_comments_by_post("post-123")
    
    def test_convert_to_dict_formats_comment_correctly(self):
        """Test that _convert_to_dict formats comment data correctly."""
        # Arrange
        comment = Comment(
            id="comment-123",
            content="Test content",
            user_id="test-user-uid",
            post_id="post-123",
            created_at=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        )
        
        # Act
        result = self.comment_service._convert_to_dict(comment)
        
        # Assert
        expected = {
            "id": "comment-123",
            "content": "Test content",
            "userId": "test-user-uid",
            "postId": "post-123",
            "createdAt": datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        }
        assert result == expected