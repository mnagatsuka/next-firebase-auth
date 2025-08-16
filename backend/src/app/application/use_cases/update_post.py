from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.domain.entities import Post
from app.domain.ports import PostRepository


@dataclass(frozen=True)
class UpdatePost:
    repo: PostRepository

    async def execute(
        self, post_id: str, *, title: str, content: str, excerpt: str | None, status: str
    ) -> Optional[Post]:
        return await self.repo.update_post(post_id, title=title, content=content, excerpt=excerpt, status=status)

