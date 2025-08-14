# Performance Guidelines

## Overview

Basic performance practices for Python FastAPI applications.

## Key Principles

- Use async/await for I/O operations
- Keep database connections efficient
- Add basic caching where needed
- Monitor performance with simple metrics

## 1. Basic Async/Await Usage

Follow basic async patterns:

```python
import asyncio
import aiohttp

# ✅ Good: Use async libraries for I/O
async def fetch_data(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# ❌ Bad: Don't use sync libraries in async functions
async def fetch_data_wrong(url: str):
    import requests
    # This blocks the event loop!
    response = requests.get(url)
    return response.json()

# ✅ Good: Run multiple requests concurrently
async def fetch_multiple(urls: list[str]):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_data_with_session(session, url) for url in urls]
        return await asyncio.gather(*tasks)

async def fetch_data_with_session(session, url):
    async with session.get(url) as response:
        return await response.json()
```

**Basic Rules:**
- Use `async`/`await` for I/O operations (database, HTTP calls, file operations)
- Use async libraries (`aiohttp`, `asyncpg`) not sync ones (`requests`, `psycopg2`)
- Use `asyncio.gather()` for concurrent operations

## 2. Simple Database Connection Management

Keep database connections simple:

```python
# Basic connection setup (example with asyncpg for PostgreSQL)
import asyncpg
import asyncio

# Simple connection pool
async def create_db_pool():
    return await asyncpg.create_pool(
        "postgresql://user:pass@localhost/db",
        min_size=2,
        max_size=10,
        command_timeout=60
    )

# Use in your application
db_pool = None

async def get_db_pool():
    global db_pool
    if db_pool is None:
        db_pool = await create_db_pool()
    return db_pool

# Simple database operations
async def get_user(user_id: str):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM users WHERE id = $1", 
            user_id
        )

async def create_user(name: str, email: str):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            "INSERT INTO users (name, email) VALUES ($1, $2) RETURNING *",
            name, email
        )
```

**Simple Rules:**
- Use connection pooling with reasonable min/max sizes
- Keep connections short-lived by using `async with pool.acquire()`
- Let the library handle connection health checks

## 3. Basic Caching

Simple caching patterns for small applications:

```python
from functools import lru_cache
from typing import Optional
import asyncio

# Simple in-memory caching with functools
@lru_cache(maxsize=128)
def get_config_value(key: str) -> str:
    """Cache configuration values."""
    import os
    return os.getenv(key, '')

# Simple async cache for frequently accessed data
user_cache = {}

async def get_user_cached(user_id: str):
    """Get user with basic caching."""
    if user_id in user_cache:
        return user_cache[user_id]
    
    # Fetch from database
    user = await get_user(user_id)
    if user:
        user_cache[user_id] = user
    
    return user

def clear_user_cache(user_id: str):
    """Clear user from cache when updated."""
    user_cache.pop(user_id, None)
```

## 4. Application Startup

Simple FastAPI startup pattern:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Simple application startup and cleanup."""
    
    # Startup: Initialize connections
    await get_db_pool()  # Initialize database pool
    
    yield  # Application is running
    
    # Cleanup: Close connections
    global db_pool
    if db_pool:
        await db_pool.close()

app = FastAPI(lifespan=lifespan)
```

## 5. Simple Performance Monitoring

Basic performance tracking:

```python
import time
import logging
from fastapi import Request

logger = logging.getLogger(__name__)

# Simple timing decorator
def time_operation(operation_name: str):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = (time.time() - start_time) * 1000
                logger.info(f"{operation_name} completed in {duration:.2f}ms")
                return result
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                logger.error(f"{operation_name} failed after {duration:.2f}ms: {e}")
                raise
        return wrapper
    return decorator

# Usage example
@time_operation("user_creation")
async def create_user(name: str, email: str):
    # Your user creation logic here
    return await user_service.create_user(name, email)
```

## Best Practices Summary

### Async Programming
- Use `async`/`await` for all I/O operations (database, HTTP calls, file operations)
- Use async libraries (`aiohttp`, `asyncpg`) instead of sync ones (`requests`, `psycopg2`)
- Use `asyncio.gather()` to run multiple operations concurrently
- Don't block the event loop with CPU-intensive work

### Database Connections
- Use connection pooling with reasonable pool sizes (2-10 connections for small apps)
- Keep database connections short-lived with `async with pool.acquire()`
- Let the database library handle connection health and retries

### Simple Caching
- Use `@lru_cache` for expensive function calls that don't change often
- Add basic in-memory caching for frequently accessed data
- Clear cache entries when the underlying data changes

### Performance Monitoring
- Use simple timing decorators to measure slow operations
- Log slow requests (>1 second) for investigation
- Monitor basic metrics like request count and average response time

### When to Avoid Over-Engineering
- Don't implement circuit breakers until you actually have reliability problems
- Don't build complex batching systems unless you have proven N+1 query issues
- Don't implement multi-level caching until simple caching isn't sufficient
- Focus on profiling and measuring before optimizing

This simplified approach focuses on proven patterns that work well for small to medium applications without the complexity of enterprise-scale solutions.