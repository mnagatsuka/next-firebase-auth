# 7. Domain Layer (Business Logic)

## Overview

Simple domain layer patterns for small to medium applications. Focus on basic business logic without complex domain-driven design patterns.

## Key Principles

- Keep business logic separate from infrastructure concerns
- Use simple data classes for entities (NOT Pydantic BaseModel)
- Implement basic validation in domain objects
- Domain layer should be framework-agnostic and dependency-free

## Directory Structure

```
domain/
├── entities.py        # Domain entities
├── services.py        # Business logic services  
└── exceptions.py      # Domain exceptions
```

## 1. Entities

### Why Dataclass Over BaseModel?

**Use `@dataclass` for domain entities because:**

- **Pure Business Logic**: Domain entities focus on business rules, not serialization
- **No External Dependencies**: Domain layer should be framework-agnostic (no Pydantic dependency)
- **Performance**: Lighter weight than BaseModel for pure business objects
- **Clean Architecture**: Domain layer should not depend on web framework concerns
- **Immutability Support**: Works well with `frozen=True` for immutable entities

**Use Pydantic BaseModel for:**
- API request/response models (generated from OpenAPI)
- Data validation at application boundaries
- Serialization/deserialization concerns

### Entity Implementation

Simple data classes for domain entities:

```python
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
import uuid

class PostStatus(Enum):
    """Blog post status enumeration."""
    DRAFT = "draft"
    PUBLISHED = "published"

@dataclass
class BlogPost:
    """Blog post domain entity with business logic."""
    
    id: str
    title: str
    content: str
    excerpt: str
    author: str
    published_at: Optional[datetime] = None
    status: PostStatus = PostStatus.DRAFT
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Basic validation and data cleaning."""
        if not self.title.strip():
            raise ValueError("Title cannot be empty")
        if not self.content.strip():
            raise ValueError("Content cannot be empty")
        if not self.excerpt.strip():
            raise ValueError("Excerpt cannot be empty")
        if not self.author.strip():
            raise ValueError("Author cannot be empty")
        
        # Clean up data
        self.title = self.title.strip()
        self.content = self.content.strip()
        self.excerpt = self.excerpt.strip()
        self.author = self.author.strip()
        
        # Set timestamps if not provided
        now = datetime.now(timezone.utc)
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now
    
    def publish(self) -> None:
        """Publish the blog post."""
        if self.status == PostStatus.PUBLISHED:
            raise ValueError("Post is already published")
        
        self.status = PostStatus.PUBLISHED
        self.published_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def unpublish(self) -> None:
        """Unpublish the blog post (set to draft)."""
        if self.status == PostStatus.DRAFT:
            raise ValueError("Post is already a draft")
        
        self.status = PostStatus.DRAFT
        self.published_at = None
        self.updated_at = datetime.now(timezone.utc)
    
    def update_content(self, title: str = None, content: str = None, excerpt: str = None) -> None:
        """Update post content fields."""
        if title is not None:
            if not title.strip():
                raise ValueError("Title cannot be empty")
            self.title = title.strip()
        
        if content is not None:
            if not content.strip():
                raise ValueError("Content cannot be empty")
            self.content = content.strip()
        
        if excerpt is not None:
            if not excerpt.strip():
                raise ValueError("Excerpt cannot be empty")
            self.excerpt = excerpt.strip()
        
        self.updated_at = datetime.now(timezone.utc)
    
    def is_published(self) -> bool:
        """Check if the post is published."""
        return self.status == PostStatus.PUBLISHED
    
    def can_be_updated_by(self, user_id: str) -> bool:
        """Check if the post can be updated by the given user."""
        return self.author == user_id
    
    @classmethod
    def create_new(cls, title: str, content: str, excerpt: str, author: str) -> 'BlogPost':
        """Factory method to create a new blog post."""
        post_id = str(uuid.uuid4())
        return cls(
            id=post_id,
            title=title,
            content=content,
            excerpt=excerpt,
            author=author,
            status=PostStatus.DRAFT
        )
```

## 2. Business Services

Simple services for business logic that doesn't belong in entities:

```python
from typing import Optional
from .entities import User
from .exceptions import DuplicateEmailError

class UserService:
    """Business logic for user operations."""
    
    def __init__(self, user_repository):
        self._user_repository = user_repository
    
    async def create_user(self, name: str, email: str) -> User:
        """Create a new user with business validation."""
        # Check for duplicate email
        existing_user = await self._user_repository.find_by_email(email)
        if existing_user:
            raise DuplicateEmailError(f"User with email {email} already exists")
        
        # Create new user
        user = User(
            id=self._generate_id(),
            name=name,
            email=email,
            created_at=datetime.utcnow()
        )
        
        return await self._user_repository.save(user)
    
    def _generate_id(self) -> str:
        """Generate unique user ID."""
        import uuid
        return str(uuid.uuid4())
```

## 3. Domain Exceptions

Simple domain-specific exceptions:

```python
class DomainError(Exception):
    """Base domain exception."""
    pass

class DuplicateEmailError(DomainError):
    """Raised when email already exists."""
    pass

class UserNotFoundError(DomainError):
    """Raised when user cannot be found."""
    pass

class InvalidUserStateError(DomainError):
    """Raised when user is in invalid state."""
    pass
```

## Best Practices

### Domain Entity Guidelines

* **Use `@dataclass`** for domain entities (NOT Pydantic BaseModel)
* **Keep domain logic pure** - no external framework dependencies
* **Implement business validation** in `__post_init__` method
* **Add business methods** for entity operations (publish, update, etc.)
* **Use factory methods** for complex entity creation
* **Include authorization logic** (can_be_updated_by, can_be_deleted_by)

### Service Guidelines  

* **Keep services focused** on specific business operations
* **Use dependency injection** for repositories and external services
* **Handle domain validation** through domain services
* **Return domain data** as dictionaries for application layer
* **Throw domain exceptions** for business rule violations

### Clean Architecture Rules

* **Domain layer** should not import from application or infrastructure layers
* **Use simple ValueError** for validation errors (domain-specific)
* **Keep entities focused** on single responsibility
* **Separate concerns** between entities, services, and repositories

