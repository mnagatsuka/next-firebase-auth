# 15. Coding Standards & Style

This section defines **coding standards** and **style guidelines** for Python + FastAPI backend projects. It covers **Ruff configuration**, **import organization**, **naming conventions**, **type hints policy**, **docstrings**, and **function/class complexity limits**.

The standards ensure **consistent code style**, **maintainable codebase**, and **effective collaboration** across team members and AI-assisted development.


## 1. Code Formatting & Linting with Ruff

We use **Ruff** as our primary tool for both linting and formatting, replacing the need for multiple tools like Black, isort, flake8, and others.

### Ruff Configuration

```toml
# backend/pyproject.toml
[tool.ruff]
target-version = "py313"
line-length = 88
indent-width = 4

[tool.ruff.lint]
# Enable specific rule sets
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # Pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "D",   # pydocstyle
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "SIM", # flake8-simplify
    "RET", # flake8-return
    "ARG", # flake8-unused-arguments
    "PTH", # flake8-use-pathlib
    "ERA", # eradicate (commented code)
    "PL",  # Pylint
    "RUF", # Ruff-specific rules
]

# Disable specific rules
ignore = [
    "D100",   # Missing docstring in public module
    "D104",   # Missing docstring in public package
    "D107",   # Missing docstring in __init__
    "PLR0913", # Too many arguments
    "PLR2004", # Magic value used in comparison
]

# Per-file ignores
[tool.ruff.lint.per-file-ignores]
"tests/**" = ["D", "ARG", "PLR2004"]
"scripts/**" = ["D"]
"__init__.py" = ["F401"]

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.ruff.lint.isort]
known-first-party = ["api", "application", "domain", "infra", "shared"]
section-order = ["future", "standard-library", "third-party", "first-party", "local-folder"]
```

### Running Ruff

```bash
# Format code
uv run ruff format .

# Check for linting issues
uv run ruff check .

# Fix auto-fixable issues
uv run ruff check --fix .

# Check specific files
uv run ruff check src/api/routes.py
```

**Rules:**

* Use Ruff for both linting and formatting.
* Follow the configured rule sets consistently.
* Fix auto-fixable issues before committing.
* Use per-file ignores sparingly and with justification.


## 2. Import Organization

### Import Order and Structure

```python
# Standard library imports
import asyncio
import logging
import os
from datetime import datetime
from typing import Optional, List, Dict

# Third-party imports
import boto3
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field

# First-party imports (our application)
from api.dependencies import get_current_user
from application.services.user_service import UserService
from domain.entities.user import User
from infra.repositories.user_repository import UserRepository
from shared.config import get_settings
```

### Import Guidelines

```python
# Good: Specific imports
from fastapi import FastAPI, HTTPException
from typing import Optional, List

# Good: Module import for many items
import boto3

# Avoid: Star imports
# from fastapi import *  # Don't do this

# Good: Relative imports within same package
from .dependencies import get_current_user
from ..services import UserService

# Good: Type-only imports (Python 3.13+)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from expensive_module import ExpensiveClass
```

**Rules:**

* Follow the standard import order: standard library, third-party, first-party.
* Use specific imports rather than star imports.
* Group imports logically with blank lines.
* Use relative imports within the same package.
* Use TYPE_CHECKING for type-only imports.


## 3. Naming Conventions

### Python Standard Naming

```python
# Variables and functions: snake_case
user_id = "12345"
current_user = None

def get_user_by_id(user_id: str) -> User:
    """Get user by ID."""
    return user_repository.get(user_id)

# Constants: UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3
DEFAULT_TIMEOUT = 30
API_VERSION = "v1"

# Classes: PascalCase
class UserService:
    """Service for user operations."""
    
    def __init__(self, repository: UserRepository):
        self.repository = repository

# Private attributes: leading underscore
class User:
    def __init__(self, id: str, email: str):
        self.id = id
        self.email = email
        self._created_at = datetime.utcnow()  # Private attribute

# Methods: snake_case
def calculate_total_price(items: List[Item]) -> float:
    """Calculate total price of items."""
    return sum(item.price for item in items)
```

### Domain-Specific Naming

