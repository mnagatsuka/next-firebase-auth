# 13. Testing Strategy

This section outlines the **testing strategy** for Python + FastAPI backend projects using **Clean Architecture** principles. It covers the **test pyramid approach**, **naming conventions**, **directory layout**, and **testing patterns** for each layer of the architecture.

The strategy emphasizes **fast unit tests** for business logic, **focused integration tests** for adapters, **end-to-end API tests**, and **contract testing** using OpenAPI examples with LocalStack for AWS service testing.


## 1. Test Pyramid Overview

We follow the test pyramid approach with three main layers:

```
     /\
    /  \     E2E Tests (Few)
   /____\    - Full API workflows
  /      \   - Real user scenarios
 /________\  - Slowest, most expensive
/          \
\__________/ Integration Tests (Some)
/          \ - Adapter boundaries
\__________/ - External service mocking
/          \ - Database interactions
\__________/
/          \ Unit Tests (Many)
\__________/ - Business logic
             - Domain entities
             - Application services
             - Fast, isolated
```

### Test Distribution Guidelines

- **70% Unit Tests**: Fast, isolated tests for domain and application layers
- **20% Integration Tests**: Tests for infrastructure adapters and external service interactions
- **10% E2E Tests**: Full API workflow tests covering critical user journeys

**Rules:**

* Prioritize unit tests for business logic and domain entities.
* Use integration tests sparingly for adapter boundaries.
* Minimize E2E tests to critical user workflows only.
* Aim for fast test execution (< 30 seconds for full suite).


## 2. Directory Structure & Organization

### Test Directory Layout

Following the established directory structure in `tests/README.md`:

```
tests/
├── frontend/              # Frontend tests (existing)
│   ├── unit/
│   └── integration/
├── backend/               # Backend-specific tests
│   ├── unit/             # Fast, isolated tests
│   │   ├── domain/       # Domain entity tests
│   │   │   ├── test_user.py
│   │   │   ├── test_order.py
│   │   │   └── __init__.py
│   │   ├── application/  # Application service tests
│   │   │   ├── test_user_service.py
│   │   │   ├── test_order_service.py
│   │   │   └── __init__.py
│   │   └── shared/       # Utility tests
│   │       ├── test_validators.py
│   │       └── __init__.py
│   ├── integration/      # Adapter and external service tests
│   │   ├── infra/
│   │   │   ├── test_user_repository.py
│   │   │   ├── test_s3_client.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── fixtures/         # Shared test fixtures
│   │   ├── __init__.py
│   │   ├── users.py
│   │   └── orders.py
│   ├── factories/        # Test data factories
│   │   ├── __init__.py
│   │   ├── user_factory.py
│   │   └── order_factory.py
│   └── conftest.py       # Backend pytest configuration
└── e2e/                  # E2E tests (handled by Playwright - see separate documentation)
```

### Naming Conventions

**File Naming:**
- Test files: `test_<module_name>.py`
- Factory files: `<entity>_factory.py`
- Fixture files: `<entity>s.py` (plural)

**Test Function Naming:**
```python
def test_<action>_<expected_outcome>():
    """Test that describes what is being tested."""
    pass

# Examples
def test_create_user_with_valid_data_returns_user():
def test_create_user_with_invalid_email_raises_validation_error():
def test_get_user_by_id_when_not_found_raises_not_found_error():
```

**Rules:**

* Follow the established directory structure in `tests/README.md`.
* Place backend-specific tests under `tests/backend/`.
* E2E tests in `tests/e2e/` are handled by Playwright (see separate documentation).
* Mirror backend source code structure within `tests/backend/`.
* Use descriptive test function names that explain the scenario.


## 3. Unit Testing (Domain & Application Layers)

Unit tests focus on business logic without external dependencies.

### Domain Entity Testing

```python
# tests/backend/unit/domain/test_user.py
import pytest
import sys
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent.parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from datetime import datetime
from domain.entities.user import User, UserStatus
from domain.exceptions import DomainValidationError

class TestUser:
    def test_create_user_with_valid_data_returns_user(self):
        """Test creating a user with valid data."""
        user = User(
            id="user123",
            email="test@example.com",
            name="Test User",
            status=UserStatus.ACTIVE
        )
        
        assert user.id == "user123"
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.status == UserStatus.ACTIVE
        assert isinstance(user.created_at, datetime)

    def test_create_user_with_invalid_email_raises_validation_error(self):
        """Test that invalid email raises validation error."""
        with pytest.raises(DomainValidationError, match="Invalid email format"):
            User(
                id="user123",
                email="invalid-email",
                name="Test User",
                status=UserStatus.ACTIVE
            )

    def test_deactivate_user_changes_status_to_inactive(self):
        """Test that deactivating a user changes status."""
        user = User(
            id="user123",
            email="test@example.com",
            name="Test User",
            status=UserStatus.ACTIVE
        )
        
        user.deactivate()
        
        assert user.status == UserStatus.INACTIVE
        assert user.deactivated_at is not None
```

