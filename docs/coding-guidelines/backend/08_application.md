# Application Layer Guidelines (Use Cases)

## Overview

The application layer orchestrates use cases and coordinates between the domain layer and infrastructure. It contains application services that implement business workflows, define transaction boundaries, and handle cross-cutting concerns like security, validation, and event publishing.

## Key Principles

- **Use case orchestration**: Coordinate domain objects and infrastructure services
- **Transaction boundaries**: Define consistent transaction scopes
- **Port-driven design**: Depend on abstractions (ports), not implementations
- **Input/output isolation**: Clean separation between external DTOs and domain models
- **Stateless services**: Application services should be stateless and composable

## Directory Structure

```
application/
├── use_cases/          # Use case implementations
│   ├── user/
│   │   ├── create_user.py
│   │   ├── update_user.py
│   │   └── get_user.py
│   ├── auth/
│   │   ├── authenticate_user.py
│   │   └── refresh_token.py
│   └── billing/
│       ├── create_subscription.py
│       └── process_payment.py
├── ports/              # Input/output ports (interfaces)
│   ├── input/
│   │   ├── user_commands.py
│   │   ├── user_queries.py
│   │   └── auth_commands.py
│   └── output/
│       ├── event_publisher.py
│       ├── notification_service.py
│       └── audit_logger.py
├── models/             # Application-level DTOs and commands
│   ├── commands/
│   │   ├── user_commands.py
│   │   └── auth_commands.py
│   ├── queries/
│   │   ├── user_queries.py
│   │   └── billing_queries.py
│   └── responses/
│       ├── user_responses.py
│       └── error_responses.py
├── services/           # Application services
│   ├── user_service.py
│   ├── auth_service.py
│   └── billing_service.py
└── exceptions/         # Application-specific exceptions
    ├── base.py
    ├── authorization_errors.py
    └── use_case_errors.py
```

## Use Case Implementation Patterns

### Command Pattern for State-Changing Operations

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from application.models.commands.user_commands import CreateUserCommand
from application.models.responses.user_responses import UserResponse
from application.ports.output.event_publisher import EventPublisher
from application.exceptions.use_case_errors import UseCaseError
from domain.entities.user import User
from domain.services.user_service import UserDomainService
from domain.ports.repositories import UserRepository
from domain.ports.time_provider import TimeProvider
from domain.ports.id_provider import IdProvider
from domain.exceptions.user_exceptions import DuplicateEmailError


@dataclass
class CreateUserCommand:
    """Command for creating a new user."""
    email: str
    display_name: str
    firebase_uid: str
    created_by: Optional[str] = None


