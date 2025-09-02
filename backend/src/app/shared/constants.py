"""Application constants."""

from typing import Final

# Pagination constants
DEFAULT_PAGE: Final[int] = 1
DEFAULT_LIMIT: Final[int] = 10
MIN_PAGE_SIZE: Final[int] = 1
MAX_PAGE_SIZE: Final[int] = 50
MAX_COMMENTS_PER_REQUEST: Final[int] = 100

# Post status constants
POST_STATUS_DRAFT: Final[str] = "draft"
POST_STATUS_PUBLISHED: Final[str] = "published"
VALID_POST_STATUSES: Final[tuple] = (POST_STATUS_DRAFT, POST_STATUS_PUBLISHED)

# API Response messages
ERROR_POST_NOT_FOUND: Final[str] = "Blog post not found"
ERROR_COMMENT_NOT_FOUND: Final[str] = "Comment not found"
ERROR_UNAUTHORIZED_UPDATE: Final[str] = "You don't have permission to update this post"
ERROR_UNAUTHORIZED_DELETE: Final[str] = "You don't have permission to delete this post"
ERROR_UNAUTHORIZED_PUBLISH: Final[str] = "You don't have permission to publish this post"