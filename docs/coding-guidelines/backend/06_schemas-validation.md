# 6. Schemas, Validation, and Mapping

This section defines the rules and best practices for **schema definition**, **data validation**, and **mapping between layers** in Python + FastAPI applications following an OpenAPI-first approach.

Our goals are:
- Maintain clear separation between OpenAPI schemas and domain models
- Implement robust validation with clear error messages
- Provide efficient mapping between transport DTOs and domain objects
- Support partial updates and flexible field handling
- Ensure type safety across all data transformations

## 1. Schema Separation: OpenAPI vs Domain Models

### OpenAPI Schemas (Transport Layer)

OpenAPI schemas define the **API contract** and are used for request/response serialization:

```yaml
# docs/openapi/components/schemas.yaml
UserResponse:
  type: object
  properties:
    id:
      type: string
      format: ulid
      example: "01ARZ3NDEKTSV4RRFFQ69G5FAV"
    name:
      type: string
      minLength: 1
      maxLength: 100
      example: "John Doe"
    email:
      type: string
      format: email
      example: "john@example.com"
    created_at:
      type: string
      format: date-time
      example: "2023-10-01T12:00:00Z"
    status:
      $ref: '#/components/schemas/UserStatus'
  required: [id, name, email, created_at, status]

CreateUserRequest:
  type: object
  properties:
    name:
      type: string
      minLength: 1
      maxLength: 100
    email:
      type: string
      format: email
  required: [name, email]
```

### Generated Pydantic DTOs

Generate Pydantic models from OpenAPI specs for transport layer:

```python
# Generated from OpenAPI spec
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Literal
from shared.types import ULID

class UserResponse(BaseModel):
    """User response DTO (generated from OpenAPI)."""
    id: ULID = Field(..., description="Unique user identifier")
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    created_at: datetime
    status: Literal["active", "inactive", "suspended"]

class CreateUserRequest(BaseModel):
    """Create user request DTO (generated from OpenAPI)."""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
```

### Domain Models (Business Layer)

Domain models focus on **business logic** and invariants:

```python
# domain/user.py
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from shared.types import ULID

class UserStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive" 
    SUSPENDED = "suspended"

@dataclass(frozen=True)
class User:
    """User domain entity."""
    id: ULID
    name: str
    email: str
    created_at: datetime
    status: UserStatus
    
    def __post_init__(self):
        """Validate domain invariants."""
        if not self.name.strip():
            raise ValueError("User name cannot be empty")
        if len(self.name) > 100:
            raise ValueError("User name cannot exceed 100 characters")
    
    def suspend(self) -> 'User':
        """Business operation: suspend user."""
        if self.status == UserStatus.SUSPENDED:
            return self
        return User(
            id=self.id,
            name=self.name,
            email=self.email,
            created_at=self.created_at,
            status=UserStatus.SUSPENDED
        )
```

**Rules:**

* **OpenAPI schemas** define transport contracts and validation rules
* **Domain models** focus on business logic and invariants
* **Generate DTOs** from OpenAPI specs, don't hand-write them
* **Never mix** transport concerns with domain logic

## 2. Field Naming and Conventions

### Consistent Naming Patterns

```python
from pydantic import BaseModel, Field, AliasChoices

class UserResponse(BaseModel):
    """User response with field naming conventions."""
    
    # Use snake_case internally, support camelCase from API
    user_id: str = Field(..., alias="userId", serialization_alias="user_id")
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")
    
    # Timestamps in ISO 8601 format
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    
    # ID formats (ULID preferred, UUID fallback)
    id: ULID = Field(..., description="ULID identifier")
    
    class Config:
        # Accept both snake_case and camelCase
        alias_generator = None
        allow_population_by_field_name = True
```

### ID Format Standards

```python
from typing import NewType
import ulid

# Type aliases for different ID formats
ULID = NewType('ULID', str)
UUID = NewType('UUID', str)

def generate_ulid() -> ULID:
    """Generate new ULID."""
    return ULID(str(ulid.new()))

# Validation functions
def validate_ulid(value: str) -> ULID:
    """Validate ULID format."""
    try:
        ulid.parse(value)
        return ULID(value)
    except ValueError as e:
        raise ValueError(f"Invalid ULID format: {e}")
```

**Rules:**

* Use **snake_case** internally in Python code
* Support **camelCase** for API compatibility when needed
* Prefer **ULID** over UUID for new identifiers (sortable, timestamp-encoded)
* Use **ISO 8601** format for all timestamps
* Define **type aliases** for different ID formats

