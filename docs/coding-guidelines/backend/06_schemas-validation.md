# 6. Schemas & Server-Side Validation

Simple schema definition and validation patterns for Python + FastAPI applications using Pydantic.

## Overview

- Use Pydantic `BaseModel` for API request/response validation
- Use `@dataclass` for domain entities (not BaseModel)
- Keep validation rules simple and focused on data integrity  
- Provide clear error messages for validation failures

## BaseModel vs Dataclass Usage

**Use Pydantic BaseModel for:**
- API request/response models
- Data validation at application boundaries
- Generated OpenAPI models
- Serialization/deserialization needs

**Use dataclass for:**
- Domain entities with business logic
- Internal data structures without API concerns
- Framework-independent code

## 1. Request/Response Models

Use Pydantic models for API request and response validation:

```python
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class CreateUserRequest(BaseModel):
    """Request model for creating a user."""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr

class UserResponse(BaseModel):
    """Response model for user data."""
    id: str
    name: str
    email: str
    created_at: datetime
    is_active: bool = True

class UpdateUserRequest(BaseModel):
    """Request model for updating a user."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
```

## 2. Custom Validation

Add custom validation logic using Pydantic validators:

```python
from pydantic import BaseModel, validator
import re

class CreateUserRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    
    @validator('name')
    def validate_name(cls, v):
        """Validate name field."""
        if not v.strip():
            raise ValueError('Name cannot be empty')
        
        # Remove extra whitespace
        return v.strip()
    
    @validator('email')
    def validate_email_domain(cls, v):
        """Custom email validation."""
        # Add any custom email domain rules here
        return v.lower()
```

## 3. Error Handling

Handle validation errors consistently:

```python
from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc: ValidationError):
    """Handle Pydantic validation errors."""
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": exc.errors()
        }
    )
```

## 4. Usage in FastAPI Routes

Example of using validation models in FastAPI:

```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/users", response_model=UserResponse)
async def create_user(user_data: CreateUserRequest):
    """Create a new user."""
    # user_data is automatically validated
    user = await create_user_service(
        name=user_data.name,
        email=user_data.email
    )
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        created_at=user.created_at,
        is_active=user.is_active
    )

@app.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, updates: UpdateUserRequest):
    """Update a user with partial data."""
    # Only fields provided in the request are included
    update_data = updates.dict(exclude_unset=True)
    user = await update_user_service(user_id, update_data)
    return UserResponse(**user.dict())
```

**Rules:**

* Keep validation simple and focused on data integrity
* Use clear, descriptive error messages
* Validate at the API boundary with Pydantic models
* Handle partial updates with `exclude_unset=True`

