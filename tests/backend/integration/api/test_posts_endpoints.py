"""Integration tests for Posts API endpoints."""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient

# Add backend to Python path
backend_path = Path(__file__).parent.parent.parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_path))

# Import test factory
tests_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(tests_path))
from factories.post_factory import PostFactory


class TestPostsEndpoints:
    """Integration tests for Posts API endpoints."""
    
    def setup_method(self):
        """Set up test client and mock dependencies."""
        # Import here to ensure proper path setup
        from app.main import app
        self.client = TestClient(app)
        
        # Mock the repository to avoid dependencies
        self.mock_posts = {}
        self.mock_repo_patcher = patch('app.api.posts_implementation.InMemoryPostRepository')
        self.mock_repo_class = self.mock_repo_patcher.start()
        self.mock_repo = Mock()
        self.mock_repo_class.return_value = self.mock_repo
        
        # Setup mock repository methods
        self.mock_repo.save.return_value = self._async_return(None)
        self.mock_repo.find_by_id.return_value = self._async_return(None)
        self.mock_repo.find_published.return_value = self._async_return([])
        self.mock_repo.delete.return_value = self._async_return(None)
        self.mock_repo.exists_by_id.return_value = self._async_return(False)
    
    def teardown_method(self):
        """Clean up mocks."""
        self.mock_repo_patcher.stop()
    
    def _async_return(self, value):
        """Helper to create async return value."""
        import asyncio
        future = asyncio.Future()
        future.set_result(value)
        return future
    
    def test_create_post_with_valid_data_returns_201(self):
        """Test creating a post with valid data returns 201."""
        # Arrange
        post_data = {
            "title": "Test Blog Post",
            "content": "This is a test blog post content.",
            "excerpt": "Test excerpt"
        }
        
        created_post = PostFactory.create()
        self.mock_repo.save.return_value = self._async_return(created_post)
        
        # Act
        response = self.client.post("/posts", json=post_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert data["data"]["title"] == "Test Blog Post"
        assert data["data"]["status"] == "draft"
    
    def test_create_post_with_invalid_data_returns_400(self):
        """Test creating a post with invalid data returns 400."""
        # Arrange
        post_data = {
            "title": "",  # Invalid empty title
            "content": "This is a test blog post content.",
            "excerpt": "Test excerpt"
        }
        
        # Act
        response = self.client.post("/posts", json=post_data)
        
        # Assert
        assert response.status_code == 400
        assert "detail" in response.json()
    
    def test_create_post_without_auth_returns_401(self):
        """Test creating a post without authentication returns 401."""
        # This test assumes Firebase auth is properly configured
        # For now, we'll skip this as auth is not fully implemented
        pytest.skip("Firebase authentication not fully implemented")
    
    def test_get_post_by_id_returns_200_when_exists(self):
        """Test getting a post by ID returns 200 when it exists."""
        # Arrange
        post = PostFactory.create()
        self.mock_repo.find_by_id.return_value = self._async_return(post)
        
        # Act
        response = self.client.get(f"/posts/{post.id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["id"] == post.id
        assert data["data"]["title"] == post.title
    
    def test_get_post_by_id_returns_404_when_not_exists(self):
        """Test getting a post by ID returns 404 when it doesn't exist."""
        # Arrange
        self.mock_repo.find_by_id.return_value = self._async_return(None)
        
        # Act
        response = self.client.get("/posts/nonexistent-id")
        
        # Assert
        assert response.status_code == 404
        assert "detail" in response.json()
    
    def test_get_posts_returns_200_with_paginated_results(self):
        """Test getting posts returns 200 with paginated results."""
        # Arrange
        posts = [PostFactory.create_published() for _ in range(3)]
        self.mock_repo.find_published.return_value = self._async_return(posts)
        
        # Act
        response = self.client.get("/posts")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert "posts" in data["data"]
        assert "pagination" in data["data"]
        assert len(data["data"]["posts"]) == 3
    
    def test_get_posts_with_pagination_parameters(self):
        """Test getting posts with pagination parameters."""
        # Arrange
        posts = [PostFactory.create_published() for _ in range(2)]
        self.mock_repo.find_published.return_value = self._async_return(posts)
        
        # Act
        response = self.client.get("/posts?page=2&limit=5")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["pagination"]["page"] == 2
        assert data["data"]["pagination"]["limit"] == 5
    
    def test_get_posts_with_status_filter(self):
        """Test getting posts with status filter."""
        # Arrange
        published_posts = [PostFactory.create_published() for _ in range(2)]
        self.mock_repo.find_published.return_value = self._async_return(published_posts)
        
        # Act
        response = self.client.get("/posts?status=published")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["posts"]) == 2
    
    def test_get_posts_with_author_filter(self):
        """Test getting posts with author filter."""
        # Arrange
        author_posts = [PostFactory.create_with_author("specific-author") for _ in range(2)]
        self.mock_repo.find_published.return_value = self._async_return(author_posts)
        
        # Act
        response = self.client.get("/posts?author=specific-author")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert all(post["author"] == "specific-author" for post in data["data"]["posts"])
    
    def test_update_post_with_valid_data_returns_200(self):
        """Test updating a post with valid data returns 200."""
        # Arrange
        existing_post = PostFactory.create()
        updated_post = PostFactory.create(title="Updated Title")
        
        self.mock_repo.find_by_id.return_value = self._async_return(existing_post)
        self.mock_repo.save.return_value = self._async_return(updated_post)
        
        update_data = {
            "title": "Updated Title",
            "content": "Updated content",
            "excerpt": "Updated excerpt"
        }
        
        # Act
        response = self.client.put(f"/posts/{existing_post.id}", json=update_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["title"] == "Updated Title"
    
    def test_update_nonexistent_post_returns_404(self):
        """Test updating a non-existent post returns 404."""
        # Arrange
        self.mock_repo.find_by_id.return_value = self._async_return(None)
        
        update_data = {
            "title": "Updated Title",
            "content": "Updated content",
            "excerpt": "Updated excerpt"
        }
        
        # Act
        response = self.client.put("/posts/nonexistent-id", json=update_data)
        
        # Assert
        assert response.status_code == 404
    
    def test_update_post_without_auth_returns_401(self):
        """Test updating a post without authentication returns 401."""
        # This test assumes Firebase auth is properly configured
        pytest.skip("Firebase authentication not fully implemented")
    
    def test_delete_post_returns_204_when_successful(self):
        """Test deleting a post returns 204 when successful."""
        # Arrange
        existing_post = PostFactory.create()
        self.mock_repo.find_by_id.return_value = self._async_return(existing_post)
        self.mock_repo.delete.return_value = self._async_return(None)
        
        # Act
        response = self.client.delete(f"/posts/{existing_post.id}")
        
        # Assert
        assert response.status_code == 204
    
    def test_delete_nonexistent_post_returns_404(self):
        """Test deleting a non-existent post returns 404."""
        # Arrange
        self.mock_repo.find_by_id.return_value = self._async_return(None)
        
        # Act
        response = self.client.delete("/posts/nonexistent-id")
        
        # Assert
        assert response.status_code == 404
    
    def test_delete_post_without_auth_returns_401(self):
        """Test deleting a post without authentication returns 401."""
        # This test assumes Firebase auth is properly configured
        pytest.skip("Firebase authentication not fully implemented")
    
    def test_api_responses_include_correct_headers(self):
        """Test that API responses include correct headers."""
        # Act
        response = self.client.get("/posts")
        
        # Assert
        assert response.status_code == 200
        assert "content-type" in response.headers
        assert response.headers["content-type"] == "application/json"
    
    def test_api_handles_internal_server_errors_gracefully(self):
        """Test that API handles internal server errors gracefully."""
        # Arrange
        self.mock_repo.find_published.side_effect = Exception("Database connection failed")
        
        # Act
        response = self.client.get("/posts")
        
        # Assert
        assert response.status_code == 500
        assert "detail" in response.json()
    
    def test_api_validates_request_payload_schema(self):
        """Test that API validates request payload schema."""
        # Arrange
        invalid_data = {
            "invalid_field": "value"
            # Missing required fields
        }
        
        # Act
        response = self.client.post("/posts", json=invalid_data)
        
        # Assert
        assert response.status_code in [400, 422]  # Validation error