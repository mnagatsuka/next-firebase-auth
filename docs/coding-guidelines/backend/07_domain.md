# 7. Domain Layer (Business Logic)

## Overview

Simple domain layer patterns for small to medium applications. Focus on basic business logic without complex domain-driven design patterns.

## Key Principles

- Keep business logic separate from infrastructure concerns
- Use simple data classes for entities
- Implement basic validation in domain objects

## Directory Structure

```
domain/
├── entities.py        # Domain entities
├── services.py        # Business logic services  
└── exceptions.py      # Domain exceptions
```

## 1. Entities

Simple data classes for domain entities:

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    """User entity with basic business logic."""
    
    id: str
    email: str
    name: str
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Basic validation."""
        if not self.name.strip():
            raise ValueError("Name cannot be empty")
        if not self.email:
            raise ValueError("Email is required")
        
        # Clean up data
        self.name = self.name.strip()
        self.email = self.email.lower()
    
    def deactivate(self) -> None:
        """Business method to deactivate user."""
        self.is_active = False
        self.updated_at = datetime.utcnow()
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

**Rules:**

* Keep domain logic simple and focused on core business rules
* Use basic data classes for entities
* Implement validation in entity constructors
* Create simple service classes for complex business operations
* Use descriptive domain exceptions

