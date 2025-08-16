from __future__ import annotations

from typing import Optional, Protocol, Sequence, Tuple

from .entities import Comment, Post, PostSummary


class PostRepository(Protocol):
    async def list_posts(self, *, page: int, limit: int) -> Tuple[Sequence[PostSummary], int]:
        """Return posts and total count for pagination."""
    async def get_post(self, post_id: str) -> Optional[Post]:
        ...

    async def create_post(
        self, *, title: str, content: str, excerpt: Optional[str], status: str, author: str
    ) -> Post:
        ...

    async def update_post(
        self, post_id: str, *, title: str, content: str, excerpt: Optional[str], status: str
    ) -> Optional[Post]:
        ...

    async def list_comments(self, post_id: str) -> Optional[Sequence[Comment]]:
        ...

    async def create_comment(self, post_id: str, *, content: str, author: str) -> Optional[Comment]:
        ...
