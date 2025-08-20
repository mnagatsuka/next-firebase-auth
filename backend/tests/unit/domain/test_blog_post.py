"""Unit tests for BlogPost domain entity."""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timezone
from freezegun import freeze_time

# Add backend to Python path
backend_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(backend_path))

from app.domain.entities import BlogPost, PostStatus


class TestBlogPost:
    """Test suite for BlogPost entity."""
    
    def test_create_blog_post_with_valid_data_returns_post(self):
        """Test creating a blog post with valid data."""
        post = BlogPost(
            id="post-123",
            title="Test Post",
            content="This is test content.",
            excerpt="Test excerpt",
            author="test-author"
        )
        
        assert post.id == "post-123"
        assert post.title == "Test Post"
        assert post.content == "This is test content."
        assert post.excerpt == "Test excerpt"
        assert post.author == "test-author"
        assert post.status == PostStatus.DRAFT
        assert post.published_at is None
        assert isinstance(post.created_at, datetime)
        assert isinstance(post.updated_at, datetime)
    
    def test_create_blog_post_with_empty_title_raises_error(self):
        """Test that empty title raises validation error."""
        with pytest.raises(ValueError, match="Title cannot be empty"):
            BlogPost(
                id="post-123",
                title="   ",  # Empty/whitespace title
                content="This is test content.",
                excerpt="Test excerpt",
                author="test-author"
            )
    
    def test_create_blog_post_with_empty_content_raises_error(self):
        """Test that empty content raises validation error."""
        with pytest.raises(ValueError, match="Content cannot be empty"):
            BlogPost(
                id="post-123",
                title="Test Post",
                content="",  # Empty content
                excerpt="Test excerpt",
                author="test-author"
            )
    
    def test_create_blog_post_with_empty_excerpt_raises_error(self):
        """Test that empty excerpt raises validation error."""
        with pytest.raises(ValueError, match="Excerpt cannot be empty"):
            BlogPost(
                id="post-123",
                title="Test Post",
                content="This is test content.",
                excerpt="   ",  # Empty/whitespace excerpt
                author="test-author"
            )
    
    def test_create_blog_post_with_empty_author_raises_error(self):
        """Test that empty author raises validation error."""
        with pytest.raises(ValueError, match="Author cannot be empty"):
            BlogPost(
                id="post-123",
                title="Test Post",
                content="This is test content.",
                excerpt="Test excerpt",
                author=""  # Empty author
            )
    
    def test_blog_post_strips_whitespace_from_fields(self):
        """Test that whitespace is stripped from string fields."""
        post = BlogPost(
            id="post-123",
            title="  Test Post  ",
            content="  This is test content.  ",
            excerpt="  Test excerpt  ",
            author="  test-author  "
        )
        
        assert post.title == "Test Post"
        assert post.content == "This is test content."
        assert post.excerpt == "Test excerpt"
        assert post.author == "test-author"
    
    @freeze_time("2024-01-01 12:00:00")
    def test_blog_post_creation_sets_correct_timestamps(self):
        """Test that blog post creation sets expected timestamps."""
        post = BlogPost(
            id="post-123",
            title="Test Post",
            content="This is test content.",
            excerpt="Test excerpt",
            author="test-author"
        )
        
        expected_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        assert post.created_at == expected_time
        assert post.updated_at == expected_time
    
    def test_publish_post_changes_status_and_sets_published_at(self):
        """Test that publishing a post changes status and sets published timestamp."""
        post = BlogPost(
            id="post-123",
            title="Test Post",
            content="This is test content.",
            excerpt="Test excerpt",
            author="test-author"
        )
        
        assert post.status == PostStatus.DRAFT
        assert post.published_at is None
        
        with freeze_time("2024-01-01 15:00:00"):
            post.publish()
        
        assert post.status == PostStatus.PUBLISHED
        assert post.published_at == datetime(2024, 1, 1, 15, 0, 0, tzinfo=timezone.utc)
        assert post.updated_at == datetime(2024, 1, 1, 15, 0, 0, tzinfo=timezone.utc)
    
    def test_publish_already_published_post_raises_error(self):
        """Test that publishing an already published post raises error."""
        post = BlogPost(
            id="post-123",
            title="Test Post",
            content="This is test content.",
            excerpt="Test excerpt",
            author="test-author",
            status=PostStatus.PUBLISHED,
            published_at=datetime.now(timezone.utc)
        )
        
        with pytest.raises(ValueError, match="Post is already published"):
            post.publish()
    
    def test_unpublish_post_changes_status_and_clears_published_at(self):
        """Test that unpublishing a post changes status and clears published timestamp."""
        post = BlogPost(
            id="post-123",
            title="Test Post",
            content="This is test content.",
            excerpt="Test excerpt",
            author="test-author",
            status=PostStatus.PUBLISHED,
            published_at=datetime.now(timezone.utc)
        )
        
        with freeze_time("2024-01-01 16:00:00"):
            post.unpublish()
        
        assert post.status == PostStatus.DRAFT
        assert post.published_at is None
        assert post.updated_at == datetime(2024, 1, 1, 16, 0, 0, tzinfo=timezone.utc)
    
    def test_unpublish_draft_post_raises_error(self):
        """Test that unpublishing a draft post raises error."""
        post = BlogPost(
            id="post-123",
            title="Test Post",
            content="This is test content.",
            excerpt="Test excerpt",
            author="test-author"
        )
        
        with pytest.raises(ValueError, match="Post is already a draft"):
            post.unpublish()
    
    def test_update_content_updates_fields_and_timestamp(self):
        """Test that updating content updates fields and timestamp."""
        post = BlogPost(
            id="post-123",
            title="Test Post",
            content="This is test content.",
            excerpt="Test excerpt",
            author="test-author"
        )
        
        with freeze_time("2024-01-01 17:00:00"):
            post.update_content(
                title="Updated Title",
                content="Updated content.",
                excerpt="Updated excerpt"
            )
        
        assert post.title == "Updated Title"
        assert post.content == "Updated content."
        assert post.excerpt == "Updated excerpt"
        assert post.updated_at == datetime(2024, 1, 1, 17, 0, 0, tzinfo=timezone.utc)
    
    def test_update_content_with_partial_data_updates_only_provided_fields(self):
        """Test that partial content update only changes provided fields."""
        post = BlogPost(
            id="post-123",
            title="Test Post",
            content="This is test content.",
            excerpt="Test excerpt",
            author="test-author"
        )
        
        original_content = post.content
        original_excerpt = post.excerpt
        
        post.update_content(title="Updated Title")
        
        assert post.title == "Updated Title"
        assert post.content == original_content
        assert post.excerpt == original_excerpt
    
    def test_update_content_with_empty_title_raises_error(self):
        """Test that updating with empty title raises error."""
        post = BlogPost(
            id="post-123",
            title="Test Post",
            content="This is test content.",
            excerpt="Test excerpt",
            author="test-author"
        )
        
        with pytest.raises(ValueError, match="Title cannot be empty"):
            post.update_content(title="")
    
    def test_is_published_returns_correct_status(self):
        """Test that is_published returns correct boolean."""
        draft_post = BlogPost(
            id="post-123",
            title="Test Post",
            content="This is test content.",
            excerpt="Test excerpt",
            author="test-author"
        )
        
        published_post = BlogPost(
            id="post-456",
            title="Published Post",
            content="This is published content.",
            excerpt="Published excerpt",
            author="test-author",
            status=PostStatus.PUBLISHED
        )
        
        assert not draft_post.is_published()
        assert published_post.is_published()
    
    def test_can_be_updated_by_returns_true_for_author(self):
        """Test that author can update their own post."""
        post = BlogPost(
            id="post-123",
            title="Test Post",
            content="This is test content.",
            excerpt="Test excerpt",
            author="test-author"
        )
        
        assert post.can_be_updated_by("test-author")
        assert not post.can_be_updated_by("other-author")
    
    def test_can_be_deleted_by_returns_true_for_author(self):
        """Test that author can delete their own post."""
        post = BlogPost(
            id="post-123",
            title="Test Post",
            content="This is test content.",
            excerpt="Test excerpt",
            author="test-author"
        )
        
        assert post.can_be_deleted_by("test-author")
        assert not post.can_be_deleted_by("other-author")
    
    def test_create_new_factory_method_creates_valid_post(self):
        """Test that create_new factory method creates valid post."""
        with freeze_time("2024-01-01 18:00:00"):
            post = BlogPost.create_new(
                title="Factory Post",
                content="Factory content.",
                excerpt="Factory excerpt",
                author="factory-author"
            )
        
        assert post.title == "Factory Post"
        assert post.content == "Factory content."
        assert post.excerpt == "Factory excerpt"
        assert post.author == "factory-author"
        assert post.status == PostStatus.DRAFT
        assert post.published_at is None
        assert len(post.id) > 0  # UUID should be generated
        assert post.created_at == datetime(2024, 1, 1, 18, 0, 0, tzinfo=timezone.utc)