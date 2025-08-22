# Schema-Driven Backend Development

This document explains how the backend leverages OpenAPI specifications for type-safe development, automated code generation, and clean architecture implementation using FastAPI and Pydantic models.

## 🎯 Overview

Our backend follows a **schema-first** approach where all Pydantic models, API routes, and data validation are derived from the centralized OpenAPI specification in `openapi/spec/`. This ensures complete type safety and API contract compliance throughout the backend stack.

### Key Benefits

- ✅ **Type-Safe API Contracts**: Pydantic models generated from OpenAPI schemas
- ✅ **Clean Architecture**: Domain-driven design with proper layer separation
- ✅ **Automated Model Generation**: Zero manual model definitions
- ✅ **Contract Compliance**: Backend automatically matches API specification
- ✅ **Comprehensive Testing**: Test pyramid with unit, integration, and API tests

## 📁 Backend Architecture

```
backend/src/app/
├── generated/                        # 🚫 Auto-generated (don't edit)
│   └── src/generated_fastapi_server/
│       ├── models/                   # Pydantic models from OpenAPI
│       │   ├── blog_post.py          # BlogPost model
│       │   ├── create_post_request.py # CreatePostRequest model
│       │   ├── blog_post_response.py  # Response wrappers
│       │   └── ...                   # Other generated models
│       ├── apis/                     # Base API classes (not used directly)
│       └── security_api.py           # Authentication helpers
│
├── api/                              # API Layer (Controllers)
│   ├── routes/
│   │   └── posts.py                  # FastAPI route handlers
│   ├── router.py                     # Main API router
│   └── posts_implementation.py       # API implementation bridge
│
├── application/                      # Application Layer
│   ├── services/
│   │   └── posts_service.py          # Application services
│   ├── use_cases/                    # Use case implementations
│   └── exceptions.py                 # Application exceptions
│
├── domain/                           # Domain Layer
│   ├── entities.py                   # Domain entities (BlogPost)
│   ├── services.py                   # Domain services
│   └── exceptions.py                 # Domain exceptions
│
├── infra/                           # Infrastructure Layer
│   └── repositories/
│       └── posts_repository.py       # Repository implementations
│
├── shared/                          # Shared utilities
│   └── config.py                    # Application settings
│
└── main.py                          # FastAPI application factory
```

## 🔄 Development Workflow

### 1. Schema-to-Code Generation

When OpenAPI schemas change, regenerate backend models:

```bash
# From project root
pnpm oas:be
```

This runs:
1. `pnpm oas:bundle` - Bundles OpenAPI spec
2. `openapi-generator-cli generate` - Generates Pydantic models

### 2. Generated Pydantic Models

**OpenAPI Schema** (`openapi/spec/components/schemas/blog-post.yml`):
```yaml
type: object
properties:
  id:
    type: string
    description: Unique identifier for the blog post
    example: "post-123"
  title:
    type: string
    description: Title of the blog post
    example: "Getting Started with Next.js"
  status:
    type: string
    enum: [draft, published]
    description: Current status of the blog post
    example: "published"
required: [id, title, status]
```

**Generated Pydantic Model** (`backend/src/app/generated/src/generated_fastapi_server/models/blog_post.py`):
```python
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class BlogPostStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"

class BlogPost(BaseModel):
    """Blog post model generated from OpenAPI specification."""
    
    id: str = Field(description="Unique identifier for the blog post")
    title: str = Field(description="Title of the blog post")
    content: str = Field(description="Full content of the blog post in markdown format")
    excerpt: str = Field(description="Short summary or excerpt of the blog post")
    author: str = Field(description="Author of the blog post")
    published_at: str = Field(description="Timestamp when the blog post was published")
    status: BlogPostStatus = Field(description="Current status of the blog post")
```

### 3. Route Implementation

Use generated models in FastAPI routes with clean architecture:

