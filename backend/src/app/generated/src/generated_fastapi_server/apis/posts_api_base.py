# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field, StrictStr, field_validator
from typing import Any, Optional
from typing_extensions import Annotated
from generated_fastapi_server.models.blog_post_list_response import BlogPostListResponse
from generated_fastapi_server.models.blog_post_response import BlogPostResponse
from generated_fastapi_server.models.create_post_request import CreatePostRequest
from generated_fastapi_server.models.error import Error
from generated_fastapi_server.security_api import get_token_firebaseAuth

class BasePostsApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BasePostsApi.subclasses = BasePostsApi.subclasses + (cls,)
    async def create_blog_post(
        self,
        create_post_request: Annotated[CreatePostRequest, Field(description="Blog post data")],
    ) -> BlogPostResponse:
        """Creates a new blog post. Requires Firebase Authentication with a non-anonymous user.  Anonymous users are forbidden from creating posts. The author is inferred from the authenticated Firebase user&#39;s UID. Posts may be created as &#x60;draft&#x60; or &#x60;published&#x60; depending on the request payload. """
        ...


    async def delete_blog_post(
        self,
        id: Annotated[StrictStr, Field(description="Unique identifier for the blog post")],
    ) -> None:
        """Deletes a blog post by its ID. Requires authentication.  Only the author of the post or users with admin privileges can delete a post. This action is irreversible. """
        ...


    async def favorite_post(
        self,
        id: Annotated[StrictStr, Field(description="Unique identifier for the blog post")],
    ) -> None:
        """Marks a post as a favorite for the current user. Requires Firebase Authentication.  Works for both anonymous and authenticated users. Anonymous users must include a valid anonymous Firebase ID token. """
        ...


    async def get_blog_post_by_id(
        self,
        id: Annotated[StrictStr, Field(description="Unique identifier for the blog post")],
    ) -> BlogPostResponse:
        """Retrieves detailed information about a specific blog post by its ID.  Returns the complete blog post including content, metadata, and author information. """
        ...


    async def get_blog_posts(
        self,
        page: Annotated[Optional[Annotated[int, Field(strict=True, ge=1)]], Field(description="Page number for pagination")],
        limit: Annotated[Optional[Annotated[int, Field(le=50, strict=True, ge=1)]], Field(description="Number of items per page")],
        status: Annotated[Optional[StrictStr], Field(description="Filter posts by status")],
        author: Annotated[Optional[StrictStr], Field(description="Filter posts by author name")],
    ) -> BlogPostListResponse:
        """Retrieves a paginated list of published blog posts.  This endpoint supports pagination and returns blog post summaries optimized for listing views (homepage, archives, etc.). """
        ...


    async def get_user_favorites(
        self,
        uid: Annotated[StrictStr, Field(description="Firebase Authentication user ID (UID)")],
        page: Annotated[Optional[Annotated[int, Field(strict=True, ge=1)]], Field(description="Page number for pagination")],
        limit: Annotated[Optional[Annotated[int, Field(le=50, strict=True, ge=1)]], Field(description="Number of items per page")],
    ) -> BlogPostListResponse:
        """Retrieves a paginated list of posts favorited by the specified user (Firebase &#x60;uid&#x60;).  Requires Firebase Authentication. The caller must be the same user as &#x60;{uid}&#x60; or have admin permissions. """
        ...


    async def get_user_posts(
        self,
        uid: Annotated[StrictStr, Field(description="Firebase Authentication user ID (UID)")],
        page: Annotated[Optional[Annotated[int, Field(strict=True, ge=1)]], Field(description="Page number for pagination")],
        limit: Annotated[Optional[Annotated[int, Field(le=50, strict=True, ge=1)]], Field(description="Number of items per page")],
        status: Annotated[Optional[StrictStr], Field(description="Optional status filter for user-owned posts")],
    ) -> BlogPostListResponse:
        """Retrieves a paginated list of blog posts owned by the specified user (identified by Firebase &#x60;uid&#x60;).  Requires Firebase Authentication. The caller must be the same user as &#x60;{uid}&#x60; or have admin permissions.  Supports filtering by &#x60;status&#x60;. When &#x60;status&#x60; is omitted, returns all posts for the user (both &#x60;published&#x60; and &#x60;draft&#x60;). """
        ...


    async def unfavorite_post(
        self,
        id: Annotated[StrictStr, Field(description="Unique identifier for the blog post")],
    ) -> None:
        """Removes a post from the current user&#39;s favorites. Requires Firebase Authentication.  Works for both anonymous and authenticated users. """
        ...


    async def update_blog_post(
        self,
        id: Annotated[StrictStr, Field(description="Unique identifier for the blog post")],
        create_post_request: Annotated[CreatePostRequest, Field(description="Updated blog post data")],
    ) -> BlogPostResponse:
        """Updates an existing blog post by its ID. Requires authentication.  Only the author of the post or users with admin privileges can update a post. Partial updates are supported - only provided fields will be updated. """
        ...
