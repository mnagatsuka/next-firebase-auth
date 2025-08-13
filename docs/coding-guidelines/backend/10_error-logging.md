# Error Handling & Logging Guidelines

## Overview

Robust error handling and comprehensive logging are critical for maintaining reliable, observable, and debuggable systems. This document covers exception taxonomy, structured logging, correlation tracking, and operational monitoring patterns for Python FastAPI applications.

## Key Principles

- **Exception taxonomy**: Organize exceptions by domain and recovery patterns
- **Structured logging**: Use consistent, machine-readable log formats
- **Correlation tracking**: Trace requests across service boundaries
- **Security-first**: Never log sensitive data or credentials
- **Operational focus**: Log for monitoring, alerting, and debugging

## Exception Taxonomy

### Exception Hierarchy

```python
from abc import ABC
from typing import Dict, Any, Optional
from enum import Enum


class ErrorSeverity(Enum):
    """Error severity levels for monitoring and alerting."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BaseApplicationError(Exception, ABC):
    """Base exception for all application errors."""
    
    def __init__(
        self,
        message: str,
        error_code: str,
        details: Optional[Dict[str, Any]] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        user_message: Optional[str] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.severity = severity
        self.user_message = user_message or "An error occurred while processing your request"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging and API responses."""
        return {
            'error_type': self.__class__.__name__,
            'error_code': self.error_code,
            'message': self.message,
            'user_message': self.user_message,
            'severity': self.severity.value,
            'details': self.details,
        }


class ValidationError(BaseApplicationError):
    """Base class for validation errors."""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs
    ):
        details = kwargs.pop('details', {})
        if field:
            details['field'] = field
        if value is not None:
            details['value'] = str(value)  # Convert to string to avoid serialization issues
        
        super().__init__(
            message=message,
            error_code='VALIDATION_ERROR',
            details=details,
            severity=ErrorSeverity.LOW,
            user_message="The provided data is invalid",
            **kwargs
        )


class BusinessRuleViolationError(BaseApplicationError):
    """Business rule violation errors."""
    
    def __init__(self, message: str, rule: str, **kwargs):
        super().__init__(
            message=message,
            error_code='BUSINESS_RULE_VIOLATION',
            details={'rule': rule, **kwargs.pop('details', {})},
            severity=ErrorSeverity.MEDIUM,
            user_message="This operation violates business rules",
            **kwargs
        )


class ResourceNotFoundError(BaseApplicationError):
    """Resource not found errors."""
    
    def __init__(self, resource_type: str, resource_id: str, **kwargs):
        super().__init__(
            message=f"{resource_type} not found: {resource_id}",
            error_code='RESOURCE_NOT_FOUND',
            details={'resource_type': resource_type, 'resource_id': resource_id},
            severity=ErrorSeverity.LOW,
            user_message=f"The requested {resource_type.lower()} was not found",
            **kwargs
        )


class AuthenticationError(BaseApplicationError):
    """Authentication failures."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            error_code='AUTHENTICATION_FAILED',
            severity=ErrorSeverity.HIGH,
            user_message="Authentication failed",
            **kwargs
        )


class AuthorizationError(BaseApplicationError):
    """Authorization failures."""
    
    def __init__(self, message: str, required_permission: Optional[str] = None, **kwargs):
        details = kwargs.pop('details', {})
        if required_permission:
            details['required_permission'] = required_permission
        
        super().__init__(
            message=message,
            error_code='AUTHORIZATION_FAILED',
            details=details,
            severity=ErrorSeverity.HIGH,
            user_message="You don't have permission to perform this action",
            **kwargs
        )


class ExternalServiceError(BaseApplicationError):
    """External service integration errors."""
    
    def __init__(
        self,
        service_name: str,
        message: str,
        status_code: Optional[int] = None,
        **kwargs
    ):
        details = {'service': service_name, **kwargs.pop('details', {})}
        if status_code:
            details['status_code'] = status_code
        
        super().__init__(
            message=f"{service_name}: {message}",
            error_code='EXTERNAL_SERVICE_ERROR',
            details=details,
            severity=ErrorSeverity.HIGH,
            user_message="A dependent service is currently unavailable",
            **kwargs
        )


class RateLimitExceededError(BaseApplicationError):
    """Rate limiting errors."""
    
    def __init__(self, limit: int, window: str, **kwargs):
        super().__init__(
            message=f"Rate limit exceeded: {limit} requests per {window}",
            error_code='RATE_LIMIT_EXCEEDED',
            details={'limit': limit, 'window': window},
            severity=ErrorSeverity.MEDIUM,
            user_message="Too many requests. Please try again later.",
            **kwargs
        )


class InfrastructureError(BaseApplicationError):
    """Infrastructure-level errors (database, network, etc.)."""
    
    def __init__(self, component: str, message: str, **kwargs):
        super().__init__(
            message=f"{component}: {message}",
            error_code='INFRASTRUCTURE_ERROR',
            details={'component': component, **kwargs.pop('details', {})},
            severity=ErrorSeverity.CRITICAL,
            user_message="A system error occurred. Please try again later.",
            **kwargs
        )
```

