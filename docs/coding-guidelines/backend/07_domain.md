# Domain Layer Guidelines

## Overview

The domain layer contains the core business logic and rules of the application. It should be pure, testable, and independent of external concerns like databases, HTTP, or third-party services. This layer implements Domain-Driven Design (DDD) principles with entities, value objects, domain services, and domain events.

## Key Principles

- **Pure business logic**: No dependencies on infrastructure or external systems
- **Side-effect isolation**: Use dependency injection for time, ID generation, and external operations
- **Invariant enforcement**: Domain objects maintain their consistency and business rules
- **Rich domain models**: Behavior-rich entities and value objects, not anemic data containers

## Directory Structure

```
domain/
├── entities/           # Domain entities with identity and lifecycle
│   ├── user.py
│   ├── organization.py
│   └── subscription.py
├── value_objects/      # Immutable value objects
│   ├── email.py
│   ├── user_id.py
│   └── money.py
├── services/          # Domain services for complex business operations
│   ├── user_service.py
│   └── billing_service.py
├── events/            # Domain events
│   ├── base.py
│   ├── user_events.py
│   └── billing_events.py
├── ports/             # Abstract interfaces for external dependencies
│   ├── repositories.py
│   ├── time_provider.py
│   └── id_provider.py
└── exceptions/        # Domain-specific exceptions
    ├── base.py
    ├── user_exceptions.py
    └── validation_exceptions.py
```

## Entities

Entities have identity and lifecycle. They encapsulate business logic and maintain invariants.

### Example: User Entity

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from domain.value_objects.user_id import UserId
from domain.value_objects.email import Email
from domain.events.user_events import UserCreated, UserEmailChanged
from domain.exceptions.user_exceptions import InvalidUserStateError


@dataclass
class User:
    """User entity with identity and business logic."""
    
    id: UserId
    email: Email
    display_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    version: int = 1
    
    # Domain events (not persisted)
    _events: list = None
    
    def __post_init__(self):
        if self._events is None:
            self._events = []
    
    @classmethod
    def create(
        cls,
        user_id: UserId,
        email: Email,
        display_name: str,
        created_at: datetime,
    ) -> "User":
        """Factory method for creating new users."""
        if not display_name.strip():
            raise InvalidUserStateError("Display name cannot be empty")
        
        user = cls(
            id=user_id,
            email=email,
            display_name=display_name.strip(),
            is_active=True,
            created_at=created_at,
            updated_at=created_at,
        )
        
        user._add_event(UserCreated(
            user_id=user_id,
            email=email,
            display_name=display_name,
            created_at=created_at,
        ))
        
        return user
    
    def change_email(self, new_email: Email, updated_at: datetime) -> None:
        """Change user email with business rules."""
        if not self.is_active:
            raise InvalidUserStateError("Cannot change email for inactive user")
        
        if self.email == new_email:
            return  # No change needed
        
        old_email = self.email
        self.email = new_email
        self.updated_at = updated_at
        self.version += 1
        
        self._add_event(UserEmailChanged(
            user_id=self.id,
            old_email=old_email,
            new_email=new_email,
            changed_at=updated_at,
        ))
    
    def deactivate(self, deactivated_at: datetime) -> None:
        """Deactivate user with business rules."""
        if not self.is_active:
            return  # Already inactive
        
        self.is_active = False
        self.updated_at = deactivated_at
        self.version += 1
    
    def get_events(self) -> list:
        """Get domain events for publishing."""
        return list(self._events)
    
    def clear_events(self) -> None:
        """Clear domain events after publishing."""
        self._events.clear()
    
    def _add_event(self, event) -> None:
        """Add domain event."""
        self._events.append(event)
```

## Value Objects

Value objects are immutable and defined by their attributes. They contain validation logic and helper methods.

### Example: Email Value Object

```python
import re
from dataclasses import dataclass

from domain.exceptions.validation_exceptions import InvalidEmailError


@dataclass(frozen=True)
class Email:
    """Email value object with validation."""
    
    value: str
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self) -> None:
        """Validate email format."""
        if not self.value:
            raise InvalidEmailError("Email cannot be empty")
        
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', self.value):
            raise InvalidEmailError(f"Invalid email format: {self.value}")
        
        if len(self.value) > 254:
            raise InvalidEmailError("Email too long")
    
    @property
    def domain(self) -> str:
        """Extract domain part of email."""
        return self.value.split('@')[1]
    
    def is_corporate_domain(self, corporate_domains: set[str]) -> bool:
        """Check if email belongs to corporate domain."""
        return self.domain.lower() in corporate_domains
    
    def __str__(self) -> str:
        return self.value
```

### Example: UserId Value Object

```python
from dataclasses import dataclass
from typing import Union

from domain.exceptions.validation_exceptions import InvalidUserIdError


