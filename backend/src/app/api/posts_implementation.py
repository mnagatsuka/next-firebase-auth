"""Posts API implementation using layered architecture."""

import sys
import os
from pathlib import Path
from typing import Optional
from datetime import datetime
from pydantic import Field, StrictStr
from typing_extensions import Annotated
from fastapi import HTTPException

# Add the generated code to Python path
generated_path = Path(__file__).parent.parent / "generated" / "src"
sys.path.insert(0, str(generated_path))

from generated_fastapi_server.apis.posts_api_base import BasePostsApi
from generated_fastapi_server.models.blog_post_list_response import BlogPostListResponse
from generated_fastapi_server.models.blog_post_response import BlogPostResponse
from generated_fastapi_server.models.create_post_request import CreatePostRequest
from generated_fastapi_server.models.blog_post import BlogPost as ApiBlogPost
from generated_fastapi_server.models.blog_post_summary import BlogPostSummary
from generated_fastapi_server.models.blog_post_list_data import BlogPostListData
from generated_fastapi_server.models.pagination import Pagination
from generated_fastapi_server.models.api_response_status import ApiResponseStatus

# Import our layered architecture
from app.application.services.posts_service import PostApplicationService
from app.application.exceptions import (
    ValidationError, 
    NotFoundError, 
    ForbiddenError,
    ApplicationError
)
from app.infra.repositories.posts_repository import InMemoryPostRepository


