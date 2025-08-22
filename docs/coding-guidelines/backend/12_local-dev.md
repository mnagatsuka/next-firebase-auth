# 12. Local Development & Docker

This section covers **local development setup** for Python + FastAPI backend projects using **Docker Compose** for orchestrating services like **LocalStack** (for AWS DynamoDB/S3 emulation), **hot reload configuration**, **seed data management**, and **port mapping**.

It ensures a consistent, reproducible development environment that closely mirrors production while providing developer-friendly features like automatic code reloading and easy service management.


## 1. Docker Compose Configuration

We use Docker Compose to orchestrate local development services, including the FastAPI application and LocalStack for AWS service emulation.

### Basic docker-compose.yml Structure

```yaml
version: '3.8'

services:
  # FastAPI Backend
  backend:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    volumes:
      - .:/app
      - /app/.venv  # Exclude virtual environment from volume mount
    environment:
      - ENVIRONMENT=development
      - DATABASE_URL=http://localstack:4566
      - AWS_ENDPOINT_URL=http://localstack:4566
      - AWS_ACCESS_KEY_ID=test
      - AWS_SECRET_ACCESS_KEY=test
      - AWS_DEFAULT_REGION=ap-northeast-1
    depends_on:
      - localstack
    command: ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

  # LocalStack for AWS Services
  localstack:
    image: localstack/localstack:latest
    ports:
      - "4566:4566"  # LocalStack main endpoint
      - "4510-4559:4510-4559"  # External service port range
    environment:
      - SERVICES=dynamodb,s3
      - DEBUG=1
      - DATA_DIR=/tmp/localstack/data
      - DOCKER_HOST=unix:///var/run/docker.sock
    volumes:
      - "/tmp/localstack:/tmp/localstack"
      - "/var/run/docker.sock:/var/run/docker.sock"
      - "./scripts/localstack-init.sh:/etc/localstack/init/ready.d/init-aws.sh"
```

**Rules:**

* Use `docker-compose.yml` for local development orchestration.
* Mount source code as volumes for hot reload capability.
* Use consistent port mappings across all projects.
* Include LocalStack for AWS service emulation.


## 2. Development Dockerfile

Create a separate `Dockerfile.dev` optimized for development with hot reload capabilities.

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --dev

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Default command (can be overridden in docker-compose.yml)
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

**Rules:**

* Use separate Dockerfile for development with dev dependencies.
* Enable hot reload with `--reload` flag.
* Include debugging tools and utilities.
* Optimize for fast rebuilds with proper layer caching.


## 3. LocalStack Configuration

### Initialization Script

Create `scripts/localstack-init.sh` to set up AWS resources on LocalStack startup:

```bash
#!/bin/bash

echo "Initializing LocalStack resources..."

# Wait for LocalStack to be ready
awslocal dynamodb list-tables || sleep 5

# Create DynamoDB tables
awslocal dynamodb create-table \
    --table-name users \
    --attribute-definitions \
        AttributeName=pk,AttributeType=S \
        AttributeName=sk,AttributeType=S \
    --key-schema \
        AttributeName=pk,KeyType=HASH \
        AttributeName=sk,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST

# Create S3 buckets
awslocal s3 mb s3://dev-uploads
awslocal s3 mb s3://dev-static-assets

echo "LocalStack initialization complete!"
```

### Environment Configuration

```python
# shared/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # AWS Configuration
    aws_endpoint_url: str = "http://localhost:4566"  # LocalStack endpoint
    aws_access_key_id: str = "test"
    aws_secret_access_key: str = "test"
    aws_region: str = "ap-northeast-1"
    
    # Database
    dynamodb_table_prefix: str = "dev_"
    
    # S3
    s3_bucket_uploads: str = "dev-uploads"
    s3_bucket_static: str = "dev-static-assets"
    
    class Config:
        env_file = ".env.development"
```

**Rules:**

* Use LocalStack for all AWS service emulation in development.
* Initialize required AWS resources automatically on startup.
* Use consistent naming conventions for local resources.
* Provide seed data for development testing.


## 4. Hot Reload Configuration

### FastAPI Hot Reload Setup

*FastAPI application setup and configuration patterns are covered in [02_project-setup.md](./02_project-setup.md). Use the established patterns with development-specific CORS configuration.*

Key considerations for development:
- Enable debug mode for better error messages
- Configure CORS for frontend integration
- Use hot reload with uvicorn for faster development

### Development Scripts

Create `scripts/dev.py` for convenient development commands:

```python
#!/usr/bin/env python3
"""Development utility scripts."""

import subprocess
import sys
from pathlib import Path

def run_dev():
    """Start development server with hot reload."""
    subprocess.run([
        "uvicorn", "main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload",
        "--reload-dir", ".",
        "--reload-exclude", "*.pyc",
        "--reload-exclude", "__pycache__",
        "--reload-exclude", ".venv"
    ])

def setup_localstack():
    """Initialize LocalStack resources."""
    subprocess.run(["bash", "scripts/localstack-init.sh"])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/dev.py [run|setup]")
        sys.exit(1)
    
    command = sys.argv[1]
    if command == "run":
        run_dev()
    elif command == "setup":
        setup_localstack()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
```

