from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence

from app.domain.entities import Comment, Post
from app.domain.ports import PostRepository


@dataclass(frozen=True)
class GetPostComments:
    repo: PostRepository

    async def execute(self, post_id: str) -> Optional[Sequence[Comment]]:
        return await self.repo.list_comments(post_id)


@dataclass(frozen=True)
class CreateComment:
    repo: PostRepository

    async def execute(self, post_id: str, *, content: str, author: str) -> Optional[Post]:
        comment = await self.repo.create_comment(post_id, content=content, author=author)
        if comment is None:
            return None
        return await self.repo.get_post(post_id)