### Application Service Testing

```python
# tests/backend/unit/application/test_user_service.py
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock

# Add backend to Python path
backend_path = Path(__file__).parent.parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from application.services.user_service import UserService
from domain.entities.user import User, UserStatus
from domain.exceptions import UserNotFoundError

class TestUserService:
    def setup_method(self):
        """Set up test dependencies."""
        self.user_repository = Mock()
        self.email_service = Mock()
        self.user_service = UserService(
            user_repository=self.user_repository,
            email_service=self.email_service
        )

    @pytest.mark.asyncio
    async def test_create_user_with_valid_data_returns_user(self):
        """Test creating a user through the service."""
        # Arrange
        user_data = {
            "email": "test@example.com",
            "name": "Test User"
        }
        expected_user = User(
            id="user123",
            email="test@example.com",
            name="Test User",
            status=UserStatus.ACTIVE
        )
        self.user_repository.save = AsyncMock(return_value=expected_user)
        self.email_service.send_welcome_email = AsyncMock()

        # Act
        result = await self.user_service.create_user(user_data)

        # Assert
        assert result.email == "test@example.com"
        assert result.name == "Test User"
        self.user_repository.save.assert_called_once()
        self.email_service.send_welcome_email.assert_called_once_with(result)

    @pytest.mark.asyncio
    async def test_get_user_by_id_when_not_found_raises_error(self):
        """Test that getting non-existent user raises error."""
        # Arrange
        self.user_repository.get_by_id = AsyncMock(return_value=None)

        # Act & Assert
        with pytest.raises(UserNotFoundError):
            await self.user_service.get_user_by_id("nonexistent")
```

**Rules:**

* Test business logic without external dependencies.
* Use mocks for all external dependencies.
* Focus on edge cases and error conditions.
* Test one behavior per test function.
* Add backend directory to Python path for imports.


## 4. Integration Testing (Infrastructure Layer)

Integration tests verify adapter implementations and external service interactions.

### Repository Testing with LocalStack

```python
# tests/backend/integration/infra/test_user_repository.py
import pytest
import sys
from pathlib import Path
import boto3
from moto import mock_dynamodb

# Add backend to Python path
backend_path = Path(__file__).parent.parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from infra.repositories.user_repository import DynamoDBUserRepository
from domain.entities.user import User, UserStatus
from shared.config import get_settings

@mock_dynamodb
class TestDynamoDBUserRepository:
    def setup_method(self):
        """Set up test database."""
        self.settings = get_settings()
        self.settings.aws_endpoint_url = None  # Use moto mock
        
        # Create DynamoDB table
        dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-1')
        self.table = dynamodb.create_table(
            TableName='users',
            KeySchema=[
                {'AttributeName': 'pk', 'KeyType': 'HASH'},
                {'AttributeName': 'sk', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'pk', 'AttributeType': 'S'},
                {'AttributeName': 'sk', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        self.repository = DynamoDBUserRepository(settings=self.settings)

    @pytest.mark.asyncio
    async def test_save_user_stores_in_dynamodb(self):
        """Test saving a user to DynamoDB."""
        # Arrange
        user = User(
            id="user123",
            email="test@example.com",
            name="Test User",
            status=UserStatus.ACTIVE
        )

        # Act
        saved_user = await self.repository.save(user)

        # Assert
        assert saved_user.id == "user123"
        
        # Verify in database
        response = self.table.get_item(
            Key={'pk': 'user#user123', 'sk': 'profile'}
        )
        assert 'Item' in response
        assert response['Item']['email'] == "test@example.com"

    @pytest.mark.asyncio
    async def test_get_by_id_returns_user_when_exists(self):
        """Test retrieving an existing user."""
        # Arrange - Save user first
        user = User(
            id="user123",
            email="test@example.com",
            name="Test User",
            status=UserStatus.ACTIVE
        )
        await self.repository.save(user)

        # Act
        retrieved_user = await self.repository.get_by_id("user123")

        # Assert
        assert retrieved_user is not None
        assert retrieved_user.id == "user123"
        assert retrieved_user.email == "test@example.com"
```

