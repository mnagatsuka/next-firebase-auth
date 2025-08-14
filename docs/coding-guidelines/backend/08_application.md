# 8. Application Layer (Use Cases)

## Overview

Simple application layer that coordinates business logic and infrastructure. Contains application services that implement use cases and handle basic cross-cutting concerns.

## Key Principles

- Coordinate between domain logic and infrastructure
- Keep application services simple and focused
- Handle basic validation and error handling

## Directory Structure

```
application/
├── services/           # Application services
│   ├── user_service.py
│   └── auth_service.py
└── exceptions.py       # Application exceptions
```

## 1. Application Services

Simple services that coordinate domain logic and infrastructure:

```python
from typing import Optional
from domain.services import UserService
from domain.exceptions import DuplicateEmailError
from .exceptions import ApplicationError

class UserApplicationService:
    """Application service for user operations."""
    
    def __init__(self, user_repository):
        self.user_service = UserService(user_repository)
        self.user_repository = user_repository
    
    async def create_user(self, name: str, email: str) -> dict:
        """Create a new user."""
        try:
            user = await self.user_service.create_user(name, email)
            return self._user_to_dict(user)
        except DuplicateEmailError as e:
            raise ApplicationError(f"User creation failed: {str(e)}")
    
    async def get_user(self, user_id: str) -> Optional[dict]:
        """Get user by ID."""
        user = await self.user_repository.find_by_id(user_id)
        return self._user_to_dict(user) if user else None
    
    def _user_to_dict(self, user) -> dict:
        """Convert user entity to dictionary (see domain layer for User entity definition)."""
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat()
        }
```

## 2. Application Exceptions

Simple exceptions for application-level errors:

```python
class ApplicationError(Exception):
    """Base application exception."""
    
    def __init__(self, message: str, code: str = None):
        super().__init__(message)
        self.message = message
        self.code = code or "APPLICATION_ERROR"

class ValidationError(ApplicationError):
    """Validation error in application layer."""
    pass

class NotFoundError(ApplicationError):
    """Resource not found error."""
    pass

class UnauthorizedError(ApplicationError):
    """Unauthorized access error."""
    pass
```

## 3. Usage in FastAPI

Example of using application services in FastAPI routes:

```python
from fastapi import FastAPI, HTTPException
from .services import UserApplicationService
from .exceptions import ApplicationError, NotFoundError

app = FastAPI()

# Dependency injection
user_service = UserApplicationService(user_repository)

@app.post("/users")
async def create_user_endpoint(user_data: dict):
    """Create user endpoint."""
    try:
        result = await user_service.create_user(
            name=user_data["name"],
            email=user_data["email"]
        )
        return result
    except ApplicationError as e:
        raise HTTPException(status_code=400, detail=e.message)

@app.get("/users/{user_id}")
async def get_user_endpoint(user_id: str):
    """Get user endpoint."""
    try:
        user = await user_service.get_user(user_id)
        if not user:
            raise NotFoundError("User not found")
        return user
    except NotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except ApplicationError as e:
        raise HTTPException(status_code=400, detail=e.message)
```

**Rules:**

* Keep application services simple and focused
* Handle domain exceptions and convert to application exceptions
* Coordinate between domain services and infrastructure
* Return simple dictionaries or Pydantic models from services
* Use dependency injection for repositories and external services

