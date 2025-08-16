from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class PostSummary:
    """Domain entity representing a blog post summary."""

    id: str
    title: str
    excerpt: str
    author: str
    published_at: datetime


@dataclass(frozen=True)
class Post:
    id: str
    title: str
    content: str
    excerpt: Optional[str]
    author: str
    status: str  # 'draft' | 'published'
    published_at: Optional[datetime]


@dataclass(frozen=True)
class Comment:
    id: str
    content: str
    author: str
    created_at: datetime
    post_id: str
