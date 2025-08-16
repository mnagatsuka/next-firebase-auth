from __future__ import annotations

from datetime import datetime
from typing import Optional, Sequence, Tuple

from app.domain.entities import Comment, Post, PostSummary
from app.domain.ports import PostRepository


class MemoryPostRepository(PostRepository):
    def __init__(self) -> None:
        # Seed summaries for list endpoint
        self._posts: list[PostSummary] = [
            PostSummary(
                id="post-123",
                title="Getting Started with Next.js",
                excerpt=(
                    "Learn the basics of Next.js in this comprehensive guide covering SSR, SSG, and CSR."
                ),
                author="John Doe",
                published_at=datetime.fromisoformat("2024-01-15T10:30:00+00:00"),
            ),
            PostSummary(
                id="post-124",
                title="Advanced React Patterns",
                excerpt=(
                    "Explore advanced React patterns including hooks, context, and state management techniques."
                ),
                author="Jane Smith",
                published_at=datetime.fromisoformat("2024-01-14T09:15:00+00:00"),
            ),
            PostSummary(
                id="post-125",
                title="TypeScript Best Practices",
                excerpt=(
                    "Learn TypeScript best practices for building scalable and maintainable applications."
                ),
                author="Bob Johnson",
                published_at=datetime.fromisoformat("2024-01-13T14:45:00+00:00"),
            ),
        ]
        # Full posts by id
        self._posts_by_id: dict[str, Post] = {
            "post-123": Post(
                id="post-123",
                title="Getting Started with Next.js",
                content=(
                    "# Introduction\n\nNext.js is a powerful React framework that enables you to build full-stack web applications."
                ),
                excerpt=(
                    "Learn the basics of Next.js in this comprehensive guide covering SSR, SSG, and CSR."
                ),
                author="John Doe",
                status="published",
                published_at=datetime.fromisoformat("2024-01-15T10:30:00+00:00"),
            )
        }
        self._comments_by_post: dict[str, list[Comment]] = {
            "post-123": [
                Comment(
                    id="comment-456",
                    content=(
                        "Great article! Very helpful explanation of Next.js features. I especially liked the section on SSR vs SSG."
                    ),
                    author="Jane Smith",
                    created_at=datetime.fromisoformat("2024-01-15T14:20:00+00:00"),
                    post_id="post-123",
                )
            ]
        }
        self._post_counter = 126
        self._comment_counter = 457

    async def list_posts(self, *, page: int, limit: int) -> Tuple[Sequence[PostSummary], int]:
        start = (page - 1) * limit
        end = start + limit
        return self._posts[start:end], len(self._posts)

    async def get_post(self, post_id: str) -> Optional[Post]:
        return self._posts_by_id.get(post_id)

    async def create_post(
        self, *, title: str, content: str, excerpt: Optional[str], status: str, author: str
    ) -> Post:
        new_id = f"post-{self._post_counter}"
        self._post_counter += 1
        published_at = datetime.utcnow() if status == "published" else None
        post = Post(
            id=new_id,
            title=title,
            content=content,
            excerpt=excerpt,
            author=author,
            status=status,
            published_at=published_at,
        )
        self._posts_by_id[new_id] = post
        # Update summaries list (prepend)
        summary = PostSummary(
            id=new_id,
            title=title,
            excerpt=excerpt or content[:120],
            author=author,
            published_at=published_at or datetime.utcnow(),
        )
        self._posts.insert(0, summary)
        return post

    async def update_post(
        self, post_id: str, *, title: str, content: str, excerpt: Optional[str], status: str
    ) -> Optional[Post]:
        existing = self._posts_by_id.get(post_id)
        if not existing:
            return None
        published_at = existing.published_at
        if status == "published" and not published_at:
            published_at = datetime.utcnow()
        updated = Post(
            id=post_id,
            title=title,
            content=content,
            excerpt=excerpt,
            author=existing.author,
            status=status,
            published_at=published_at,
        )
        self._posts_by_id[post_id] = updated
        # Update summary entry
        for i, s in enumerate(self._posts):
            if s.id == post_id:
                self._posts[i] = PostSummary(
                    id=post_id,
                    title=title,
                    excerpt=excerpt or content[:120],
                    author=existing.author,
                    published_at=published_at or datetime.utcnow(),
                )
                break
        return updated

    async def list_comments(self, post_id: str) -> Optional[Sequence[Comment]]:
        if post_id not in self._posts_by_id:
            return None
        return list(self._comments_by_post.get(post_id, []))

    async def create_comment(self, post_id: str, *, content: str, author: str) -> Optional[Comment]:
        if post_id not in self._posts_by_id:
            return None
        new_id = f"comment-{self._comment_counter}"
        self._comment_counter += 1
        comment = Comment(
            id=new_id,
            content=content,
            author=author,
            created_at=datetime.utcnow(),
            post_id=post_id,
        )
        self._comments_by_post.setdefault(post_id, []).append(comment)
        return comment