```python
# Entities: Descriptive nouns
class User:
    """User entity."""

class Order:
    """Order entity."""

class PaymentMethod:
    """Payment method entity."""

# Services: Noun + Service
class UserService:
    """Service for user operations."""

class OrderService:
    """Service for order operations."""

# Repositories: Noun + Repository
class UserRepository:
    """Repository for user data access."""

class OrderRepository:
    """Repository for order data access."""

# Use cases: Verb + Noun
class CreateUser:
    """Use case to create a new user."""

class ProcessPayment:
    """Use case to process payment."""

# Exceptions: Descriptive + Error/Exception
class UserNotFoundError(Exception):
    """Raised when user is not found."""

class InvalidPaymentMethodError(Exception):
    """Raised when payment method is invalid."""
```

### File and Directory Naming

```python
# Files: snake_case
user_service.py
order_repository.py
firebase_auth.py

# Directories: snake_case
api/
application/
    services/
    use_cases/
domain/
    entities/
    exceptions/
infra/
    repositories/
    external_services/
shared/
    config/
    logging/

# Test files: test_ prefix
test_user_service.py
test_order_repository.py
```

**Rules:**

* Use snake_case for variables, functions, and modules.
* Use PascalCase for classes.
* Use UPPER_SNAKE_CASE for constants.
* Use descriptive names that express intent.
* Follow domain-specific naming patterns.


## 4. Type Hints Policy

### When to Use Type Hints

```python
# Always: Public function signatures
def get_user_by_id(user_id: str) -> Optional[User]:
    """Get user by ID."""
    return user_repository.get(user_id)

# Always: Class attributes and properties
class User:
    """User entity."""
    
    def __init__(self, id: str, email: str, name: str):
        self.id: str = id
        self.email: str = email
        self.name: str = name
        self._created_at: datetime = datetime.utcnow()

# Always: Function parameters and return types
async def create_user(
    user_data: CreateUserRequest,
    user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Create a new user."""
    user = await user_service.create(user_data)
    return UserResponse.from_domain(user)

# Complex types: Use type aliases
UserDict = Dict[str, Any]
UserList = List[User]
UserHandler = Callable[[User], Awaitable[None]]

# Generic types
from typing import TypeVar, Generic

T = TypeVar('T')

class Repository(Generic[T]):
    """Generic repository pattern."""
    
    async def get_by_id(self, id: str) -> Optional[T]:
        """Get entity by ID."""
        ...
```

### Type Hint Best Practices

```python
# Good: Use Optional for nullable values
def get_user_email(user_id: str) -> Optional[str]:
    """Get user email, may return None."""
    user = get_user(user_id)
    return user.email if user else None

# Good: Use Union for multiple types
from typing import Union

def process_id(user_id: Union[str, int]) -> str:
    """Process user ID from string or int."""
    return str(user_id)

# Good: Use Literal for specific values
from typing import Literal

def set_log_level(level: Literal["DEBUG", "INFO", "WARNING", "ERROR"]) -> None:
    """Set logging level."""
    logging.getLogger().setLevel(level)

# Good: Use Protocol for duck typing
from typing import Protocol

class Serializable(Protocol):
    """Protocol for serializable objects."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        ...

# Good: Use dataclasses with types
from dataclasses import dataclass

@dataclass
class CreateUserRequest:
    """Request to create user."""
    email: str
    name: str
    age: Optional[int] = None
```

**Rules:**

* Always use type hints for public function signatures.
* Use type hints for class attributes and properties.
* Use Optional for nullable values.
* Create type aliases for complex types.
* Use Protocols for duck typing when appropriate.


## 5. Docstrings

### Google Style Docstrings

```python
def create_user(email: str, name: str, age: Optional[int] = None) -> User:
    """Create a new user with the provided information.
    
    Args:
        email: User's email address. Must be valid email format.
        name: User's full name. Cannot be empty.
        age: User's age in years. Must be positive if provided.
        
    Returns:
        User: The created user entity with generated ID.
        
    Raises:
        InvalidEmailError: If email format is invalid.
        ValueError: If name is empty or age is negative.
        
    Examples:
        >>> user = create_user("john@example.com", "John Doe", 30)
        >>> print(user.email)
        john@example.com
    """
    if not email or "@" not in email:
        raise InvalidEmailError(f"Invalid email: {email}")
    
    if not name.strip():
        raise ValueError("Name cannot be empty")
        
    if age is not None and age < 0:
        raise ValueError("Age cannot be negative")
    
    return User(
        id=generate_id(),
        email=email,
        name=name,
        age=age
    )

class UserService:
    """Service for managing user operations.
    
    This service provides high-level operations for user management,
    including creation, retrieval, updating, and deletion of users.
    It coordinates between the domain layer and infrastructure layer.
    
    Attributes:
        repository: Repository for user data access.
        email_service: Service for sending emails.
        
    Examples:
        >>> repository = UserRepository()
        >>> email_service = EmailService()
        >>> service = UserService(repository, email_service)
        >>> user = await service.create_user(user_data)
    """
    
    def __init__(self, repository: UserRepository, email_service: EmailService):
        """Initialize user service.
        
        Args:
            repository: Repository for user data access.
            email_service: Service for sending emails.
        """
        self.repository = repository
        self.email_service = email_service
```

