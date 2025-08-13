# 1. Introduction & Scope

This document outlines the **purpose**, **scope**, and **applicable context** for our backend coding guidelines for **Python + FastAPI** projects built with **Clean Architecture** and **OpenAPI-first** principles.

It is intended to be read before diving into the individual sections, as it explains the audience, versions, and libraries that these rules cover.


## Purpose of the Guidelines

The primary goals of these guidelines are to:

- **Ensure consistency** across the codebase, regardless of who writes the code (human developers or AI-assisted tools).
- **Improve maintainability** by standardizing patterns for architecture, structure, naming, and design.
- **Promote best practices** in performance, security, scalability, and operational excellence.
- **Facilitate collaboration** between team members by reducing friction in code reviews and onboarding.
- **Enable AI-assisted development** by providing clear, machine-readable rules.
- **Enforce architectural boundaries** through Clean Architecture and hexagonal ports/adapters patterns.

These rules are not static  they should evolve as our tech stack, project requirements, and the Python/FastAPI ecosystem grow.


## Target Audience

These guidelines apply to:

- **Human developers**  backend engineers working on our Python/FastAPI projects.
- **AI coding assistants**  tools like GitHub Copilot, ChatGPT, and similar, to help produce compliant code automatically.
- **Automated code quality tools**  linters, formatters, type checkers, and CI/CD pipelines.


## Applicable Versions

These guidelines are written for:

- **Python**: `3.13` and later
- **FastAPI**: Latest stable version with ASGI support
- **AWS Lambda Web Adapter**: For serverless deployment
- **Firebase Auth**: For authentication and authorization

The recommendations may not apply to older versions.


## Libraries & Tools in Scope

While the primary focus is **Python + FastAPI**, the following libraries and tools are part of our standard setup:

### 1. Web Framework & API
- **FastAPI**  modern, fast web framework for building APIs with Python
- **ASGI**  asynchronous server gateway interface
- **AWS Lambda Web Adapter**  serverless deployment adapter

### 2. Authentication & Security
- **Firebase Auth**  authentication with identity providers and token verification

### 3. Data Storage & AWS Services
- **DynamoDB**  NoSQL database for scalable data storage
- **S3**  object storage for media and file uploads
- **AWS SDK (boto3)**  AWS service integration

### 4. Validation & Schema Management
- **Pydantic**  data validation and settings management using Python type annotations
- **OpenAPI/Swagger**  API documentation and contract-first development

### 5. Development Tools & Environment
- **uv**  fast Python package installer and resolver for dependency management
- **Ruff**  extremely fast Python linter and formatter
- **pyproject.toml**  modern Python project configuration

### 6. Testing Framework
- **pytest**  mature full-featured Python testing tool
- **LocalStack**  local AWS cloud stack for testing

### 7. Optional Developer Experience
- **pyright/mypy**  static type checking
- **pre-commit**  git hook framework for code quality
- **task runner**  automation of common development tasks


## Architectural Principles

Our backend follows these core architectural principles:

### 1. OpenAPI-First Development
- Single source of truth in `openapi/` directory
- Contract-driven development with schema validation
- Code generation from OpenAPI specifications

### 2. Clean Architecture
- Clear separation of concerns across layers
- Dependency inversion and ports/adapters pattern
- Domain-driven design principles

### 3. Hexagonal Architecture (Ports & Adapters)
- **Domain Layer**: Pure business logic, entities, and value objects
- **Application Layer**: Use cases and orchestration
- **Infrastructure Layer**: External adapters (databases, APIs, services)
- **API Layer**: Transport layer with FastAPI routers


## Layer Structure

Our codebase is organized into distinct layers:

- **`api/`**  Transport layer: FastAPI routers, request/response mappers
- **`application/`**  Use cases/services, orchestrations, ports (interfaces)
- **`domain/`**  Entities, value objects, domain services, domain events
- **`infra/`**  Adapters: DynamoDB repos, S3 gateways, outbound HTTP clients, Firebase verification
- **`shared/`**  Cross-cutting concerns: config, errors, logging, time, ULID/UUID generation


## Out of Scope

These guidelines do **not** cover:

- Frontend development (covered in separate frontend guidelines)
- Non-Python backend frameworks
- Non-FastAPI web frameworks
- Project management and workflow conventions (e.g., Git branching)
- Infrastructure as Code (IaC) or deployment infrastructure


## Non-Goals

These guidelines explicitly do **not** aim to:

- Replace FastAPI's official documentation
- Cover every possible Python pattern or library
- Provide exhaustive AWS service configuration details
- Define business logic or domain-specific requirements


By following these guidelines, we aim to keep our backend codebase **clean, predictable, and scalable**, making it easier for both humans and AI tools to contribute effectively while maintaining architectural integrity and operational excellence.