# 3. Directory Structure & Module Boundaries

This section defines the **directory structure** and **module organization** for Python + FastAPI projects using **Clean Architecture** principles with **hexagonal ports/adapters** pattern.

Our goals are:
- Maintain clear separation of concerns across architectural layers
- Enforce dependency direction (inward dependencies only)
- Enable testability and maintainability through proper boundaries
- Follow Clean Architecture and Domain-Driven Design principles


## 1. Overall Project Structure

```
project-root/
├── backend/
│   ├── src/
│   │   └── app/
│   │       ├── api/           # Transport Layer (FastAPI routers, request/response mappers)
│   │       ├── application/   # Use Cases/Services, Orchestrations, Ports (interfaces)
│   │       ├── domain/        # Entities, Value Objects, Domain Services, Domain Events
│   │       ├── infra/         # Adapters: DynamoDB repos, S3 gateways, HTTP clients, Firebase verification
│   │       └── shared/        # Cross-cutting: config, errors, logging, time, ULID/UUID
│   ├── pyproject.toml
│   └── .env
├── tests/
│   └── backend/
│       ├── unit/              # Domain & Application tests
│       ├── integration/       # Infrastructure adapter tests
│       └── e2e/              # End-to-end API tests
├── docs/
│   └── specifications/
│       └── api/              # OpenAPI specifications
└── .venv/
```


## 2. Layer Structure Details

### API Layer (`backend/src/app/api/`)
```
api/
├── __init__.py
├── router.py              # Main API router
├── dependencies.py        # FastAPI dependencies
├── middleware.py          # Custom middleware
└── v1/
    ├── __init__.py
    ├── posts.py          # Posts endpoints
    ├── comments.py       # Comments endpoints
    └── auth.py           # Authentication endpoints
```

### Application Layer (`backend/src/app/application/`)
```
application/
├── __init__.py
├── ports/                 # Interfaces/Protocols
│   ├── __init__.py
│   ├── repositories.py    # Repository interfaces
│   ├── services.py        # External service interfaces
│   └── events.py         # Event publisher interfaces
├── use_cases/            # Application services
│   ├── __init__.py
│   ├── create_post.py    # Use case implementations
│   └── get_posts.py      
├── dto/                  # Data Transfer Objects
│   ├── __init__.py
│   └── posts.py         
└── exceptions.py         # Application-specific exceptions
```

### Domain Layer (`backend/src/app/domain/`)
```
domain/
├── __init__.py
├── entities/             # Domain entities
│   ├── __init__.py
│   ├── post.py          
│   └── comment.py       
├── value_objects/        # Value objects
│   ├── __init__.py
│   ├── post_id.py       
│   └── email.py         
├── services/            # Domain services
│   ├── __init__.py
│   └── post_service.py  
├── events/              # Domain events
│   ├── __init__.py
│   └── post_created.py  
└── exceptions.py        # Domain-specific exceptions
```

### Infrastructure Layer (`backend/src/app/infra/`)
```
infra/
├── __init__.py
├── repositories/         # Data access implementations
│   ├── __init__.py
│   └── dynamodb_posts.py 
├── services/            # External service adapters
│   ├── __init__.py
│   ├── firebase_auth.py 
│   └── s3_storage.py    
├── clients/             # HTTP clients for external APIs
│   ├── __init__.py
│   └── analytics_client.py 
└── config/              # Infrastructure configuration
    ├── __init__.py
    └── aws.py          
```

### Shared Layer (`backend/src/app/shared/`)
```
shared/
├── __init__.py
├── config/              # Application configuration
│   ├── __init__.py
│   └── settings.py      # Pydantic settings
├── exceptions/          # Common exception types
│   ├── __init__.py
│   └── base.py         
├── utils/               # Utility functions
│   ├── __init__.py
│   ├── time.py         # Time utilities
│   └── ids.py          # ID generation (ULID/UUID)
└── constants.py         # Application constants
```


## 3. Test Structure (`tests/backend/`)

Tests mirror the source structure:

```
tests/backend/
├── unit/                # Fast, isolated tests
│   ├── domain/         # Domain logic tests
│   └── application/    # Use case tests
├── integration/        # Tests with real adapters
│   └── infra/         # Repository and service tests
├── e2e/               # End-to-end API tests
│   └── api/
│       └── v1/
├── fixtures/          # Test data and factories
└── conftest.py       # Pytest configuration
```


## 4. Module Placement Guidelines

### Where to Place Different Components

- **Routers**: `api/v1/` - Group by domain/resource
- **Schemas (DTOs)**: 
  - API DTOs: `api/v1/` (co-located with routers)
  - Application DTOs: `application/dto/`
- **Services**: 
  - Use cases: `application/use_cases/`
  - Domain services: `domain/services/`
- **Repositories**: 
  - Interfaces: `application/ports/`
  - Implementations: `infra/repositories/`
- **Adapters**: `infra/services/` and `infra/clients/`


## 5. Dependency Direction Rules

Dependencies must flow inward only:

```
API → Application → Domain
 ↓         ↓
Infrastructure → Application (via interfaces)
```

**Allowed:**
- `api` → `application`, `shared`
- `application` → `domain`, `shared`
- `domain` → `shared` (minimal)
- `infra` → `application` (interfaces), `domain`, `shared`

**Forbidden:**
- `domain` → `application`, `api`, `infra`
- `application` → `api`, `infra` (except interfaces)
- Any circular dependencies

**Enforcement:**
Use `import-linter` in CI to verify dependency rules automatically.


## 6. File Naming Conventions

- **Snake_case** for all Python files and directories
- **Descriptive names** that indicate purpose
- **Plural for collections** (`entities/`, `repositories/`)
- **Singular for individual concepts** (`post.py`, `user.py`)
- **Interface suffix** for protocols (`_repository.py`, `_service.py`)


By following this structure, each layer has clear responsibilities and the codebase remains maintainable and testable.