### Domain-Specific Exceptions

```python
# User domain exceptions
class UserDomainError(BaseApplicationError):
    """Base class for user domain errors."""
    pass


class UserNotFoundError(ResourceNotFoundError):
    """User not found error."""
    
    def __init__(self, user_id: str):
        super().__init__(resource_type="User", resource_id=user_id)


class DuplicateEmailError(BusinessRuleViolationError):
    """Duplicate email error."""
    
    def __init__(self, email: str):
        super().__init__(
            message=f"User with email {email} already exists",
            rule="unique_email",
            details={'email': email},
            user_message="An account with this email already exists",
        )


class InvalidEmailFormatError(ValidationError):
    """Invalid email format error."""
    
    def __init__(self, email: str):
        super().__init__(
            message=f"Invalid email format: {email}",
            field="email",
            value=email,
        )


# Authentication domain exceptions
class InvalidTokenError(AuthenticationError):
    """Invalid authentication token."""
    
    def __init__(self, token_type: str = "access_token"):
        super().__init__(
            message=f"Invalid {token_type}",
            details={'token_type': token_type},
        )


class TokenExpiredError(AuthenticationError):
    """Expired authentication token."""
    
    def __init__(self, token_type: str = "access_token"):
        super().__init__(
            message=f"Expired {token_type}",
            details={'token_type': token_type},
        )


# Infrastructure exceptions
class DatabaseConnectionError(InfrastructureError):
    """Database connection error."""
    
    def __init__(self, database: str, message: str):
        super().__init__(
            component=f"Database({database})",
            message=message,
        )


class S3OperationError(InfrastructureError):
    """S3 operation error."""
    
    def __init__(self, operation: str, bucket: str, key: Optional[str] = None):
        details = {'operation': operation, 'bucket': bucket}
        if key:
            details['key'] = key
        
        super().__init__(
            component="S3",
            message=f"{operation} failed",
            details=details,
        )
```

## HTTP Problem Details Translation

### RFC7807 Problem Details

```python
from typing import Dict, Any, Optional
from fastapi import HTTPException
from fastapi.responses import JSONResponse


class ProblemDetails:
    """RFC7807 Problem Details for HTTP APIs."""
    
    def __init__(
        self,
        type_uri: str,
        title: str,
        status: int,
        detail: Optional[str] = None,
        instance: Optional[str] = None,
        **extensions
    ):
        self.type_uri = type_uri
        self.title = title
        self.status = status
        self.detail = detail
        self.instance = instance
        self.extensions = extensions
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response."""
        result = {
            'type': self.type_uri,
            'title': self.title,
            'status': self.status,
        }
        
        if self.detail:
            result['detail'] = self.detail
        if self.instance:
            result['instance'] = self.instance
        
        result.update(self.extensions)
        return result


class ErrorTranslator:
    """Translate application exceptions to HTTP Problem Details."""
    
    BASE_URI = "https://api.example.com/problems"
    
    @classmethod
    def translate(
        self,
        error: BaseApplicationError,
        request_path: Optional[str] = None,
        trace_id: Optional[str] = None,
    ) -> ProblemDetails:
        """Translate application error to Problem Details."""
        
        # Map error types to HTTP status codes
        status_map = {
            ValidationError: 400,
            BusinessRuleViolationError: 422,
            ResourceNotFoundError: 404,
            AuthenticationError: 401,
            AuthorizationError: 403,
            RateLimitExceededError: 429,
            ExternalServiceError: 502,
            InfrastructureError: 503,
        }
        
        status_code = 500  # Default to internal server error
        for error_type, code in status_map.items():
            if isinstance(error, error_type):
                status_code = code
                break
        
        # Create extensions with safe details
        extensions = {
            'error_code': error.error_code,
            'severity': error.severity.value,
        }
        
        if trace_id:
            extensions['trace_id'] = trace_id
        
        # Add safe details (no sensitive information)
        if hasattr(error, 'details') and error.details:
            safe_details = self._sanitize_details(error.details)
            if safe_details:
                extensions['details'] = safe_details
        
        return ProblemDetails(
            type_uri=f"{self.BASE_URI}/{error.error_code.lower()}",
            title=error.__class__.__name__,
            status=status_code,
            detail=error.user_message,
            instance=request_path,
            **extensions
        )
    
    @staticmethod
    def _sanitize_details(details: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from error details."""
        sensitive_keys = {
            'password', 'token', 'secret', 'key', 'credential',
            'authorization', 'authentication', 'session'
        }
        
        return {
            k: v for k, v in details.items()
            if not any(sensitive in k.lower() for sensitive in sensitive_keys)
        }


def create_error_response(
    error: BaseApplicationError,
    request_path: Optional[str] = None,
    trace_id: Optional[str] = None,
) -> JSONResponse:
    """Create HTTP error response from application error."""
    problem_details = ErrorTranslator.translate(error, request_path, trace_id)
    
    return JSONResponse(
        status_code=problem_details.status,
        content=problem_details.to_dict(),
        headers={
            'Content-Type': 'application/problem+json',
            'X-Trace-ID': trace_id,
        } if trace_id else {'Content-Type': 'application/problem+json'}
    )
```

