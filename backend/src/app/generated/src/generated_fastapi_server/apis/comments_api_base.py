# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field, StrictStr
from typing import Optional
from typing_extensions import Annotated
from generated_fastapi_server.models.comment import Comment
from generated_fastapi_server.models.comments_response import CommentsResponse
from generated_fastapi_server.models.create_comment_request import CreateCommentRequest
from generated_fastapi_server.models.error import Error
from generated_fastapi_server.security_api import get_token_firebaseAuth

class BaseCommentsApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseCommentsApi.subclasses = BaseCommentsApi.subclasses + (cls,)
    async def create_comment(
        self,
        id: Annotated[StrictStr, Field(description="Unique identifier for the blog post")],
        create_comment_request: Annotated[CreateCommentRequest, Field(description="Comment data")],
    ) -> Comment:
        """Creates a new comment on a specific blog post. Requires authentication.  The author field will be automatically set based on the authenticated user. Comments are moderated and may not appear immediately. """
        ...


    async def get_post_comments(
        self,
        id: Annotated[StrictStr, Field(description="Unique identifier for the blog post")],
        limit: Annotated[Optional[Annotated[int, Field(le=100, strict=True, ge=1)]], Field(description="Maximum number of comments to return")],
    ) -> CommentsResponse:
        """Retrieves all comments for a specific blog post.  Comments are returned in chronological order (oldest first). This endpoint is public and does not require authentication. """
        ...