@dataclass
class UserResponse:
    """Response model for user operations."""
    id: str
    email: str
    display_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CreateUserUseCase:
    """Use case for creating a new user."""
    
    def __init__(
        self,
        user_repository: UserRepository,
        user_domain_service: UserDomainService,
        event_publisher: EventPublisher,
        time_provider: TimeProvider,
        id_provider: IdProvider,
    ):
        self._user_repository = user_repository
        self._user_domain_service = user_domain_service
        self._event_publisher = event_publisher
        self._time_provider = time_provider
        self._id_provider = id_provider
    
    async def execute(self, command: CreateUserCommand) -> UserResponse:
        """Execute the create user use case."""
        try:
            # Validate command
            await self._validate_command(command)
            
            # Create domain objects
            email = Email(command.email)
            
            # Execute domain logic
            user = await self._user_domain_service.create_unique_user(
                email=email,
                display_name=command.display_name,
            )
            
            # Store additional metadata if needed
            user.firebase_uid = command.firebase_uid
            
            # Persist changes
            await self._user_repository.save(user)
            
            # Publish domain events
            await self._publish_events(user)
            
            # Return response
            return self._map_to_response(user)
            
        except DuplicateEmailError as e:
            raise UseCaseError(f"User creation failed: {e.message}", "USER_ALREADY_EXISTS")
        except Exception as e:
            raise UseCaseError(f"User creation failed: {str(e)}", "CREATION_FAILED")
    
    async def _validate_command(self, command: CreateUserCommand) -> None:
        """Validate command input."""
        if not command.email or not command.email.strip():
            raise UseCaseError("Email is required", "VALIDATION_ERROR")
        
        if not command.display_name or not command.display_name.strip():
            raise UseCaseError("Display name is required", "VALIDATION_ERROR")
        
        if not command.firebase_uid or not command.firebase_uid.strip():
            raise UseCaseError("Firebase UID is required", "VALIDATION_ERROR")
    
    async def _publish_events(self, user: User) -> None:
        """Publish domain events."""
        events = user.get_events()
        for event in events:
            await self._event_publisher.publish(event)
        user.clear_events()
    
    def _map_to_response(self, user: User) -> UserResponse:
        """Map domain entity to response model."""
        return UserResponse(
            id=str(user.id),
            email=str(user.email),
            display_name=user.display_name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
```

### Query Pattern for Read Operations

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List

from application.models.queries.user_queries import GetUserQuery, ListUsersQuery
from application.models.responses.user_responses import UserResponse, UserListResponse
from application.exceptions.use_case_errors import UseCaseError
from domain.ports.repositories import UserRepository
from domain.value_objects.user_id import UserId
from domain.exceptions.user_exceptions import UserNotFoundError


@dataclass
class GetUserQuery:
    """Query for getting a user by ID."""
    user_id: str
    requested_by: Optional[str] = None


@dataclass
class ListUsersQuery:
    """Query for listing users with pagination."""
    limit: int = 20
    offset: int = 0
    active_only: bool = True
    requested_by: Optional[str] = None


@dataclass
class UserListResponse:
    """Response for user list operations."""
    users: List[UserResponse]
    total_count: int
    has_more: bool


class GetUserUseCase:
    """Use case for retrieving a user."""
    
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository
    
    async def execute(self, query: GetUserQuery) -> UserResponse:
        """Execute the get user query."""
        try:
            # Validate query
            user_id = UserId(query.user_id)
            
            # Fetch user
            user = await self._user_repository.find_by_id(user_id)
            if user is None:
                raise UserNotFoundError(f"User not found: {query.user_id}")
            
            # Return response
            return UserResponse(
                id=str(user.id),
                email=str(user.email),
                display_name=user.display_name,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
            
        except UserNotFoundError as e:
            raise UseCaseError(e.message, "USER_NOT_FOUND")
        except Exception as e:
            raise UseCaseError(f"Failed to retrieve user: {str(e)}", "QUERY_FAILED")


class ListUsersUseCase:
    """Use case for listing users."""
    
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository
    
    async def execute(self, query: ListUsersQuery) -> UserListResponse:
        """Execute the list users query."""
        try:
            # Validate query
            if query.limit <= 0 or query.limit > 100:
                raise UseCaseError("Limit must be between 1 and 100", "VALIDATION_ERROR")
            
            if query.offset < 0:
                raise UseCaseError("Offset must be non-negative", "VALIDATION_ERROR")
            
            # Fetch users
            users = await self._user_repository.find_paginated(
                limit=query.limit,
                offset=query.offset,
                active_only=query.active_only,
            )
            
            # Get total count for pagination
            total_count = await self._user_repository.count(active_only=query.active_only)
            
            # Map to response
            user_responses = [
                UserResponse(
                    id=str(user.id),
                    email=str(user.email),
                    display_name=user.display_name,
                    is_active=user.is_active,
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                )
                for user in users
            ]
            
            return UserListResponse(
                users=user_responses,
                total_count=total_count,
                has_more=query.offset + len(users) < total_count,
            )
            
        except Exception as e:
            raise UseCaseError(f"Failed to list users: {str(e)}", "QUERY_FAILED")
```

## Application Services

Application services provide higher-level orchestration and handle complex workflows.

```python
from typing import Optional, List
from datetime import datetime

from application.use_cases.user.create_user import CreateUserUseCase
from application.use_cases.user.update_user import UpdateUserUseCase
from application.use_cases.user.get_user import GetUserUseCase
from application.models.commands.user_commands import CreateUserCommand, UpdateUserCommand
from application.models.queries.user_queries import GetUserQuery
from application.models.responses.user_responses import UserResponse
from application.ports.output.notification_service import NotificationService
from application.ports.output.audit_logger import AuditLogger


class UserApplicationService:
    """Application service for user-related operations."""
    
    def __init__(
        self,
        create_user_use_case: CreateUserUseCase,
        update_user_use_case: UpdateUserUseCase,
        get_user_use_case: GetUserUseCase,
        notification_service: NotificationService,
        audit_logger: AuditLogger,
    ):
        self._create_user = create_user_use_case
        self._update_user = update_user_use_case
        self._get_user = get_user_use_case
        self._notification_service = notification_service
        self._audit_logger = audit_logger
    
    async def create_user(
        self,
        email: str,
        display_name: str,
        firebase_uid: str,
        created_by: Optional[str] = None,
    ) -> UserResponse:
        """Create a new user with full workflow."""
        command = CreateUserCommand(
            email=email,
            display_name=display_name,
            firebase_uid=firebase_uid,
            created_by=created_by,
        )
        
        # Execute use case
        user_response = await self._create_user.execute(command)
        
        # Send welcome notification
        await self._notification_service.send_welcome_email(
            email=user_response.email,
            display_name=user_response.display_name,
        )
        
        # Log audit trail
        await self._audit_logger.log_user_created(
            user_id=user_response.id,
            created_by=created_by,
            timestamp=datetime.utcnow(),
        )
        
        return user_response
    
    async def get_user_profile(
        self,
        user_id: str,
        requested_by: Optional[str] = None,
    ) -> UserResponse:
        """Get user profile with access control."""
        query = GetUserQuery(
            user_id=user_id,
            requested_by=requested_by,
        )
        
        # Execute query
        user_response = await self._get_user.execute(query)
        
        # Log access for audit
        if requested_by and requested_by != user_id:
            await self._audit_logger.log_profile_access(
                user_id=user_id,
                accessed_by=requested_by,
                timestamp=datetime.utcnow(),
            )
        
        return user_response
```

## Idempotency and Deduplication

### Idempotency Key Pattern

```python
from dataclasses import dataclass
from typing import Optional
import hashlib

from application.ports.output.idempotency_store import IdempotencyStore
from application.models.responses.user_responses import UserResponse
from application.exceptions.use_case_errors import IdempotencyConflictError


@dataclass
class IdempotentOperation:
    """Wrapper for idempotent operations."""
    operation_id: str
    request_hash: str
    response: Optional[dict] = None
    completed: bool = False


class IdempotentCreateUserUseCase:
    """Idempotent version of create user use case."""
    
    def __init__(
        self,
        create_user_use_case: CreateUserUseCase,
        idempotency_store: IdempotencyStore,
    ):
        self._create_user = create_user_use_case
        self._idempotency_store = idempotency_store
    
    async def execute(
        self,
        command: CreateUserCommand,
        idempotency_key: str,
    ) -> UserResponse:
        """Execute create user with idempotency protection."""
        # Generate request hash for conflict detection
        request_hash = self._hash_command(command)
        
        # Check for existing operation
        existing_op = await self._idempotency_store.get(idempotency_key)
        
        if existing_op:
            # Verify request matches (prevent key reuse)
            if existing_op.request_hash != request_hash:
                raise IdempotencyConflictError(
                    "Idempotency key reused with different request"
                )
            
            # Return cached response if completed
            if existing_op.completed and existing_op.response:
                return UserResponse(**existing_op.response)
            
            # Operation in progress, could retry or return conflict
            raise IdempotencyConflictError("Operation already in progress")
        
        # Create new operation record
        operation = IdempotentOperation(
            operation_id=idempotency_key,
            request_hash=request_hash,
        )
        await self._idempotency_store.store(idempotency_key, operation)
        
        try:
            # Execute the operation
            result = await self._create_user.execute(command)
            
            # Store successful result
            operation.response = {
                'id': result.id,
                'email': result.email,
                'display_name': result.display_name,
                'is_active': result.is_active,
                'created_at': result.created_at.isoformat(),
                'updated_at': result.updated_at.isoformat(),
            }
            operation.completed = True
            await self._idempotency_store.store(idempotency_key, operation)
            
            return result
            
        except Exception:
            # Remove operation record on failure
            await self._idempotency_store.delete(idempotency_key)
            raise
    
    def _hash_command(self, command: CreateUserCommand) -> str:
        """Generate hash of command for conflict detection."""
        content = f"{command.email}:{command.display_name}:{command.firebase_uid}"
        return hashlib.sha256(content.encode()).hexdigest()
```

## Port Definitions

### Input Ports (Use Case Interfaces)

```python
from abc import ABC, abstractmethod
from typing import List

from application.models.commands.user_commands import CreateUserCommand, UpdateUserCommand
from application.models.queries.user_queries import GetUserQuery, ListUsersQuery
from application.models.responses.user_responses import UserResponse, UserListResponse


class UserCommands(ABC):
    """Input port for user commands."""
    
    @abstractmethod
    async def create_user(self, command: CreateUserCommand) -> UserResponse:
        pass
    
    @abstractmethod
    async def update_user(self, command: UpdateUserCommand) -> UserResponse:
        pass


class UserQueries(ABC):
    """Input port for user queries."""
    
    @abstractmethod
    async def get_user(self, query: GetUserQuery) -> UserResponse:
        pass
    
    @abstractmethod
    async def list_users(self, query: ListUsersQuery) -> UserListResponse:
        pass
```

### Output Ports (External Service Interfaces)

```python
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any

from domain.events.base import DomainEvent


class EventPublisher(ABC):
    """Port for publishing domain events."""
    
    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        pass
    
    @abstractmethod
    async def publish_batch(self, events: List[DomainEvent]) -> None:
        pass


class NotificationService(ABC):
    """Port for sending notifications."""
    
    @abstractmethod
    async def send_welcome_email(self, email: str, display_name: str) -> None:
        pass
    
    @abstractmethod
    async def send_password_reset(self, email: str, reset_token: str) -> None:
        pass


class AuditLogger(ABC):
    """Port for audit logging."""
    
    @abstractmethod
    async def log_user_created(
        self,
        user_id: str,
        created_by: str,
        timestamp: datetime,
    ) -> None:
        pass
    
    @abstractmethod
    async def log_profile_access(
        self,
        user_id: str,
        accessed_by: str,
        timestamp: datetime,
    ) -> None:
        pass


class IdempotencyStore(ABC):
    """Port for idempotency operations."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[IdempotentOperation]:
        pass
    
    @abstractmethod
    async def store(self, key: str, operation: IdempotentOperation) -> None:
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        pass
```

## Transaction Management

```python
from abc import ABC, abstractmethod
from typing import AsyncContextManager
from contextlib import asynccontextmanager


class TransactionManager(ABC):
    """Port for transaction management."""
    
    @abstractmethod
    @asynccontextmanager
    async def transaction(self) -> AsyncContextManager[None]:
        pass


class TransactionalUserService:
    """User service with transaction support."""
    
    def __init__(
        self,
        user_repository: UserRepository,
        event_publisher: EventPublisher,
        transaction_manager: TransactionManager,
    ):
        self._user_repository = user_repository
        self._event_publisher = event_publisher
        self._transaction_manager = transaction_manager
    
    async def create_user_transactional(
        self,
        command: CreateUserCommand,
    ) -> UserResponse:
        """Create user within a transaction."""
        async with self._transaction_manager.transaction():
            # Create user
            user = await self._create_domain_user(command)
            
            # Save to repository
            await self._user_repository.save(user)
            
            # Collect events
            events = user.get_events()
            user.clear_events()
            
            # Publish events (within transaction)
            for event in events:
                await self._event_publisher.publish(event)
            
            return self._map_to_response(user)
```

## Exception Handling

```python
from typing import Optional


class ApplicationError(Exception):
    """Base application layer exception."""
    
    def __init__(
        self,
        message: str,
        error_code: str,
        details: Optional[dict] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class UseCaseError(ApplicationError):
    """Exception raised by use case execution."""
    pass


class AuthorizationError(ApplicationError):
    """Exception raised for authorization failures."""
    pass


class ValidationError(ApplicationError):
    """Exception raised for validation failures."""
    pass


class IdempotencyConflictError(ApplicationError):
    """Exception raised for idempotency conflicts."""
    pass
```

## Testing Strategy

### Use Case Testing

```python
import pytest
from unittest.mock import Mock, AsyncMock

from application.use_cases.user.create_user import CreateUserUseCase
from application.models.commands.user_commands import CreateUserCommand
from domain.entities.user import User
from domain.value_objects.user_id import UserId
from domain.value_objects.email import Email


@pytest.fixture
def mock_dependencies():
    return {
        'user_repository': Mock(),
        'user_domain_service': Mock(),
        'event_publisher': AsyncMock(),
        'time_provider': Mock(),
        'id_provider': Mock(),
    }


@pytest.mark.asyncio
async def test_create_user_success(mock_dependencies):
    """Test successful user creation."""
    # Arrange
    use_case = CreateUserUseCase(**mock_dependencies)
    
    command = CreateUserCommand(
        email="john@example.com",
        display_name="John Doe",
        firebase_uid="firebase_123",
    )
    
    user = User.create(
        user_id=UserId("01HKQC7G5R8N9P2M1T4V6X8Z0B"),
        email=Email("john@example.com"),
        display_name="John Doe",
        created_at=datetime.utcnow(),
    )
    
    mock_dependencies['user_domain_service'].create_unique_user.return_value = user
    mock_dependencies['user_repository'].save.return_value = None
    
    # Act
    result = await use_case.execute(command)
    
    # Assert
    assert result.email == "john@example.com"
    assert result.display_name == "John Doe"
    assert result.is_active
    
    mock_dependencies['user_repository'].save.assert_called_once_with(user)
    mock_dependencies['event_publisher'].publish.assert_called()


@pytest.mark.asyncio
async def test_create_user_duplicate_email(mock_dependencies):
    """Test user creation with duplicate email."""
    # Arrange
    use_case = CreateUserUseCase(**mock_dependencies)
    
    command = CreateUserCommand(
        email="john@example.com",
        display_name="John Doe",
        firebase_uid="firebase_123",
    )
    
    mock_dependencies['user_domain_service'].create_unique_user.side_effect = \
        DuplicateEmailError("User with email already exists")
    
    # Act & Assert
    with pytest.raises(UseCaseError) as exc_info:
        await use_case.execute(command)
    
    assert exc_info.value.error_code == "USER_ALREADY_EXISTS"
```

## Best Practices

### Use Case Design

- **Single responsibility**: Each use case should handle one business operation
- **Input validation**: Validate all inputs at the application layer boundary
- **Domain coordination**: Orchestrate domain services and repositories
- **Event publishing**: Always publish domain events after successful persistence
- **Error translation**: Convert domain exceptions to application exceptions

### Transaction Boundaries

- **Keep transactions short**: Minimize transaction scope and duration
- **Single aggregate per transaction**: Avoid distributed transactions when possible
- **Compensating actions**: Design for eventual consistency with compensation patterns
- **Idempotency**: Support idempotent operations for reliability

### Port Design

- **Interface segregation**: Keep ports focused and cohesive
- **Dependency direction**: Application layer depends on abstractions, not concretions
- **Testability**: Design ports to enable easy mocking and testing
- **Async-first**: Design for asynchronous operations by default

### Command/Query Separation

- **Commands**: State-changing operations with validation and events
- **Queries**: Read-only operations optimized for specific views
- **Separate models**: Use different models for commands, queries, and responses
- **Caching strategy**: Apply caching at the query level where appropriate

This application layer serves as the orchestration hub between domain logic and external concerns, ensuring clean separation of responsibilities while maintaining transactional consistency and system reliability.