### Docstring Requirements

```python
# Always: Public functions and methods
def public_function() -> None:
    """Public function must have docstring."""
    pass

# Always: Classes
class PublicClass:
    """Public class must have docstring."""
    pass

# Optional: Private functions (but recommended for complex logic)
def _private_helper(data: str) -> str:
    """Private helper function.
    
    Complex private functions should have docstrings
    explaining their purpose and behavior.
    """
    return data.strip().lower()

# Always: Modules (at the top of file)
"""Module for user management operations.

This module contains services, repositories, and utilities
for managing user entities and their related operations.
"""

# Domain entities and value objects
@dataclass
class User:
    """User entity representing a system user.
    
    Attributes:
        id: Unique identifier for the user.
        email: User's email address.
        name: User's full name.
        created_at: Timestamp when user was created.
    """
    id: str
    email: str
    name: str
    created_at: datetime
```

**Rules:**

* Use Google-style docstrings consistently.
* Document all public functions, classes, and modules.
* Include Args, Returns, Raises, and Examples sections when appropriate.
* Keep docstrings concise but comprehensive.
* Document complex private functions.


## 6. Function and Class Size Limits

### Function Complexity Guidelines

```python
# Good: Small, focused function
def validate_email(email: str) -> bool:
    """Validate email format."""
    return "@" in email and "." in email.split("@")[1]

# Good: Single responsibility
def calculate_tax(amount: float, rate: float) -> float:
    """Calculate tax amount."""
    return amount * rate

# Acceptable: Moderate complexity (under 20 lines)
def process_user_registration(user_data: CreateUserRequest) -> User:
    """Process user registration with validation and creation.
    
    Performs email validation, checks for existing users,
    creates new user entity, and sends welcome email.
    """
    # Validate email format
    if not validate_email(user_data.email):
        raise InvalidEmailError("Invalid email format")
    
    # Check if user already exists
    existing_user = user_repository.get_by_email(user_data.email)
    if existing_user:
        raise UserAlreadyExistsError("User already exists")
    
    # Create new user
    user = User(
        id=generate_id(),
        email=user_data.email,
        name=user_data.name,
        created_at=datetime.utcnow()
    )
    
    # Save user
    saved_user = user_repository.save(user)
    
    # Send welcome email
    email_service.send_welcome_email(saved_user)
    
    return saved_user

# Refactor: Break down complex functions
def process_complex_workflow(data: ComplexData) -> Result:
    """Process complex workflow by breaking into steps."""
    validated_data = _validate_input_data(data)
    processed_data = _process_data(validated_data)
    result = _generate_result(processed_data)
    _notify_completion(result)
    return result

def _validate_input_data(data: ComplexData) -> ValidatedData:
    """Validate input data."""
    # Validation logic here
    pass

def _process_data(data: ValidatedData) -> ProcessedData:
    """Process validated data."""
    # Processing logic here
    pass
```

### Class Design Guidelines