## Structured Logging

### Logging Configuration

```python
import logging
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional
import traceback
import uuid


class StructuredFormatter(logging.Formatter):
    """JSON structured log formatter."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }
        
        # Add trace information if available
        if hasattr(record, 'trace_id'):
            log_entry['trace_id'] = record.trace_id
        
        if hasattr(record, 'span_id'):
            log_entry['span_id'] = record.span_id
        
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        
        # Add request context
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        
        if hasattr(record, 'method'):
            log_entry['http_method'] = record.method
        
        if hasattr(record, 'path'):
            log_entry['http_path'] = record.path
        
        if hasattr(record, 'status_code'):
            log_entry['http_status'] = record.status_code
        
        if hasattr(record, 'duration'):
            log_entry['duration_ms'] = record.duration
        
        # Add extra fields
        if hasattr(record, 'extra_fields') and record.extra_fields:
            log_entry.update(record.extra_fields)
        
        # Add exception information
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info),
            }
        
        return json.dumps(log_entry, default=str)


def setup_logging(
    level: str = "INFO",
    service_name: str = "api",
    environment: str = "development",
) -> None:
    """Setup structured logging configuration."""
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler with structured formatter
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredFormatter())
    root_logger.addHandler(handler)
    
    # Add service context to all logs
    class ServiceFilter(logging.Filter):
        def filter(self, record):
            record.service = service_name
            record.environment = environment
            return True
    
    handler.addFilter(ServiceFilter())
    
    # Configure third-party loggers
    logging.getLogger('boto3').setLevel(logging.WARNING)
    logging.getLogger('botocore').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)


class ContextualLogger:
    """Logger with request context management."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._context: Dict[str, Any] = {}
    
    def set_context(self, **kwargs) -> None:
        """Set logging context for subsequent log calls."""
        self._context.update(kwargs)
    
    def clear_context(self) -> None:
        """Clear logging context."""
        self._context.clear()
    
    def _log_with_context(self, level: int, msg: str, *args, **kwargs) -> None:
        """Log message with current context."""
        extra = kwargs.get('extra', {})
        extra.update(self._context)
        kwargs['extra'] = extra
        
        self.logger.log(level, msg, *args, **kwargs)
    
    def debug(self, msg: str, *args, **kwargs) -> None:
        self._log_with_context(logging.DEBUG, msg, *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs) -> None:
        self._log_with_context(logging.INFO, msg, *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs) -> None:
        self._log_with_context(logging.WARNING, msg, *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs) -> None:
        self._log_with_context(logging.ERROR, msg, *args, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs) -> None:
        self._log_with_context(logging.CRITICAL, msg, *args, **kwargs)
    
    def exception(self, msg: str, *args, **kwargs) -> None:
        """Log exception with traceback."""
        kwargs['exc_info'] = True
        self.error(msg, *args, **kwargs)
```

## Correlation and Trace IDs

### Request Tracing Middleware

