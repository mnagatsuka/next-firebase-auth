# Error Handling & Logging

## Overview

Simple error handling and logging practices for Python FastAPI applications.

## Key Principles

- Keep exception handling simple and focused
- Use structured logging for better debugging
- Never log sensitive data or credentials
- Make errors helpful for debugging and users

## 1. Simple Exception Handling

Keep exceptions simple and focused on core needs:

```python
# Basic application exceptions
class ApplicationError(Exception):
    """Base application exception."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

class ValidationError(ApplicationError):
    """Validation error."""
    pass

class NotFoundError(ApplicationError):
    """Resource not found error."""
    pass

class AuthenticationError(ApplicationError):
    """Authentication error."""
    pass

class ExternalServiceError(ApplicationError):
    """External service error."""
    pass
```

### Domain-Specific Exceptions

```python
# Simple domain exceptions (from domain/exceptions.py)
class DomainError(Exception):
    """Base domain exception."""
    pass

class DuplicateEmailError(DomainError):
    """Email already exists."""
    pass

class UserNotFoundError(DomainError):
    """User not found."""
    pass
```

## 2. FastAPI Error Handling

Simple error handling with FastAPI:

```python
from fastapi import HTTPException
from app.core.exceptions import ApplicationError, NotFoundError, AuthenticationError

# Convert domain/application errors to HTTP responses
def handle_domain_error(error: Exception):
    """Convert domain errors to HTTP exceptions."""
    
    if isinstance(error, NotFoundError):
        raise HTTPException(status_code=404, detail=str(error))
    elif isinstance(error, AuthenticationError):
        raise HTTPException(status_code=401, detail=str(error))
    elif isinstance(error, ApplicationError):
        raise HTTPException(status_code=400, detail=str(error))
    else:
        # Unexpected error
        raise HTTPException(status_code=500, detail="Internal server error")

# Use in FastAPI routes
@app.get("/users/{user_id}")
async def get_user(user_id: str):
    try:
        user = await user_service.get_user(user_id)
        return user
    except Exception as e:
        handle_domain_error(e)
```

## 3. Simple Logging Setup

Basic logging configuration for development and production:

```python
import logging
import sys

def setup_logging(level: str = "INFO"):
    """Setup basic logging."""
    
    # Basic logging configuration
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Quiet down noisy third-party loggers
    logging.getLogger('boto3').setLevel(logging.WARNING)
    logging.getLogger('botocore').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

# Usage in your application
logger = logging.getLogger(__name__)

# Log examples
logger.info("User created successfully", extra={'user_id': user.id})
logger.error("Failed to connect to database", exc_info=True)
logger.warning("Rate limit exceeded for user", extra={'user_id': user.id})
```

## 4. Simple Request Logging

Basic request logging middleware:

```python
from fastapi import Request
from fastapi.middleware.base import BaseHTTPMiddleware
import time
import logging

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Simple request logging middleware."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log incoming request
        logger.info(f"Request started: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = (time.time() - start_time) * 1000
            
            # Log successful response
            logger.info(
                f"Request completed: {request.method} {request.url.path} - "
                f"{response.status_code} - {duration:.2f}ms"
            )
            
            return response
            
        except Exception as e:
            # Log error
            duration = (time.time() - start_time) * 1000
            logger.error(
                f"Request failed: {request.method} {request.url.path} - "
                f"{e.__class__.__name__}: {str(e)} - {duration:.2f}ms",
                exc_info=True
            )
            raise

# Add to FastAPI app
app.add_middleware(LoggingMiddleware)
```

## 5. Security Guidelines

Simple rules for secure logging:

```python
# Basic sensitive data protection
SENSITIVE_FIELDS = {'password', 'token', 'secret', 'key', 'auth'}

def safe_log_data(data: dict) -> dict:
    """Remove sensitive fields from data before logging."""
    safe_data = {}
    for key, value in data.items():
        if any(sensitive in key.lower() for sensitive in SENSITIVE_FIELDS):
            safe_data[key] = '[REDACTED]'
        else:
            safe_data[key] = value
    return safe_data

# Usage
logger.info("User data", extra={'data': safe_log_data(user_data)})
```

**Security Rules:**
- Never log passwords, tokens, or API keys
- Redact sensitive fields in logs
- Don't log full request/response bodies in production
- Use log levels appropriately (DEBUG only in development)

## 6. Global Exception Handler

Simple global exception handling for FastAPI:

```python
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    
    logger.error(
        f"Unhandled exception: {exc}",
        extra={
            'path': request.url.path,
            'method': request.method,
            'error_type': exc.__class__.__name__
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

## Best Practices Summary

### Exception Handling
- Keep exception types simple and focused
- Use domain-specific exceptions for business logic errors
- Convert domain errors to appropriate HTTP status codes
- Log errors with sufficient context for debugging
- Never expose sensitive information in error messages

### Logging
- Use appropriate log levels (INFO for normal operations, ERROR for failures)
- Include relevant context in log messages (user IDs, operation details)
- Log structured data using the `extra` parameter
- Never log passwords, tokens, or sensitive data
- Use middleware to log all HTTP requests automatically

### Error Responses
- Return consistent error response formats
- Use FastAPI's built-in validation for request data
- Provide helpful error messages to API consumers
- Log detailed errors for debugging but return simple messages to clients

This simplified approach focuses on essential error handling and logging practices without over-engineering for small to medium applications.