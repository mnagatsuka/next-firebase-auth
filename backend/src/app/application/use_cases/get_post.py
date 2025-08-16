from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.domain.entities import Post
from app.domain.ports import PostRepository


@dataclass(frozen=True)
class GetPost:
    repo: PostRepository

    async def execute(self, post_id: str) -> Optional[Post]:
        return await self.repo.get_post(post_id)

