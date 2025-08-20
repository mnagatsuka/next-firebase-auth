"""Unit tests for Comment domain entity."""

import pytest
import sys
from pathlib import Path
from freezegun import freeze_time
from datetime import datetime, timezone

# Add backend to Python path
backend_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(backend_path))

from app.domain.entities import Comment


class TestComment:
    """Test suite for Comment entity business rules."""
    
    def test_create_comment_with_valid_data_returns_comment(self):
        """Test creating a comment with valid data."""
        comment = Comment(
            id="comment-123",
            content="This is a test comment.",
            author="test-author",
            post_id="post-123"
        )
        
        assert comment.id == "comment-123"
        assert comment.content == "This is a test comment."
        assert comment.author == "test-author"
        assert comment.post_id == "post-123"
        assert comment.created_at is not None
    
    @freeze_time("2024-01-01 12:00:00")
    def test_create_comment_sets_created_timestamp(self):
        """Test that creating a comment sets the created timestamp."""
        comment = Comment(
            id="comment-123",
            content="Test comment",
            author="author",
            post_id="post-123"
        )
        
        assert comment.created_at == datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    
    def test_create_comment_with_empty_content_raises_error(self):
        """Test that creating a comment with empty content raises an error."""
        with pytest.raises(ValueError, match="Comment content cannot be empty"):
            Comment(
                id="comment-123",
                content="",
                author="author",
                post_id="post-123"
            )
    
    def test_create_comment_with_empty_author_raises_error(self):
        """Test that creating a comment with empty author raises an error."""
        with pytest.raises(ValueError, match="Author cannot be empty"):
            Comment(
                id="comment-123",
                content="Test content",
                author="",
                post_id="post-123"
            )
    
    def test_create_comment_with_empty_post_id_raises_error(self):
        """Test that creating a comment with empty post_id raises an error."""
        with pytest.raises(ValueError, match="Post ID cannot be empty"):
            Comment(
                id="comment-123",
                content="Test content",
                author="author",
                post_id=""
            )
    
    def test_update_content_with_valid_data_updates_content(self):
        """Test updating comment content with valid data."""
        comment = Comment(
            id="comment-123",
            content="Original content",
            author="author",
            post_id="post-123"
        )
        
        comment.update_content("Updated content")
        
        assert comment.content == "Updated content"
    
    def test_update_content_with_empty_data_raises_error(self):
        """Test that updating with empty content raises an error."""
        comment = Comment(
            id="comment-123",
            content="Original content",
            author="author",
            post_id="post-123"
        )
        
        with pytest.raises(ValueError, match="Comment content cannot be empty"):
            comment.update_content("")
    
    def test_can_be_updated_by_author_returns_true(self):
        """Test that author can update their comment."""
        comment = Comment(
            id="comment-123",
            content="Test content",
            author="test-author",
            post_id="post-123"
        )
        
        assert comment.can_be_updated_by("test-author") is True
    
    def test_can_be_updated_by_other_user_returns_false(self):
        """Test that other users cannot update the comment."""
        comment = Comment(
            id="comment-123",
            content="Test content",
            author="test-author",
            post_id="post-123"
        )
        
        assert comment.can_be_updated_by("other-user") is False
    
    def test_can_be_deleted_by_author_returns_true(self):
        """Test that author can delete their comment."""
        comment = Comment(
            id="comment-123",
            content="Test content",
            author="test-author",
            post_id="post-123"
        )
        
        assert comment.can_be_deleted_by("test-author") is True
    
    def test_can_be_deleted_by_other_user_returns_false(self):
        """Test that other users cannot delete the comment."""
        comment = Comment(
            id="comment-123",
            content="Test content",
            author="test-author",
            post_id="post-123"
        )
        
        assert comment.can_be_deleted_by("other-user") is False
    
    def test_create_new_factory_method_creates_comment_with_uuid(self):
        """Test that create_new factory method creates comment with UUID."""
        comment = Comment.create_new(
            content="Test content",
            author="test-author",
            post_id="post-123"
        )
        
        assert comment.content == "Test content"
        assert comment.author == "test-author"
        assert comment.post_id == "post-123"
        assert comment.id is not None
        assert len(comment.id) > 10  # UUID should be longer than 10 chars
        assert comment.created_at is not None