## 3. Validation Rules and Custom Validators

### Field-Level Validation

```python
from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional
import re

class CreateUserRequest(BaseModel):
    """Create user request with comprehensive validation."""
    
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=100,
        description="User's full name"
    )
    email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    age: Optional[int] = Field(None, ge=13, le=150)
    phone: Optional[str] = Field(None, regex=r'^\+?1?\d{9,15}$')
    
    @validator('name')
    def validate_name(cls, v):
        """Custom name validation."""
        if not v.strip():
            raise ValueError('Name cannot be empty or whitespace only')
        
        # Check for prohibited characters
        if re.search(r'[<>\"\'&]', v):
            raise ValueError('Name contains invalid characters')
        
        return v.strip().title()
    
    @validator('email')
    def validate_email_domain(cls, v):
        """Validate email domain."""
        domain = v.split('@')[1].lower()
        
        # Block temporary email services
        blocked_domains = {'tempmail.com', '10minutemail.com'}
        if domain in blocked_domains:
            raise ValueError('Email from temporary services not allowed')
        
        return v.lower()
    
    @root_validator
    def validate_user_data(cls, values):
        """Cross-field validation."""
        age = values.get('age')
        email = values.get('email')
        
        # Business rule: users under 16 need parental consent
        if age and age < 16:
            if not email or not email.endswith('.edu'):
                raise ValueError('Users under 16 require educational email')
        
        return values
```

### Normalized Error Messages

```python
from pydantic import ValidationError
from typing import Dict, Any

class ValidationErrorHandler:
    """Handle and normalize validation errors."""
    
    @staticmethod
    def format_validation_errors(exc: ValidationError) -> Dict[str, Any]:
        """Format Pydantic validation errors for API responses."""
        formatted_errors = {}
        
        for error in exc.errors():
            field_path = '.'.join(str(loc) for loc in error['loc'])
            error_type = error['type']
            message = error['msg']
            
            # Normalize common error messages
            if error_type == 'value_error.missing':
                message = f"Field '{field_path}' is required"
            elif error_type == 'type_error.str':
                message = f"Field '{field_path}' must be a string"
            elif error_type == 'value_error.email':
                message = f"Field '{field_path}' must be a valid email address"
            
            formatted_errors[field_path] = {
                'message': message,
                'type': error_type,
                'value': error.get('input')
            }
        
        return formatted_errors

# Usage in FastAPI exception handler
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors."""
    
    errors = ValidationErrorHandler.format_validation_errors(exc)
    
    return JSONResponse(
        status_code=422,
        content={
            "type": "/problems/validation-error",
            "title": "Validation Error",
            "status": 422,
            "detail": "The request contains invalid data",
            "errors": errors
        }
    )
```

**Rules:**

* Use **Pydantic validators** for complex validation logic
* Provide **clear, actionable** error messages
* Implement **cross-field validation** when business rules require it
* **Normalize error formats** for consistent API responses
* **Sanitize input data** in validators (trim whitespace, normalize case)

## 4. PATCH Semantics and Partial Updates

### Partial Update DTOs

```python
from typing import Optional
from pydantic import BaseModel

class UpdateUserRequest(BaseModel):
    """Partial user update request."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    status: Optional[UserStatus] = None
    
    class Config:
        # Only include fields that are explicitly set
        exclude_unset = True
    
    def get_update_fields(self) -> Dict[str, Any]:
        """Get only the fields that should be updated."""
        return self.dict(exclude_unset=True)

# Alternative: Use None to explicitly unset fields
class UpdateUserRequestWithNulls(BaseModel):
    """User update with explicit null handling."""
    
    name: Optional[str] = Field(None)
    bio: Optional[str] = Field(None)  # None means "unset this field"
    
    def get_updates(self) -> Dict[str, Any]:
        """Get updates, distinguishing between unset and null."""
        updates = {}
        set_fields = self.__fields_set__
        
        for field, value in self.dict().items():
            if field in set_fields:
                updates[field] = value  # Include None values for explicit nulls
        
        return updates
```

### Merge Strategies

