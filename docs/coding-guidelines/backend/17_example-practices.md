# 17. Example Practices

This section provides **practical examples** of recommended practices and common pitfalls to avoid in Python + FastAPI backend development. It includes **concrete code examples**, **pre-PR self-review checklist**, and **common anti-patterns** to help maintain code quality and consistency.

The examples follow the established **Clean Architecture** patterns and tech stack: Python 3.13, FastAPI, Firebase Auth, DynamoDB, and S3.


## 1. Clean Architecture Do's and Don'ts

### ✅ DO: Proper Layer Separation

```python
# Good: Domain layer - pure business logic
# domain/entities/user.py
@dataclass
class User:
    """User domain entity."""
    id: str
    email: str
    name: str
    created_at: datetime
    
    def update_email(self, new_email: str) -> None:
        """Update user email with validation."""
        if not self._is_valid_email(new_email):
            raise InvalidEmailError(f"Invalid email: {new_email}")
        self.email = new_email
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format."""
        return "@" in email and "." in email.split("@")[1]

# Good: Application layer - use cases
# application/services/user_service.py
class UserService:
    """User application service."""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def create_user(self, request: CreateUserRequest) -> User:
        """Create new user use case."""
        # Check if user exists
        existing_user = await self.user_repository.get_by_email(request.email)
        if existing_user:
            raise UserAlreadyExistsError(request.email)
        
        # Create domain entity
        user = User(
            id=generate_id(),
            email=request.email,
            name=request.name,
            created_at=datetime.utcnow()
        )
        
        # Save through repository
        return await self.user_repository.save(user)

# Good: Infrastructure layer - external concerns
# infra/repositories/user_repository.py
class DynamoDBUserRepository(UserRepository):
    """DynamoDB implementation of user repository."""
    
    def __init__(self, table_name: str):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)
    
    async def save(self, user: User) -> User:
        """Save user to DynamoDB."""
        self.table.put_item(
            Item={
                'pk': f'user#{user.id}',
                'sk': 'profile',
                'user_id': user.id,
                'email': user.email,
                'name': user.name,
                'created_at': user.created_at.isoformat()
            }
        )
        return user

# Good: API layer - transport concerns
# api/routes/users.py
@router.post("/users", response_model=UserResponse)
async def create_user(
    request: CreateUserRequest,
    user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Create new user endpoint."""
    user = await user_service.create_user(request)
    return UserResponse.from_domain(user)
```

### ❌ DON'T: Mix Layer Concerns

```python
# Bad: Domain entity with infrastructure concerns
class User:
    def __init__(self, id: str, email: str):
        self.id = id
        self.email = email
        # DON'T: Database logic in domain
        self.dynamodb = boto3.resource('dynamodb')
    
    def save(self):
        # DON'T: Infrastructure in domain layer
        self.dynamodb.Table('users').put_item(Item=self.__dict__)

# Bad: API layer with business logic
@router.post("/users")
async def create_user(request: CreateUserRequest):
    # DON'T: Business logic in API layer
    if await check_user_exists(request.email):
        raise HTTPException(400, "User exists")
    
    # DON'T: Direct database access from API
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('users')
    table.put_item(Item=request.dict())

# Bad: Repository with business logic
class UserRepository:
    async def create_user(self, email: str, name: str):
        # DON'T: Business rules in repository
        if len(name) < 2:
            raise ValueError("Name too short")
        
        # DON'T: Email validation in repository
        if "@" not in email:
            raise ValueError("Invalid email")
```

## 2. FastAPI Do's and Don'ts

### ✅ DO: Proper FastAPI Patterns

