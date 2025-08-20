"""Integration tests for Posts API endpoints with FastAPI DI."""

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


class TestPostsEndpoints:
    """Integration tests for Posts API endpoints using FastAPI DI."""
    
    def test_create_post_with_valid_data_returns_201(self, test_client, sample_create_post_request):
        """Test creating a post with valid data returns 201."""
        # Act
        response = test_client.post("/posts", json=sample_create_post_request)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert data["data"]["title"] == sample_create_post_request["title"]
        assert data["data"]["content"] == sample_create_post_request["content"]
        assert data["data"]["excerpt"] == sample_create_post_request["excerpt"]
        assert data["data"]["status"] == "published"
        assert data["data"]["author"] == "test-user-uid"
        assert "id" in data["data"]
        assert "publishedAt" in data["data"]
    
    def test_create_post_with_invalid_data_returns_400(self, test_client):
        """Test creating a post with invalid data returns 400."""
        # Arrange - missing required fields but valid request structure
        invalid_post_data = {
            "title": "",  # Invalid empty title
            "content": "",  # Invalid empty content
            "excerpt": "",  # Invalid empty excerpt
            "status": "published"  # Valid status to avoid NoneType error
        }
        
        # Act
        response = test_client.post("/posts", json=invalid_post_data)
        
        # Assert - Our domain validation returns 400, not 422
        assert response.status_code == 400  # Domain validation error
        assert "detail" in response.json()
    
    def test_create_post_with_draft_status(self, test_client):
        """Test creating a post with draft status."""
        # Arrange
        draft_post = {
            "title": "Draft Post",
            "content": "This is a draft post content.",
            "excerpt": "Draft excerpt",
            "status": "draft"
        }
        
        # Act
        response = test_client.post("/posts", json=draft_post)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["data"]["status"] == "draft"
    
    def test_get_post_by_id_returns_200_when_exists(self, test_client, sample_create_post_request):
        """Test getting a post by ID returns 200 when it exists."""
        # Arrange - create a post first
        create_response = test_client.post("/posts", json=sample_create_post_request)
        post_id = create_response.json()["data"]["id"]
        
        # Act
        response = test_client.get(f"/posts/{post_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["id"] == post_id
        assert data["data"]["title"] == sample_create_post_request["title"]
    
    def test_get_post_by_id_returns_404_when_not_exists(self, test_client):
        """Test getting a post by ID returns 404 when it doesn't exist."""
        # Act
        response = test_client.get("/posts/nonexistent-id")
        
        # Assert
        assert response.status_code == 404
        assert "detail" in response.json()
    
    def test_get_posts_returns_200_with_empty_list_initially(self, test_client):
        """Test getting posts returns 200 with empty list initially."""
        # Act
        response = test_client.get("/posts")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert "posts" in data["data"]
        assert "pagination" in data["data"]
        assert len(data["data"]["posts"]) == 0
        assert data["data"]["pagination"]["total"] == 0
    
    def test_get_posts_returns_published_posts_only(self, test_client):
        """Test getting posts returns published posts only."""
        # Arrange - create both published and draft posts
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
        response = test_client.get("/posts")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["posts"]) == 1  # Only published post
        assert data["data"]["posts"][0]["title"] == "Published Post"
        assert data["data"]["pagination"]["total"] == 1
    
    def test_get_posts_with_pagination_parameters(self, test_client):
        """Test getting posts with pagination parameters."""
        # Arrange - create multiple published posts
        for i in range(5):
            post_data = {
                "title": f"Post {i+1}",
                "content": f"Content {i+1}",
                "excerpt": f"Excerpt {i+1}",
                "status": "published"
            }
            create_response = test_client.post("/posts", json=post_data)
            print(f"Created post {i+1}: {create_response.status_code} - {create_response.json().get('data', {}).get('status', 'unknown')}")
        
        # Check all posts first to see what's actually stored
        all_posts_response = test_client.get("/posts?limit=10")
        print(f"All posts: {all_posts_response.json()}")
        
        # Act
        response = test_client.get("/posts?page=1&limit=3")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        print(f"Paginated response: {data}")
        assert len(data["data"]["posts"]) == 3
        assert data["data"]["pagination"]["page"] == 1
        assert data["data"]["pagination"]["limit"] == 3
        assert data["data"]["pagination"]["total"] == 5
        assert data["data"]["pagination"]["hasNext"] is True
    
    def test_update_post_returns_200_when_exists(self, test_client, sample_create_post_request):
        """Test updating a post returns 200 when it exists."""
        # Arrange - create a post first
        create_response = test_client.post("/posts", json=sample_create_post_request)
        post_id = create_response.json()["data"]["id"]
        
        update_data = {
            "title": "Updated Title",
            "content": "Updated content",
            "excerpt": "Updated excerpt",
            "status": "published"
        }
        
        # Act
        response = test_client.put(f"/posts/{post_id}", json=update_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["title"] == "Updated Title"
        assert data["data"]["content"] == "Updated content"
    
    def test_update_post_returns_404_when_not_exists(self, test_client):
        """Test updating a post returns 404 when it doesn't exist."""
        # Arrange
        update_data = {
            "title": "Updated Title",
            "content": "Updated content", 
            "excerpt": "Updated excerpt",
            "status": "published"
        }
        
        # Act
        response = test_client.put("/posts/nonexistent-id", json=update_data)
        
        # Assert
        assert response.status_code == 404
        assert "detail" in response.json()
    
    def test_delete_post_returns_204_when_exists(self, test_client, sample_create_post_request):
        """Test deleting a post returns 204 when it exists."""
        # Arrange - create a post first
        create_response = test_client.post("/posts", json=sample_create_post_request)
        post_id = create_response.json()["data"]["id"]
        
        # Act
        response = test_client.delete(f"/posts/{post_id}")
        
        # Assert
        assert response.status_code == 204
        
        # Verify post is deleted
        get_response = test_client.get(f"/posts/{post_id}")
        assert get_response.status_code == 404
    
    def test_delete_post_returns_404_when_not_exists(self, test_client):
        """Test deleting a post returns 404 when it doesn't exist."""
        # Act
        response = test_client.delete("/posts/nonexistent-id")
        
        # Assert
        assert response.status_code == 404
        assert "detail" in response.json()