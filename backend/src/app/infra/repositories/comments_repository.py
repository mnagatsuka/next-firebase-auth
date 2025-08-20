"""In-memory and DynamoDB repository implementations for comments."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError
from boto3.resources.base import ServiceResource

from app.domain.entities import Comment


class InMemoryCommentRepository:
    """In-memory implementation of comment repository for development/testing."""
    
    def __init__(self):
        self._comments: Dict[str, Comment] = {}
    
    async def save(self, comment: Comment) -> Comment:
        """Save a comment to the in-memory store."""
        self._comments[comment.id] = comment
        return comment
    
    async def find_by_id(self, comment_id: str) -> Optional[Comment]:
        """Find a comment by ID."""
        return self._comments.get(comment_id)
    
    async def find_by_post_id(self, post_id: str, limit: int = 10) -> List[Comment]:
        """Find comments by post ID with limit."""
        comments = [
            comment for comment in self._comments.values() 
            if comment.post_id == post_id
        ]
        # Sort by creation time (oldest first)
        comments.sort(key=lambda c: c.created_at)
        return comments[:limit]
    
    async def find_by_author(self, author: str) -> List[Comment]:
        """Find comments by author."""
        comments = [
            comment for comment in self._comments.values() 
            if comment.user_id == author
        ]
        # Sort by creation time (newest first)
        comments.sort(key=lambda c: c.created_at, reverse=True)
        return comments
    
    async def delete(self, comment_id: str) -> None:
        """Delete a comment."""
        if comment_id in self._comments:
            del self._comments[comment_id]
    
    async def exists_by_id(self, comment_id: str) -> bool:
        """Check if a comment exists."""
        return comment_id in self._comments
    
    def count_all(self) -> int:
        """Get total count of comments (for testing/debugging)."""
        return len(self._comments)
    
    def clear_all(self) -> None:
        """Clear all comments (for testing)."""
        self._comments.clear()
    
    def count_by_post_id(self, post_id: str) -> int:
        """Count comments for a specific post (for testing/debugging)."""
        return sum(1 for comment in self._comments.values() if comment.post_id == post_id)


class DynamoDBCommentRepository:
    """DynamoDB implementation for comments repository."""

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
        self._dynamodb: ServiceResource = boto3.resource(
            "dynamodb",
            endpoint_url=endpoint_url,
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        self._table = self._dynamodb.Table(table_name)

    def _comment_to_item(self, comment: Comment) -> Dict[str, Any]:
        return {
            "id": comment.id,
            "content": comment.content,
            "user_id": comment.user_id,
            "post_id": comment.post_id,
            "created_at": comment.created_at.isoformat() if comment.created_at else None,
        }

    def _item_to_comment(self, item: Dict[str, Any]) -> Comment:
        def parse_dt(v: Optional[str]) -> Optional[datetime]:
            if not v:
                return None
            try:
                return datetime.fromisoformat(v)
            except Exception:
                return datetime.fromisoformat(v.replace("Z", "+00:00"))

        return Comment(
            id=item["id"],
            content=item.get("content", ""),
            user_id=item.get("user_id") or item.get("author", ""),
            post_id=item.get("post_id", ""),
            created_at=parse_dt(item.get("created_at")),
        )

    async def save(self, comment: Comment) -> Comment:
        item = self._comment_to_item(comment)
        try:
            self._table.put_item(Item=item)
        except ClientError as e:
            raise Exception(f"Failed to save comment: {e}")
        return comment

    async def find_by_id(self, comment_id: str) -> Optional[Comment]:
        try:
            resp = self._table.get_item(Key={"id": comment_id})
        except ClientError:
            return None
        item = resp.get("Item")
        return self._item_to_comment(item) if item else None

    async def find_by_post_id(self, post_id: str, limit: int = 10) -> List[Comment]:
        from boto3.dynamodb.conditions import Attr

        try:
            resp = self._table.scan(
                FilterExpression=Attr("post_id").eq(post_id)
            )
        except ClientError:
            return []
        items = resp.get("Items", [])
        comments = [self._item_to_comment(i) for i in items]
        comments.sort(key=lambda c: c.created_at or datetime.min.replace(tzinfo=timezone.utc))
        return comments[:limit]

    async def find_by_author(self, author: str) -> List[Comment]:
        from boto3.dynamodb.conditions import Attr

        try:
            resp = self._table.scan(
                FilterExpression=Attr("user_id").eq(author) | Attr("author").eq(author)
            )
        except ClientError:
            return []
        items = resp.get("Items", [])
        comments = [self._item_to_comment(i) for i in items]
        comments.sort(key=lambda c: c.created_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
        return comments

    async def delete(self, comment_id: str) -> None:
        try:
            self._table.delete_item(Key={"id": comment_id})
        except ClientError:
            return None

    async def exists_by_id(self, comment_id: str) -> bool:
        try:
            resp = self._table.get_item(Key={"id": comment_id}, ProjectionExpression="id")
        except ClientError:
            return False
        return "Item" in resp
