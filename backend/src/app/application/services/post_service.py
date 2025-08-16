from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class PostSummary:
    id: str
    title: str
    excerpt: str
    author: str
    publishedAt: datetime


@dataclass
class PostListResult:
    posts: List[PostSummary]
    total: int


class PostService:
    """Simple in-memory service for listing posts.

    In a real implementation, this would query a database or repository.
    """

    def __init__(self) -> None:
        self._all_posts: List[PostSummary] = [
            PostSummary(
                id="post-123",
                title="Getting Started with Next.js",
                excerpt="Learn the basics of Next.js in this comprehensive guide covering SSR, SSG, and CSR.",
                author="John Doe",
                publishedAt=datetime.fromisoformat("2024-01-15T10:30:00+00:00"),
            ),
            PostSummary(
                id="post-124",
                title="Advanced React Patterns",
                excerpt="Explore advanced React patterns including hooks, context, and state management techniques.",
                author="Jane Smith",
                publishedAt=datetime.fromisoformat("2024-01-14T09:15:00+00:00"),
            ),
            PostSummary(
                id="post-125",
                title="TypeScript Best Practices",
                excerpt="Learn TypeScript best practices for building scalable and maintainable applications.",
                author="Bob Johnson",
                publishedAt=datetime.fromisoformat("2024-01-13T14:45:00+00:00"),
            ),
        ]

    async def list_posts(self, *, page: int, limit: int) -> PostListResult:
        start = (page - 1) * limit
        end = start + limit
        sliced = self._all_posts[start:end]
        total = len(self._all_posts)
        return PostListResult(posts=sliced, total=total)

