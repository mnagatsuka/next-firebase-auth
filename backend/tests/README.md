# Backend Testing Guide

This directory contains comprehensive tests for the backend API following the **Test Pyramid** approach with clean architecture principles.

## Test Structure

```
tests/backend/
├── unit/                    # Fast, isolated unit tests (70%)
│   ├── domain/             # Domain entity and service tests
│   └── application/        # Application service tests
├── integration/            # Integration tests with real adapters (20%)
│   ├── infra/             # Repository and infrastructure tests
│   └── api/               # API endpoint tests
├── factories/             # Test data factories
├── conftest.py           # Pytest configuration and fixtures
├── pytest.ini           # Test configuration
└── requirements-test.txt # Test dependencies
```

## Quick Start

### 1. Install Dependencies

```bash
# From project root directory
uv sync --dev

# This installs all dependencies including test dependencies 
# defined in pyproject.toml [project.optional-dependencies.dev]
```

### 2. Run All Tests

```bash
# From project root directory
uv run pytest tests/backend/

# Or activate the virtual environment first
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pytest tests/backend/
```

## Test Categories

### Unit Tests (Fast, Isolated)

Test business logic without external dependencies:

```bash
# Run all unit tests
uv run pytest tests/backend/unit/

# Domain entity tests
uv run pytest tests/backend/unit/domain/test_blog_post.py

# Domain service tests  
uv run pytest tests/backend/unit/domain/test_post_service.py

# Application service tests
uv run pytest tests/backend/unit/application/test_posts_service.py
```

### Integration Tests

Test adapter implementations and API endpoints:

```bash
# Run all integration tests
uv run pytest tests/backend/integration/

# Repository tests
uv run pytest tests/backend/integration/infra/test_posts_repository.py

# API endpoint tests
uv run pytest tests/backend/integration/api/test_posts_endpoints.py
```

## Test Execution Options

### Coverage Reports

```bash
# Run with coverage
uv run pytest tests/backend/ --cov=backend --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Parallel Execution

```bash
# Install pytest-xdist for parallel execution
uv add --dev pytest-xdist

# Run tests in parallel
uv run pytest tests/backend/ -n auto
```

### Specific Test Selection

```bash
# Run tests by marker
uv run pytest tests/backend/ -m unit
uv run pytest tests/backend/ -m integration

# Run specific test method
uv run pytest tests/backend/unit/domain/test_blog_post.py::TestBlogPost::test_create_blog_post_with_valid_data_returns_post

# Run tests matching pattern
uv run pytest tests/backend/ -k "test_create"
```

### Verbose Output

```bash
# Detailed output
uv run pytest tests/backend/ -v

# Show test output even for passing tests
uv run pytest tests/backend/ -s

# Stop on first failure
uv run pytest tests/backend/ -x
```

## Test Configuration

### Pytest Configuration (`pyproject.toml`)

The test suite is configured in the root `pyproject.toml` with:
- **Coverage reporting** (minimum 80%)
- **Async test support**
- **Strict markers and configuration**
- **HTML coverage reports**
- **Test path**: `tests/backend/`
- **Python path**: `backend/src/`

### Test Fixtures (`conftest.py`)

Provides shared fixtures:
- `test_client`: FastAPI test client
- `mock_post_repository`: Mock repository
- `sample_post_data`: Test data templates

### Test Factories (`factories/`)

Use `PostFactory` for consistent test data:

```python
from factories.post_factory import PostFactory

# Create test data
post = PostFactory.create()
published_post = PostFactory.create_published()
author_post = PostFactory.create_with_author("john-doe")
```

## Writing New Tests

### Test Naming Convention

```python
def test_<action>_<expected_outcome>():
    """Test description explaining what is being tested."""
    # Arrange
    # Act  
    # Assert
```

### Domain Entity Tests

```python
class TestBlogPost:
    def test_create_blog_post_with_valid_data_returns_post(self):
        """Test creating a blog post with valid data."""
        # Test entity creation and validation
        
    def test_create_blog_post_with_invalid_data_raises_error(self):
        """Test validation errors are raised."""
        # Test error conditions
```

### Service Tests with Mocks

```python
class TestPostService:
    def setup_method(self):
        self.repository = Mock()
        self.service = PostService(self.repository)
    
    @pytest.mark.asyncio
    async def test_create_post_calls_repository_save(self):
        """Test service coordinates with repository."""
        # Test service orchestration
```

### API Endpoint Tests

```python
class TestPostsEndpoints:
    def test_create_post_returns_201_with_valid_data(self):
        """Test API endpoint returns correct status and data."""
        response = self.client.post("/api/v1/posts", json=data)
        assert response.status_code == 201
```

## Test Data Management

### Using Factories

```python
# Create minimal valid post
post = PostFactory.create()

# Create with specific attributes
post = PostFactory.create(
    title="Custom Title",
    author="specific-author"
)

# Create published post
published_post = PostFactory.create_published()
```

### Time-Sensitive Tests

```python
from freezegun import freeze_time

@freeze_time("2024-01-01 12:00:00")
def test_timestamps_are_set_correctly(self):
    """Test with frozen time for predictable results."""
    post = BlogPost.create_new(...)
    assert post.created_at == datetime(2024, 1, 1, 12, 0, 0)
```

## Debugging Tests

### Run with Debug Output

```bash
# Show print statements
pytest tests/backend/ -s

# Show detailed tracebacks
pytest tests/backend/ --tb=long

# Drop into debugger on failure
pytest tests/backend/ --pdb
```

### IDE Integration

For VS Code, add to `.vscode/settings.json`:

```json
{
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/backend"],
    "python.testing.unittestEnabled": false
}
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Backend Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r tests/backend/requirements-test.txt
      - run: pytest tests/backend/ --cov=backend --cov-report=xml
      - uses: codecov/codecov-action@v3
```

## Best Practices

### Test Organization

- **One test class per production class**
- **Group related tests in classes**
- **Use descriptive test and class names**
- **Keep tests focused and independent**

### Test Data

- **Use factories for consistent data creation**
- **Minimize test data complexity**
- **Make test data realistic but simple**
- **Avoid sharing mutable test data between tests**

### Mocking

- **Mock external dependencies (databases, APIs)**
- **Don't mock the system under test**
- **Use dependency injection for easier testing**
- **Verify mock interactions when relevant**

### Assertions

- **Use specific assertions**
- **Test one thing per test**
- **Include meaningful error messages**
- **Test both happy path and error conditions**

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure Python path includes backend directory
2. **Async Test Failures**: Use `@pytest.mark.asyncio` for async tests
3. **Mock Issues**: Verify mock setup and patch locations
4. **Coverage Problems**: Check file paths and exclusions

### Getting Help

- Review test examples in existing test files
- Check pytest documentation: https://docs.pytest.org/
- Review FastAPI testing guide: https://fastapi.tiangolo.com/tutorial/testing/

## Test Metrics

### Coverage Goals

- **Minimum**: 80% overall coverage
- **Domain Layer**: 95%+ (business logic critical)
- **Application Layer**: 90%+
- **Infrastructure Layer**: 80%+

### Performance Targets

- **Unit tests**: < 10ms per test
- **Integration tests**: < 100ms per test
- **Full test suite**: < 30 seconds

Run `pytest tests/backend/ --durations=10` to see slowest tests.