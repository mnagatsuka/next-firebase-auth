# Performance & Concurrency Guidelines

## Overview

Python's asyncio-based FastAPI applications require careful attention to performance patterns, especially around blocking operations, connection management, and resource utilization. This document covers async best practices, cold start optimization, concurrency patterns, and performance monitoring for scalable backend services.

## Key Principles

- **Never block the event loop**: Keep all I/O operations asynchronous
- **Connection pooling**: Reuse connections and manage resource lifecycles efficiently
- **Cold start optimization**: Minimize initialization time and memory footprint
- **Batching and caching**: Reduce network calls and computation overhead
- **Graceful degradation**: Handle load gracefully with proper timeouts and limits

## Async Programming Rules

### Event Loop Best Practices

```python
import asyncio
import time
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
import functools


class AsyncRules:
    """Examples of proper async patterns."""
    
    @staticmethod
    async def good_async_io():
        """Correct: Non-blocking I/O operations."""
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.example.com/data') as response:
                return await response.json()
    
    @staticmethod
    async def bad_blocking_io():
        """WRONG: Blocking the event loop."""
        import requests
        
        # DON'T DO THIS - blocks event loop
        response = requests.get('https://api.example.com/data')
        return response.json()
    
    @staticmethod
    async def good_cpu_intensive(data: List[int]) -> int:
        """Correct: CPU-intensive work in thread pool."""
        def cpu_work(numbers):
            # Simulated CPU-intensive computation
            return sum(n * n for n in numbers)
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(executor, cpu_work, data)
        return result
    
    @staticmethod
    async def bad_cpu_intensive(data: List[int]) -> int:
        """WRONG: CPU-intensive work blocking event loop."""
        # DON'T DO THIS - blocks event loop
        return sum(n * n for n in data)
    
    @staticmethod
    async def good_concurrent_requests(urls: List[str]) -> List[Dict]:
        """Correct: Concurrent HTTP requests."""
        import aiohttp
        
        async def fetch_url(session, url):
            async with session.get(url) as response:
                return await response.json()
        
        async with aiohttp.ClientSession() as session:
            tasks = [fetch_url(session, url) for url in urls]
            return await asyncio.gather(*tasks)
    
    @staticmethod
    async def bad_sequential_requests(urls: List[str]) -> List[Dict]:
        """WRONG: Sequential HTTP requests (inefficient)."""
        import aiohttp
        results = []
        
        async with aiohttp.ClientSession() as session:
            for url in urls:
                async with session.get(url) as response:
                    results.append(await response.json())
        return results


# Utility for making sync functions async-safe
def run_in_executor(executor=None):
    """Decorator to run sync functions in thread pool."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            loop = asyncio.get_event_loop()
            bound_func = functools.partial(func, *args, **kwargs)
            return await loop.run_in_executor(executor, bound_func)
        return wrapper
    return decorator


# Example usage
@run_in_executor()
def expensive_computation(data: bytes) -> str:
    """CPU-intensive function that's now async-safe."""
    import hashlib
    return hashlib.sha256(data).hexdigest()
```

### Database Connection Management