class PostsImplementation(BasePostsApi):
    """Implementation of the Posts API using layered architecture."""
    
    def __init__(self):
        # Initialize with layered architecture
        self.post_repository = InMemoryPostRepository()
        self.post_service = PostApplicationService(self.post_repository)
    
    async def create_blog_post(
        self,
        create_post_request: Annotated[CreatePostRequest, Field(description="Blog post data")]
    ) -> BlogPostResponse:
        """Creates a new blog post."""
        try:
            # TODO: Extract user ID from Firebase Auth token
            # For now, use test-author to match test data
            author = "test-author"
            
            post_data = await self.post_service.create_post(
                title=create_post_request.title,
                content=create_post_request.content,
                excerpt=create_post_request.excerpt,
                author=author
            )
            
            # Handle publishedAt field - use a placeholder datetime for draft posts
            published_at = post_data["publishedAt"]
            if published_at is None:
                # For draft posts, use epoch time as placeholder
                published_at = datetime.fromtimestamp(0).isoformat()
            
            api_post = ApiBlogPost(
                id=post_data["id"],
                title=post_data["title"],
                content=post_data["content"],
                excerpt=post_data["excerpt"],
                author=post_data["author"],
                publishedAt=published_at,
                status=post_data["status"]
            )
            
            return BlogPostResponse(
                status=ApiResponseStatus.SUCCESS,
                data=api_post
            )
            
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=e.message)
        except ApplicationError as e:
            raise HTTPException(status_code=500, detail=e.message)
    
    async def delete_blog_post(
        self,
        id: Annotated[StrictStr, Field(description="Unique identifier for the blog post")]
    ) -> None:
        """Deletes a blog post by its ID."""
        try:
            # TODO: Extract user ID from Firebase Auth token
            # For now, use test-author to match test data
            user_id = "test-author"
            await self.post_service.delete_post(id, user_id)
        except NotFoundError:
            raise HTTPException(status_code=404, detail="Blog post not found")
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=e.message)
        except ApplicationError as e:
            raise HTTPException(status_code=500, detail=e.message)
    
    async def get_blog_post_by_id(
        self,
        id: Annotated[StrictStr, Field(description="Unique identifier for the blog post")]
    ) -> BlogPostResponse:
        """Retrieves detailed information about a specific blog post by its ID."""
        try:
            post_data = await self.post_service.get_post_by_id(id)
            
            # Handle publishedAt field - use a placeholder datetime for draft posts
            published_at = post_data["publishedAt"]
            if published_at is None:
                published_at = datetime.fromtimestamp(0).isoformat()
            
            api_post = ApiBlogPost(
                id=post_data["id"],
                title=post_data["title"],
                content=post_data["content"],
                excerpt=post_data["excerpt"],
                author=post_data["author"],
                publishedAt=published_at,
                status=post_data["status"]
            )
            
            return BlogPostResponse(
                status=ApiResponseStatus.SUCCESS,
                data=api_post
            )
            
        except NotFoundError:
            raise HTTPException(status_code=404, detail="Blog post not found")
        except ApplicationError as e:
            raise HTTPException(status_code=500, detail=e.message)
    
    async def get_blog_posts(
        self,
        page: Annotated[Optional[Annotated[int, Field(strict=True, ge=1)]], Field(description="Page number for pagination")],
        limit: Annotated[Optional[Annotated[int, Field(le=50, strict=True, ge=1)]], Field(description="Number of items per page")],
        status: Annotated[Optional[StrictStr], Field(description="Filter posts by status")],
        author: Annotated[Optional[StrictStr], Field(description="Filter posts by author name")]
    ) -> BlogPostListResponse:
        """Retrieves a paginated list of blog posts."""
        try:
            page = page or 1
            limit = limit or 10
            status = status or "published"
            
            response_data = await self.post_service.get_posts(
                page=page,
                limit=limit,
                status=status,
                author=author
            )
            
            post_summaries = []
            for post in response_data["data"]:
                # Handle publishedAt field for summary
                published_at = post["publishedAt"]
                if published_at is None:
                    published_at = datetime.fromtimestamp(0).isoformat()
                
                post_summaries.append(BlogPostSummary(
                    id=post["id"],
                    title=post["title"],
                    excerpt=post["excerpt"],
                    author=post["author"],
                    publishedAt=published_at,
                    status=post["status"]
                ))
            
            # Calculate has_next for pagination
            total = response_data["pagination"]["total"]
            current_page = response_data["pagination"]["page"]
            limit = response_data["pagination"]["limit"]
            has_next = (current_page * limit) < total
            
            data = BlogPostListData(
                posts=post_summaries,
                pagination=Pagination(
                    page=current_page,
                    limit=limit,
                    total=total,
                    hasNext=has_next
                )
            )
            
            return BlogPostListResponse(
                status=ApiResponseStatus.SUCCESS,
                data=data
            )
            
        except ApplicationError as e:
            raise HTTPException(status_code=500, detail=e.message)
    
    async def update_blog_post(
        self,
        id: Annotated[StrictStr, Field(description="Unique identifier for the blog post")],
        create_post_request: Annotated[CreatePostRequest, Field(description="Updated blog post data")]
    ) -> BlogPostResponse:
        """Updates an existing blog post by its ID."""
        try:
            # TODO: Extract user ID from Firebase Auth token
            # For now, use test-author to match test data
            user_id = "test-author"
            
            post_data = await self.post_service.update_post(
                post_id=id,
                user_id=user_id,
                title=create_post_request.title,
                content=create_post_request.content,
                excerpt=create_post_request.excerpt
            )
            
            # Handle publishedAt field - use a placeholder datetime for draft posts
            published_at = post_data["publishedAt"]
            if published_at is None:
                published_at = datetime.fromtimestamp(0).isoformat()
            
            api_post = ApiBlogPost(
                id=post_data["id"],
                title=post_data["title"],
                content=post_data["content"],
                excerpt=post_data["excerpt"],
                author=post_data["author"],
                publishedAt=published_at,
                status=post_data["status"]
            )
            
            return BlogPostResponse(
                status=ApiResponseStatus.SUCCESS,
                data=api_post
            )
            
        except NotFoundError:
            raise HTTPException(status_code=404, detail="Blog post not found")
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=e.message)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=e.message)
        except ApplicationError as e:
            raise HTTPException(status_code=500, detail=e.message)