```python
# Good: Use Pydantic models for validation
class CreateUserRequest(BaseModel):
    """Request model for user creation."""
    email: EmailStr = Field(..., description="User email address")
    name: str = Field(..., min_length=2, max_length=100, description="User full name")
    age: Optional[int] = Field(None, ge=0, le=120, description="User age")

class UserResponse(BaseModel):
    """Response model for user data."""
    id: str
    email: str
    name: str
    created_at: datetime
    
    @classmethod
    def from_domain(cls, user: User) -> 'UserResponse':
        """Convert domain entity to response model."""
        return cls(
            id=user.id,
            email=user.email,
            name=user.name,
            created_at=user.created_at
        )

# Good: Use dependency injection
async def get_user_service() -> UserService:
    """Get user service dependency."""
    repository = DynamoDBUserRepository(settings.dynamodb_table)
    return UserService(repository)

@router.get("/users/{user_id}")
async def get_user(
    user_id: str = Path(..., description="User ID"),
    user_service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_current_user)
) -> UserResponse:
    """Get user by ID."""
    user = await user_service.get_by_id(user_id)
    return UserResponse.from_domain(user)

# Good: Proper error handling
@router.post("/users")
async def create_user(
    request: CreateUserRequest,
    user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Create new user."""
    try:
        user = await user_service.create_user(request)
        return UserResponse.from_domain(user)
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=409,
            detail=f"User already exists: {e.email}"
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=422,
            detail=f"Validation error: {e.message}"
        )
```

### ❌ DON'T: FastAPI Anti-patterns

```python
# Bad: No input validation
@router.post("/users")
async def create_user(email: str, name: str):  # DON'T: Use raw types
    # No validation, type checking, or documentation
    pass

# Bad: Manual dependency management
@router.get("/users/{user_id}")
async def get_user(user_id: str):
    # DON'T: Create dependencies manually
    dynamodb = boto3.resource('dynamodb')
    repository = UserRepository(dynamodb)
    service = UserService(repository)
    return await service.get_by_id(user_id)

# Bad: Generic error responses
@router.post("/users")
async def create_user(request: CreateUserRequest):
    try:
        # Logic here
        pass
    except Exception as e:
        # DON'T: Generic error handling
        raise HTTPException(500, "Something went wrong")

# Bad: No response models
@router.get("/users/{user_id}")
async def get_user(user_id: str):
    user = await get_user_from_db(user_id)
    # DON'T: Return raw dictionaries
    return {
        "id": user.id,
        "email": user.email,
        # Inconsistent field names and types
    }
```

## 3. Database/DynamoDB Do's and Don'ts

### ✅ DO: Proper DynamoDB Patterns

```python
# Good: Single-table design with proper keys
class DynamoDBUserRepository:
    """DynamoDB user repository with single-table design."""
    
    async def save(self, user: User) -> User:
        """Save user with proper key structure."""
        item = {
            'pk': f'user#{user.id}',           # Partition key
            'sk': 'profile',                   # Sort key
            'gsi1pk': f'email#{user.email}',   # GSI for email lookup
            'gsi1sk': f'user#{user.id}',
            'entity_type': 'user',
            'user_id': user.id,
            'email': user.email,
            'name': user.name,
            'created_at': user.created_at.isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        self.table.put_item(Item=item)
        return user
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email using GSI."""
        response = self.table.query(
            IndexName='GSI1',
            KeyConditionExpression=Key('gsi1pk').eq(f'email#{email}')
        )
        
        items = response.get('Items', [])
        if not items:
            return None
            
        return self._item_to_user(items[0])

# Good: Proper error handling
async def get_by_id(self, user_id: str) -> Optional[User]:
    """Get user by ID with error handling."""
    try:
        response = self.table.get_item(
            Key={'pk': f'user#{user_id}', 'sk': 'profile'}
        )
        
        if 'Item' not in response:
            return None
            
        return self._item_to_user(response['Item'])
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceNotFoundException':
            logger.warning(f"Table not found: {self.table.name}")
            raise InfrastructureError("Database table not available")
        else:
            logger.error(f"DynamoDB error: {e}")
            raise InfrastructureError("Database operation failed")

# Good: Use batching for multiple operations
async def save_multiple(self, users: List[User]) -> List[User]:
    """Save multiple users using batch operations."""
    with self.table.batch_writer() as batch:
        for user in users:
            item = self._user_to_item(user)
            batch.put_item(Item=item)
    
    return users
```

### ❌ DON'T: DynamoDB Anti-patterns

*Complete DynamoDB patterns are covered in [16_data-modeling.md](./16_data-modeling.md).*