```python
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
import asyncio
import time
from dataclasses import dataclass


@dataclass
class ConnectionPoolConfig:
    """Connection pool configuration."""
    min_size: int = 5
    max_size: int = 20
    max_inactive_time: int = 300  # 5 minutes
    max_queries: int = 50000  # Max queries per connection
    acquire_timeout: int = 30
    query_timeout: int = 60


class AsyncConnectionPool:
    """Efficient async connection pool implementation."""
    
    def __init__(self, config: ConnectionPoolConfig, connection_factory):
        self.config = config
        self.connection_factory = connection_factory
        self._pool: asyncio.Queue = None
        self._created_connections = 0
        self._lock = asyncio.Lock()
        self._closed = False
    
    async def initialize(self):
        """Initialize connection pool."""
        self._pool = asyncio.Queue(maxsize=self.config.max_size)
        
        # Pre-create minimum connections
        for _ in range(self.config.min_size):
            conn = await self._create_connection()
            await self._pool.put(conn)
    
    @asynccontextmanager
    async def acquire(self) -> AsyncGenerator:
        """Acquire connection from pool."""
        if self._closed:
            raise RuntimeError("Connection pool is closed")
        
        try:
            # Try to get connection with timeout
            conn = await asyncio.wait_for(
                self._pool.get(),
                timeout=self.config.acquire_timeout
            )
            
            # Check if connection is still healthy
            if not await self._is_connection_healthy(conn):
                conn = await self._create_connection()
            
            yield conn
            
        except asyncio.TimeoutError:
            raise RuntimeError("Failed to acquire connection: timeout")
        finally:
            # Return connection to pool
            if not self._closed and conn:
                await self._pool.put(conn)
    
    async def _create_connection(self):
        """Create new database connection."""
        async with self._lock:
            if self._created_connections >= self.config.max_size:
                raise RuntimeError("Maximum connections reached")
            
            conn = await self.connection_factory()
            conn._created_at = time.time()
            conn._query_count = 0
            self._created_connections += 1
            return conn
    
    async def _is_connection_healthy(self, conn) -> bool:
        """Check if connection is healthy and should be reused."""
        now = time.time()
        
        # Check age
        if now - conn._created_at > self.config.max_inactive_time:
            return False
        
        # Check query count
        if conn._query_count > self.config.max_queries:
            return False
        
        # Check if connection is still alive
        try:
            await asyncio.wait_for(conn.ping(), timeout=1.0)
            return True
        except:
            return False
    
    async def close(self):
        """Close all connections in pool."""
        self._closed = True
        
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                await conn.close()
            except asyncio.QueueEmpty:
                break


# Usage example with database operations
class DatabaseManager:
    """Database manager with connection pooling."""
    
    def __init__(self, pool: AsyncConnectionPool):
        self.pool = pool
    
    async def execute_query(self, query: str, params=None):
        """Execute database query with connection from pool."""
        async with self.pool.acquire() as conn:
            conn._query_count += 1
            
            try:
                result = await asyncio.wait_for(
                    conn.execute(query, params),
                    timeout=self.pool.config.query_timeout
                )
                return result
            except asyncio.TimeoutError:
                raise RuntimeError("Query timeout")
    
    async def execute_transaction(self, operations):
        """Execute multiple operations in transaction."""
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                results = []
                for operation in operations:
                    result = await operation(conn)
                    results.append(result)
                return results
```

## Cold Start Optimization

### Module-Level Initialization

```python
import asyncio
from typing import Dict, Any, Optional
import logging
from functools import lru_cache
import os


# Module-level clients (initialized once)
_database_pool: Optional[AsyncConnectionPool] = None
_http_client: Optional = None
_cache_client: Optional = None
_logger: Optional[logging.Logger] = None


async def get_database_pool() -> AsyncConnectionPool:
    """Get or create database connection pool."""
    global _database_pool
    
    if _database_pool is None:
        config = ConnectionPoolConfig(
            min_size=int(os.getenv('DB_POOL_MIN', '2')),
            max_size=int(os.getenv('DB_POOL_MAX', '10')),
        )
        _database_pool = AsyncConnectionPool(config, create_db_connection)
        await _database_pool.initialize()
    
    return _database_pool


async def get_http_client():
    """Get or create HTTP client with connection pooling."""
    global _http_client
    
    if _http_client is None:
        import aiohttp
        
        connector = aiohttp.TCPConnector(
            limit=100,  # Total connection pool size
            limit_per_host=30,  # Per-host connection limit
            ttl_dns_cache=300,  # DNS cache TTL
            use_dns_cache=True,
            keepalive_timeout=60,
            enable_cleanup_closed=True,
        )
        
        timeout = aiohttp.ClientTimeout(
            total=30,
            connect=10,
        )
        
        _http_client = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
        )
    
    return _http_client


@lru_cache(maxsize=128)
def get_cached_config(key: str) -> str:
    """Cache configuration values to avoid repeated environment lookups."""
    return os.getenv(key, '')


class LazyInitializer:
    """Lazy initialization pattern for expensive resources."""
    
    def __init__(self, factory_func):
        self.factory_func = factory_func
        self._instance = None
        self._lock = asyncio.Lock()
    
    async def get(self):
        """Get instance, creating it if necessary."""
        if self._instance is None:
            async with self._lock:
                if self._instance is None:
                    self._instance = await self.factory_func()
        return self._instance


# Example usage
s3_client = LazyInitializer(lambda: create_s3_client())
redis_client = LazyInitializer(lambda: create_redis_client())


async def create_s3_client():
    """Create S3 client with optimized configuration."""
    import aiobotocore.session
    
    session = aiobotocore.session.get_session()
    return session.create_client(
        's3',
        config=aiobotocore.config.AioConfig(
            max_pool_connections=50,
            retries={'max_attempts': 3, 'mode': 'adaptive'},
        )
    )
```

