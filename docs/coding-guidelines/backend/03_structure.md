# 3. Directory Structure & Organization

Simple layered architecture for Python + FastAPI applications with clear separation of concerns.

## Overview

Use a straightforward layered approach:
- API layer handles HTTP requests and responses
- Application layer coordinates business operations  
- Domain layer contains business entities and rules
- Infrastructure layer manages external dependencies
- Shared layer provides common utilities

## 1. Overall Project Structure

```
project-root/
├── backend/
│   ├── src/
│   │   └── app/
│   │       ├── api/           # FastAPI routes and request/response handling
│   │       ├── application/   # Application services (see 08_application.md)
│   │       ├── domain/        # Business entities and domain logic (see 07_domain.md)
│   │       ├── infra/         # Database, external services (see 09_infrastructure.md)
│   │       └── shared/        # Configuration, utilities, and shared code
│   ├── pyproject.toml
│   └── .env
├── tests/
│   └── backend/
│       ├── unit/              # Fast, isolated tests
│       ├── integration/       # Tests with real adapters
│       └── e2e/              # End-to-end API tests
├── docs/
└── .venv/
```

## 2. Layer Structure Details

### API Layer (`backend/src/app/api/`)
```
api/
├── __init__.py
├── main.py               # FastAPI app setup
├── dependencies.py       # FastAPI dependencies (auth, database)
├── users.py             # User endpoints
├── auth.py              # Authentication endpoints
└── health.py            # Health check endpoints
```

### Application Layer (`backend/src/app/application/`)
```
application/
├── __init__.py
├── services/            # Application services
│   ├── __init__.py
│   ├── user_service.py
│   └── auth_service.py
└── exceptions.py        # Application exceptions
```

### Domain Layer (`backend/src/app/domain/`)
```
domain/
├── __init__.py
├── entities.py          # Domain entities
├── services.py          # Business logic services
└── exceptions.py        # Domain exceptions
```

### Infrastructure Layer (`backend/src/app/infra/`)
```
infra/
├── __init__.py
├── repositories/        # Data access implementations
│   ├── __init__.py
│   ├── user_repository.py
│   └── memory_repository.py  # For testing
├── adapters/           # External service adapters
│   ├── __init__.py
│   ├── firebase_auth.py
│   ├── s3_storage.py
│   └── http_client.py
└── config.py           # Infrastructure configuration
```

### Shared Layer (`backend/src/app/shared/`)
```
shared/
├── __init__.py
├── config.py           # Application settings
├── exceptions.py       # Common exceptions
├── security.py         # Security utilities
└── utils.py           # Helper functions
```

## 3. Test Structure (`tests/backend/`)

```
tests/backend/
├── unit/               # Fast, isolated tests
│   ├── domain/         # Domain logic tests
│   └── application/    # Application service tests
├── integration/        # Tests with real adapters
│   └── infra/         # Repository and service tests
├── e2e/               # End-to-end API tests
│   └── api/           # API endpoint tests
├── fixtures/          # Test data and factories
└── conftest.py       # Pytest configuration
```

## 4. Component Placement Guidelines

**What goes where:**
- **API Routes**: `api/` directory, grouped by feature
- **Business Logic**: `application/services/` for coordination, `domain/` for core rules
- **Data Access**: `infra/repositories/` for database operations
- **External Services**: `infra/adapters/` for third-party integrations
- **Configuration**: `shared/config.py`
- **Common Utilities**: `shared/utils.py`

## 5. Simple Dependency Rules

Keep dependencies flowing in one direction:
- `api` → `application` → `domain`
- `infra` → `application` and `domain`
- `shared` ← all layers (for common utilities)

**Avoid:**
- Domain depending on infrastructure or API layers
- Circular dependencies between any layers

## 6. File Naming Conventions

- **snake_case** for all files and directories
- **Descriptive names** that indicate purpose
- **Singular for entities** (`user.py`, `post.py`)
- **Plural for collections** (`users.py` for user endpoints)

This structure keeps code organized while remaining simple enough for small to medium applications.