**Rules:**

* Enable hot reload for all code changes during development.
* Exclude unnecessary files from reload watching.
* Provide convenient scripts for common development tasks.
* Configure CORS appropriately for local development.


## 5. Seed Data Management

### Database Seeding

Create `scripts/seed_data.py` for populating development data:

```python
#!/usr/bin/env python3
"""Seed development database with test data."""

import asyncio
import boto3
from datetime import datetime
from shared.config import get_settings

async def seed_users():
    """Seed user data for development."""
    settings = get_settings()
    
    dynamodb = boto3.resource(
        'dynamodb',
        endpoint_url=settings.aws_endpoint_url,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region
    )
    
    table = dynamodb.Table('users')
    
    # Sample users
    users = [
        {
            'pk': 'user#1',
            'sk': 'profile',
            'email': 'dev@example.com',
            'name': 'Dev User',
            'created_at': datetime.utcnow().isoformat()
        },
        {
            'pk': 'user#2',
            'sk': 'profile',
            'email': 'test@example.com',
            'name': 'Test User',
            'created_at': datetime.utcnow().isoformat()
        }
    ]
    
    for user in users:
        table.put_item(Item=user)
        print(f"Created user: {user['email']}")

async def main():
    """Run all seeding operations."""
    print("Seeding development data...")
    await seed_users()
    print("Seeding complete!")

if __name__ == "__main__":
    asyncio.run(main())
```

**Rules:**

* Provide realistic seed data for development and testing.
* Make seeding idempotent (safe to run multiple times).
* Include data for all major entities and relationships.
* Document seeded data credentials and access patterns.


## 6. Development Workflow

### Common Commands

```bash
# Start all services
docker-compose up -d

# Start with rebuild
docker-compose up --build

# View logs
docker-compose logs -f backend
docker-compose logs -f localstack

# Run commands in backend container
docker-compose exec backend uv run python scripts/seed_data.py
docker-compose exec backend uv run pytest
docker-compose exec backend uv run ruff check .

# Stop services
docker-compose down

# Clean restart
docker-compose down -v && docker-compose up --build
```

### Makefile for Convenience

```makefile
.PHONY: dev dev-build dev-down dev-clean seed test lint format

# Start development environment
dev:
	docker-compose up -d

# Start with rebuild
dev-build:
	docker-compose up --build -d

# Stop development environment
dev-down:
	docker-compose down

# Clean restart (removes volumes)
dev-clean:
	docker-compose down -v
	docker-compose up --build -d

# Seed development data
seed:
	docker-compose exec backend uv run python scripts/seed_data.py

# Run tests
test:
	docker-compose exec backend uv run pytest

# Run linting
lint:
	docker-compose exec backend uv run ruff check .

# Format code
format:
	docker-compose exec backend uv run ruff format .
```

**Rules:**

* Provide convenient commands for common development tasks.
* Use consistent naming for development scripts and commands.
* Include health checks and service dependency management.
* Document all available development commands.


## 7. Port Mapping & Service Discovery

### Standard Port Assignments

| Service | Host Port | Container Port | Purpose |
|---------|-----------|----------------|---------|
| FastAPI Backend | 8000 | 8000 | Main API |
| LocalStack | 4566 | 4566 | AWS Services |
| LocalStack Services | 4510-4559 | 4510-4559 | Service Range |

### Service URLs

```python
# Development service URLs
BACKEND_URL = "http://localhost:8000"
LOCALSTACK_URL = "http://localhost:4566"
DYNAMODB_URL = "http://localhost:4566"
S3_URL = "http://localhost:4566"
```

**Rules:**

* Use consistent port assignments across all projects.
* Document all service endpoints and their purposes.
* Provide environment-specific service discovery.
* Include health check endpoints for all services.


## 8. Environment Variables

### .env.development Template

```bash
# Environment
ENVIRONMENT=development

# AWS LocalStack
AWS_ENDPOINT_URL=http://localhost:4566
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_DEFAULT_REGION=ap-northeast-1

# Database
DYNAMODB_TABLE_PREFIX=dev_

# S3
S3_BUCKET_UPLOADS=dev-uploads
S3_BUCKET_STATIC=dev-static-assets

# API Configuration
API_DEBUG=true
API_HOST=0.0.0.0
API_PORT=8000

# Logging
LOG_LEVEL=DEBUG
```

**Rules:**

* Use `.env.development` for local development overrides.
* Never commit actual credentials to version control.
* Provide template files with placeholder values.
* Document all required environment variables.


## 9. Troubleshooting

### Common Issues

**LocalStack not starting:**
```bash
# Check Docker daemon
docker ps

# Check port conflicts
lsof -i :4566

# Restart with clean state
docker-compose down -v && docker-compose up --build
```

**Hot reload not working:**
```bash
# Check volume mounts
docker-compose exec backend ls -la /app

# Restart backend service
docker-compose restart backend
```

**Port conflicts:**
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

**Rules:**

* Document common development issues and solutions.
* Provide debugging commands for service problems.
* Include health check commands for all services.
* Maintain troubleshooting runbook for team reference.