**Common mistakes to avoid:**
- Multiple tables instead of single-table design
- Scanning entire tables instead of using proper key design
- No error handling for DynamoDB operations
- Individual requests in loops instead of batch operations
- Ignoring GSI design for alternative access patterns

## 4. Authentication & Security Do's and Don'ts

### ✅ DO: Proper Firebase Auth Integration

*Complete Firebase Auth integration patterns are covered in [09_infrastructure.md](./09_infrastructure.md).*

**Key principles:**
- Use Firebase Admin SDK for token verification
- Implement proper error handling for different token errors
- Use FastAPI Security dependencies for authentication
- Implement role-based access control where needed

### ❌ DON'T: Security Anti-patterns

**Avoid these security mistakes:**
- Trusting client-provided user information without verification
- Logging sensitive information like passwords or tokens
- No input validation on user-provided data
- Exposing internal error details to clients
- Missing authentication on protected endpoints

## 5. Testing Do's and Don'ts

### ✅ DO: Proper Testing Patterns

*Comprehensive testing patterns are covered in [13_testing.md](./13_testing.md). Follow the test pyramid approach with unit, integration, and E2E tests.*

**Key principles:**
- Unit tests for domain logic without external dependencies
- Integration tests for adapter boundaries with mocking
- E2E tests for critical user workflows
- Use fixtures and factories for test data

### ❌ DON'T: Testing Anti-patterns

**Avoid these common mistakes:**
- Testing implementation details instead of behavior
- Large, unfocused tests that test multiple concerns
- Sharing state between tests
- Making real external service calls in tests

## 6. Error Handling Do's and Don'ts

*Comprehensive error handling patterns are covered in [10_error-logging.md](./10_error-logging.md).*

### ✅ DO: Proper Error Handling

**Key principles:**
- Create custom exception hierarchies for domain errors
- Handle errors appropriately at each layer
- Provide structured error responses with proper HTTP status codes
- Log errors with sufficient context for debugging
- Don't expose internal implementation details

### ❌ DON'T: Poor Error Handling

**Avoid these mistakes:**
- Using generic exceptions without context
- Swallowing exceptions silently
- Exposing internal error details to clients
- Providing unclear error messages
- No error handling for external service calls

## 7. Performance Do's and Don'ts

*Comprehensive performance guidelines are covered in [11_performance.md](./11_performance.md).*

### ✅ DO: Efficient Patterns

**Key principles:**
- Use async/await for I/O operations and run them concurrently
- Implement caching for expensive calculations
- Use generators and batching for large datasets
- Design database queries and indexes efficiently
- Implement proper pagination

### ❌ DON'T: Performance Anti-patterns

**Avoid these mistakes:**
- Synchronous I/O in async contexts
- N+1 query problems (querying in loops)
- Loading unnecessary data from databases
- No pagination for large result sets
- Blocking the event loop with CPU-intensive tasks

## 8. Pre-PR Self-Review Checklist

### Code Quality Checklist

```markdown
## Architecture & Design
- [ ] Code follows Clean Architecture layer separation
- [ ] Dependencies point inward (dependency inversion)
- [ ] Single responsibility principle followed
- [ ] No business logic in API or infrastructure layers
- [ ] Proper use of dependency injection

## Code Style & Standards
- [ ] Code formatted with Ruff
- [ ] Imports organized correctly
- [ ] Naming conventions followed (snake_case, PascalCase)
- [ ] Functions under 25 lines
- [ ] Classes focused on single responsibility

## Type Safety & Documentation
- [ ] Type hints used for all public functions
- [ ] Docstrings added for public functions and classes
- [ ] Complex types have aliases or are well-documented
- [ ] Optional used for nullable values

## Error Handling
- [ ] Custom exceptions used where appropriate
- [ ] Proper error handling in all layers
- [ ] No generic exceptions or bare except clauses
- [ ] Error messages are helpful and don't expose internals

## Testing
- [ ] Unit tests for business logic
- [ ] Integration tests for repositories/external services
- [ ] Test coverage meets standards (>80%)
- [ ] Tests are focused and test behavior, not implementation

## Security
- [ ] No hardcoded secrets or credentials
- [ ] Input validation implemented
- [ ] Authentication/authorization properly applied
- [ ] No sensitive data in logs

## Performance
- [ ] Async/await used for I/O operations
- [ ] No N+1 query problems
- [ ] Proper use of caching where beneficial
- [ ] Database queries optimized

## Configuration & Environment
- [ ] Environment-specific configurations used
- [ ] No hardcoded values that should be configurable
- [ ] Proper use of Pydantic Settings

## Database (DynamoDB)
- [ ] Single-table design followed
- [ ] Proper partition and sort key design
- [ ] GSIs used appropriately
- [ ] Batch operations used for multiple items
```