```python
# Good: Focused single responsibility
class UserValidator:
    """Validator for user-related data."""
    
    def validate_email(self, email: str) -> bool:
        """Validate email format."""
        return "@" in email and "." in email.split("@")[1]
    
    def validate_name(self, name: str) -> bool:
        """Validate name format."""
        return len(name.strip()) >= 2

# Good: Clear separation of concerns
class User:
    """User domain entity."""
    
    def __init__(self, id: str, email: str, name: str):
        self.id = id
        self.email = email
        self.name = name
        self._created_at = datetime.utcnow()
    
    def update_email(self, new_email: str) -> None:
        """Update user email."""
        if not self._is_valid_email(new_email):
            raise InvalidEmailError("Invalid email format")
        self.email = new_email
    
    def _is_valid_email(self, email: str) -> bool:
        """Check if email is valid."""
        return "@" in email and "." in email.split("@")[1]

# Refactor: Break down large classes
class UserService:
    """Service for user operations."""
    
    def __init__(
        self,
        repository: UserRepository,
        validator: UserValidator,
        email_service: EmailService
    ):
        self.repository = repository
        self.validator = validator
        self.email_service = email_service
    
    async def create_user(self, user_data: CreateUserRequest) -> User:
        """Create new user."""
        return await self._user_creator.create(user_data)
    
    async def update_user(self, user_id: str, update_data: UpdateUserRequest) -> User:
        """Update existing user."""
        return await self._user_updater.update(user_id, update_data)
    
    @property
    def _user_creator(self) -> UserCreator:
        """Get user creator component."""
        return UserCreator(self.repository, self.validator, self.email_service)
    
    @property  
    def _user_updater(self) -> UserUpdater:
        """Get user updater component."""
        return UserUpdater(self.repository, self.validator)
```

### Complexity Thresholds

```python
# Function guidelines:
# - Maximum 25 lines of code
# - Maximum 4 parameters (use dataclasses/objects for more)
# - Maximum cyclomatic complexity of 10
# - Single responsibility principle

# Good: Using dataclass to reduce parameters
@dataclass
class UserCreationData:
    """Data for user creation."""
    email: str
    name: str
    age: Optional[int] = None
    preferences: Dict[str, Any] = field(default_factory=dict)

def create_user(data: UserCreationData) -> User:
    """Create user with consolidated data."""
    # Implementation here
    pass

# Class guidelines:
# - Maximum 200 lines of code
# - Maximum 20 public methods
# - Clear single responsibility
# - Proper composition over inheritance
```

**Rules:**

* Keep functions under 25 lines when possible.
* Limit function parameters to 4 or fewer.
* Break down complex functions into smaller helper functions.
* Keep classes focused on single responsibility.
* Use composition and dependency injection.


## 7. Code Quality Tools Integration

### Pre-commit Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.8
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
      - id: check-json
```

### Makefile Integration

*Task runner setup and development workflow commands are covered in [02_project-setup.md](./02_project-setup.md). Use the established task runner patterns for consistent development workflows.*

Key principles:
- Integrate quality checks into development workflow
- Use consistent task names across projects
- Automate repetitive development tasks

**Rules:**

* Use pre-commit hooks for consistent code quality.
* Run quality checks before committing.
* Integrate tools into development workflow.
* Automate formatting and linting where possible.


## 8. Code Review Guidelines

### Code Review Checklist

```python
# 1. Code Style
# ✓ Follows Ruff configuration
# ✓ Consistent naming conventions
# ✓ Proper import organization
# ✓ Appropriate docstrings

# 2. Type Safety
# ✓ Type hints for public functions
# ✓ Optional used for nullable values
# ✓ Complex types have aliases

# 3. Function Design
# ✓ Single responsibility
# ✓ Under 25 lines
# ✓ Clear parameter names
# ✓ Proper error handling

# 4. Class Design
# ✓ Single responsibility
# ✓ Clear interface
# ✓ Proper encapsulation
# ✓ Composition over inheritance

# 5. Testing
# ✓ Unit tests for business logic
# ✓ Integration tests for adapters
# ✓ Test coverage meets standards
```

### Common Review Comments

```python
# Style issues
"Use snake_case for variable names"
"Add docstring to public function"
"Organize imports according to isort configuration"
"Use type hints for function parameters"

# Design issues
"Function is too complex, consider breaking down"
"Class has too many responsibilities"
"Consider using dependency injection"
"Extract magic numbers to constants"