@dataclass(frozen=True)
class UserId:
    """User ID value object supporting ULID and UUID formats."""
    
    value: str
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self) -> None:
        """Validate user ID format (ULID or UUID)."""
        if not self.value:
            raise InvalidUserIdError("User ID cannot be empty")
        
        # ULID: 26 characters, base32
        if len(self.value) == 26 and self.value.replace('-', '').isalnum():
            return
        
        # UUID: with or without hyphens
        cleaned = self.value.replace('-', '')
        if len(cleaned) == 32 and all(c in '0123456789abcdefABCDEF' for c in cleaned):
            return
        
        raise InvalidUserIdError(f"Invalid user ID format: {self.value}")
    
    @classmethod
    def from_string(cls, value: str) -> "UserId":
        """Create UserId from string."""
        return cls(value.strip())
    
    def __str__(self) -> str:
        return self.value
```

## Domain Services

Domain services encapsulate business logic that doesn't naturally belong to any single entity or value object.

### Example: User Domain Service

```python
from datetime import datetime
from typing import Optional

from domain.entities.user import User
from domain.value_objects.user_id import UserId
from domain.value_objects.email import Email
from domain.ports.repositories import UserRepository
from domain.ports.time_provider import TimeProvider
from domain.ports.id_provider import IdProvider
from domain.exceptions.user_exceptions import DuplicateEmailError


class UserDomainService:
    """Domain service for user-related business operations."""
    
    def __init__(
        self,
        user_repository: UserRepository,
        time_provider: TimeProvider,
        id_provider: IdProvider,
    ):
        self._user_repository = user_repository
        self._time_provider = time_provider
        self._id_provider = id_provider
    
    async def create_unique_user(
        self,
        email: Email,
        display_name: str,
    ) -> User:
        """Create user ensuring email uniqueness."""
        # Check for existing user with same email
        existing_user = await self._user_repository.find_by_email(email)
        if existing_user is not None:
            raise DuplicateEmailError(f"User with email {email} already exists")
        
        # Generate new user ID and create user
        user_id = UserId(self._id_provider.generate_ulid())
        created_at = self._time_provider.now()
        
        return User.create(
            user_id=user_id,
            email=email,
            display_name=display_name,
            created_at=created_at,
        )
    
    async def can_change_email(
        self,
        user: User,
        new_email: Email,
    ) -> bool:
        """Check if user can change to new email."""
        if not user.is_active:
            return False
        
        if user.email == new_email:
            return True
        
        # Check if new email is already taken
        existing_user = await self._user_repository.find_by_email(new_email)
        return existing_user is None
```

## Domain Events

Domain events represent significant business occurrences. They enable loose coupling and eventual consistency.

### Base Event

```python
from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any

from domain.value_objects.user_id import UserId


@dataclass
class DomainEvent(ABC):
    """Base class for all domain events."""
    
    aggregate_id: str
    occurred_at: datetime
    event_version: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            'event_type': self.__class__.__name__,
            'aggregate_id': self.aggregate_id,
            'occurred_at': self.occurred_at.isoformat(),
            'event_version': self.event_version,
            'payload': self._payload_to_dict(),
        }
    
    def _payload_to_dict(self) -> Dict[str, Any]:
        """Convert event payload to dictionary."""
        # Override in subclasses
        return {}
```

### User Events

```python
from dataclasses import dataclass
from datetime import datetime

from domain.events.base import DomainEvent
from domain.value_objects.user_id import UserId
from domain.value_objects.email import Email


@dataclass
class UserCreated(DomainEvent):
    """Event raised when a user is created."""
    
    user_id: UserId
    email: Email
    display_name: str
    created_at: datetime
    
    def __post_init__(self):
        super().__init__(
            aggregate_id=str(self.user_id),
            occurred_at=self.created_at,
        )
    
    def _payload_to_dict(self) -> dict:
        return {
            'user_id': str(self.user_id),
            'email': str(self.email),
            'display_name': self.display_name,
        }


@dataclass
class UserEmailChanged(DomainEvent):
    """Event raised when user email is changed."""
    
    user_id: UserId
    old_email: Email
    new_email: Email
    changed_at: datetime
    
    def __post_init__(self):
        super().__init__(
            aggregate_id=str(self.user_id),
            occurred_at=self.changed_at,
        )
    
    def _payload_to_dict(self) -> dict:
        return {
            'user_id': str(self.user_id),
            'old_email': str(self.old_email),
            'new_email': str(self.new_email),
        }
```

## Ports (Abstract Interfaces)

Ports define contracts for external dependencies without coupling to specific implementations.

### Repository Port

```python
from abc import ABC, abstractmethod
from typing import Optional, List

from domain.entities.user import User
from domain.value_objects.user_id import UserId
from domain.value_objects.email import Email


