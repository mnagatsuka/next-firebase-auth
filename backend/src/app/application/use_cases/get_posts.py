from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from app.domain.entities import PostSummary
from app.domain.ports import PostRepository


@dataclass(frozen=True)
class PostListResult:
    posts: Sequence[PostSummary]
    total: int


class GetPosts:
    def __init__(self, repo: PostRepository) -> None:
        self._repo = repo

    async def execute(self, *, page: int, limit: int) -> PostListResult:
        posts, total = await self._repo.list_posts(page=page, limit=limit)
        return PostListResult(posts=posts, total=total)