### Application Startup Optimization

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
import asyncio
import time


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Optimized application lifespan with parallel initialization."""
    startup_start = time.time()
    
    # Initialize all resources concurrently
    initialization_tasks = [
        get_database_pool(),
        get_http_client(),
        s3_client.get(),
        redis_client.get(),
    ]
    
    try:
        # Wait for all initialization tasks
        await asyncio.gather(*initialization_tasks, return_exceptions=True)
        
        startup_time = (time.time() - startup_start) * 1000
        logger = logging.getLogger('startup')
        logger.info(f"Application startup completed in {startup_time:.2f}ms")
        
        yield
        
    finally:
        # Cleanup resources
        cleanup_tasks = []
        
        if _database_pool:
            cleanup_tasks.append(_database_pool.close())
        
        if _http_client and not _http_client.closed:
            cleanup_tasks.append(_http_client.close())
        
        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)


# Create FastAPI app with optimized lifespan
app = FastAPI(lifespan=lifespan)
```

## Batching and Caching Strategies

### Request Batching

```python
import asyncio
from typing import List, Dict, Any, Callable, TypeVar, Generic
from dataclasses import dataclass, field
from collections import defaultdict
import time

T = TypeVar('T')
K = TypeVar('K')


@dataclass
class BatchRequest(Generic[K, T]):
    """Individual request in a batch."""
    key: K
    future: asyncio.Future[T] = field(default_factory=asyncio.Future)


class RequestBatcher(Generic[K, T]):
    """Batch similar requests together to reduce overhead."""
    
    def __init__(
        self,
        batch_func: Callable[[List[K]], Dict[K, T]],
        max_batch_size: int = 100,
        max_wait_time: float = 0.01,  # 10ms
    ):
        self.batch_func = batch_func
        self.max_batch_size = max_batch_size
        self.max_wait_time = max_wait_time
        self._pending: Dict[K, BatchRequest[K, T]] = {}
        self._batch_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
    
    async def get(self, key: K) -> T:
        """Get value for key, batching with other concurrent requests."""
        async with self._lock:
            # Check if already pending
            if key in self._pending:
                return await self._pending[key].future
            
            # Create new batch request
            request = BatchRequest(key=key)
            self._pending[key] = request
            
            # Start batch processing if not already running
            if self._batch_task is None or self._batch_task.done():
                self._batch_task = asyncio.create_task(self._process_batch())
            
            return await request.future
    
    async def _process_batch(self):
        """Process pending batch requests."""
        # Wait for more requests or timeout
        await asyncio.sleep(self.max_wait_time)
        
        async with self._lock:
            if not self._pending:
                return
            
            # Get current batch
            batch = dict(self._pending)
            self._pending.clear()
        
        try:
            # Execute batch operation
            keys = list(batch.keys())
            results = await self.batch_func(keys)
            
            # Resolve futures
            for key, request in batch.items():
                if key in results:
                    request.future.set_result(results[key])
                else:
                    request.future.set_exception(
                        KeyError(f"Result not found for key: {key}")
                    )
        
        except Exception as e:
            # Reject all futures in batch
            for request in batch.values():
                if not request.future.done():
                    request.future.set_exception(e)


# Example: Batch database queries
class UserRepository:
    """Repository with request batching."""
    
    def __init__(self, db_pool):
        self.db_pool = db_pool
        self._user_batcher = RequestBatcher(
            batch_func=self._fetch_users_batch,
            max_batch_size=50,
            max_wait_time=0.005,  # 5ms
        )
    
    async def get_user(self, user_id: str) -> Dict[str, Any]:
        """Get user with automatic batching."""
        return await self._user_batcher.get(user_id)
    
    async def _fetch_users_batch(self, user_ids: List[str]) -> Dict[str, Dict]:
        """Fetch multiple users in single database query."""
        placeholders = ','.join(['%s'] * len(user_ids))
        query = f"SELECT * FROM users WHERE id IN ({placeholders})"
        
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(query, user_ids)
            return {row['id']: dict(row) for row in rows}
```

### Multi-Level Caching

```python
from typing import Optional, Any, Union
from dataclasses import dataclass
import time
import hashlib
import pickle
import asyncio


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    value: Any
    created_at: float
    ttl: Optional[float] = None
    hit_count: int = 0
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl
    
    def touch(self) -> None:
        """Update hit count."""
        self.hit_count += 1


class MultiLevelCache:
    """Multi-level caching with L1 (memory) and L2 (Redis) tiers."""
    
    def __init__(
        self,
        l1_max_size: int = 1000,
        l1_ttl: int = 300,  # 5 minutes
        l2_ttl: int = 3600,  # 1 hour
        redis_client=None,
    ):
        self.l1_max_size = l1_max_size
        self.l1_ttl = l1_ttl
        self.l2_ttl = l2_ttl
        self.redis_client = redis_client
        
        # L1 cache (in-memory)
        self._l1_cache: Dict[str, CacheEntry] = {}
        self._l1_access_order: List[str] = []
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache (L1 then L2)."""
        # Try L1 cache first
        l1_value = await self._get_l1(key)
        if l1_value is not None:
            return l1_value
        
        # Try L2 cache (Redis)
        if self.redis_client:
            l2_value = await self._get_l2(key)
            if l2_value is not None:
                # Store in L1 for faster future access
                await self._set_l1(key, l2_value, self.l1_ttl)
                return l2_value
        
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        l1_only: bool = False,
    ) -> None:
        """Set value in cache."""
        # Always set in L1
        await self._set_l1(key, value, ttl or self.l1_ttl)
        
        # Set in L2 if available and not L1-only
        if not l1_only and self.redis_client:
            await self._set_l2(key, value, ttl or self.l2_ttl)
    
    async def delete(self, key: str) -> None:
        """Delete from all cache levels."""
        async with self._lock:
            if key in self._l1_cache:
                del self._l1_cache[key]
                if key in self._l1_access_order:
                    self._l1_access_order.remove(key)
        
        if self.redis_client:
            await self.redis_client.delete(key)
    
    async def _get_l1(self, key: str) -> Optional[Any]:
        """Get from L1 cache."""
        async with self._lock:
            entry = self._l1_cache.get(key)
            if entry is None or entry.is_expired():
                return None
            
            entry.touch()
            # Move to end for LRU
            if key in self._l1_access_order:
                self._l1_access_order.remove(key)
            self._l1_access_order.append(key)
            
            return entry.value
    
    async def _set_l1(self, key: str, value: Any, ttl: int) -> None:
        """Set in L1 cache with LRU eviction."""
        async with self._lock:
            # Evict if at capacity
            while len(self._l1_cache) >= self.l1_max_size:
                oldest_key = self._l1_access_order.pop(0)
                del self._l1_cache[oldest_key]
            
            # Store entry
            entry = CacheEntry(
                value=value,
                created_at=time.time(),
                ttl=ttl,
            )
            self._l1_cache[key] = entry
            
            if key in self._l1_access_order:
                self._l1_access_order.remove(key)
            self._l1_access_order.append(key)
    
    async def _get_l2(self, key: str) -> Optional[Any]:
        """Get from L2 cache (Redis)."""
        try:
            data = await self.redis_client.get(key)
            if data:
                return pickle.loads(data)
        except Exception:
            # Redis error - degrade gracefully
            pass
        return None
    
    async def _set_l2(self, key: str, value: Any, ttl: int) -> None:
        """Set in L2 cache (Redis)."""
        try:
            data = pickle.dumps(value)
            await self.redis_client.setex(key, ttl, data)
        except Exception:
            # Redis error - degrade gracefully
            pass


