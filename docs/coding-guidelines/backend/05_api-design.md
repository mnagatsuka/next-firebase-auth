# 5. API Design & Best Practices

Simple REST API design patterns for Python + FastAPI applications.

## Overview

- Design consistent, resource-oriented REST APIs
- Keep versioning simple when needed
- Provide clear error responses
- Use FastAPI's built-in documentation features

## 1. API Models: BaseModel vs Dataclass

### When to Use Pydantic BaseModel

**Use Pydantic `BaseModel` for API layer models:**

- **API Request/Response Models**: Generated from OpenAPI or manual API contracts
- **Data Validation**: Input validation and serialization at API boundaries
- **HTTP-Specific Concerns**: Status codes, headers, API responses
- **Generated Models**: OpenAPI Generator creates BaseModel classes

```python
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class ApiResponseStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"

class CreatePostRequest(BaseModel):
    """API request model for creating posts."""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    excerpt: str = Field(..., max_length=500)

class BlogPostResponse(BaseModel):
    """API response model for blog posts."""
    status: ApiResponseStatus
    data: Optional["ApiBlogPost"] = None
    error: Optional[str] = None
```

### When to Use Dataclass

**Use `@dataclass` for domain entities:**

- **Domain Layer**: Business entities with pure business logic
- **No Serialization**: Focus on business rules, not API concerns
- **Framework Independence**: Domain should not depend on web frameworks

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class PostStatus(Enum):
    DRAFT = "draft"
    PUBLISHED = "published"

@dataclass
class BlogPost:
    """Domain entity - pure business logic."""
    id: str
    title: str
    content: str
    # Business methods, no serialization concerns
```

### Layer Separation

```
API Layer (BaseModel)     ←→ Application Layer ←→ Domain Layer (dataclass)
   ↓ HTTP/JSON                    ↓ Orchestration        ↓ Business Logic
CreatePostRequest                 PostService            BlogPost
BlogPostResponse                  Validation             Business Rules
```

## 2. Basic REST API Design

### HTTP Methods & Resource Patterns

Follow REST conventions:

```python
# Users resource
GET    /users              # List users
POST   /users              # Create user
GET    /users/{user_id}    # Get user
PATCH  /users/{user_id}    # Update user
DELETE /users/{user_id}    # Delete user
```

**Simple Rules:**

* Use **plural nouns** for resource names (`/users`, not `/user`)
* Use **HTTP methods** to indicate operations
* Keep URLs simple and avoid deep nesting
* Use **snake_case** for multi-word resources (`/user_profiles`)

### FastAPI Route Examples

Simple FastAPI endpoint examples:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from app.models.user import User, UserCreate, UserUpdate
from app.services.user_service import UserService

app = FastAPI()
user_service = UserService()

@app.get("/users")
async def list_users():
    """List all users."""
    return await user_service.list_users()

@app.post("/users", response_model=User)
async def create_user(user_data: UserCreate):
    """Create a new user."""
    return await user_service.create_user(user_data)

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    """Get user by ID."""
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

## 2. Simple Versioning (When Needed)

For small applications, avoid versioning until actually needed. When you do need it:

```python
# Simple URL-based versioning
@app.get("/v1/users/{user_id}")
async def get_user_v1(user_id: str):
    return await user_service.get_user(user_id)

# Or use API prefix if preferred
@app.get("/api/v1/users/{user_id}")
async def get_user_v1_prefixed(user_id: str):
    return await user_service.get_user(user_id)
```

**Simple Rules:**

* Start without versioning for small applications
* Add URL versioning (`/v1`) only when you need breaking changes
* Keep old versions running temporarily during transitions

## 3. Basic Pagination and Filtering

Keep pagination simple for small to medium applications:

```python
from fastapi import Query
from typing import Optional

@app.get("/users")
async def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None)
):
    """List users with simple pagination and search."""
    
    users = await user_service.list_users(
        page=page,
        limit=limit,
        search=search
    )
    
    return {
        "users": users.items,
        "page": page,
        "total": users.total,
        "has_more": users.has_more
    }
```

**Simple Rules:**

* Use **offset-based pagination** (page/limit) for simplicity
* Add basic **search/filtering** with query parameters
* Keep pagination responses consistent

## 4. Simple Error Handling

### Basic Error Responses

Keep error responses simple and consistent:

```python
from fastapi import HTTPException

# Simple error responses
@app.get("/users/{user_id}")
async def get_user(user_id: str):
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=404, 
            detail="User not found"
        )
    return user

# For validation errors, FastAPI handles this automatically
from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')

@app.post("/users")
async def create_user(user_data: UserCreate):
    # FastAPI automatically validates and returns 422 for invalid data
    return await user_service.create_user(user_data)
```
```

### Global Exception Handler

Handle unexpected errors gracefully:

```python
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    
    # Log the error
    logger.error(
        f"Unhandled exception: {exc}",
        extra={
            "path": request.url.path,
            "method": request.method,
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

**Simple Rules:**

* Use FastAPI's built-in validation for request data
* Raise `HTTPException` for expected errors (404, 400, etc.)
* Log unexpected errors but don't expose details to clients
* Keep error responses simple and consistent

## 5. Documentation with FastAPI

### Built-in Documentation

FastAPI automatically generates API documentation - use it effectively:

```python
from fastapi import FastAPI
from app.models.user import User, UserCreate

app = FastAPI(
    title="My API",
    description="A simple API for managing users",
    version="1.0.0"
)

@app.post("/users", response_model=User, tags=["Users"])
async def create_user(user_data: UserCreate):
    """
    Create a new user.
    
    - **name**: User's full name
    - **email**: Valid email address
    """
    return await user_service.create_user(user_data)
```

### Good Documentation Practices

```python
# ✅ Good: Clear descriptions and examples
class UserCreate(BaseModel):
    """User creation data."""
    
    name: str = Field(..., description="User's full name", example="John Doe")
    email: str = Field(..., description="Valid email address", example="john@example.com")

# ✅ Good: Helpful endpoint documentation
@app.get("/users", summary="List all users", tags=["Users"])
async def list_users():
    """
    Get a list of all users in the system.
    
    Returns a list of user objects with basic information.
    """
    return await user_service.list_users()
```

**Simple Rules:**

* Use FastAPI's built-in documentation features (`/docs` and `/redoc`)
* Add clear descriptions to your Pydantic models and endpoints
* Group related endpoints with `tags`
* Keep documentation simple and helpful for API users

This approach leverages FastAPI's strengths while keeping the development process simple and focused on building features rather than maintaining complex documentation workflows.