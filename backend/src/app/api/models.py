from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class BlogPostSummary(BaseModel):
    """Summary view of a blog post, matching OpenAPI BlogPostSummary."""

    id: str = Field(..., description="Unique identifier for the blog post")
    title: str = Field(..., description="Title of the blog post")
    excerpt: str = Field(..., description="Short summary of the blog post")
    author: str = Field(..., description="Author of the blog post")
    publishedAt: datetime = Field(..., description="Published timestamp (ISO 8601)")


class PaginationInfo(BaseModel):
    page: int
    limit: int
    total: int
    hasNext: bool


class BlogPostListData(BaseModel):
    posts: List[BlogPostSummary]
    pagination: PaginationInfo


class BlogPostListResponse(BaseModel):
    status: Literal["success"] = "success"
    data: BlogPostListData


# Full post model and response
class BlogPost(BaseModel):
    id: str
    title: str
    content: str
    excerpt: Optional[str] = None
    author: str
    publishedAt: Optional[datetime] = None
    status: Literal["draft", "published"]


class BlogPostResponse(BaseModel):
    status: Literal["success"] = "success"
    data: BlogPost


# Comments
class Comment(BaseModel):
    id: str
    content: str
    author: str
    createdAt: datetime
    postId: str


class CommentsResponse(BaseModel):
    status: Literal["success"] = "success"
    data: List[Comment]


# Requests
class CreatePostRequest(BaseModel):
    title: str
    content: str
    excerpt: Optional[str] = None
    status: Literal["draft", "published"] = "draft"


class CreateCommentRequest(BaseModel):
    content: str
    author: str
