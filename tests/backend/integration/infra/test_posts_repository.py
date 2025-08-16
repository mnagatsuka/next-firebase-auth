"""Integration tests for PostRepository implementations."""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add backend to Python path
backend_path = Path(__file__).parent.parent.parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_path))

from app.infra.repositories.posts_repository import InMemoryPostRepository
from app.domain.entities import BlogPost, PostStatus

# Import test factory
tests_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(tests_path))
from factories.post_factory import PostFactory


class TestInMemoryPostRepository:
    """Integration tests for InMemoryPostRepository."""
    
    def setup_method(self):
        """Set up test repository."""
        self.repository = InMemoryPostRepository()
    
    @pytest.mark.asyncio
    async def test_save_post_stores_and_returns_post(self):
        """Test saving a post stores it and returns the post."""
        # Arrange
        post = PostFactory.create()
        original_updated_at = post.updated_at
        
        # Act
        saved_post = await self.repository.save(post)
        
        # Assert
        assert saved_post.id == post.id
        assert saved_post.title == post.title
        assert saved_post.updated_at >= original_updated_at  # Should be updated
        
        # Verify it's stored
        found_post = await self.repository.find_by_id(post.id)
        assert found_post is not None
        assert found_post.id == post.id
    
    @pytest.mark.asyncio
    async def test_find_by_id_returns_post_when_exists(self):
        """Test finding a post by ID when it exists."""
        # Arrange
        post = PostFactory.create()
        await self.repository.save(post)
        
        # Act
        found_post = await self.repository.find_by_id(post.id)
        
        # Assert
        assert found_post is not None
        assert found_post.id == post.id
        assert found_post.title == post.title
        assert found_post.content == post.content
    
    @pytest.mark.asyncio
    async def test_find_by_id_returns_none_when_not_exists(self):
        """Test finding a post by ID when it doesn't exist."""
        # Act
        found_post = await self.repository.find_by_id("nonexistent-id")
        
        # Assert
        assert found_post is None
    
    @pytest.mark.asyncio
    async def test_find_by_author_returns_author_posts(self):
        """Test finding posts by author."""
        # Arrange
        author_posts = [
            PostFactory.create(id="post-1", author="author-1"),
            PostFactory.create(id="post-2", author="author-1"),
            PostFactory.create(id="post-3", author="author-2")
        ]
        
        for post in author_posts:
            await self.repository.save(post)
        
        # Act
        found_posts = await self.repository.find_by_author("author-1")
        
        # Assert
        assert len(found_posts) == 2
        assert all(post.author == "author-1" for post in found_posts)
        
        # Should be sorted by created_at descending
        assert found_posts[0].created_at >= found_posts[1].created_at
    
    @pytest.mark.asyncio
    async def test_find_by_author_with_status_filter_returns_filtered_posts(self):
        """Test finding posts by author with status filter."""
        # Arrange
        draft_post = PostFactory.create_draft()
        draft_post.id = "draft-post"
        draft_post.author = "test-author"
        
        published_post = PostFactory.create_published()
        published_post.id = "published-post"
        published_post.author = "test-author"
        
        await self.repository.save(draft_post)
        await self.repository.save(published_post)
        
        # Act
        draft_posts = await self.repository.find_by_author("test-author", PostStatus.DRAFT)
        published_posts = await self.repository.find_by_author("test-author", PostStatus.PUBLISHED)
        
        # Assert
        assert len(draft_posts) == 1
        assert draft_posts[0].status == PostStatus.DRAFT
        
        assert len(published_posts) == 1
        assert published_posts[0].status == PostStatus.PUBLISHED
    
    @pytest.mark.asyncio
    async def test_find_published_returns_only_published_posts(self):
        """Test finding published posts returns only published ones."""
        # Arrange
        draft_post = PostFactory.create_draft()
        published_post1 = PostFactory.create_published()
        published_post1.id = "post-1"
        published_post2 = PostFactory.create_published()
        published_post2.id = "post-2"
        
        await self.repository.save(draft_post)
        await self.repository.save(published_post1)
        await self.repository.save(published_post2)
        
        # Act
        found_posts = await self.repository.find_published()
        
        # Assert
        assert len(found_posts) == 2
        assert all(post.status == PostStatus.PUBLISHED for post in found_posts)
        
        # Should be sorted by published_at descending
        if len(found_posts) > 1:
            assert found_posts[0].published_at >= found_posts[1].published_at
    
    @pytest.mark.asyncio
    async def test_find_published_with_author_filter_returns_filtered_posts(self):
        """Test finding published posts with author filter."""
        # Arrange
        published_post1 = PostFactory.create_published()
        published_post1.id = "post-1"
        published_post1.author = "author-1"
        
        published_post2 = PostFactory.create_published()
        published_post2.id = "post-2"
        published_post2.author = "author-2"
        
        await self.repository.save(published_post1)
        await self.repository.save(published_post2)
        
        # Act
        found_posts = await self.repository.find_published(author="author-1")
        
        # Assert
        assert len(found_posts) == 1
        assert found_posts[0].author == "author-1"
        assert found_posts[0].status == PostStatus.PUBLISHED
    
    @pytest.mark.asyncio
    async def test_find_published_with_pagination_returns_correct_slice(self):
        """Test finding published posts with pagination."""
        # Arrange - Create 5 published posts
        published_posts = []
        for i in range(5):
            post = PostFactory.create_published()
            post.id = f"post-{i}"
            post.published_at = datetime.now(timezone.utc).replace(microsecond=i * 1000)  # Different timestamps
            published_posts.append(post)
            await self.repository.save(post)
        
        # Act - Get page 1 with limit 2
        page1_posts = await self.repository.find_published(page=1, limit=2)
        page2_posts = await self.repository.find_published(page=2, limit=2)
        page3_posts = await self.repository.find_published(page=3, limit=2)
        
        # Assert
        assert len(page1_posts) == 2
        assert len(page2_posts) == 2
        assert len(page3_posts) == 1  # Only 1 remaining
        
        # Verify no overlap
        page1_ids = {post.id for post in page1_posts}
        page2_ids = {post.id for post in page2_posts}
        page3_ids = {post.id for post in page3_posts}
        
        assert len(page1_ids & page2_ids) == 0
        assert len(page1_ids & page3_ids) == 0
        assert len(page2_ids & page3_ids) == 0
    
    @pytest.mark.asyncio
    async def test_delete_removes_post_from_repository(self):
        """Test deleting a post removes it from repository."""
        # Arrange
        post = PostFactory.create()
        await self.repository.save(post)
        
        # Verify it exists
        found_post = await self.repository.find_by_id(post.id)
        assert found_post is not None
        
        # Act
        await self.repository.delete(post.id)
        
        # Assert
        found_post = await self.repository.find_by_id(post.id)
        assert found_post is None
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_post_does_not_error(self):
        """Test deleting non-existent post doesn't raise error."""
        # Act & Assert - Should not raise exception
        await self.repository.delete("nonexistent-id")
    
    @pytest.mark.asyncio
    async def test_exists_by_id_returns_true_when_exists(self):
        """Test exists_by_id returns True when post exists."""
        # Arrange
        post = PostFactory.create()
        await self.repository.save(post)
        
        # Act
        exists = await self.repository.exists_by_id(post.id)
        
        # Assert
        assert exists is True
    
    @pytest.mark.asyncio
    async def test_exists_by_id_returns_false_when_not_exists(self):
        """Test exists_by_id returns False when post doesn't exist."""
        # Act
        exists = await self.repository.exists_by_id("nonexistent-id")
        
        # Assert
        assert exists is False
    
    @pytest.mark.asyncio
    async def test_multiple_operations_maintain_data_integrity(self):
        """Test multiple operations maintain data integrity."""
        # Arrange
        posts = [PostFactory.create(id=f"post-{i}") for i in range(3)]
        
        # Save all posts
        for post in posts:
            await self.repository.save(post)
        
        # Update one post
        posts[0].title = "Updated Title"
        await self.repository.save(posts[0])
        
        # Delete one post
        await self.repository.delete(posts[1].id)
        
        # Act - Check final state
        post_0 = await self.repository.find_by_id("post-0")
        post_1 = await self.repository.find_by_id("post-1")
        post_2 = await self.repository.find_by_id("post-2")
        
        # Assert
        assert post_0 is not None
        assert post_0.title == "Updated Title"
        
        assert post_1 is None  # Should be deleted
        
        assert post_2 is not None
        assert post_2.title != "Updated Title"