```python
from fastapi import FastAPI, Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
import time
import uuid
from contextvars import ContextVar
from typing import Optional


# Context variables for request tracing
trace_id_var: ContextVar[Optional[str]] = ContextVar('trace_id', default=None)
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar('user_id', default=None)


class TracingMiddleware(BaseHTTPMiddleware):
    """Middleware for request tracing and correlation."""
    
    async def dispatch(self, request: Request, call_next):
        # Generate or extract trace ID
        trace_id = request.headers.get('X-Trace-ID') or str(uuid.uuid4())
        request_id = str(uuid.uuid4())
        
        # Set context variables
        trace_id_var.set(trace_id)
        request_id_var.set(request_id)
        
        # Extract user ID from auth token if available
        user_id = self._extract_user_id(request)
        if user_id:
            user_id_var.set(user_id)
        
        # Add to request state for access in handlers
        request.state.trace_id = trace_id
        request.state.request_id = request_id
        request.state.user_id = user_id
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Add tracing headers to response
            response.headers['X-Trace-ID'] = trace_id
            response.headers['X-Request-ID'] = request_id
            
            # Log successful request
            duration = (time.time() - start_time) * 1000
            self._log_request(request, response, duration)
            
            return response
            
        except Exception as e:
            # Log failed request
            duration = (time.time() - start_time) * 1000
            self._log_request(request, None, duration, error=e)
            raise
    
    def _extract_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from request (implement based on auth mechanism)."""
        # Example implementation - adapt based on your auth
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            # Parse JWT token or lookup session
            # Return user ID if found
            pass
        return None
    
    def _log_request(
        self,
        request: Request,
        response: Optional[Response],
        duration: float,
        error: Optional[Exception] = None,
    ) -> None:
        """Log request details."""
        logger = ContextualLogger('request')
        logger.set_context(
            trace_id=trace_id_var.get(),
            request_id=request_id_var.get(),
            user_id=user_id_var.get(),
        )
        
        extra = {
            'method': request.method,
            'path': request.url.path,
            'duration': duration,
            'user_agent': request.headers.get('user-agent'),
            'remote_addr': request.client.host if request.client else None,
        }
        
        if response:
            extra['status_code'] = response.status_code
            logger.info("Request completed", extra=extra)
        elif error:
            extra['error_type'] = error.__class__.__name__
            extra['error_message'] = str(error)
            logger.error("Request failed", extra=extra)


def get_trace_id() -> Optional[str]:
    """Get current trace ID from context."""
    return trace_id_var.get()


def get_request_id() -> Optional[str]:
    """Get current request ID from context."""
    return request_id_var.get()


def get_user_id() -> Optional[str]:
    """Get current user ID from context."""
    return user_id_var.get()
```

## Data Redaction Policy

### Sensitive Data Scrubber