### Common Anti-patterns to Avoid

```python
# ❌ Mixing concerns
class UserService:
    def create_user(self, user_data):
        # DON'T: Mix database logic with business logic
        user = User(**user_data)
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('users')
        table.put_item(Item=user.__dict__)

# ❌ Tight coupling
class OrderService:
    def __init__(self):
        # DON'T: Create dependencies directly
        self.user_repo = DynamoDBUserRepository()
        self.email_service = SendGridEmailService()

# ❌ No error handling
async def get_user(user_id: str):
    # DON'T: Ignore potential errors
    user = await user_repository.get(user_id)
    return user.email  # Will crash if user is None

# ❌ Exposing implementation details
@router.get("/users/{user_id}")
async def get_user(user_id: str):
    try:
        return await user_service.get(user_id)
    except Exception as e:
        # DON'T: Expose internal details
        raise HTTPException(500, f"DynamoDB error: {str(e)}")

# ❌ No input validation
@router.post("/users")
async def create_user(email: str, name: str):
    # DON'T: Skip validation
    user = User(id=generate_id(), email=email, name=name)
    return await user_service.create(user)
```

## 9. Code Review Guidelines

### What to Look For

```python
# ✅ Good: Clear, testable, maintainable
class UserService:
    """Service for user operations."""
    
    def __init__(self, repository: UserRepository, validator: UserValidator):
        self.repository = repository
        self.validator = validator
    
    async def create_user(self, request: CreateUserRequest) -> User:
        """Create new user with validation."""
        await self.validator.validate_create_request(request)
        
        existing_user = await self.repository.get_by_email(request.email)
        if existing_user:
            raise UserAlreadyExistsError(request.email)
        
        user = User(
            id=generate_id(),
            email=request.email,
            name=request.name,
            created_at=datetime.utcnow()
        )
        
        return await self.repository.save(user)

# Comments you might make in review:
# ✅ "Good separation of concerns"
# ✅ "Clear error handling"
# ✅ "Proper dependency injection"
# ✅ "Good use of domain exceptions"
```

### Review Feedback Examples

```python
# Constructive feedback examples:

# Style feedback
"Consider using snake_case for variable names (user_id instead of userId)"
"Add docstring to explain what this function does"
"This function is getting complex - consider breaking it down"

# Design feedback  
"This looks like business logic - should it be in the domain layer instead?"
"Consider using dependency injection here instead of creating the service directly"
"This exception is too generic - consider creating a specific domain exception"

# Performance feedback
"This query could cause an N+1 problem - consider batching"
"Consider caching this expensive calculation"
"This endpoint might need pagination for large datasets"

# Security feedback
"This input should be validated before processing"
"Consider adding authentication to this endpoint"
"This error message exposes too much internal detail"
```

## 10. Quick Reference

### Daily Development Checklist

```bash
# Before committing
make format                    # Format code
make lint                      # Check linting
make type-check               # Type checking
make test                     # Run tests
make quality-check            # All quality checks

# Code review checklist
- Architecture follows Clean Architecture
- Proper error handling implemented
- Tests cover new functionality
- Documentation updated
- Security considerations addressed
```

### Common Commands

```bash
# Code quality
uv run ruff format .          # Format code
uv run ruff check .           # Lint code
uv run pytest tests/         # Run tests
uv run mypy .                # Type check

# Testing
pytest tests/unit/           # Unit tests only
pytest tests/integration/    # Integration tests
pytest --cov=src            # With coverage
```

**Rules:**

* Follow the established patterns consistently
* Review code for architecture, style, and quality
* Test thoroughly before submitting PRs
* Keep security and performance in mind
* Use the checklist for self-review before requesting review