# Decorator for caching function results
def cached(
    cache: MultiLevelCache,
    ttl: int = 300,
    key_func: Optional[Callable] = None,
):
    """Decorator for caching function results."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                key_data = f"{func.__name__}:{args}:{sorted(kwargs.items())}"
                cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # Try cache first
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator
```

## Timeout and Circuit Breaker Patterns

### Circuit Breaker Implementation

```python
import asyncio
from enum import Enum
from typing import Callable, Any, Optional
from dataclasses import dataclass
import time
import logging


class CircuitBreakerState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""
    failure_threshold: int = 5
    success_threshold: int = 3
    timeout: float = 60.0  # seconds
    expected_exceptions: tuple = (Exception,)


class CircuitBreaker:
    """Circuit breaker for external service calls."""
    
    def __init__(self, config: CircuitBreakerConfig, name: str = "default"):
        self.config = config
        self.name = name
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.logger = logging.getLogger(f'circuit_breaker.{name}')
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
                self.logger.info(f"Circuit breaker {self.name} moving to HALF_OPEN")
            else:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker {self.name} is OPEN"
                )
        
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
            
        except self.config.expected_exceptions as e:
            await self._on_failure()
            raise
    
    async def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitBreakerState.CLOSED
                self.success_count = 0
                self.logger.info(f"Circuit breaker {self.name} moving to CLOSED")
    
    async def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.config.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            self.logger.warning(
                f"Circuit breaker {self.name} moving to OPEN "
                f"after {self.failure_count} failures"
            )
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        return (
            self.last_failure_time and
            time.time() - self.last_failure_time >= self.config.timeout
        )


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open."""
    pass


