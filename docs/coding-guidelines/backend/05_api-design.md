# 5. API Design & Versioning (Transport Layer)

This section defines the rules and best practices for **RESTful API design**, **versioning**, **error handling**, and **OpenAPI documentation** in Python + FastAPI applications.

Our goals are:
- Design consistent, resource-oriented REST APIs
- Implement robust versioning and deprecation strategies  
- Provide comprehensive error handling with RFC7807 Problem Details
- Generate and maintain accurate OpenAPI documentation
- Support pagination, filtering, and field selection

## 1. Resource-First API Design

### HTTP Methods & Resource Patterns

Follow REST conventions for predictable API behavior:

```python
# Users resource
GET    /api/v1/users              # List users
POST   /api/v1/users              # Create user
GET    /api/v1/users/{user_id}    # Get user
PUT    /api/v1/users/{user_id}    # Update user (full replace)
PATCH  /api/v1/users/{user_id}    # Update user (partial)
DELETE /api/v1/users/{user_id}    # Delete user

# Nested resources
GET    /api/v1/users/{user_id}/posts        # List user's posts
POST   /api/v1/users/{user_id}/posts        # Create post for user
GET    /api/v1/users/{user_id}/posts/{id}   # Get specific post
```

**Rules:**

* Use **plural nouns** for resource names (`/users`, not `/user`)
* Use **HTTP methods** to indicate operations, not URL paths
* Keep URLs **hierarchical** but avoid deep nesting (max 2-3 levels)
* Use **kebab-case** for multi-word resources (`/user-profiles`)

### Idempotency Patterns

Implement idempotency for safe retries:

```python
from fastapi import FastAPI, Header, HTTPException
from typing import Optional

@app.post("/api/v1/users")
async def create_user(
    user_data: CreateUserRequest,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key")
):
    """Create user with idempotency support."""
    
    if idempotency_key:
        # Check if request was already processed
        existing = await user_service.get_by_idempotency_key(idempotency_key)
        if existing:
            return existing
    
    user = await user_service.create(user_data, idempotency_key)
    return user
```

**Rules:**

* Support **idempotency keys** for POST operations
* Make PUT and DELETE operations **naturally idempotent**
* Store idempotency results for reasonable time period (24h)
* Return same response for repeated idempotent requests

## 2. API Versioning Strategy

### URL-Based Versioning

Use URL path versioning for clear API evolution:

```python
# Version 1
@app.get("/api/v1/users/{user_id}")
async def get_user_v1(user_id: str) -> UserResponseV1:
    return await user_service.get_v1(user_id)

# Version 2 with enhanced fields
@app.get("/api/v2/users/{user_id}")
async def get_user_v2(user_id: str) -> UserResponseV2:
    return await user_service.get_v2(user_id)
```

### Deprecation Workflow

Implement graceful deprecation:

```python
from fastapi import FastAPI, Response
from datetime import datetime, timezone

@app.get("/api/v1/users/{user_id}")
async def get_user_deprecated(user_id: str, response: Response):
    """Get user (DEPRECATED - use v2)."""
    
    # Add deprecation headers
    response.headers["Deprecation"] = "true"
    response.headers["Sunset"] = "2024-12-31T23:59:59Z"
    response.headers["Link"] = '</api/v2/users>; rel="successor-version"'
    
    return await user_service.get_v1(user_id)
```

**Rules:**

* Use **URL versioning** (`/v1`, `/v2`) for major changes
* Maintain **backward compatibility** within same major version
* Provide **6+ months notice** before deprecating versions
* Use **HTTP headers** to communicate deprecation status
* Document migration guides for version upgrades

## 3. Pagination, Filtering, and Sorting

### Cursor-Based Pagination

Implement efficient cursor pagination for large datasets:

