"""Comment domain entity with business logic."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
import uuid


@dataclass
class Comment:
    """Comment domain entity with business logic."""

    id: str
    content: str
    user_id: str
    post_id: str
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Basic validation and data cleaning."""
        if not self.content.strip():
            raise ValueError("Comment content cannot be empty")
        if not self.user_id.strip():
            raise ValueError("User ID cannot be empty")
        if not self.post_id.strip():
            raise ValueError("Post ID cannot be empty")

        # Clean up data
        self.content = self.content.strip()
        self.user_id = self.user_id.strip()
        self.post_id = self.post_id.strip()

        # Set timestamp if not provided
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)

    def update_content(self, content: str) -> None:
        """Update comment content."""
        if not content.strip():
            raise ValueError("Comment content cannot be empty")

        self.content = content.strip()

    def can_be_updated_by(self, user_id: str) -> bool:
        """Check if the comment can be updated by the given user."""
        # For now, only the author can update
        return self.user_id == user_id

    def can_be_deleted_by(self, user_id: str) -> bool:
        """Check if the comment can be deleted by the given user."""
        # For now, only the author can delete
        return self.user_id == user_id

    @classmethod
    def create_new(cls, content: str, user_id: str, post_id: str) -> "Comment":
        """Factory method to create a new comment."""
        comment_id = str(uuid.uuid4())
        return cls(id=comment_id, content=content, user_id=user_id, post_id=post_id)

