"""Standardized error handling utilities."""

from functools import wraps
from typing import Callable, Any
from fastapi import HTTPException, status

from app.application.exceptions import (
    ValidationError, 
    NotFoundError, 
    ForbiddenError, 
    ApplicationError, 
    AuthenticationError
)
from app.shared.constants import ERROR_POST_NOT_FOUND


def handle_service_exceptions(func: Callable) -> Callable:
    """
    Decorator to standardize exception handling across API routes.
    
    Converts application exceptions to appropriate HTTP responses.
    """
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.message
            )
        except AuthenticationError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=e.message
            )
        except ForbiddenError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=e.message
            )
        except NotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=e.message if hasattr(e, 'message') else ERROR_POST_NOT_FOUND
            )
        except ApplicationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=e.message
            )
    
    return wrapper


def raise_not_found_error(resource_type: str = "resource") -> None:
    """Raise a standardized not found error."""
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{resource_type.capitalize()} not found"
    )


def raise_forbidden_error(message: str = "Access forbidden") -> None:
    """Raise a standardized forbidden error."""
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=message
    )


def raise_validation_error(message: str) -> None:
    """Raise a standardized validation error."""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=message
    )