**Example**: `backend/src/app/api/routes/posts.py`
```python
"""Posts API routes using generated models."""

from fastapi import APIRouter, Body, HTTPException
from pydantic import Field
from typing_extensions import Annotated

# Import generated models
import sys
from pathlib import Path
generated_path = Path(__file__).parent.parent.parent / "generated" / "src"
sys.path.insert(0, str(generated_path))

from generated_fastapi_server.models.blog_post_response import BlogPostResponse
from generated_fastapi_server.models.create_post_request import CreatePostRequest
from generated_fastapi_server.models.blog_post_list_response import BlogPostListResponse

from app.api.posts_implementation import PostsImplementation

posts_router = APIRouter(prefix="/posts", tags=["posts"])

def get_posts_impl():
    """Get PostsImplementation instance - called at request time for proper mocking."""
    return PostsImplementation()

@posts_router.post("", status_code=201)
async def create_blog_post(
    create_post_request: Annotated[CreatePostRequest, Field(description="Blog post data")] = Body(None),
) -> BlogPostResponse:
    """Create a new blog post."""
    posts_impl = get_posts_impl()
    return await posts_impl.create_blog_post(create_post_request)

@posts_router.get("")
async def get_blog_posts(
    page: int = 1,
    limit: int = 10
) -> BlogPostListResponse:
    """Get list of blog posts with pagination."""
    posts_impl = get_posts_impl()
    return await posts_impl.get_blog_posts(page=page, limit=limit)
```

### 4. Clean Architecture Implementation

Bridge generated models with domain logic:

**Example**: `backend/src/app/api/posts_implementation.py`
```python
"""Implementation of Posts API using clean architecture."""

from app.application.services.posts_service import PostApplicationService
from app.infra.repositories.posts_repository import InMemoryPostRepository
from app.domain.exceptions import PostNotFoundError, PostValidationError

# Generated models
from generated_fastapi_server.models.blog_post_response import BlogPostResponse
from generated_fastapi_server.models.create_post_request import CreatePostRequest
from generated_fastapi_server.models.api_response_status import ApiResponseStatus

class PostsImplementation:
    """Implementation of the Posts API using layered architecture."""
    
    def __init__(self):
        # Infrastructure layer
        self.post_repository = InMemoryPostRepository()
        # Application layer
        self.post_service = PostApplicationService(self.post_repository)
    
    async def create_blog_post(self, create_post_request: CreatePostRequest) -> BlogPostResponse:
        """Create a new blog post using clean architecture layers."""
        try:
            # Call application service (use case)
            post_data = await self.post_service.create_post(
                title=create_post_request.title,
                content=create_post_request.content,
                excerpt=create_post_request.excerpt,
                author="system"
            )
            
            # Convert domain data to generated API models
            api_post = self._convert_to_api_model(post_data)
            return BlogPostResponse(
                status=ApiResponseStatus.SUCCESS, 
                data=api_post
            )
            
        except PostNotFoundError:
            raise HTTPException(status_code=404, detail="Post not found")
        except PostValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    def _convert_to_api_model(self, post_data: dict):
        """Convert domain data to generated API model."""
        from generated_fastapi_server.models.blog_post import BlogPost
        return BlogPost(**post_data)
```

### 5. Domain Layer

Implement business logic separate from API concerns:

**Example**: `backend/src/app/domain/entities.py`
```python
"""Domain entities with business rules."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from app.domain.exceptions import PostValidationError

class PostStatus(Enum):
    DRAFT = "draft"
    PUBLISHED = "published"

@dataclass
class BlogPost:
    """Blog post domain entity with business rules."""
    id: str
    title: str
    content: str
    excerpt: str
    author: str
    status: PostStatus = PostStatus.DRAFT
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    published_at: Optional[datetime] = None
    
    def publish(self) -> None:
        """Publish the blog post with business rules validation."""
        if self.status == PostStatus.PUBLISHED:
            raise PostValidationError("Post is already published")
        
        self.status = PostStatus.PUBLISHED
        self.published_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def update_content(self, title: str, content: str, excerpt: str) -> None:
        """Update post content with validation."""
        if not title.strip():
            raise PostValidationError("Title cannot be empty")
        if not content.strip():
            raise PostValidationError("Content cannot be empty")
        
        self.title = title.strip()
        self.content = content.strip()
        self.excerpt = excerpt.strip()
        self.updated_at = datetime.now(timezone.utc)
```

### 6. Application Services

Orchestrate domain logic and coordinate with infrastructure:

