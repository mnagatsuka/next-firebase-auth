"""Domain exceptions for the blog application."""


class DomainError(Exception):
    """Base domain exception."""
    pass


class PostNotFoundError(DomainError):
    """Raised when a blog post cannot be found."""
    pass


class InvalidPostStateError(DomainError):
    """Raised when a blog post is in an invalid state for the requested operation."""
    pass


class UnauthorizedPostAccessError(DomainError):
    """Raised when a user tries to access/modify a post they don't have permission for."""
    pass


class PostValidationError(DomainError):
    """Raised when post data fails domain validation."""
    pass


class CommentNotFoundError(DomainError):
    """Raised when a comment cannot be found."""
    pass


class CommentValidationError(DomainError):
    """Raised when comment data fails domain validation."""
    pass


class UnauthorizedCommentAccessError(DomainError):
    """Raised when a user tries to access/modify a comment they don't have permission for."""
    pass


class UserValidationError(DomainError):
    """Raised when user data validation fails"""
    pass


class UserNotFoundError(DomainError):
    """Raised when a user is not found"""
    pass


class AnonymousUserNotFoundError(DomainError):
    """Raised when an anonymous user is not found during promotion"""
    pass


class EmailAlreadyExistsError(DomainError):
    """Raised when attempting to use an email that already exists"""
    pass


class AccountLinkingConflictError(DomainError):
    """Raised when account linking encounters conflicts"""
    pass