```python
import re
from typing import Any, Dict, List, Set, Union


class DataRedactor:
    """Redact sensitive information from logs and responses."""
    
    # Patterns for sensitive data detection
    SENSITIVE_PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        'ssn': r'\b\d{3}[-.]?\d{2}[-.]?\d{4}\b',
        'credit_card': r'\b\d{4}[-.\s]?\d{4}[-.\s]?\d{4}[-.\s]?\d{4}\b',
        'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
        'aws_key': r'\b[A-Z0-9]{20}\b',
        'jwt': r'\beyJ[A-Za-z0-9_/+\-]{10,}={0,2}\b',
    }
    
    # Sensitive field names (case-insensitive)
    SENSITIVE_FIELDS = {
        'password', 'passwd', 'secret', 'token', 'key', 'auth',
        'authorization', 'authentication', 'credential', 'session',
        'cookie', 'csrf', 'api_key', 'private_key', 'access_key',
        'secret_key', 'client_secret', 'refresh_token', 'id_token',
    }
    
    @classmethod
    def redact_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Redact sensitive data from dictionary."""
        if not isinstance(data, dict):
            return data
        
        redacted = {}
        for key, value in data.items():
            if cls._is_sensitive_field(key):
                redacted[key] = cls._redact_value(value)
            elif isinstance(value, dict):
                redacted[key] = cls.redact_dict(value)
            elif isinstance(value, list):
                redacted[key] = cls.redact_list(value)
            elif isinstance(value, str):
                redacted[key] = cls.redact_string(value)
            else:
                redacted[key] = value
        
        return redacted
    
    @classmethod
    def redact_list(cls, data: List[Any]) -> List[Any]:
        """Redact sensitive data from list."""
        return [
            cls.redact_dict(item) if isinstance(item, dict)
            else cls.redact_list(item) if isinstance(item, list)
            else cls.redact_string(item) if isinstance(item, str)
            else item
            for item in data
        ]
    
    @classmethod
    def redact_string(cls, text: str) -> str:
        """Redact sensitive patterns from string."""
        if not isinstance(text, str):
            return text
        
        result = text
        for pattern_name, pattern in cls.SENSITIVE_PATTERNS.items():
            result = re.sub(pattern, cls._get_redaction_mask(pattern_name), result)
        
        return result
    
    @classmethod
    def _is_sensitive_field(cls, field_name: str) -> bool:
        """Check if field name indicates sensitive data."""
        return any(
            sensitive in field_name.lower()
            for sensitive in cls.SENSITIVE_FIELDS
        )
    
    @classmethod
    def _redact_value(cls, value: Any) -> str:
        """Redact a value completely."""
        if value is None:
            return None
        
        if isinstance(value, str) and len(value) > 0:
            # Show first and last character for debugging
            if len(value) <= 4:
                return '***'
            return f"{value[0]}{'*' * (len(value) - 2)}{value[-1]}"
        
        return '[REDACTED]'
    
    @classmethod
    def _get_redaction_mask(cls, pattern_name: str) -> str:
        """Get redaction mask for specific pattern."""
        masks = {
            'email': '[EMAIL]',
            'phone': '[PHONE]',
            'ssn': '[SSN]',
            'credit_card': '[CREDIT_CARD]',
            'ip_address': '[IP]',
            'aws_key': '[AWS_KEY]',
            'jwt': '[JWT_TOKEN]',
        }
        return masks.get(pattern_name, '[REDACTED]')
```

## Application Error Handler

### FastAPI Exception Handlers

```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.exception_handlers import http_exception_handler
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers."""
    
    @app.exception_handler(BaseApplicationError)
    async def application_error_handler(request: Request, exc: BaseApplicationError):
        """Handle application-specific errors."""
        logger = ContextualLogger('error_handler')
        logger.set_context(
            trace_id=get_trace_id(),
            request_id=get_request_id(),
            user_id=get_user_id(),
        )
        
        # Log error with context
        logger.error(
            "Application error occurred",
            extra={
                'error_type': exc.__class__.__name__,
                'error_code': exc.error_code,
                'severity': exc.severity.value,
                'error_details': DataRedactor.redact_dict(exc.details),
                'path': request.url.path,
                'method': request.method,
            },
            exc_info=True,
        )
        
        # Return Problem Details response
        return create_error_response(
            exc,
            request_path=str(request.url.path),
            trace_id=get_trace_id(),
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler_override(request: Request, exc: HTTPException):
        """Handle HTTP exceptions with logging."""
        logger = ContextualLogger('error_handler')
        logger.set_context(
            trace_id=get_trace_id(),
            request_id=get_request_id(),
            user_id=get_user_id(),
        )
        
        if exc.status_code >= 500:
            logger.error(
                "HTTP error occurred",
                extra={
                    'status_code': exc.status_code,
                    'detail': exc.detail,
                    'path': request.url.path,
                    'method': request.method,
                }
            )
        else:
            logger.info(
                "HTTP client error",
                extra={
                    'status_code': exc.status_code,
                    'detail': exc.detail,
                    'path': request.url.path,
                    'method': request.method,
                }
            )
        
        return await http_exception_handler(request, exc)
    
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions."""
        logger = ContextualLogger('error_handler')
        logger.set_context(
            trace_id=get_trace_id(),
            request_id=get_request_id(),
            user_id=get_user_id(),
        )
        
        logger.critical(
            "Unhandled exception occurred",
            extra={
                'error_type': exc.__class__.__name__,
                'path': request.url.path,
                'method': request.method,
            },
            exc_info=True,
        )
        
        # Create generic error response
        internal_error = InfrastructureError(
            component="Application",
            message="An unexpected error occurred",
        )
        
        return create_error_response(
            internal_error,
            request_path=str(request.url.path),
            trace_id=get_trace_id(),
        )
```

## Retry-Safe Operations and Idempotency

### Idempotency Key Handling

