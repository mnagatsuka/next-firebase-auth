"""Infrastructure implementation of post repository."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import boto3
from boto3.resources.base import ServiceResource
from botocore.client import BaseClient
from botocore.exceptions import ClientError

from app.domain.entities import BlogPost, PostStatus
from app.domain.services import PostRepository


class InMemoryPostRepository(PostRepository):
    """In-memory implementation of post repository for development/testing."""
    
    def __init__(self):
        self._posts: Dict[str, BlogPost] = {}
    
    async def save(self, post: BlogPost) -> BlogPost:
        """Save a blog post."""
        # Update the updated_at timestamp
        post.updated_at = datetime.now(timezone.utc)
        self._posts[post.id] = post
        return post
    
    async def find_by_id(self, post_id: str) -> Optional[BlogPost]:
        """Find a blog post by ID."""
        return self._posts.get(post_id)
    
    async def find_by_author(self, author: str, status: Optional[PostStatus] = None) -> List[BlogPost]:
        """Find blog posts by author."""
        posts = [post for post in self._posts.values() if post.author == author]
        
        if status:
            posts = [post for post in posts if post.status == status]
        
        # Sort by created_at descending
        posts.sort(key=lambda p: p.created_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
        return posts
    
    async def find_by_author_with_pagination(self, author: str, page: int = 1, limit: int = 10, status: Optional[PostStatus] = None) -> List[BlogPost]:
        """Find blog posts by author with pagination and status filtering."""
        posts = [post for post in self._posts.values() if post.author == author]
        
        if status:
            posts = [post for post in posts if post.status == status]
        
        # Sort by created_at descending
        posts.sort(key=lambda p: p.created_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
        
        # Apply pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        return posts[start_idx:end_idx]
    
    async def find_published(self, page: int = 1, limit: int = 10, author: Optional[str] = None) -> List[BlogPost]:
        """Find published blog posts with pagination."""
        # Filter for published posts
        posts = [post for post in self._posts.values() if post.status == PostStatus.PUBLISHED]
        
        # Filter by author if specified
        if author:
            posts = [post for post in posts if post.author == author]
        
        # Sort by published_at descending
        posts.sort(key=lambda p: p.published_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
        
        # Apply pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        return posts[start_idx:end_idx]
    
    async def delete(self, post_id: str) -> None:
        """Delete a blog post."""
        if post_id in self._posts:
            del self._posts[post_id]
    
    async def exists_by_id(self, post_id: str) -> bool:
        """Check if a blog post exists."""
        return post_id in self._posts


# Future database implementation would go here
class DatabasePostRepository(PostRepository):
    """Database implementation of post repository (placeholder)."""
    
    def __init__(self, db_connection):
        self._db = db_connection
    
    async def save(self, post: BlogPost) -> BlogPost:
        """Save a blog post to database."""
        # This would implement actual database operations
        # For now, raising NotImplementedError to indicate it's a placeholder
        raise NotImplementedError("Database repository not implemented yet")


class DynamoDBPostRepository(PostRepository):
    """DynamoDB implementation of PostRepository for local dev via LocalStack."""

    def __init__(
        self,
        table_name: str,
        *,
        endpoint_url: str,
        region_name: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
    ) -> None:
        self._table_name = table_name
        # Create a dedicated resource bound to LocalStack/AWS per settings
        self._dynamodb: ServiceResource = boto3.resource(
            "dynamodb",
            endpoint_url=endpoint_url,
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        self._table = self._dynamodb.Table(table_name)

    # Serialization helpers
    def _post_to_item(self, post: BlogPost) -> Dict[str, Any]:
        return {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "excerpt": post.excerpt,
            "author": post.author,
            "status": post.status.value,
            "published_at": post.published_at.isoformat() if post.published_at else None,
            "created_at": post.created_at.isoformat() if post.created_at else None,
            "updated_at": post.updated_at.isoformat() if post.updated_at else None,
        }

    def _item_to_post(self, item: Dict[str, Any]) -> BlogPost:
        def parse_dt(v: Optional[str]) -> Optional[datetime]:
            if not v:
                return None
            try:
                return datetime.fromisoformat(v)
            except Exception:
                # Fallback: treat as UTC naive
                return datetime.fromisoformat(v.replace("Z", "+00:00"))

        status = PostStatus.PUBLISHED if item.get("status") == "published" else PostStatus.DRAFT
        return BlogPost(
            id=item["id"],
            title=item["title"],
            content=item.get("content", ""),
            excerpt=item.get("excerpt", ""),
            author=item.get("author", ""),
            status=status,
            published_at=parse_dt(item.get("published_at")),
            created_at=parse_dt(item.get("created_at")),
            updated_at=parse_dt(item.get("updated_at")),
        )

    # Repository methods
    async def save(self, post: BlogPost) -> BlogPost:
        post.updated_at = datetime.now(timezone.utc)
        item = self._post_to_item(post)
        try:
            self._table.put_item(Item=item)
        except ClientError as e:
            raise Exception(f"Failed to save post: {e}")
        return post

    async def find_by_id(self, post_id: str) -> Optional[BlogPost]:
        try:
            resp = self._table.get_item(Key={"id": post_id})
        except ClientError:
            return None
        item = resp.get("Item")
        return self._item_to_post(item) if item else None

    async def find_by_author(self, author: str, status: Optional[PostStatus] = None) -> List[BlogPost]:
        from boto3.dynamodb.conditions import Attr

        filt = Attr("author").eq(author)
        if status is not None:
            filt = filt & Attr("status").eq(status.value)
        try:
            resp = self._table.scan(FilterExpression=filt)
        except ClientError:
            return []
        items = resp.get("Items", [])
        posts = [self._item_to_post(i) for i in items]
        posts.sort(
            key=lambda p: p.created_at or datetime.min.replace(tzinfo=timezone.utc),
            reverse=True,
        )
        return posts
    
    async def find_by_author_with_pagination(self, author: str, page: int = 1, limit: int = 10, status: Optional[PostStatus] = None) -> List[BlogPost]:
        """Find blog posts by author with pagination and status filtering."""
        from boto3.dynamodb.conditions import Attr

        filt = Attr("author").eq(author)
        if status is not None:
            filt = filt & Attr("status").eq(status.value)
        try:
            resp = self._table.scan(FilterExpression=filt)
        except ClientError:
            return []
        items = resp.get("Items", [])
        posts = [self._item_to_post(i) for i in items]
        posts.sort(
            key=lambda p: p.created_at or datetime.min.replace(tzinfo=timezone.utc),
            reverse=True,
        )
        
        # Apply pagination
        start = (page - 1) * limit
        end = start + limit
        return posts[start:end]

    async def find_published(
        self, page: int = 1, limit: int = 10, author: Optional[str] = None
    ) -> List[BlogPost]:
        from boto3.dynamodb.conditions import Attr

        filt = Attr("status").eq("published")
        if author:
            filt = filt & Attr("author").eq(author)
        try:
            resp = self._table.scan(FilterExpression=filt)
        except ClientError:
            return []
        items = resp.get("Items", [])
        posts = [self._item_to_post(i) for i in items]
        posts.sort(
            key=lambda p: p.published_at or datetime.min.replace(tzinfo=timezone.utc),
            reverse=True,
        )
        start = (page - 1) * limit
        end = start + limit
        return posts[start:end]

    async def delete(self, post_id: str) -> None:
        try:
            self._table.delete_item(Key={"id": post_id})
        except ClientError:
            return None

    async def exists_by_id(self, post_id: str) -> bool:
        try:
            resp = self._table.get_item(Key={"id": post_id}, ProjectionExpression="id")
        except ClientError:
            return False
        return "Item" in resp
    
