"""Integration tests for Comments API endpoints."""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from datetime import datetime, timezone

from app.main import app
from app.domain.entities import Comment


class TestCommentsEndpoints:
    """Integration tests for Comments API endpoints using generated models."""
    
    def setup_method(self):
        """Set up test client and mock dependencies."""
        self.client = TestClient(app)
        
        # Mock the comment repository to avoid dependencies
        self.mock_comment_repo_patcher = patch('app.api.comments_implementation.InMemoryCommentRepository')
        self.mock_comment_repo_class = self.mock_comment_repo_patcher.start()
        self.mock_comment_repo = Mock()
        self.mock_comment_repo_class.return_value = self.mock_comment_repo
        
        # Mock the post repository in the comment service
        self.mock_post_repo_patcher = patch('app.application.services.comments_service.InMemoryPostRepository')
        self.mock_post_repo_class = self.mock_post_repo_patcher.start()
        self.mock_post_repo = Mock()
        self.mock_post_repo_class.return_value = self.mock_post_repo
        
        # Setup default mock behavior
        self.mock_comment_repo.save.return_value = self._async_return(None)
        self.mock_comment_repo.find_by_post_id.return_value = self._async_return([])
        self.mock_post_repo.exists_by_id.return_value = self._async_return(True)
    
    def teardown_method(self):
        """Clean up mocks."""
        self.mock_comment_repo_patcher.stop()
        self.mock_post_repo_patcher.stop()
    
    def _async_return(self, value):
        """Helper to create async return value."""
        import asyncio
        future = asyncio.Future()
        future.set_result(value)
        return future
    
    def test_create_comment_with_valid_data_returns_201(self):
        """Test creating a comment with valid data returns 201 and correct response structure."""
        # Arrange
        comment_data = {
            "content": "This is a test comment.",
            "author": "test-author"
        }
        
        created_comment = Comment(
            id="comment-123",
            content="This is a test comment.",
            author="test-author",
            post_id="post-123",
            created_at=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        )
        
        self.mock_comment_repo.save.return_value = self._async_return(created_comment)
        
        # Act
        response = self.client.post("/posts/post-123/comments", json=comment_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == "comment-123"
        assert data["content"] == "This is a test comment."
        assert data["author"] == "test-author"
        assert data["postId"] == "post-123"
        
        # Verify post existence was checked
        self.mock_post_repo.exists_by_id.assert_called()
        # Verify comment was saved
        self.mock_comment_repo.save.assert_called()
    
    def test_create_comment_for_nonexistent_post_returns_404(self):
        """Test creating a comment for nonexistent post returns 404."""
        # Arrange
        comment_data = {
            "content": "This is a test comment.",
            "author": "test-author"
        }
        
        # Mock post doesn't exist
        self.mock_post_repo.exists_by_id.return_value = self._async_return(False)
        
        # Act
        response = self.client.post("/posts/nonexistent-post/comments", json=comment_data)
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Post not found" in data["detail"]
        
        # Verify post existence was checked
        self.mock_post_repo.exists_by_id.assert_called()
        # Verify comment was not saved
        self.mock_comment_repo.save.assert_not_called()
    
    def test_get_post_comments_returns_list_with_correct_structure(self):
        """Test getting post comments returns properly structured list response."""
        # Arrange
        mock_comments = [
            Comment(
                id="comment-1",
                content="First comment",
                author="author-1",
                post_id="post-123",
                created_at=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            ),
            Comment(
                id="comment-2",
                content="Second comment",
                author="author-2",
                post_id="post-123",
                created_at=datetime(2024, 1, 1, 13, 0, 0, tzinfo=timezone.utc)
            )
        ]
        
        self.mock_comment_repo.find_by_post_id.return_value = self._async_return(mock_comments)
        
        # Act
        response = self.client.get("/posts/post-123/comments?limit=10")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) == 2
        assert data["data"][0]["id"] == "comment-1"
        assert data["data"][0]["content"] == "First comment"
        assert data["data"][1]["id"] == "comment-2"
        assert data["data"][1]["content"] == "Second comment"
        
        # Verify post existence was checked
        self.mock_post_repo.exists_by_id.assert_called()
        # Verify comments were fetched
        self.mock_comment_repo.find_by_post_id.assert_called()
    
    def test_get_comments_for_nonexistent_post_returns_404(self):
        """Test getting comments for nonexistent post returns 404."""
        # Arrange
        self.mock_post_repo.exists_by_id.return_value = self._async_return(False)
        
        # Act
        response = self.client.get("/posts/nonexistent-post/comments")
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Post not found" in data["detail"]
        
        # Verify post existence was checked
        self.mock_post_repo.exists_by_id.assert_called()
        # Verify comments were not fetched
        self.mock_comment_repo.find_by_post_id.assert_not_called()
    
    def test_create_comment_with_invalid_data_returns_422(self):
        """Test creating a comment with invalid data returns 422."""
        # Arrange - missing required fields
        invalid_comment_data = {
            "content": "Test comment"
            # Missing "author" field
        }
        
        # Act
        response = self.client.post("/posts/post-123/comments", json=invalid_comment_data)
        
        # Assert
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        # Should mention missing author field
        assert any("author" in str(error).lower() for error in data["detail"])
    
    def test_get_comments_with_custom_limit_respects_limit(self):
        """Test getting comments with custom limit parameter."""
        # Arrange
        mock_comments = [
            Comment(
                id=f"comment-{i}",
                content=f"Comment {i}",
                author=f"author-{i}",
                post_id="post-123",
                created_at=datetime(2024, 1, 1, 12, i, 0, tzinfo=timezone.utc)
            ) for i in range(5)
        ]
        
        self.mock_comment_repo.find_by_post_id.return_value = self._async_return(mock_comments)
        
        # Act
        response = self.client.get("/posts/post-123/comments?limit=3")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) == 5  # Mock returns all, but limit should be passed through
        
        # Verify limit was passed to repository
        self.mock_comment_repo.find_by_post_id.assert_called_with("post-123", 3)