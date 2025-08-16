from __future__ import annotations

from dataclasses import dataclass

from app.domain.entities import Post
from app.domain.ports import PostRepository


@dataclass(frozen=True)
class CreatePost:
    repo: PostRepository

    async def execute(self, *, title: str, content: str, excerpt: str | None, status: str, author: str) -> Post:
        return await self.repo.create_post(title=title, content=content, excerpt=excerpt, status=status, author=author)