**Example**: `backend/src/app/application/services/posts_service.py`
```python
"""Application service for post-related use cases."""

from typing import Dict, Any
from datetime import datetime, timezone

from app.domain.entities import BlogPost, PostStatus
from app.domain.services import PostService
from app.infra.repositories.posts_repository import PostRepository

class PostApplicationService:
    """Application service for post-related use cases."""
    
    def __init__(self, post_repository: PostRepository):
        self.post_repository = post_repository
        self.post_service = PostService()  # Domain service
    
    async def create_post(
        self, title: str, content: str, excerpt: str, author: str
    ) -> Dict[str, Any]:
        """Create a new blog post use case."""
        # Domain validation through domain service
        validated_data = self.post_service.validate_post_data(
            title, content, excerpt
        )
        
        # Create domain entity
        post = BlogPost(
            id=self._generate_id(),
            title=validated_data["title"],
            content=validated_data["content"],
            excerpt=validated_data["excerpt"],
            author=author
        )
        
        # Persist through repository
        await self.post_repository.save(post)
        
        # Return domain data compatible with generated models
        return {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "excerpt": post.excerpt,
            "author": post.author,
            "status": post.status.value,
            "publishedAt": post.published_at.isoformat() if post.published_at else None,
            "createdAt": post.created_at.isoformat(),
            "updatedAt": post.updated_at.isoformat()
        }
    
    def _generate_id(self) -> str:
        """Generate unique post ID."""
        import uuid
        return f"post-{uuid.uuid4().hex[:8]}"
```

## 🧪 Comprehensive Testing Strategy

### Test Structure Overview

Following the Test Pyramid principle with three distinct layers:

```
tests/backend/
├── unit/                           # Fast, isolated unit tests (70%)
│   ├── domain/                    # Domain entity and service tests
│   │   ├── test_blog_post.py      # BlogPost entity tests
│   │   └── test_post_service.py   # PostService domain logic tests
│   └── application/               # Application service tests
│       └── test_posts_service.py  # PostApplicationService tests
├── integration/                   # Integration tests with real adapters (20%)
│   ├── infra/                     # Repository and infrastructure tests
│   │   └── test_posts_repository.py
│   └── api/                       # API endpoint tests
│       └── test_posts_endpoints.py  # FastAPI route tests
├── factories/                     # Test data factories
│   └── post_factory.py           # BlogPost test data factory
├── conftest.py                   # Pytest configuration and fixtures
└── requirements-test.txt         # Test dependencies
```

### Unit Tests - Domain Layer

Test business logic without external dependencies:

```python
# tests/backend/unit/domain/test_blog_post.py
import pytest
from freezegun import freeze_time
from datetime import datetime, timezone

from app.domain.entities import BlogPost, PostStatus
from app.domain.exceptions import PostValidationError

class TestBlogPost:
    """Test suite for BlogPost entity business rules."""
    
    def test_create_blog_post_with_valid_data_returns_post(self):
        """Test creating a blog post with valid data."""
        post = BlogPost(
            id="post-123",
            title="Test Post",
            content="This is test content.",
            excerpt="Test excerpt",
            author="test-author"
        )
        
        assert post.id == "post-123"
        assert post.title == "Test Post"
        assert post.status == PostStatus.DRAFT
        assert post.published_at is None
    
    @freeze_time("2024-01-01 12:00:00")
    def test_publish_post_sets_published_timestamp(self):
        """Test that publishing a post sets the published timestamp."""
        post = BlogPost(
            id="post-123", title="Test", content="Content", 
            excerpt="Excerpt", author="author"
        )
        
        post.publish()
        
        assert post.status == PostStatus.PUBLISHED
        assert post.published_at == datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    
    def test_publish_already_published_post_raises_error(self):
        """Test that publishing an already published post raises an error."""
        post = BlogPost(
            id="post-123", title="Test", content="Content",
            excerpt="Excerpt", author="author", status=PostStatus.PUBLISHED
        )
        
        with pytest.raises(PostValidationError, match="Post is already published"):
            post.publish()
```

### Integration Tests - API Layer

Test API endpoints with generated models:

