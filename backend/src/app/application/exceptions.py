"""Application exceptions for the blog application."""


class ApplicationError(Exception):
    """Base application exception."""
    
    def __init__(self, message: str, code: str = None):
        super().__init__(message)
        self.message = message
        self.code = code or "APPLICATION_ERROR"


class ValidationError(ApplicationError):
    """Validation error in application layer."""
    
    def __init__(self, message: str, field: str = None):
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field


class NotFoundError(ApplicationError):
    """Resource not found error."""
    
    def __init__(self, message: str):
        super().__init__(message, "NOT_FOUND")


class UnauthorizedError(ApplicationError):
    """Unauthorized access error."""
    
    def __init__(self, message: str):
        super().__init__(message, "UNAUTHORIZED")


class ForbiddenError(ApplicationError):
    """Forbidden access error."""
    
    def __init__(self, message: str):
        super().__init__(message, "FORBIDDEN")


class ConflictError(ApplicationError):
    """Resource conflict error."""
    
    def __init__(self, message: str):
        super().__init__(message, "CONFLICT")


class AuthenticationError(ApplicationError):
    """Firebase authentication error."""
    
    def __init__(self, message: str):
        super().__init__(message, "AUTHENTICATION_ERROR")


class InvalidTokenError(AuthenticationError):
    """Invalid Firebase token error."""
    
    def __init__(self, message: str = "Invalid or expired token"):
        super().__init__(message)