# Usage example
class ExternalServiceClient:
    """HTTP client with circuit breaker protection."""
    
    def __init__(self, http_client, base_url: str):
        self.http_client = http_client
        self.base_url = base_url
        
        # Circuit breaker for this service
        self.circuit_breaker = CircuitBreaker(
            config=CircuitBreakerConfig(
                failure_threshold=3,
                success_threshold=2,
                timeout=30.0,
                expected_exceptions=(aiohttp.ClientError, asyncio.TimeoutError),
            ),
            name=f"external_service_{base_url}",
        )
    
    async def get_data(self, endpoint: str) -> dict:
        """Get data with circuit breaker protection."""
        async def _make_request():
            async with self.http_client.get(
                f"{self.base_url}/{endpoint}"
            ) as response:
                response.raise_for_status()
                return await response.json()
        
        return await self.circuit_breaker.call(_make_request)
```

## Performance Monitoring

### Request Performance Tracking

```python
import time
import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict, deque
import statistics


@dataclass
class PerformanceMetrics:
    """Performance metrics for monitoring."""
    request_count: int = 0
    total_duration: float = 0.0
    error_count: int = 0
    min_duration: Optional[float] = None
    max_duration: Optional[float] = None
    recent_durations: deque = field(default_factory=lambda: deque(maxlen=100))
    
    def add_request(self, duration: float, is_error: bool = False):
        """Add request metrics."""
        self.request_count += 1
        self.total_duration += duration
        
        if is_error:
            self.error_count += 1
        
        if self.min_duration is None or duration < self.min_duration:
            self.min_duration = duration
        
        if self.max_duration is None or duration > self.max_duration:
            self.max_duration = duration
        
        self.recent_durations.append(duration)
    
    @property
    def avg_duration(self) -> float:
        """Average request duration."""
        if self.request_count == 0:
            return 0.0
        return self.total_duration / self.request_count
    
    @property
    def error_rate(self) -> float:
        """Error rate percentage."""
        if self.request_count == 0:
            return 0.0
        return (self.error_count / self.request_count) * 100
    
    @property
    def p95_duration(self) -> float:
        """95th percentile duration from recent requests."""
        if not self.recent_durations:
            return 0.0
        return statistics.quantiles(self.recent_durations, n=20)[18]  # 95th percentile


