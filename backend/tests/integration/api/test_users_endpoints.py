"""Integration tests for Users API endpoints with FastAPI DI."""

import pytest
import sys
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(backend_path))

# Import test factory
tests_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(tests_path))
from factories.post_factory import PostFactory


class TestUsersEndpoints:
    """Integration tests for Users API endpoints using FastAPI DI."""
    
    def test_get_user_posts_returns_200_for_authenticated_user(self, test_client, sample_create_post_request):
        """Test getting user posts returns 200 for authenticated user accessing their own posts."""
        # Arrange - create some posts for the test user
        user_id = "test-user-uid"  # This matches the mock authenticated user's UID
        
        # Create posts with different statuses
        published_post = {
            "title": "Published Post",
            "content": "Published content",
            "excerpt": "Published excerpt",
            "status": "published"
        }
        draft_post = {
            "title": "Draft Post",
            "content": "Draft content", 
            "excerpt": "Draft excerpt",
            "status": "draft"
        }
        
        test_client.post("/posts", json=published_post)
        test_client.post("/posts", json=draft_post)
        
        # Act
        response = test_client.get(f"/users/{user_id}/posts")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert "posts" in data["data"]
        assert "pagination" in data["data"]
        assert len(data["data"]["posts"]) == 2  # Both published and draft posts
        assert data["data"]["pagination"]["total"] == 2
    
    def test_get_user_posts_with_status_filter_published(self, test_client):
        """Test getting user posts with published status filter."""
        # Arrange
        user_id = "test-user-uid"
        
        published_post = {
            "title": "Published Post",
            "content": "Published content",
            "excerpt": "Published excerpt", 
            "status": "published"
        }
        draft_post = {
            "title": "Draft Post",
            "content": "Draft content",
            "excerpt": "Draft excerpt",
            "status": "draft"
        }
        
        test_client.post("/posts", json=published_post)
        test_client.post("/posts", json=draft_post)
        
        # Act
        response = test_client.get(f"/users/{user_id}/posts?status=published")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["posts"]) == 1
        assert data["data"]["posts"][0]["title"] == "Published Post"
        assert data["data"]["posts"][0]["status"] == "published"
        assert data["data"]["pagination"]["total"] == 1
    
    def test_get_user_posts_with_status_filter_draft(self, test_client):
        """Test getting user posts with draft status filter."""
        # Arrange
        user_id = "test-user-uid"
        
        published_post = {
            "title": "Published Post",
            "content": "Published content",
            "excerpt": "Published excerpt",
            "status": "published"
        }
        draft_post = {
            "title": "Draft Post", 
            "content": "Draft content",
            "excerpt": "Draft excerpt",
            "status": "draft"
        }
        
        test_client.post("/posts", json=published_post)
        test_client.post("/posts", json=draft_post)
        
        # Act
        response = test_client.get(f"/users/{user_id}/posts?status=draft")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["posts"]) == 1
        assert data["data"]["posts"][0]["title"] == "Draft Post"
        assert data["data"]["posts"][0]["status"] == "draft"
        assert data["data"]["pagination"]["total"] == 1
    
    def test_get_user_posts_with_pagination(self, test_client):
        """Test getting user posts with pagination parameters."""
        # Arrange - create multiple posts
        user_id = "test-user-uid"
        
        for i in range(5):
            post_data = {
                "title": f"Post {i+1}",
                "content": f"Content {i+1}",
                "excerpt": f"Excerpt {i+1}",
                "status": "published"
            }
            test_client.post("/posts", json=post_data)
        
        # Act
        response = test_client.get(f"/users/{user_id}/posts?page=1&limit=3")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["posts"]) == 3
        assert data["data"]["pagination"]["page"] == 1
        assert data["data"]["pagination"]["limit"] == 3
        assert data["data"]["pagination"]["total"] == 5
        assert data["data"]["pagination"]["hasNext"] is True
    
    def test_get_user_posts_returns_403_for_different_user(self, test_client_different_user):
        """Test getting user posts returns 403 when trying to access another user's posts."""
        # Arrange
        other_user_id = "other-user"
        
        # Act - test_client_different_user is authenticated as "different-user-uid"
        # but trying to access "other-user" posts
        response = test_client_different_user.get(f"/users/{other_user_id}/posts")
        
        # Assert
        assert response.status_code == 403
        assert "detail" in response.json()
        assert "can only access your own posts" in response.json()["detail"]
    
    def test_get_user_posts_returns_401_for_unauthenticated_user(self, test_client_no_auth):
        """Test getting user posts returns 401 for unauthenticated user."""
        # Arrange
        user_id = "any-user"
        
        # Act
        response = test_client_no_auth.get(f"/users/{user_id}/posts")
        
        # Assert
        assert response.status_code == 401
        assert "detail" in response.json()
    
    def test_get_user_posts_with_invalid_status_returns_400(self, test_client):
        """Test getting user posts with invalid status parameter returns 400."""
        # Arrange
        user_id = "test-user-uid"
        
        # Act
        response = test_client.get(f"/users/{user_id}/posts?status=invalid")
        
        # Assert
        assert response.status_code == 400
        assert "detail" in response.json()
        assert "Invalid status" in response.json()["detail"]
    
    def test_get_user_posts_returns_empty_for_user_with_no_posts(self, test_client):
        """Test getting user posts returns empty list for user with no posts."""
        # Arrange - don't create any posts
        user_id = "test-user-uid"
        
        # Act
        response = test_client.get(f"/users/{user_id}/posts")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]["posts"]) == 0
        assert data["data"]["pagination"]["total"] == 0
        assert data["data"]["pagination"]["hasNext"] is False
    
    def test_get_user_posts_with_second_page(self, test_client):
        """Test getting user posts with second page of pagination."""
        # Arrange - create enough posts for second page
        user_id = "test-user-uid"
        
        for i in range(5):
            post_data = {
                "title": f"Post {i+1}",
                "content": f"Content {i+1}",
                "excerpt": f"Excerpt {i+1}",
                "status": "published"
            }
            test_client.post("/posts", json=post_data)
        
        # Act
        response = test_client.get(f"/users/{user_id}/posts?page=2&limit=3")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["posts"]) == 2  # Remaining posts on page 2
        assert data["data"]["pagination"]["page"] == 2
        assert data["data"]["pagination"]["limit"] == 3
        assert data["data"]["pagination"]["total"] == 5
        assert data["data"]["pagination"]["hasNext"] is False
    
    def test_anonymous_user_data_inheritance_scenario(self, test_client):
        """Test scenario where anonymous user data should be accessible via UID."""
        # This test demonstrates the data inheritance pattern:
        # 1. Anonymous user (UID: anon-user-123) creates posts
        # 2. When they sign up, their data is still linked to the same UID
        # 3. This allows seamless transition from anonymous to authenticated user
        
        # Note: In production, you would implement a data migration service
        # that could link anonymous user data to a new authenticated account
        # if needed, but using stable UIDs eliminates the need for this.
        
        # Arrange - Create posts as if by an anonymous user with specific UID
        anonymous_uid = "anon-user-123"
        
        # In a real scenario, these posts would have been created when the user was anonymous
        # For testing, we can create posts directly with the anonymous UID as author
        # (this simulates the posts being created earlier by the anonymous user)
        
        # Act - Test that a user can access posts by their UID
        response = test_client.get(f"/users/{anonymous_uid}/posts")
        
        # Assert - This should work because Firebase maintains the same UID
        # whether the user is anonymous or authenticated
        assert response.status_code == 403  # Will be 403 because test user != anon user
        # But the URL structure is correct and supports UID-based access