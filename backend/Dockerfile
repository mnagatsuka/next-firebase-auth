FROM python:3.13-slim AS base

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project config
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-cache || true

# Copy application code
COPY backend/ ./backend/

EXPOSE 8000

WORKDIR /app/backend
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

