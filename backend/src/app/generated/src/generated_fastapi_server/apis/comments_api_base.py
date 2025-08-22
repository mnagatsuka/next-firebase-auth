# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field, StrictStr
from typing import Optional
from typing_extensions import Annotated
from generated_fastapi_server.models.comments_acknowledgment_response import CommentsAcknowledgmentResponse
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
    ) -> CommentsAcknowledgmentResponse:
        """Creates a new comment on a specific blog post. Requires authentication.  **Response Pattern:** - HTTP Response: Acknowledgment response only (no comment data) - WebSocket Broadcast: New comment data is broadcast to all connected clients via API Gateway WebSocket  **WebSocket Message Format (sent to all clients after successful creation):** &#x60;&#x60;&#x60;json {   \&quot;type\&quot;: \&quot;NEW_COMMENT\&quot;,   \&quot;postId\&quot;: \&quot;string\&quot;,   \&quot;comment\&quot;: {     \&quot;id\&quot;: \&quot;string\&quot;,     \&quot;content\&quot;: \&quot;string\&quot;,     \&quot;authorId\&quot;: \&quot;string\&quot;,      \&quot;authorName\&quot;: \&quot;string\&quot;,     \&quot;createdAt\&quot;: \&quot;timestamp\&quot;   } } &#x60;&#x60;&#x60;  The userId will be automatically set based on the authenticated user&#39;s Firebase UID. Comments are moderated and may not appear immediately. """
        ...


    async def get_post_comments(
        self,
        id: Annotated[StrictStr, Field(description="Unique identifier for the blog post")],
        limit: Annotated[Optional[Annotated[int, Field(le=100, strict=True, ge=1)]], Field(description="Maximum number of comments to return")],
    ) -> CommentsResponse:
        """Retrieves all comments for a specific blog post via standard REST API.  **Response Pattern:** - HTTP Response: Direct JSON response with comments array - No WebSocket involvement for this endpoint  Comments are returned in chronological order (oldest first). This endpoint is public and does not require authentication. """
        ...