**Rules:**

* Use LocalStack or mocking for external services in integration tests.
* Test adapter implementations against real service interfaces.
* Focus on data transformation and error handling.
* Keep integration tests focused on single adapter responsibilities.


## 5. Test Fixtures & Factories

*Note: E2E testing is handled separately with Playwright. See the dedicated E2E testing documentation for full-stack workflow testing.*

### Backend Test Configuration

```python
# tests/backend/conftest.py
import pytest
import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock
from fastapi.testclient import TestClient

# Add backend to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from main import app

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def test_client():
    """FastAPI test client."""
    return TestClient(app)

@pytest.fixture
def mock_user_repository():
    """Mock user repository."""
    return Mock()

@pytest.fixture
def mock_email_service():
    """Mock email service."""
    return Mock()

@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "name": "Test User"
    }
```

### Test Data Factories

```python
# tests/backend/factories/user_factory.py
import sys
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

# Add backend to Python path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from domain.entities.user import User, UserStatus

@dataclass
class UserFactory:
    """Factory for creating test user instances."""
    
    @staticmethod
    def create(
        id: str = "user123",
        email: str = "test@example.com",
        name: str = "Test User",
        status: UserStatus = UserStatus.ACTIVE,
        created_at: Optional[datetime] = None
    ) -> User:
        """Create a user with default or provided values."""
        return User(
            id=id,
            email=email,
            name=name,
            status=status,
            created_at=created_at or datetime.utcnow()
        )
    
    @staticmethod
    def create_inactive() -> User:
        """Create an inactive user."""
        return UserFactory.create(status=UserStatus.INACTIVE)
    
    @staticmethod
    def create_with_email(email: str) -> User:
        """Create a user with specific email."""
        return UserFactory.create(email=email)

# Usage in tests
# user = UserFactory.create()
# inactive_user = UserFactory.create_inactive()
# custom_user = UserFactory.create(name="Custom Name", email="custom@example.com")
```

**Rules:**

* Use fixtures for shared test setup and dependencies.
* Create factories for test data generation.
* Keep test data realistic but minimal.
* Use parameterized tests for testing multiple scenarios.


## 6. Time & ID Faking

### Freezing Time for Tests

```python
# tests/backend/unit/domain/test_user.py
import pytest
from freezegun import freeze_time
from datetime import datetime
from domain.entities.user import User, UserStatus

class TestUser:
    @freeze_time("2024-01-01 12:00:00")
    def test_user_creation_sets_correct_timestamp(self):
        """Test that user creation sets expected timestamp."""
        user = User(
            id="user123",
            email="test@example.com",
            name="Test User",
            status=UserStatus.ACTIVE
        )
        
        expected_time = datetime(2024, 1, 1, 12, 0, 0)
        assert user.created_at == expected_time
```

### Mocking ID Generation

```python
# tests/backend/unit/application/test_user_service.py
import pytest
from unittest.mock import patch
from application.services.user_service import UserService

class TestUserService:
    @patch('uuid.uuid4')
    def test_create_user_generates_expected_id(self, mock_uuid):
        """Test that user ID is generated correctly."""
        # Arrange
        mock_uuid.return_value.hex = "abc123def456"
        # ... rest of test
```

**Rules:**

* Use `freezegun` for time-sensitive tests.
* Mock ID generation for predictable test outcomes.
* Keep time and ID mocking minimal and focused.
* Document any time-dependent behavior in tests.


## 7. LocalStack Integration for AWS Services

### DynamoDB Testing with LocalStack