```python
# tests/backend/integration/api/test_posts_endpoints.py
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from app.main import app
from tests.backend.factories.post_factory import PostFactory

class TestPostsEndpoints:
    """Integration tests for Posts API endpoints using generated models."""
    
    def setup_method(self):
        """Set up test client and mock dependencies."""
        self.client = TestClient(app)
        
        # Mock the repository to avoid dependencies
        self.mock_repo_patcher = patch('app.api.posts_implementation.InMemoryPostRepository')
        self.mock_repo_class = self.mock_repo_patcher.start()
        self.mock_repo = Mock()
        self.mock_repo_class.return_value = self.mock_repo
        
        # Setup mock repository methods
        self.mock_repo.save.return_value = self._async_return(None)
        self.mock_repo.find_by_id.return_value = self._async_return(None)
        self.mock_repo.find_published.return_value = self._async_return([])
    
    def teardown_method(self):
        """Clean up mocks."""
        self.mock_repo_patcher.stop()
    
    def _async_return(self, value):
        """Helper to create async return value."""
        import asyncio
        future = asyncio.Future()
        future.set_result(value)
        return future
    
    def test_create_post_with_valid_data_returns_201(self):
        """Test creating a post with valid data returns 201 and correct response structure."""
        # Arrange
        post_data = {
            "title": "Test Blog Post",
            "content": "This is a test blog post content.",
            "excerpt": "Test excerpt"
        }
        created_post = PostFactory.create()
        self.mock_repo.save.return_value = self._async_return(created_post)
        
        # Act
        response = self.client.post("/posts", json=post_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["title"] == "Test Blog Post"
        assert data["data"]["status"] == "draft"
        
        # Verify repository was called
        self.mock_repo.save.assert_called_once()
    
    def test_get_posts_returns_list_with_pagination(self):
        """Test getting posts returns properly structured list response."""
        # Arrange
        mock_posts = [PostFactory.create(), PostFactory.create()]
        self.mock_repo.find_published.return_value = self._async_return(mock_posts)
        
        # Act
        response = self.client.get("/posts?page=1&limit=10")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "posts" in data["data"]
        assert "pagination" in data["data"]
        assert data["data"]["pagination"]["page"] == 1
        assert data["data"]["pagination"]["limit"] == 10
```

### Test Data Factories

Provide consistent test data that matches generated models:

```python
# tests/backend/factories/post_factory.py
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from app.domain.entities import BlogPost, PostStatus

@dataclass
class PostFactory:
    """Factory for creating test blog post instances that match generated models."""
    
    @staticmethod
    def create(
        id: str = "post-123",
        title: str = "Test Blog Post",
        content: str = "This is a test blog post content.",
        excerpt: str = "This is a test excerpt.",
        author: str = "test-author",
        status: PostStatus = PostStatus.DRAFT,
        published_at: Optional[datetime] = None
    ) -> BlogPost:
        """Create a blog post with default or provided values."""
        return BlogPost(
            id=id, title=title, content=content, excerpt=excerpt,
            author=author, status=status, published_at=published_at
        )
    
    @staticmethod
    def create_published() -> BlogPost:
        """Create a published blog post with proper timestamp."""
        now = datetime.now(timezone.utc)
        return PostFactory.create(status=PostStatus.PUBLISHED, published_at=now)
    
    @staticmethod
    def create_api_compatible_dict(post: BlogPost) -> dict:
        """Convert domain entity to dict compatible with generated API models."""
        return {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "excerpt": post.excerpt,
            "author": post.author,
            "status": post.status.value,
            "publishedAt": post.published_at.isoformat() if post.published_at else None,
            "createdAt": post.created_at.isoformat(),
            "updatedAt": post.updated_at.isoformat()
        }
```

## ⚙️ Configuration

### OpenAPI Generator Configuration

**File**: `openapi-generator.config.json` (project root)
```json
{
  "generatorName": "python-fastapi",
  "inputSpec": "openapi/dist/openapi.yml",
  "outputDir": "backend/src/app/generated/",
  "globalProperty": {
    "apis": "true",
    "models": "true",
    "supportingFiles": "true",
    "apiTests": "true",
    "modelTests": "true"
  },
  "additionalProperties": {
    "packageName": "generated_fastapi_server",
    "projectName": "generated-fastapi-server"
  }
}
```

### FastAPI Application Setup

**File**: `backend/src/app/main.py`
```python
"""FastAPI application factory with generated model integration."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.shared.config import get_settings

def create_app() -> FastAPI:
    """Create FastAPI application with proper configuration."""
    settings = get_settings()

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url="/openapi.json",  # Matches generated models
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API router without versioning
    app.include_router(api_router)
    return app

app = create_app()
```

## 📋 Best Practices

### 1. Generated Model Usage