```python
from typing import TypeVar, Dict, Any

T = TypeVar('T')

class MergeStrategy:
    """Strategies for merging partial updates."""
    
    @staticmethod
    def shallow_merge(original: T, updates: Dict[str, Any]) -> T:
        """Simple field replacement."""
        original_dict = original.__dict__.copy()
        original_dict.update(updates)
        return type(original)(**original_dict)
    
    @staticmethod
    def deep_merge(original: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge for nested objects."""
        result = original.copy()
        
        for key, value in updates.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = MergeStrategy.deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result

# Usage in service layer
async def update_user(user_id: ULID, updates: UpdateUserRequest) -> User:
    """Update user with partial data."""
    
    existing_user = await user_repository.get(user_id)
    if not existing_user:
        raise UserNotFound(user_id)
    
    # Get only the fields that were provided
    update_data = updates.get_update_fields()
    
    # Apply merge strategy
    updated_user = MergeStrategy.shallow_merge(existing_user, update_data)
    
    # Validate business rules after merge
    updated_user.validate_invariants()
    
    return await user_repository.save(updated_user)
```

**Rules:**

* Use **`exclude_unset=True`** for partial update DTOs
* **Distinguish** between unset fields and explicit null values
* Implement **merge strategies** appropriate for your data model
* **Validate business rules** after applying partial updates
* Support both **shallow and deep merge** strategies as needed

## 5. DTO ↔ Domain Mapping (Anti-Corruption Layer)

### Mapping Between Layers

```python
from abc import ABC, abstractmethod
from typing import Protocol

class UserMapper:
    """Maps between User DTOs and domain objects."""
    
    @staticmethod
    def to_domain(dto: CreateUserRequest) -> User:
        """Convert DTO to domain object."""
        return User(
            id=generate_ulid(),
            name=dto.name,
            email=dto.email.lower(),  # Normalize in mapping layer
            created_at=datetime.utcnow(),
            status=UserStatus.ACTIVE
        )
    
    @staticmethod
    def to_response_dto(domain_obj: User) -> UserResponse:
        """Convert domain object to response DTO."""
        return UserResponse(
            id=domain_obj.id,
            name=domain_obj.name,
            email=domain_obj.email,
            created_at=domain_obj.created_at,
            status=domain_obj.status.value  # Convert enum to string
        )
    
    @staticmethod
    def to_list_response(domain_objects: List[User]) -> List[UserResponse]:
        """Convert list of domain objects to response DTOs."""
        return [UserMapper.to_response_dto(obj) for obj in domain_objects]

# Generic mapper interface
class Mapper(Protocol[T, U]):
    """Generic mapper protocol."""
    
    @abstractmethod
    def to_domain(self, dto: T) -> U:
        """Convert DTO to domain object."""
        ...
    
    @abstractmethod
    def to_dto(self, domain_obj: U) -> T:
        """Convert domain object to DTO."""
        ...

# Usage in API layer
@app.post("/api/v1/users", response_model=UserResponse)
async def create_user(request: CreateUserRequest) -> UserResponse:
    """Create user endpoint."""
    
    # Map DTO to domain
    user = UserMapper.to_domain(request)
    
    # Business logic
    created_user = await user_service.create(user)
    
    # Map domain back to DTO
    return UserMapper.to_response_dto(created_user)
```

### Complex Mapping Scenarios

```python
class OrderMapper:
    """Complex mapper with nested objects and calculations."""
    
    @staticmethod
    def to_domain(dto: CreateOrderRequest, user: User) -> Order:
        """Convert order DTO with additional context."""
        
        # Map line items
        line_items = [
            LineItem(
                product_id=ULID(item.product_id),
                quantity=item.quantity,
                unit_price=item.unit_price
            )
            for item in dto.items
        ]
        
        return Order(
            id=generate_ulid(),
            user_id=user.id,
            line_items=line_items,
            created_at=datetime.utcnow(),
            status=OrderStatus.PENDING
        )
    
    @staticmethod
    def to_response_dto(domain_obj: Order, include_items: bool = True) -> OrderResponse:
        """Convert with optional nested data."""
        
        response = OrderResponse(
            id=domain_obj.id,
            user_id=domain_obj.user_id,
            total_amount=domain_obj.calculate_total(),  # Computed field
            status=domain_obj.status.value,
            created_at=domain_obj.created_at
        )
        
        if include_items:
            response.items = [
                LineItemResponse(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    subtotal=item.calculate_subtotal()
                )
                for item in domain_obj.line_items
            ]
        
        return response
```

**Rules:**

* Create **dedicated mapper classes** for each aggregate
* **Separate mapping logic** from business logic
* Handle **data normalization** in the mapping layer
* Support **computed fields** and **optional nested data**
* Use **type-safe mapping** with proper error handling
* **Never expose** domain objects directly in API responses

By following these schema and validation patterns, we ensure **data integrity**, **clear separation of concerns**, and **maintainable mapping** between different layers of the application while leveraging the OpenAPI-first approach for contract definition.