```python
# tests/backend/integration/infra/test_dynamodb_integration.py
import pytest
import boto3
import pytest_asyncio
from testcontainers.localstack import LocalStackContainer
from infra.repositories.user_repository import DynamoDBUserRepository

@pytest.fixture(scope="session")
def localstack_container():
    """Start LocalStack container for testing."""
    with LocalStackContainer(image="localstack/localstack:latest") as container:
        container.with_services("dynamodb")
        yield container

@pytest.fixture
async def dynamodb_table(localstack_container):
    """Create DynamoDB table for testing."""
    endpoint_url = localstack_container.get_url()
    
    dynamodb = boto3.resource(
        'dynamodb',
        endpoint_url=endpoint_url,
        aws_access_key_id='test',
        aws_secret_access_key='test',
        region_name='ap-northeast-1'
    )
    
    table = dynamodb.create_table(
        TableName='users',
        KeySchema=[
            {'AttributeName': 'pk', 'KeyType': 'HASH'},
            {'AttributeName': 'sk', 'KeyType': 'RANGE'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'pk', 'AttributeType': 'S'},
            {'AttributeName': 'sk', 'AttributeType': 'S'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    
    yield table
    
    table.delete()

class TestDynamoDBIntegration:
    @pytest.mark.asyncio
    async def test_repository_crud_operations(self, dynamodb_table, localstack_container):
        """Test CRUD operations against real DynamoDB."""
        # Test implementation using real LocalStack DynamoDB
        pass
```

**Rules:**

* Use LocalStack containers for AWS service testing.
* Create clean test environments for each test.
* Test against real AWS service interfaces when possible.
* Keep LocalStack tests focused on integration scenarios.


## 8. Contract Testing from OpenAPI Examples

### Generating Contract Tests

```python
# tests/backend/integration/test_openapi_contracts.py
import pytest
import yaml
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add backend to Python path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from main import app

class TestOpenAPIContracts:
    def setup_method(self):
        """Load OpenAPI specification."""
        self.client = TestClient(app)
        
        # Load OpenAPI spec
        spec_path = Path("backend/api/openapi.yml")
        with open(spec_path) as f:
            self.openapi_spec = yaml.safe_load(f)

    def test_create_user_matches_openapi_example(self):
        """Test that API response matches OpenAPI example."""
        # Extract example from OpenAPI spec
        create_user_example = (
            self.openapi_spec["paths"]["/users"]["post"]
            ["responses"]["201"]["content"]["application/json"]["example"]
        )
        
        # Make API call
        response = self.client.post("/users", json={
            "email": "test@example.com",
            "name": "Test User"
        })
        
        # Verify response matches example structure
        assert response.status_code == 201
        data = response.json()
        
        # Verify all expected fields are present
        expected_fields = set(create_user_example.keys())
        actual_fields = set(data.keys())
        assert expected_fields <= actual_fields

    def test_api_responses_validate_against_schema(self):
        """Test that API responses validate against OpenAPI schema."""
        # Implementation for schema validation testing
        pass
```

**Rules:**

* Generate contract tests from OpenAPI examples.
* Validate API responses against OpenAPI schemas.
* Test both success and error response formats.
* Keep contract tests focused on API boundaries.


## 9. Test Configuration & Environment

### Backend pytest Configuration

```ini
# tests/backend/pytest.ini
[tool:pytest]
testpaths = tests/backend
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --verbose
    --tb=short
    --cov=backend
    --cov-report=term-missing
    --cov-report=html:tests/backend/htmlcov
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
asyncio_mode = auto
```

### Test Environment Variables

```bash
# tests/backend/.env.test
ENVIRONMENT=test
DATABASE_URL=sqlite:///test.db
AWS_ENDPOINT_URL=http://localhost:4566
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
LOG_LEVEL=WARNING
```

### Test Commands

```bash
# Run all backend tests from project root
pytest tests/backend/

# Run by category
pytest tests/backend/ -m unit
pytest tests/backend/ -m integration

# Run with coverage
pytest tests/backend/ --cov=backend --cov-report=html

# Run specific test file
pytest tests/backend/unit/domain/test_user.py

# Run tests in parallel
pytest tests/backend/ -n auto
```

### Makefile Integration

```makefile
.PHONY: test-backend test-backend-unit test-backend-integration

# Run all backend tests
test-backend:
	pytest tests/backend/

# Run backend unit tests
test-backend-unit:
	pytest tests/backend/ -m unit

# Run backend integration tests
test-backend-integration:
	pytest tests/backend/ -m integration

# Run backend tests with coverage
test-backend-coverage:
	pytest tests/backend/ --cov=backend --cov-report=html
```

**Rules:**

* Follow the established test directory structure.
* Configure pytest for backend-specific testing.
* Use separate environment configuration for backend tests.
* Provide convenient commands for different test categories.
* Maintain high test coverage (>80%) while focusing on meaningful tests.
* Ensure all tests can run from project root directory.
* E2E testing is handled separately with Playwright (see separate documentation).
