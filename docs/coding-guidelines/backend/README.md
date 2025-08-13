# Python + FastAPI Backend Coding Guidelines

This document is the table of contents for backend coding rules and best practices. Each section links to a dedicated file with detailed rules, patterns, and examples. It is intended for developers and AI-based tools to ensure quality, maintainability, and consistency.

## 1. Introduction & Scope

- [01_introduction.md](./01_introduction.md)
- Purpose, goals, and audience
- Supported versions and assumptions (Python 3.13, FastAPI, ASGI, AWS Lambda Web Adapter, Firebase Auth, DynamoDB, S3)
- Architectural principles: OpenAPI-first, Clean Architecture, hexagonal ports/adapters
- Non-goals and out-of-scope items

## 2. Project Setup & Tooling

- [02_project-setup.md](./02_project-setup.md)
- uv for environments/locking; `pyproject.toml` layout
- Ruff for lint/format; baseline rules
- Optional: pyright/mypy; pre-commit hooks; task runner

## 3. Directory Structure & Module Boundaries

- [03_structure.md](./03_structure.md)
- Layers and boundaries:

  - `api/` (transport layer: FastAPI routers, request/response mappers)
  - `application/` (use cases/services, orchestrations, ports)
  - `domain/` (entities, value objects, domain services, domain events)
  - `infra/` (adapters: DynamoDB repos, S3 gateways, outbound HTTP clients, Firebase verification)
  - `shared/` (cross-cutting: config, errors, logging, time, ULID/UUID)
- Mirrored `tests/` tree: `tests/unit`, `tests/integration`, `tests/e2e`
- Where to place routers, schemas (DTO), services, repositories, adapters

## 4. Configuration & Environments

- [04_configuration.md](./04_configuration.md)
- Typed settings with Pydantic Settings; precedence and safe defaults
- Environment separation (local, dev, staging, prod)
- Secrets handling, feature flags, operational toggles

## 5. API Design & Versioning (Transport Layer)

- [05_api-design.md](./05_api-design.md)
- Resource-first URLs, HTTP methods, idempotency patterns
- Versioning strategy (`/v1` paths vs. header-based), deprecation flow
- Pagination (cursor tokens), filtering, sorting, partial responses (fields)
- Error model (RFC7807 Problem Details) and correlation IDs
- OpenAPI docs curation and live examples

## 6. Schemas, Validation, and Mapping

- [06_schemas-validation.md](./06_schemas-validation.md)
- OpenAPI schemas vs. Pydantic DTOs; separation from domain models
- Field naming, timestamps, ID formats (ULID/UUID), enums
- Validation rules, custom validators, normalized error messages
- PATCH semantics (merge vs. JSON Patch) and partial DTOs
- Mapping: DTO ⇄ domain (anti-corruption mapping layer)

## 7. Domain Layer Guidelines

- [07_domain.md](./07_domain.md)
- Entities, value objects, invariants, domain services
- Domain events and transaction boundaries
- Pure functions, side-effect isolation, time/ID providers

## 8. Application Layer (Use Cases)

- [08_application.md](./08_application.md)
- Use case orchestration, ports (in/out), input/output models
- Transaction scripts vs. domain services: when to use which
- Idempotency and deduplication strategies at the use-case level

## 9. Infrastructure Layer (Adapters & Data Access)

- [09_infrastructure.md](./09_infrastructure.md)
- Repositories for DynamoDB (single-table or per-aggregate), conditional writes for exactly-once
- S3 adapters (content addresses, media types, presigned URLs)
- Outbound HTTP adapters (timeouts, retries with jitter, backoff)
- Firebase Auth verification adapter (token verification, caching)
- Configuration of AWS SDK clients, connection reuse

## 10. Error Handling & Logging

  - [10_error-logging.md](./10_error-logging.md)
- Exception taxonomy and translation to HTTP Problem Details
- Structured logging, correlation/trace IDs, redaction policy
- Retry-safe operations, idempotency keys, poison message handling

## 11. Performance & Concurrency

- [11_performance.md](./11_performance.md)
- Async rules (never block the event loop); CPU-bound isolation
- Cold start mitigation (module-level clients, lazy init)
- Batching, connection pooling, timeouts, retries; caching
- Pagination efficiency, selective projections

## 12. Local Development & Docker

- [12_local-dev.md](./12_local-dev.md)
- docker-compose for FastAPI + LocalStack (DynamoDB/S3)
- Hot reload, seed data, port mapping
- Parity guidelines between local and cloud

## 13. Testing Strategy

- [13_testing.md](./13_testing.md)
- Test pyramid; naming and layout
- Unit tests (domain/application), integration (adapters), e2e (API)
- Fixtures, factories, time/ID fakes
- LocalStack for AWS services; contract tests from OpenAPI examples

## 14. Deployment & Operations

- [14_cicd-deploy.md](./14_cicd-deploy.md)
- CI gates: lint/format/type-check/tests/contract checks
- SAM build/deploy; per-env workflows; artifact/image caching
- Lambda Web Adapter configuration and tuning
- Progressive delivery, rollback, and config drift detection

## 15. Coding Standards & Style

- [15_coding-standards.md](./15_coding-standards.md)
- Ruff ruleset, import order, naming conventions
- Type hints policy (strict where valuable), docstrings
- Function/class size limits and complexity thresholds

## 16. Data Modeling & Migrations (NoSQL)

- [16_data-modeling.md](./16_data-modeling.md)
- DynamoDB single-table patterns (PK/SK, GSIs, entity composition)
- Item versioning and optimistic concurrency control

## 17. Do's and Don'ts Checklist

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
