"""Integration tests for Comments API endpoints with FastAPI DI."""

import pytest
import sys
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(backend_path))


class TestCommentsEndpoints:
    """Integration tests for Comments API endpoints using FastAPI DI."""
    
    def test_create_comment_with_valid_data_returns_201(self, test_client, sample_create_post_request, sample_comment_data):
        """Test creating a comment with valid data returns 201."""
        # Arrange - create a post first
        post_response = test_client.post("/posts", json=sample_create_post_request)
        post_id = post_response.json()["data"]["id"]
        
        # Act
        response = test_client.post(f"/posts/{post_id}/comments", json=sample_comment_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == sample_comment_data["content"]
        assert data["userId"] == "test-user-uid"
        assert data["postId"] == post_id
        assert "id" in data
        assert "createdAt" in data
    
    def test_create_comment_with_invalid_data_returns_400(self, test_client, sample_create_post_request):
        """Test creating a comment with invalid data returns 400."""
        # Arrange - create a post first
        post_response = test_client.post("/posts", json=sample_create_post_request)
        post_id = post_response.json()["data"]["id"]
        
        invalid_comment_data = {
            "content": "",  # Invalid empty content
            "author": ""    # Invalid empty author
        }
        
        # Act
        response = test_client.post(f"/posts/{post_id}/comments", json=invalid_comment_data)
        
        # Assert
        assert response.status_code == 400  # Domain validation returns 400
        assert "detail" in response.json()
    
    def test_create_comment_on_nonexistent_post_returns_404(self, test_client, sample_comment_data):
        """Test creating a comment on nonexistent post returns 404."""
        # Act
        response = test_client.post("/posts/nonexistent-id/comments", json=sample_comment_data)
        
        # Assert
        assert response.status_code == 404
        assert "detail" in response.json()
        assert "Post not found" in response.json()["detail"]
    
    def test_get_comments_for_existing_post_returns_200(self, test_client, sample_create_post_request, sample_comment_data):
        """Test getting comments for existing post returns acknowledgment response (WebSocket sends actual data)."""
        # Arrange - create a post and comment
        post_response = test_client.post("/posts", json=sample_create_post_request)
        post_id = post_response.json()["data"]["id"]
        
        test_client.post(f"/posts/{post_id}/comments", json=sample_comment_data)
        
        # Act
        response = test_client.get(f"/posts/{post_id}/comments")
        
        # Assert - Now returns acknowledgment response, data sent via WebSocket
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "Comments retrieved successfully"
        assert data["count"] == 1
        # WebSocket data is not included in REST response
    
    def test_get_comments_for_post_with_no_comments_returns_empty_list(self, test_client, sample_create_post_request):
        """Test getting comments for post with no comments returns acknowledgment with count 0."""
        # Arrange - create a post without comments
        post_response = test_client.post("/posts", json=sample_create_post_request)
        post_id = post_response.json()["data"]["id"]
        
        # Act
        response = test_client.get(f"/posts/{post_id}/comments")
        
        # Assert - Returns acknowledgment response
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "Comments retrieved successfully"
        assert data["count"] == 0
    
    def test_get_comments_for_nonexistent_post_returns_404(self, test_client):
        """Test getting comments for nonexistent post returns 404."""
        # Act
        response = test_client.get("/posts/nonexistent-id/comments")
        
        # Assert
        assert response.status_code == 404
        assert "detail" in response.json()
        assert "Post not found" in response.json()["detail"]
    
    def test_get_comments_with_limit_parameter(self, test_client, sample_create_post_request):
        """Test getting comments with limit parameter returns acknowledgment with correct count."""
        # Arrange - create a post and multiple comments
        post_response = test_client.post("/posts", json=sample_create_post_request)
        post_id = post_response.json()["data"]["id"]
        
        # Create 5 comments
        for i in range(5):
            comment_data = {
                "content": f"Comment {i+1}",
                "author": f"Author {i+1}"
            }
            test_client.post(f"/posts/{post_id}/comments", json=comment_data)
        
        # Act
        response = test_client.get(f"/posts/{post_id}/comments?limit=3")
        
        # Assert - Returns acknowledgment with count (actual data via WebSocket)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "Comments retrieved successfully"
        assert data["count"] == 3  # Limited to 3 as requested
    
    def test_create_multiple_comments_on_same_post(self, test_client, sample_create_post_request):
        """Test creating multiple comments on the same post."""
        # Arrange - create a post
        post_response = test_client.post("/posts", json=sample_create_post_request)
        post_id = post_response.json()["data"]["id"]
        
        comments = [
            {"content": "First comment", "author": "User1"},
            {"content": "Second comment", "author": "User2"},
            {"content": "Third comment", "author": "User3"}
        ]
        
        # Act - create multiple comments
        for comment in comments:
            response = test_client.post(f"/posts/{post_id}/comments", json=comment)
            assert response.status_code == 201
        
        # Assert - verify GET returns acknowledgment with correct count
        response = test_client.get(f"/posts/{post_id}/comments")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "Comments retrieved successfully"
        assert data["count"] == 3