# Backend Development and Testing

This backend is a Python + FastAPI service organized with a simple layered architecture. Tests live at the project root under `tests/backend/` and cover unit, integration, and e2e levels.

## Project Layout

```
backend/
├── src/app/
│   ├── api/            # FastAPI routes, dependencies, DTOs
│   ├── application/    # Use cases
│   ├── domain/         # Entities, ports (interfaces)
│   ├── infra/          # Adapters (e.g., repositories)
│   └── shared/         # Settings and shared utilities
├── pyproject.toml
└── README.md

# Tests live at repo root (not under backend/)
tests/backend/
├── unit/
├── integration/
└── e2e/
```

## Environment Setup

- Use a single virtual env at the repo root (`.venv`).
- Manage dependencies with `uv`.

```bash
# From repository root
uv venv && source .venv/bin/activate

# Install backend dependencies (including dev/test)
cd backend
uv sync --active --extra dev
```

## Running Tests

You can run tests from the repo root or from `backend/`. Because tests live at `tests/backend/`, prefer these commands:

- From repo root (loads backend pytest config):
```bash
uv run --active pytest -c backend/pyproject.toml tests/backend -q
```

- Or from backend directory:
```bash
cd backend
uv run --active pytest ../tests/backend -q
```

### Run Specific Suites

- Unit tests only:
```bash
uv run --active pytest -c backend/pyproject.toml tests/backend/unit -q
```

- Integration tests only:
```bash
uv run --active pytest -c backend/pyproject.toml tests/backend/integration -q
```

- E2E tests only:
```bash
uv run --active pytest -c backend/pyproject.toml tests/backend/e2e -q
```

### Target a Single Test File or Test

```bash
# Single file
uv run --active pytest -c backend/pyproject.toml tests/backend/integration/test_posts_api.py -q

# By node id (class/test function)
uv run --active pytest -c backend/pyproject.toml tests/backend/integration/test_posts_api.py::test_get_single_post_by_id -q

# By keyword
uv run --active pytest -c backend/pyproject.toml -k "posts and not e2e" tests/backend -q
```

### Coverage (Optional)

```bash
uv run --active pytest -c backend/pyproject.toml \
  --cov=backend/src/app --cov-report=term-missing tests/backend
```

## Running the API Locally

```bash
# Ensure root .venv is active and deps are synced (see setup above)
uv run --active uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Quick checks
curl http://localhost:8000/health
curl "http://localhost:8000/posts?page=1&limit=10"
```

## Local AWS (LocalStack) Setup

Local development can use LocalStack to emulate DynamoDB. Repositories can switch between in-memory and DynamoDB via env.

1) Copy the example env and adjust as needed
```bash
cp backend/.env.local.example backend/.env.local
# optional: set APP_REPOSITORY_PROVIDER=memory to keep in-memory repos
```

2) Start services with Docker Compose (from repo root)
```bash
# Recommended: pass env file so table names & provider are injected
docker compose --env-file backend/.env.local up -d
```

This mounts `scripts/localstack-init.sh` which creates DynamoDB tables (`dev_posts`, `dev_comments`).

3) Use DynamoDB repositories
```bash
# In backend/.env.local, set (example):
APP_REPOSITORY_PROVIDER=dynamodb
APP_DYNAMODB_TABLE_POSTS=dev_posts
APP_DYNAMODB_TABLE_COMMENTS=dev_comments
```

4) Seed sample data
```bash
docker compose exec backend uv run python scripts/seed_data.py
```

5) Hit endpoints and verify persistence across restarts
```bash
curl "http://localhost:8000/posts?page=1&limit=10"
```

Notes
- Default remains in-memory to keep unit tests and CI fast.
- DynamoDB queries use Scan + FilterExpression for simplicity in local dev.

## Docker Scripts (pnpm)

Use package.json scripts to manage the stack with `.env.local` automatically:

```bash
# Start services with backend/.env.local
pnpm dc:up

# Rebuild images and start
pnpm dc:up:rebuild

# Stop services
pnpm dc:down

# Show status
pnpm dc:ps

# Tail logs
pnpm dc:logs:backend
pnpm dc:logs:localstack

# Seed DynamoDB through backend container
pnpm dc:seed
```

## Troubleshooting

- "Failed to spawn: pytest": install dev deps first: `cd backend && uv sync --active --extra dev`.
- Imports fail when running from root: include backend config with `-c backend/pyproject.toml` (sets `pythonpath=backend/src`).
- Multiple virtual envs: remove `backend/.venv` and use the root env: `rm -rf backend/.venv`.
