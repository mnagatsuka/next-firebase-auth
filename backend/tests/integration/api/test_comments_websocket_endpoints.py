"""Integration tests for Comments API WebSocket functionality."""

import pytest
import sys
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(backend_path))


class TestCommentsWebSocketEndpoints:
    """Integration tests for Comments API WebSocket functionality."""
    
    def test_get_comments_returns_acknowledgment_response(self, test_client, sample_create_post_request, sample_comment_data):
        """Test GET comments endpoint returns WebSocket acknowledgment response."""
        # Arrange - create a post and comment first
        post_response = test_client.post("/posts", json=sample_create_post_request)
        post_id = post_response.json()["data"]["id"]
        test_client.post(f"/posts/{post_id}/comments", json=sample_comment_data)
        
        # Act
        response = test_client.get(f"/posts/{post_id}/comments")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Check acknowledgment response structure
        assert "status" in data
        assert "message" in data
        assert "count" in data
        assert data["status"] == "success"
        assert "Comments retrieved successfully" in data["message"]
        assert data["count"] == 1  # One comment created
        
    def test_get_comments_calls_websocket_broadcast(self, test_client, sample_create_post_request, sample_comment_data, mock_websocket_service):
        """Test GET comments endpoint calls WebSocket broadcast method."""
        # Arrange - create a post and comment first
        post_response = test_client.post("/posts", json=sample_create_post_request)
        post_id = post_response.json()["data"]["id"]
        test_client.post(f"/posts/{post_id}/comments", json=sample_comment_data)
        
        # Act
        response = test_client.get(f"/posts/{post_id}/comments")
        
        # Assert
        assert response.status_code == 200
        
        # Verify WebSocket broadcast was called
        mock_websocket_service.broadcast_comments_list.assert_called_once()
        call_args = mock_websocket_service.broadcast_comments_list.call_args
        
        # Check broadcast parameters
        assert call_args[0][0] == post_id  # post_id
        comments_list = call_args[0][1]  # comments
        assert len(comments_list) == 1
        assert comments_list[0]["content"] == sample_comment_data["content"]
        
    def test_get_comments_empty_list_returns_zero_count(self, test_client, sample_create_post_request, mock_websocket_service):
        """Test GET comments endpoint with empty comments returns count 0."""
        # Arrange - create a post without comments
        post_response = test_client.post("/posts", json=sample_create_post_request)
        post_id = post_response.json()["data"]["id"]
        
        # Act
        response = test_client.get(f"/posts/{post_id}/comments")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        
        # Verify WebSocket broadcast was called with empty list
        mock_websocket_service.broadcast_comments_list.assert_called_once()
        call_args = mock_websocket_service.broadcast_comments_list.call_args
        assert call_args[0][0] == post_id
        assert call_args[0][1] == []  # empty comments list
        
    def test_get_comments_with_limit_parameter(self, test_client, sample_create_post_request, sample_comment_data, mock_websocket_service):
        """Test GET comments endpoint with limit parameter."""
        # Arrange - create a post and multiple comments
        post_response = test_client.post("/posts", json=sample_create_post_request)
        post_id = post_response.json()["data"]["id"]
        
        # Create 3 comments
        for i in range(3):
            comment_data = {**sample_comment_data, "content": f"Comment {i+1}"}
            test_client.post(f"/posts/{post_id}/comments", json=comment_data)
        
        # Act - request with limit=2
        response = test_client.get(f"/posts/{post_id}/comments?limit=2")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2  # Limited to 2
        
        # Verify WebSocket broadcast was called with limited results
        mock_websocket_service.broadcast_comments_list.assert_called_once()
        call_args = mock_websocket_service.broadcast_comments_list.call_args
        assert len(call_args[0][1]) == 2  # 2 comments in broadcast
        
    def test_get_comments_nonexistent_post_returns_404(self, test_client, mock_websocket_service):
        """Test GET comments for nonexistent post returns 404."""
        # Act
        response = test_client.get("/posts/nonexistent-post/comments")
        
        # Assert
        assert response.status_code == 404
        
        # Verify WebSocket broadcast was NOT called
        mock_websocket_service.broadcast_comments_list.assert_not_called()
        
    def test_get_comments_preserves_original_comment_structure(self, test_client, sample_create_post_request, sample_comment_data, mock_websocket_service):
        """Test GET comments preserves original comment data structure in WebSocket broadcast."""
        # Arrange - create a post and comment
        post_response = test_client.post("/posts", json=sample_create_post_request)
        post_id = post_response.json()["data"]["id"]
        comment_response = test_client.post(f"/posts/{post_id}/comments", json=sample_comment_data)
        original_comment = comment_response.json()
        
        # Act
        response = test_client.get(f"/posts/{post_id}/comments")
        
        # Assert
        assert response.status_code == 200
        
        # Verify WebSocket broadcast contains correct comment structure
        mock_websocket_service.broadcast_comments_list.assert_called_once()
        call_args = mock_websocket_service.broadcast_comments_list.call_args
        broadcasted_comment = call_args[0][1][0]
        
        # Check all original comment fields are preserved
        # Note: model_dump() uses internal field names, not aliases
        assert broadcasted_comment["id"] == original_comment["id"]
        assert broadcasted_comment["content"] == original_comment["content"]
        assert broadcasted_comment["user_id"] == original_comment["userId"]  # internal field name
        # datetime comparison: broadcasted contains datetime object, original contains ISO string
        assert broadcasted_comment["created_at"].isoformat().replace('+00:00', 'Z') == original_comment["createdAt"]
        assert broadcasted_comment["post_id"] == original_comment["postId"]  # internal field name


class TestWebSocketManagementEndpoints:
    """Integration tests for WebSocket management endpoints."""
    
    def test_websocket_connections_info_endpoint(self, test_client, mock_websocket_service):
        """Test WebSocket connections info endpoint."""
        # Arrange - mock connection count
        mock_websocket_service.get_connection_count.return_value = 5
        
        # Act
        response = test_client.get("/websocket/connections")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["active_connections"] == 5
        assert data["status"] == "healthy"
        mock_websocket_service.get_connection_count.assert_called_once()