class UserRepository(ABC):
    """Repository port for user persistence."""
    
    @abstractmethod
    async def save(self, user: User) -> None:
        """Save user to storage."""
        pass
    
    @abstractmethod
    async def find_by_id(self, user_id: UserId) -> Optional[User]:
        """Find user by ID."""
        pass
    
    @abstractmethod
    async def find_by_email(self, email: Email) -> Optional[User]:
        """Find user by email."""
        pass
    
    @abstractmethod
    async def find_active_users(self, limit: int = 100) -> List[User]:
        """Find active users with pagination."""
        pass
    
    @abstractmethod
    async def delete(self, user_id: UserId) -> bool:
        """Delete user. Returns True if user existed."""
        pass
```

### Time Provider Port

```python
from abc import ABC, abstractmethod
from datetime import datetime


class TimeProvider(ABC):
    """Time provider port for testable time operations."""
    
    @abstractmethod
    def now(self) -> datetime:
        """Get current UTC datetime."""
        pass
    
    @abstractmethod
    def timestamp(self) -> float:
        """Get current Unix timestamp."""
        pass
```

### ID Provider Port

```python
from abc import ABC, abstractmethod


class IdProvider(ABC):
    """ID provider port for generating unique identifiers."""
    
    @abstractmethod
    def generate_ulid(self) -> str:
        """Generate ULID string."""
        pass
    
    @abstractmethod
    def generate_uuid4(self) -> str:
        """Generate UUID4 string."""
        pass
```

## Domain Exceptions

Domain-specific exceptions communicate business rule violations.

### Base Exception

```python
class DomainError(Exception):
    """Base class for all domain exceptions."""
    
    def __init__(self, message: str, error_code: str = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
```

### User Exceptions

```python
from domain.exceptions.base import DomainError


class UserDomainError(DomainError):
    """Base class for user domain errors."""
    pass


class InvalidUserStateError(UserDomainError):
    """Raised when user is in invalid state for operation."""
    pass


class DuplicateEmailError(UserDomainError):
    """Raised when attempting to use duplicate email."""
    pass


class UserNotFoundError(UserDomainError):
    """Raised when user cannot be found."""
    pass
```

### Validation Exceptions

```python
from domain.exceptions.base import DomainError


class ValidationError(DomainError):
    """Base class for validation errors."""
    pass


class InvalidEmailError(ValidationError):
    """Raised when email format is invalid."""
    pass


class InvalidUserIdError(ValidationError):
    """Raised when user ID format is invalid."""
    pass
```

## Best Practices

### Entity Design

- **Rich behavior**: Entities should contain business logic, not just data
- **Invariant enforcement**: Validate state changes in entity methods
- **Immutable value objects**: Use value objects for IDs and other identifiers
- **Factory methods**: Use static factory methods for complex creation logic
- **Domain events**: Raise events for significant business occurrences

### Value Object Design

- **Immutability**: Value objects should be immutable (`frozen=True`)
- **Validation**: Validate in `__post_init__` or constructor
- **Self-validating**: Value objects validate their own consistency
- **Primitive obsession**: Wrap primitives in value objects when they have business meaning

### Domain Service Usage

- **Cross-entity logic**: Use domain services for logic spanning multiple entities
- **Complex business rules**: Encapsulate complex business operations
- **Repository coordination**: Coordinate multiple repository operations
- **Pure functions**: Domain services should be stateless where possible

### Testing Strategy

```python
# Unit tests for domain objects
def test_user_creation():
    """Test user creation with valid data."""
    user_id = UserId("01HKQC7G5R8N9P2M1T4V6X8Z0B")
    email = Email("john@example.com")
    created_at = datetime(2024, 1, 1, 12, 0, 0)
    
    user = User.create(
        user_id=user_id,
        email=email,
        display_name="John Doe",
        created_at=created_at,
    )
    
    assert user.id == user_id
    assert user.email == email
    assert user.display_name == "John Doe"
    assert user.is_active
    assert len(user.get_events()) == 1
    assert isinstance(user.get_events()[0], UserCreated)

def test_user_email_change():
    """Test user email change business logic."""
    user = create_test_user()
    new_email = Email("jane@example.com")
    changed_at = datetime(2024, 1, 2, 12, 0, 0)
    
    user.change_email(new_email, changed_at)
    
    assert user.email == new_email
    assert user.updated_at == changed_at
    assert user.version == 2
    assert len(user.get_events()) == 1
    assert isinstance(user.get_events()[0], UserEmailChanged)
```

## Common Pitfalls

- **Anemic domain models**: Don't create entities that are just data containers
- **Infrastructure coupling**: Never import infrastructure modules in domain layer
- **Side effects**: Don't perform I/O operations directly in domain objects
- **Primitive obsession**: Don't use primitives for domain concepts (use value objects)
- **Missing invariants**: Always validate business rules and constraints
- **Leaky abstractions**: Keep ports abstract and implementation-agnostic

## Transaction Boundaries

- **Aggregate consistency**: Maintain strong consistency within aggregate boundaries
- **Eventual consistency**: Use domain events for cross-aggregate consistency
- **Single aggregate per transaction**: Modify only one aggregate per transaction
- **Event publishing**: Publish domain events after successful persistence