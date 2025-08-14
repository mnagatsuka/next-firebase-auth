# 2. Project Setup & Tooling

This section describes how to initialize and configure a **Python + FastAPI** project using **Clean Architecture** principles with our standard tooling and libraries.

It covers **project initialization**, **dependency management with uv**, **code quality tools**, **FastAPI configuration**, **Docker setup**, and **environment variable management** to ensure consistency across all development environments.


## 1. Project Initialization

We use **uv** as the package manager for its speed, reliability, and modern Python project management capabilities.

```bash
# From the project root directory
# Create virtual environment at project root
uv venv

# Activate the virtual environment
source .venv/bin/activate  # On Unix/macOS
# .venv\Scripts\activate     # On Windows

# Navigate to backend directory for development
cd backend
```

**Rules:**

* Always use `uv` (`uv add`, `uv remove`, `uv sync`)  do **not** use `pip` or `conda`.
* Pin exact versions for critical dependencies in production.
* Use `uv add --dev` for development-only dependencies.


## 2. Project Configuration (`pyproject.toml`)

We use `pyproject.toml` as the single source of truth for project configuration.

Example `pyproject.toml`:

```toml
[project]
name = "my-backend-project"
version = "0.1.0"
description = "FastAPI backend with Clean Architecture"
authors = [{name = "Your Name", email = "your.email@example.com"}]
requires-python = ">=3.13"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "boto3>=1.34.0",
    "firebase-admin>=6.4.0",
    "python-multipart>=0.0.6",
]

[project.optional-dependencies]
dev = [
    "ruff>=0.1.8",
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "httpx>=0.25.0",
    "localstack>=3.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
target-version = "py313"
line-length = 100
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "B",  # flake8-bugbear
    "C4", # flake8-comprehensions
    "UP", # pyupgrade
]
ignore = [
    "E501",  # line too long, handled by formatter
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false

[tool.ruff.isort]
known-first-party = ["app"]

[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q --strict-markers --strict-config"
testpaths = ["tests/backend"]
pythonpath = ["backend/src"]
asyncio_mode = "auto"
```

**Rules:**

* Use semantic versioning for project version.
* Pin minimum versions for security-critical dependencies.
* Separate dev dependencies from runtime dependencies.


## 3. Code Quality Tools (Ruff)

We use **[Ruff](https://docs.astral.sh/ruff/)** as our primary linter and formatter for its speed and comprehensive rule coverage.

Install and configure Ruff:

```bash
# Add Ruff as a dev dependency
uv add --dev ruff
```

**Rules:**

* Run `ruff check .` for linting before committing.
* Run `ruff format .` for code formatting.
* Use `ruff check --fix .` to auto-fix issues where possible.


## 4. Optional Type Checking

We recommend **pyright** or **mypy** for static type checking.

```bash
# Add type checker as dev dependency
uv add --dev pyright
# OR
uv add --dev mypy
```

Example `pyrightconfig.json` (place at project root):

```json
{
  "include": ["backend/src"],
  "exclude": ["**/__pycache__", "tests"],
  "venvPath": ".",
  "venv": ".venv",
  "pythonVersion": "3.13",
  "typeCheckingMode": "strict",
  "useLibraryCodeForTypes": true,
  "reportMissingImports": true,
  "reportMissingTypeStubs": false
}
```

**Rules:**

* Use type hints for all function parameters and return values.
* Avoid `Any` type unless absolutely necessary and documented.


## 5. FastAPI Configuration

Structure your FastAPI application with proper configuration management.

Example `backend/src/app/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings

def create_app() -> FastAPI:
    settings = get_settings()
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
    )
    
    # Set up CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    return app

app = create_app()
```

**Rules:**

* Use Pydantic Settings for configuration management.
* Separate app creation logic into a factory function.
* Configure CORS, middleware, and routers explicitly.


## 6. Pre-commit Hooks (Optional)

Set up pre-commit hooks for automated code quality checks.

```bash
# Add pre-commit as dev dependency
uv add --dev pre-commit

# Create .pre-commit-config.yaml
```

Example `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.8
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

**Rules:**

* Install hooks with `pre-commit install`.
* Run `pre-commit run --all-files` to test all hooks.


## 7. Task Runner (Optional)

Use a task runner like **invoke** or **just** for common development tasks.

```bash
# Add task runner
uv add --dev invoke
```

Example `tasks.py`:

```python
from invoke import task

@task
def lint(c):
    """Run code linting"""
    c.run("ruff check .")

@task
def format(c):
    """Format code"""
    c.run("ruff format .")

@task
def test(c):
    """Run tests"""
    c.run("pytest")

@task
def dev(c):
    """Start development server"""
    c.run("uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
```

**Rules:**

* Define common tasks for development workflow.
* Use consistent task names across projects.


## 8. Docker & Docker Compose for Local Development

We use **Docker** and **Docker Compose** to standardize local development and testing environments.

Example `Dockerfile`:

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-cache

# Copy application code
COPY . .

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Example `docker-compose.yml`:

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - '8000:8000'
    volumes:
      - .:/app
    environment:
      - ENVIRONMENT=development
      - DEBUG=true
    depends_on:
      - localstack

  localstack:
    image: localstack/localstack:latest
    ports:
      - '4566:4566'
    environment:
      - SERVICES=dynamodb,s3
      - DEBUG=1
      - DATA_DIR=/tmp/localstack/data
    volumes:
      - /tmp/localstack:/tmp/localstack
      - /var/run/docker.sock:/var/run/docker.sock
```

**Rules:**

* Use multi-stage builds for production optimization.
* Mount source code as volumes for live reload in development.
* Include LocalStack for AWS service emulation.


## 9. Environment Variables

Structure environment variables following the 12-factor app methodology.

Environment files:
* `.env`  Development defaults (committed)
* `.env.local`  Local overrides (not committed)
* `.env.test`  Testing environment
* `.env.production`  Production environment

*Complete environment variable examples and configuration patterns are detailed in [04_configuration.md](./04_configuration.md).*

**Key principles:**
- Use Pydantic Settings for type-safe configuration loading
- Never commit secrets or sensitive data
- Follow the patterns established in the configuration guidelines


## 10. Directory Structure Setup

Create the recommended directory structure from project root:

```bash
# Backend source code
mkdir -p backend/src/app/{api,application,domain,infra,shared}
mkdir -p backend/src/app/api/v1

# Tests at root level, mirroring backend structure
mkdir -p tests/backend/{unit,integration,e2e}

# Project-level directories  
mkdir -p docs/specifications/api/{components/{schemas,examples,parameters,responses},paths}
mkdir -p docs/coding-guidelines/{frontend,backend}
```

**Rules:**

* Follow the Clean Architecture layer separation within `backend/src/`.
* Mirror the `backend/src/` structure in `tests/backend/`.
* Keep OpenAPI specifications in `docs/specifications/api/` with proper component organization.
* Place documentation in `docs/` at project root.


By following this setup, all developers and CI/CD pipelines share the **same baseline configuration**, ensuring consistent and predictable behavior across environments while maintaining the architectural principles of Clean Architecture and OpenAPI-first development.