class PerformanceMonitor:
    """Monitor and track performance metrics."""
    
    def __init__(self):
        self.metrics: Dict[str, PerformanceMetrics] = defaultdict(PerformanceMetrics)
        self.logger = logging.getLogger('performance')
    
    async def track_request(self, endpoint: str, method: str = "GET"):
        """Context manager for tracking request performance."""
        key = f"{method} {endpoint}"
        start_time = time.time()
        is_error = False
        
        try:
            yield
        except Exception:
            is_error = True
            raise
        finally:
            duration = (time.time() - start_time) * 1000  # milliseconds
            self.metrics[key].add_request(duration, is_error)
            
            # Log slow requests
            if duration > 1000:  # > 1 second
                self.logger.warning(
                    f"Slow request: {key} took {duration:.2f}ms",
                    extra={'endpoint': endpoint, 'method': method, 'duration': duration}
                )
    
    def get_metrics(self, endpoint: Optional[str] = None) -> Dict[str, Dict]:
        """Get performance metrics."""
        if endpoint:
            metrics = {endpoint: self.metrics.get(endpoint, PerformanceMetrics())}
        else:
            metrics = dict(self.metrics)
        
        return {
            key: {
                'request_count': metric.request_count,
                'avg_duration_ms': metric.avg_duration,
                'min_duration_ms': metric.min_duration or 0,
                'max_duration_ms': metric.max_duration or 0,
                'p95_duration_ms': metric.p95_duration,
                'error_rate_pct': metric.error_rate,
                'error_count': metric.error_count,
            }
            for key, metric in metrics.items()
        }
    
    async def start_reporting(self, interval: int = 60):
        """Start periodic performance reporting."""
        while True:
            await asyncio.sleep(interval)
            
            # Report metrics for all endpoints
            for endpoint, metrics in self.metrics.items():
                if metrics.request_count > 0:
                    self.logger.info(
                        f"Performance metrics for {endpoint}",
                        extra={
                            'endpoint': endpoint,
                            'request_count': metrics.request_count,
                            'avg_duration_ms': metrics.avg_duration,
                            'error_rate_pct': metrics.error_rate,
                            'p95_duration_ms': metrics.p95_duration,
                        }
                    )


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


# FastAPI middleware for automatic performance tracking
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware for automatic performance monitoring."""
    
    async def dispatch(self, request: Request, call_next):
        async with performance_monitor.track_request(
            request.url.path,
            request.method
        ):
            response = await call_next(request)
            return response
```

## Best Practices Summary

### Async Programming

- **Never block the event loop**: Use `await` for all I/O operations
- **Use ThreadPoolExecutor**: For CPU-intensive or blocking operations
- **Connection pooling**: Reuse database and HTTP connections
- **Concurrent execution**: Use `asyncio.gather()` for parallel operations
- **Proper error handling**: Handle exceptions in async contexts appropriately

### Performance Optimization

- **Lazy initialization**: Initialize expensive resources only when needed
- **Module-level clients**: Create shared clients at module level for connection reuse
- **Request batching**: Batch similar requests to reduce overhead
- **Multi-level caching**: Use both memory and distributed caching appropriately
- **Circuit breakers**: Protect against cascading failures in distributed systems

### Monitoring and Observability

- **Performance metrics**: Track request duration, error rates, and throughput
- **Resource monitoring**: Monitor connection pool usage, memory, and CPU
- **Slow query detection**: Log and alert on slow operations
- **Circuit breaker metrics**: Monitor circuit breaker state changes
- **Health checks**: Implement comprehensive health checks for dependencies

### Scalability Patterns

- **Horizontal scaling**: Design for stateless, horizontally scalable services
- **Load shedding**: Implement graceful degradation under high load
- **Rate limiting**: Protect services with appropriate rate limiting
- **Caching strategies**: Use caching at multiple levels (CDN, application, database)
- **Asynchronous processing**: Use queues for non-real-time operations