```python
import hashlib
from typing import Optional, Any, Dict
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class IdempotencyRecord:
    """Record for tracking idempotent operations."""
    key: str
    request_hash: str
    response_data: Optional[Dict[str, Any]]
    status: str  # 'pending', 'completed', 'failed'
    created_at: datetime
    expires_at: datetime
    attempts: int = 0


class IdempotencyManager:
    """Manage idempotent operations."""
    
    def __init__(self, store):  # Abstract store interface
        self._store = store
        self.logger = ContextualLogger('idempotency')
    
    async def ensure_idempotency(
        self,
        key: str,
        request_data: Any,
        operation_func,
        ttl_seconds: int = 3600,
    ) -> Any:
        """Ensure operation is executed only once for given key."""
        request_hash = self._hash_request(request_data)
        
        # Check for existing operation
        record = await self._store.get_record(key)
        
        if record:
            # Verify request consistency
            if record.request_hash != request_hash:
                self.logger.error(
                    "Idempotency key reused with different request",
                    extra={
                        'idempotency_key': key,
                        'original_hash': record.request_hash,
                        'new_hash': request_hash,
                    }
                )
                raise BusinessRuleViolationError(
                    "Idempotency key reused with different request data",
                    rule="idempotency_consistency",
                )
            
            # Return cached result if completed
            if record.status == 'completed':
                self.logger.info(
                    "Returning cached result for idempotent operation",
                    extra={'idempotency_key': key}
                )
                return record.response_data
            
            # Check if operation is still pending
            if record.status == 'pending':
                if datetime.utcnow() < record.expires_at:
                    raise BusinessRuleViolationError(
                        "Operation already in progress",
                        rule="operation_in_progress",
                    )
                else:
                    # Expired pending operation - can retry
                    self.logger.warning(
                        "Expired pending operation, allowing retry",
                        extra={'idempotency_key': key}
                    )
        
        # Create or update record as pending
        record = IdempotencyRecord(
            key=key,
            request_hash=request_hash,
            response_data=None,
            status='pending',
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(seconds=ttl_seconds),
            attempts=(record.attempts + 1) if record else 1,
        )
        
        await self._store.store_record(record)
        
        try:
            # Execute operation
            result = await operation_func()
            
            # Store successful result
            record.response_data = result
            record.status = 'completed'
            await self._store.store_record(record)
            
            self.logger.info(
                "Idempotent operation completed successfully",
                extra={'idempotency_key': key}
            )
            
            return result
            
        except Exception as e:
            # Mark as failed
            record.status = 'failed'
            await self._store.store_record(record)
            
            self.logger.error(
                "Idempotent operation failed",
                extra={
                    'idempotency_key': key,
                    'error_type': e.__class__.__name__,
                    'attempts': record.attempts,
                },
                exc_info=True,
            )
            
            raise
    
    def _hash_request(self, request_data: Any) -> str:
        """Create hash of request data for consistency checking."""
        if isinstance(request_data, dict):
            # Sort keys for consistent hashing
            sorted_data = json.dumps(request_data, sort_keys=True)
        else:
            sorted_data = str(request_data)
        
        return hashlib.sha256(sorted_data.encode()).hexdigest()
```

## Best Practices Summary

### Exception Handling

- **Specific exceptions**: Create specific exception types for different error conditions
- **Rich error context**: Include relevant details for debugging and monitoring
- **User-friendly messages**: Provide clear, actionable messages for end users
- **Severity classification**: Classify errors by severity for alerting and monitoring
- **Consistent error codes**: Use consistent error codes across the application

### Logging

- **Structured format**: Always use structured logging (JSON) for machine processing
- **Correlation IDs**: Include trace and request IDs in all log entries
- **Appropriate levels**: Use correct log levels (DEBUG, INFO, WARN, ERROR, CRITICAL)
- **Security-first**: Never log sensitive data or credentials
- **Performance impact**: Be mindful of logging performance in high-throughput scenarios

### Monitoring and Alerting

- **Error rates**: Monitor error rates by type and endpoint
- **Response times**: Track request duration and identify slow operations
- **Dependency health**: Monitor external service availability and performance
- **Resource usage**: Track database connections, memory usage, and CPU utilization
- **Business metrics**: Include business-relevant metrics in logs for analysis

### Operations

- **Runbooks**: Document common error scenarios and resolution steps
- **Health checks**: Implement comprehensive health checks for monitoring
- **Graceful degradation**: Design systems to handle partial failures gracefully
- **Circuit breakers**: Implement circuit breaker pattern for external dependencies
- **Observability**: Ensure system behavior is observable through logs, metrics, and traces