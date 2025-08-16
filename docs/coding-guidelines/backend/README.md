# Python + FastAPI Backend Coding Guidelines

Simple coding guidelines for Python + FastAPI backend development. These guidelines focus on practical patterns suitable for small to medium applications without over-engineering.

## 1. Introduction & Scope

- [01_introduction.md](./01_introduction.md)
- Purpose, goals, and audience
- Supported versions (Python 3.13, FastAPI, Firebase Auth, DynamoDB, S3)
- Simple layered architecture principles
- Libraries and tools in scope

## 2. Project Setup & Tooling

- [02_project-setup.md](./02_project-setup.md)
- uv for package management and `pyproject.toml` configuration
- Ruff for linting and formatting
- Optional: pyright/mypy for type checking; pre-commit hooks

## 3. Directory Structure & Organization

- [03_structure.md](./03_structure.md)
- Simple layered architecture:
  - `api/` - FastAPI routes and request/response handling
  - `application/` - Application services that coordinate business logic
  - `domain/` - Business entities and domain logic
  - `infra/` - Database, external services, and infrastructure code
  - `shared/` - Configuration, utilities, and shared code
- Test structure: `tests/unit`, `tests/integration`, `tests/e2e`

## 4. Configuration & Environment Variables

- [04_configuration.md](./04_configuration.md)
- Simple configuration with Pydantic Settings
- Basic environment variable management
- Configuration validation

## 5. API Design & Best Practices

- [05_api-design.md](./05_api-design.md)
- Simple REST API design patterns
- Basic versioning when needed
- Simple pagination and filtering
- Clear error responses
- Using FastAPI's built-in documentation

## 6. Schemas & Server-Side Validation

- [06_schemas-validation.md](./06_schemas-validation.md)
- Simple Pydantic models for request/response validation
- Custom validation where needed
- Clear error handling for validation failures

## 7. Domain Layer (Business Logic)

- [07_domain.md](./07_domain.md)
- Simple domain entities using dataclasses
- Basic business logic services
- Simple domain exceptions

## 8. Application Layer (Use Cases)

- [08_application.md](./08_application.md)
- Simple application services that coordinate business logic
- Basic exception handling and conversion
- Clean separation between domain and infrastructure

## 9. Infrastructure Layer (Data Access & External Services)

- [09_infrastructure.md](./09_infrastructure.md)
- Simple repository patterns for data access
- Firebase Auth integration
- Basic HTTP clients for external services

## 10. Error Handling & Logging

- [10_error-logging.md](./10_error-logging.md)
- Simple exception handling patterns
- Basic logging setup and best practices
- Security guidelines for logging
- Simple request logging middleware

## 11. Performance Guidelines

- [11_performance.md](./11_performance.md)
- Basic async/await usage
- Simple database connection management
- Basic caching patterns
- Simple performance monitoring

## 12. Local Development & Docker

- [12_local-dev.md](./12_local-dev.md)
- docker-compose for FastAPI + LocalStack (DynamoDB/S3)
- Hot reload, seed data, port mapping

## 13. Testing Strategy

- [13_testing.md](./13_testing.md)
- Test pyramid; naming and layout
- Unit tests (domain/application), integration (adapters), e2e (API)
- Fixtures, factories, time/ID fakes
- LocalStack for AWS services; contract tests from OpenAPI examples

## 14. Deployment & Operations

- [14_cicd-deploy.md](./14_cicd-deploy.md)
- SAM build/deploy; per-env workflows; artifact/image caching
- Lambda Web Adapter configuration and tuning

## 15. Coding Standards & Style

- [15_coding-standards.md](./15_coding-standards.md)
- Ruff ruleset, import order, naming conventions
- Type hints policy (strict where valuable), docstrings
- Function/class size limits and complexity thresholds

## 16. Data Modeling & Migrations (NoSQL)

- [16_data-modeling.md](./16_data-modeling.md)
- DynamoDB single-table patterns (PK/SK, GSIs, entity composition)
- Item versioning and optimistic concurrency control

## 17. Example Practices

- [17_example-practices.md](./17_example-practices.md)
- Recommended practices
- Common pitfalls to avoid
- Pre-PR self-review list

### Notes on “layering + OpenAPI” interplay

- **OpenAPI workflow**: For full-stack OpenAPI-first development workflow, see [OpenAPI Workflow](../../development-workflow/openapi-workflow.md)
- OpenAPI schemas define transport DTOs only; domain models live in `domain/`.
- The `api/` layer maps DTOs to use-case inputs and back to DTOs for responses.
- The `application/` layer exposes ports; `infra/` supplies adapters that implement them.
- Contract tests are generated from OpenAPI examples and exercised against `api/` boundaries, not domain internals.