# Code quality
"Add error handling for edge cases"
"Use more descriptive variable names"
"Consider using dataclass for this structure"
"Remove commented-out code"
```

**Rules:**

* Review code for style, design, and quality.
* Provide constructive feedback with examples.
* Focus on maintainability and readability.
* Ensure code follows established patterns.


## 9. Exception Handling Standards

### Exception Hierarchy

```python
# Base exception classes
class DomainError(Exception):
    """Base class for domain-related errors."""
    
    def __init__(self, message: str, code: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.code = code

class ValidationError(DomainError):
    """Raised when validation fails."""
    pass

class NotFoundError(DomainError):
    """Raised when entity is not found."""
    pass

class ConflictError(DomainError):
    """Raised when entity already exists."""
    pass

# Specific exceptions
class UserNotFoundError(NotFoundError):
    """Raised when user is not found."""
    
    def __init__(self, user_id: str):
        super().__init__(f"User not found: {user_id}", "USER_NOT_FOUND")
        self.user_id = user_id

class InvalidEmailError(ValidationError):
    """Raised when email format is invalid."""
    
    def __init__(self, email: str):
        super().__init__(f"Invalid email format: {email}", "INVALID_EMAIL")
        self.email = email
```

### Error Handling Patterns

```python
# Good: Specific exception handling
async def get_user_by_id(user_id: str) -> User:
    """Get user by ID."""
    try:
        user = await user_repository.get(user_id)
        if not user:
            raise UserNotFoundError(user_id)
        return user
    except DatabaseError as e:
        logger.error(f"Database error retrieving user {user_id}: {e}")
        raise InternalServerError("Failed to retrieve user")

# Good: Early validation
def create_user(email: str, name: str) -> User:
    """Create user with validation."""
    if not email:
        raise ValidationError("Email is required")
    
    if not name:
        raise ValidationError("Name is required")
    
    if not _is_valid_email(email):
        raise InvalidEmailError(email)
    
    return User(id=generate_id(), email=email, name=name)

# Good: Context managers for resources
async def process_file(file_path: str) -> None:
    """Process file with proper resource management."""
    try:
        async with aiofiles.open(file_path, 'r') as file:
            content = await file.read()
            await process_content(content)
    except FileNotFoundError:
        raise FileProcessingError(f"File not found: {file_path}")
    except PermissionError:
        raise FileProcessingError(f"Permission denied: {file_path}")
```

**Rules:**

* Use specific exception types for different error conditions.
* Create custom exceptions for domain-specific errors.
* Include relevant context in exception messages.
* Use proper exception chaining when re-raising.


## 10. Performance and Best Practices

### Async/Await Guidelines

```python
# Good: Proper async function definition
async def fetch_user_data(user_id: str) -> UserData:
    """Fetch user data asynchronously."""
    user = await user_repository.get(user_id)
    profile = await profile_service.get(user_id)
    return UserData(user=user, profile=profile)

# Good: Concurrent operations
async def fetch_multiple_users(user_ids: List[str]) -> List[User]:
    """Fetch multiple users concurrently."""
    tasks = [user_repository.get(user_id) for user_id in user_ids]
    users = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out exceptions
    return [user for user in users if isinstance(user, User)]

# Good: Async context managers
class DatabaseConnection:
    """Database connection with async context manager."""
    
    async def __aenter__(self):
        self.connection = await get_connection()
        return self.connection
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.connection.close()
```

### Memory and Performance

```python
# Good: Use generators for large datasets
def process_large_dataset(items: Iterable[Item]) -> Iterator[ProcessedItem]:
    """Process large dataset efficiently."""
    for item in items:
        if item.is_valid():
            yield ProcessedItem.from_item(item)

# Good: Use dataclasses for simple data structures
@dataclass(frozen=True)
class UserSummary:
    """Immutable user summary."""
    id: str
    name: str
    email: str

# Good: Cache expensive operations
from functools import lru_cache

@lru_cache(maxsize=128)
def calculate_expensive_value(input_data: str) -> float:
    """Calculate expensive value with caching."""
    # Expensive calculation here
    return result
```

**Rules:**

* Use async/await for I/O operations.
* Leverage concurrent execution where appropriate.
* Use generators for memory-efficient processing.
* Cache expensive computations when beneficial.
* Profile performance-critical code paths.


## 11. Quick Reference

### Command Quick Reference

*Development commands and task runner setup are detailed in [02_project-setup.md](./02_project-setup.md). Use the established development workflow commands.*

### Style Checklist

- [ ] Code formatted with Ruff
- [ ] Imports organized correctly
- [ ] Functions have docstrings
- [ ] Type hints used appropriately
- [ ] Names follow conventions
- [ ] Functions under 25 lines
- [ ] Classes focused on single responsibility
- [ ] Proper exception handling

**Rules:**

* Follow established coding standards consistently.
* Use automated tools for formatting and linting.
* Focus on readability and maintainability.
* Review code for style and quality before committing.