```python
# ✅ Good: Import and use generated models
from generated_fastapi_server.models.blog_post import BlogPost
from generated_fastapi_server.models.create_post_request import CreatePostRequest

async def create_post(request: CreatePostRequest) -> BlogPostResponse:
    # Use generated models for type safety
    pass

# ❌ Bad: Manual model definitions that duplicate OpenAPI
class ManualBlogPost(BaseModel):
    id: str
    title: str
    # This duplicates the OpenAPI schema
```

### 2. Clean Architecture Patterns

```python
# ✅ Good: Separate concerns with proper layering
class PostsImplementation:
    def __init__(self):
        self.repository = InMemoryPostRepository()  # Infrastructure
        self.service = PostApplicationService(self.repository)  # Application
    
    async def create_blog_post(self, request: CreatePostRequest):
        # Bridge API layer to application layer
        return await self.service.create_post(...)

# ❌ Bad: Mixing business logic with API concerns
async def create_blog_post_direct(request: CreatePostRequest):
    # Database logic mixed with API logic
    post = BlogPost(...)
    db.save(post)  # No domain validation or business rules
```

### 3. Testing Patterns

```python
# ✅ Good: Test with proper mocking and isolation
@patch('app.api.posts_implementation.InMemoryPostRepository')
def test_create_post_calls_repository(mock_repo_class):
    mock_repo = Mock()
    mock_repo_class.return_value = mock_repo
    # Test specific behavior

# ✅ Good: Use factories for consistent test data
post = PostFactory.create(title="Test Post")
api_data = PostFactory.create_api_compatible_dict(post)
```

## 🚀 Development Commands

### Daily Workflow

```bash
# 1. When OpenAPI schemas change, regenerate backend models
pnpm oas:be

# 2. Start development server
cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 3. Run tests
uv run pytest tests/backend/

# 4. Type check (if using mypy)
uv run mypy backend/src/
```

### Validation

```bash
# Ensure generated models work correctly
cd backend && uv run pytest tests/backend/integration/

# Run specific test categories
uv run pytest tests/backend/unit/          # Unit tests only
uv run pytest tests/backend/integration/   # Integration tests only

# Run with coverage
uv run pytest tests/backend/ --cov=backend --cov-report=html
```

## 🔍 Troubleshooting

### Common Issues

1. **Models Not Updating After Schema Changes**
   ```bash
   # Solution: Regenerate models
   pnpm oas:be
   cd backend && uv run pytest tests/backend/
   ```

2. **Import Errors with Generated Models**
   - Check: Generated models are in `backend/src/app/generated/src/`
   - Verify: Path manipulation in route files is correct
   - Update: Ensure `sys.path.insert()` points to correct directory

3. **Test Failures After Model Changes**
   - Update: Test factories to match new model fields
   - Verify: Mock data structure matches generated models
   - Check: Domain entities are compatible with API models

4. **DateTime Field Issues**
   ```python
   # Handle None values for draft posts
   published_at = post_data["publishedAt"]
   if published_at is None:
       published_at = datetime.fromtimestamp(0).isoformat()
   ```

## 📚 Related Files

- **OpenAPI Specification**: `openapi/spec/openapi.yml`
- **Generated Models**: `backend/src/app/generated/src/generated_fastapi_server/models/`
- **API Routes**: `backend/src/app/api/routes/`
- **Domain Entities**: `backend/src/app/domain/entities.py`
- **Application Services**: `backend/src/app/application/services/`
- **Frontend Schema Document**: [Schema-Driven Frontend Development](../frontend/schema-driven-frontend-development.md)

## ✅ Success Checklist

A properly implemented schema-driven backend should have:

- [ ] **Zero manual model definitions** that duplicate OpenAPI schemas
- [ ] **Type-safe API endpoints** using generated Pydantic models
- [ ] **Clean architecture separation** between domain, application, and API layers
- [ ] **Comprehensive test coverage** following the test pyramid pattern
- [ ] **Consistent error handling** using generated error response models
- [ ] **Proper dependency injection** for testability and mocking
- [ ] **Domain validation** separate from API validation
- [ ] **Up-to-date generated code** that matches current OpenAPI specification

This approach ensures robust, maintainable backend code with excellent type safety and clear separation of concerns while maintaining full compliance with the API contract defined in the OpenAPI specification.