```python
from pydantic import BaseModel
from typing import Optional, List

class PaginationParams(BaseModel):
    cursor: Optional[str] = None
    limit: int = Field(default=20, ge=1, le=100)
    
class PaginatedResponse[T](BaseModel):
    data: List[T]
    next_cursor: Optional[str] = None
    has_more: bool
    total_count: Optional[int] = None  # Include only if efficient to compute

@app.get("/api/v1/users")
async def list_users(
    pagination: PaginationParams = Depends(),
    name: Optional[str] = Query(None, description="Filter by name"),
    status: Optional[UserStatus] = Query(None, description="Filter by status"),
    sort: str = Query("created_at", description="Sort field")
) -> PaginatedResponse[UserResponse]:
    """List users with pagination, filtering, and sorting."""
    
    filters = UserFilters(
        name=name,
        status=status,
        sort=sort
    )
    
    result = await user_service.list_paginated(
        cursor=pagination.cursor,
        limit=pagination.limit,
        filters=filters
    )
    
    return PaginatedResponse(
        data=result.users,
        next_cursor=result.next_cursor,
        has_more=result.has_more
    )
```

### Partial Response (Field Selection)

Support field selection for bandwidth optimization:

```python
@app.get("/api/v1/users/{user_id}")
async def get_user(
    user_id: str,
    fields: Optional[str] = Query(None, description="Comma-separated fields to include")
) -> UserResponse:
    """Get user with optional field selection."""
    
    requested_fields = None
    if fields:
        requested_fields = {f.strip() for f in fields.split(",")}
    
    user = await user_service.get(user_id, fields=requested_fields)
    return user
```

**Rules:**

* Use **cursor-based pagination** for scalability
* Support **filtering** with query parameters
* Allow **field selection** to reduce payload size
* Implement **consistent sorting** options
* Limit **maximum page size** to prevent abuse

## 4. Error Model (RFC7807 Problem Details)

### Standardized Error Responses

Use RFC7807 Problem Details for consistent error format:

```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from fastapi import HTTPException, status

class ProblemDetail(BaseModel):
    """RFC7807 Problem Details for HTTP APIs."""
    
    type: str = Field(..., description="A URI reference that identifies the problem type")
    title: str = Field(..., description="A short, human-readable summary")
    status: int = Field(..., description="HTTP status code")
    detail: Optional[str] = Field(None, description="Human-readable explanation")
    instance: Optional[str] = Field(None, description="URI reference to specific occurrence")
    correlation_id: Optional[str] = Field(None, description="Request correlation ID")
    errors: Optional[Dict[str, Any]] = Field(None, description="Validation errors")

class ValidationError(HTTPException):
    """Validation error with problem details."""
    
    def __init__(self, errors: Dict[str, Any], correlation_id: str):
        detail = ProblemDetail(
            type="/problems/validation-error",
            title="Validation Error",
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The request contains invalid data",
            correlation_id=correlation_id,
            errors=errors
        )
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail.model_dump()
        )

class ResourceNotFound(HTTPException):
    """Resource not found error."""
    
    def __init__(self, resource_type: str, resource_id: str, correlation_id: str):
        detail = ProblemDetail(
            type="/problems/resource-not-found",
            title="Resource Not Found",
            status=status.HTTP_404_NOT_FOUND,
            detail=f"{resource_type} with ID '{resource_id}' was not found",
            instance=f"/{resource_type.lower()}s/{resource_id}",
            correlation_id=correlation_id
        )
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail.model_dump()
        )
```

### Global Exception Handler

Implement consistent error handling:

```python
from fastapi import Request
from fastapi.responses import JSONResponse
import uuid
import logging

logger = logging.getLogger(__name__)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler with correlation ID."""
    
    correlation_id = str(uuid.uuid4())
    
    # Log the error
    logger.error(
        "Unhandled exception",
        extra={
            "correlation_id": correlation_id,
            "path": request.url.path,
            "method": request.method,
            "error": str(exc)
        },
        exc_info=True
    )
    
    # Return problem details
    problem = ProblemDetail(
        type="/problems/internal-server-error",
        title="Internal Server Error",
        status=500,
        detail="An unexpected error occurred",
        correlation_id=correlation_id
    )
    
    return JSONResponse(
        status_code=500,
        content=problem.model_dump()
    )
```

**Rules:**

* Use **RFC7807 Problem Details** for all error responses
* Include **correlation IDs** for request tracing
* Provide **actionable error messages** for client errors
* **Log errors** with sufficient context for debugging
* Never expose **sensitive information** in error responses

## 5. OpenAPI-First Development

### Single Source of Truth

We follow an **OpenAPI-first** approach where the OpenAPI specification is the authoritative source for API contracts, not the FastAPI code.

**Workflow:**

1. **Define API in OpenAPI spec** (YAML/JSON) with complete documentation
2. **Generate FastAPI code** from the spec using code generation tools
3. **Implement minimal FastAPI endpoints** focused on business logic

### Code Generation from OpenAPI

Use tools to generate FastAPI boilerplate from OpenAPI specs:

```bash
# Using fastapi-code-generator
pip install fastapi-code-generator
fastapi-codegen --input openapi.yaml --output ./generated

# Using openapi-generator  
openapi-generator generate -i openapi.yaml -g python-fastapi -o ./generated
```

### Minimal FastAPI Documentation

Keep FastAPI code focused on implementation, not API documentation:

```python
# ✅ Minimal, implementation-focused
@app.post("/api/v1/users")
async def create_user(user_data: CreateUserRequest) -> UserResponse:
    """Implementation of POST /users from OpenAPI spec."""
    return await user_service.create(user_data)

# ❌ Avoid duplicating OpenAPI spec details
@app.post(
    "/api/v1/users",
    summary="Create a new user",  # Already in OpenAPI spec
    description="Creates a new user account...",  # Already in OpenAPI spec
    responses={201: {"description": "User created"}},  # Already in OpenAPI spec
    tags=["Users"]  # Already in OpenAPI spec
)
async def create_user(user_data: CreateUserRequest) -> UserResponse:
    return await user_service.create(user_data)
```

### Serving OpenAPI Documentation

Configure FastAPI to serve the existing OpenAPI spec:

```python
import yaml
from fastapi import FastAPI
from pathlib import Path

def load_openapi_spec():
    """Load OpenAPI spec from file."""
    spec_path = Path("docs/openapi/api.yaml")
    with open(spec_path) as f:
        return yaml.safe_load(f)

app = FastAPI()

# Override FastAPI's generated OpenAPI with our spec
@app.get("/openapi.json", include_in_schema=False)
async def get_openapi():
    """Serve the authoritative OpenAPI spec."""
    return load_openapi_spec()

# Alternative: Set openapi_url to external spec
app = FastAPI(
    openapi_url="/docs/openapi/api.yaml",  # Point to existing spec
    docs_url="/docs",
    redoc_url="/redoc"
)
```

### Contract Testing

Generate tests from OpenAPI examples to ensure implementation matches spec:

```python
import pytest
from openapi_spec_validator import validate_spec
from your_app import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_api_matches_openapi_spec():
    """Verify FastAPI implementation matches OpenAPI spec."""
    
    # Get OpenAPI spec from FastAPI
    response = client.get("/openapi.json")
    generated_spec = response.json()
    
    # Load authoritative spec
    with open("docs/openapi/api.yaml") as f:
        authoritative_spec = yaml.safe_load(f)
    
    # Validate specs match critical elements
    assert generated_spec["paths"] == authoritative_spec["paths"]
    assert generated_spec["components"] == authoritative_spec["components"]

def test_openapi_examples():
    """Test API endpoints using examples from OpenAPI spec."""
    
    spec = load_openapi_spec()
    
    for path, methods in spec["paths"].items():
        for method, details in methods.items():
            if "requestBody" in details:
                example = details["requestBody"]["content"]["application/json"]["example"]
                response = getattr(client, method.lower())(path, json=example)
                
                # Verify response matches OpenAPI spec
                expected_status = list(details["responses"].keys())[0]
                assert response.status_code == int(expected_status)
```

**Rules:**

* **OpenAPI spec** is the single source of truth for API contracts
* **FastAPI code** focuses on implementation, not documentation  
* Use **code generation** to maintain consistency between spec and code
* Implement **contract tests** to verify spec compliance
* Keep **minimal documentation** in FastAPI for implementation details only
* **Never duplicate** what's already defined in the OpenAPI spec

By following these API design principles, we ensure **consistency**, **discoverability**, and **maintainability** across all backend services while providing excellent developer experience for API consumers.