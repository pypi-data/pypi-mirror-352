"""Reactive authorization Cosmos repository with async/reactive patterns."""

import asyncio
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import (
    List,
    Optional,
    Dict,
    Any,
    TypeVar,
    Generic,
    Iterable,
    AsyncGenerator,
    Set,
    Union,
    Callable,
    Type,
)
import logging
from contextlib import asynccontextmanager

from apexnova.stub.model.base_model import IBaseModel

T = TypeVar("T", bound=IBaseModel)
AM = TypeVar("AM")  # Authorization model type variable without bound
ID = TypeVar("ID")

logger = logging.getLogger(__name__)


@dataclass
class CircuitBreakerState:
    """Circuit breaker state for fault tolerance."""

    failure_count: int = 0
    last_failure_time: float = 0
    state: str = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    failure_threshold: int = 5
    recovery_timeout: int = 60  # seconds
    half_open_max_calls: int = 3
    half_open_calls: int = 0


@dataclass
class CacheEntry:
    """Cache entry with TTL support."""

    data: Any
    created_at: float = field(default_factory=time.time)
    ttl: int = 300  # 5 minutes default

    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        return time.time() - self.created_at > self.ttl


@dataclass
class PerformanceMetrics:
    """Performance metrics for monitoring."""

    operation_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    average_latencies: Dict[str, float] = field(default_factory=dict)
    error_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    cache_hits: int = 0
    cache_misses: int = 0

    def record_operation(self, operation: str, latency: float, success: bool = True):
        """Record operation metrics."""
        self.operation_counts[operation] += 1
        current_avg = self.average_latencies.get(operation, 0)
        count = self.operation_counts[operation]
        self.average_latencies[operation] = (
            current_avg * (count - 1) + latency
        ) / count

        if not success:
            self.error_counts[operation] += 1


class ReactiveAuthorizationCosmosRepository(ABC, Generic[AM, T, ID]):
    """
    Reactive Cosmos DB repository with async/reactive patterns, authorization,
    circuit breaker, caching, and comprehensive monitoring.
    """

    def __init__(
        self,
        max_concurrent_operations: int = 50,
        enable_caching: bool = True,
        cache_ttl: int = 300,
        circuit_breaker_failure_threshold: int = 5,
        circuit_breaker_recovery_timeout: int = 60,
        thread_pool_size: int = 10,
        enable_authorization: bool = True,
    ):
        """
        Initialize reactive Cosmos repository.

        Args:
            max_concurrent_operations: Maximum concurrent operations
            enable_caching: Whether to enable caching
            cache_ttl: Cache TTL in seconds
            circuit_breaker_failure_threshold: Circuit breaker failure threshold
            circuit_breaker_recovery_timeout: Circuit breaker recovery timeout
            thread_pool_size: Thread pool size for blocking operations
            enable_authorization: Whether to enable authorization checks
        """
        # Async concurrency control
        self._semaphore = asyncio.Semaphore(max_concurrent_operations)

        # Circuit breaker for fault tolerance
        self._circuit_breaker = CircuitBreakerState(
            failure_threshold=circuit_breaker_failure_threshold,
            recovery_timeout=circuit_breaker_recovery_timeout,
        )

        # Caching
        self._enable_caching = enable_caching
        self._cache_ttl = cache_ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._cache_lock = asyncio.Lock()

        # Thread pool for blocking operations
        self._thread_pool = ThreadPoolExecutor(max_workers=thread_pool_size)

        # Performance metrics
        self._metrics = PerformanceMetrics()

        # Authorization
        self._enable_authorization = enable_authorization

        # Cleanup task for cache
        self._cleanup_task: Optional[asyncio.Task] = None
        self._start_cleanup_task()

    def _start_cleanup_task(self):
        """Start background cache cleanup task."""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_cache_periodically())

    async def _cleanup_cache_periodically(self):
        """Periodically cleanup expired cache entries."""
        while True:
            try:
                await asyncio.sleep(60)  # Cleanup every minute
                await self._cleanup_expired_cache()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"Cache cleanup error: {e}")

    async def _cleanup_expired_cache(self):
        """Remove expired cache entries."""
        async with self._cache_lock:
            expired_keys = [
                key for key, entry in self._cache.items() if entry.is_expired()
            ]
            for key in expired_keys:
                del self._cache[key]

    def _get_cache_key(self, operation: str, **kwargs) -> str:
        """Generate cache key for operation."""
        key_parts = [operation] + [f"{k}={v}" for k, v in sorted(kwargs.items())]
        return ":".join(str(part) for part in key_parts)

    async def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Get data from cache."""
        if not self._enable_caching:
            return None

        async with self._cache_lock:
            entry = self._cache.get(cache_key)
            if entry and not entry.is_expired():
                self._metrics.cache_hits += 1
                return entry.data
            elif entry:
                # Remove expired entry
                del self._cache[cache_key]

            self._metrics.cache_misses += 1
            return None

    async def _put_in_cache(self, cache_key: str, data: Any, ttl: Optional[int] = None):
        """Put data in cache."""
        if not self._enable_caching:
            return

        async with self._cache_lock:
            self._cache[cache_key] = CacheEntry(data=data, ttl=ttl or self._cache_ttl)

    async def _check_circuit_breaker(self, operation: str):
        """Check circuit breaker state."""
        current_time = time.time()

        if self._circuit_breaker.state == "OPEN":
            if (
                current_time - self._circuit_breaker.last_failure_time
                > self._circuit_breaker.recovery_timeout
            ):
                self._circuit_breaker.state = "HALF_OPEN"
                self._circuit_breaker.half_open_calls = 0
                logger.info(f"Circuit breaker half-open for operation: {operation}")
            else:
                raise RuntimeError(f"Circuit breaker open for operation: {operation}")

        elif self._circuit_breaker.state == "HALF_OPEN":
            if (
                self._circuit_breaker.half_open_calls
                >= self._circuit_breaker.half_open_max_calls
            ):
                raise RuntimeError(
                    f"Circuit breaker half-open limit exceeded: {operation}"
                )

    async def _record_success(self, operation: str, latency: float):
        """Record successful operation."""
        self._metrics.record_operation(operation, latency, success=True)

        if self._circuit_breaker.state == "HALF_OPEN":
            self._circuit_breaker.half_open_calls += 1
            if (
                self._circuit_breaker.half_open_calls
                >= self._circuit_breaker.half_open_max_calls
            ):
                self._circuit_breaker.state = "CLOSED"
                self._circuit_breaker.failure_count = 0
                logger.info(f"Circuit breaker closed for operation: {operation}")

    async def _record_failure(self, operation: str, latency: float, error: Exception):
        """Record failed operation."""
        self._metrics.record_operation(operation, latency, success=False)
        self._circuit_breaker.failure_count += 1
        self._circuit_breaker.last_failure_time = time.time()

        if (
            self._circuit_breaker.failure_count
            >= self._circuit_breaker.failure_threshold
        ):
            self._circuit_breaker.state = "OPEN"
            logger.warning(
                f"Circuit breaker opened for operation: {operation} due to: {error}"
            )

    @asynccontextmanager
    async def _with_circuit_breaker(self, operation: str):
        """Context manager for circuit breaker pattern."""
        start_time = time.time()

        try:
            await self._check_circuit_breaker(operation)
            async with self._semaphore:
                yield

            latency = time.time() - start_time
            await self._record_success(operation, latency)

        except Exception as e:
            latency = time.time() - start_time
            await self._record_failure(operation, latency, e)
            raise

    async def _check_authorization(
        self, operation: str, entity: Optional[T] = None, context: Optional[AM] = None
    ):
        """Check authorization for operation."""
        if not self._enable_authorization:
            return

        # Placeholder for authorization logic
        # In real implementation, this would check permissions
        # against the authorization context and entity
        pass

    # Core async repository operations

    async def save_async(self, entity: T, context: Optional[AM] = None) -> T:
        """Save an entity asynchronously."""
        async with self._with_circuit_breaker("save"):
            await self._check_authorization("save", entity, context)

            # Delegate to sync method in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(self._thread_pool, self.save, entity)

            # Cache the result
            if hasattr(entity, "id"):
                cache_key = self._get_cache_key("find_by_id", id=entity.id)
                await self._put_in_cache(cache_key, result)

            return result

    async def find_by_id_async(
        self, id: ID, context: Optional[AM] = None
    ) -> Optional[T]:
        """Find entity by ID asynchronously."""
        cache_key = self._get_cache_key("find_by_id", id=id)

        # Try cache first
        cached_result = await self._get_from_cache(cache_key)
        if cached_result is not None:
            await self._check_authorization("read", cached_result, context)
            return cached_result

        async with self._with_circuit_breaker("find_by_id"):
            await self._check_authorization("read", None, context)

            # Delegate to sync method in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(self._thread_pool, self.find_by_id, id)

            # Cache the result
            if result is not None:
                await self._put_in_cache(cache_key, result)

            return result

    async def find_all_async(
        self, context: Optional[AM] = None
    ) -> AsyncGenerator[T, None]:
        """Find all entities asynchronously as a stream."""
        async with self._with_circuit_breaker("find_all"):
            await self._check_authorization("read", None, context)

            # Delegate to sync method in thread pool
            loop = asyncio.get_event_loop()
            entities = await loop.run_in_executor(
                self._thread_pool, lambda: list(self.find_all())
            )

            # Stream results
            for entity in entities:
                await self._check_authorization("read", entity, context)
                yield entity

    async def delete_async(self, entity: T, context: Optional[AM] = None) -> None:
        """Delete an entity asynchronously."""
        async with self._with_circuit_breaker("delete"):
            await self._check_authorization("delete", entity, context)

            # Delegate to sync method in thread pool
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(self._thread_pool, self.delete, entity)

            # Remove from cache
            if hasattr(entity, "id"):
                cache_key = self._get_cache_key("find_by_id", id=entity.id)
                async with self._cache_lock:
                    self._cache.pop(cache_key, None)

    async def delete_by_id_async(self, id: ID, context: Optional[AM] = None) -> None:
        """Delete entity by ID asynchronously."""
        async with self._with_circuit_breaker("delete_by_id"):
            await self._check_authorization("delete", None, context)

            # Delegate to sync method in thread pool
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(self._thread_pool, self.delete_by_id, id)

            # Remove from cache
            cache_key = self._get_cache_key("find_by_id", id=id)
            async with self._cache_lock:
                self._cache.pop(cache_key, None)

    async def exists_by_id_async(self, id: ID, context: Optional[AM] = None) -> bool:
        """Check if entity exists by ID asynchronously."""
        cache_key = self._get_cache_key("exists_by_id", id=id)

        # Try cache first
        cached_result = await self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result

        async with self._with_circuit_breaker("exists_by_id"):
            await self._check_authorization("read", None, context)

            # Delegate to sync method in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self._thread_pool, self.exists_by_id, id
            )

            # Cache the result
            await self._put_in_cache(
                cache_key, result, ttl=60
            )  # Shorter TTL for existence checks

            return result

    async def count_async(self, context: Optional[AM] = None) -> int:
        """Count all entities asynchronously."""
        cache_key = self._get_cache_key("count")

        # Try cache first
        cached_result = await self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result

        async with self._with_circuit_breaker("count"):
            await self._check_authorization("read", None, context)

            # Delegate to sync method in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(self._thread_pool, self.count)

            # Cache the result
            await self._put_in_cache(cache_key, result, ttl=30)  # Short TTL for counts

            return result

    async def save_all_async(
        self, entities: List[T], context: Optional[AM] = None
    ) -> AsyncGenerator[T, None]:
        """Save multiple entities asynchronously as a stream."""
        async with self._with_circuit_breaker("save_all"):
            # Check authorization for all entities
            for entity in entities:
                await self._check_authorization("save", entity, context)

            # Process in batches to avoid overwhelming the database
            batch_size = 10
            for i in range(0, len(entities), batch_size):
                batch = entities[i : i + batch_size]

                # Delegate to sync method in thread pool
                loop = asyncio.get_event_loop()
                saved_entities = await loop.run_in_executor(
                    self._thread_pool, lambda: list(self.save_all(batch))
                )

                # Stream results and update cache
                for entity in saved_entities:
                    if hasattr(entity, "id"):
                        cache_key = self._get_cache_key("find_by_id", id=entity.id)
                        await self._put_in_cache(cache_key, entity)
                    yield entity

    async def find_by_id_with_partition_key_async(
        self, id: ID, partition_key: str, context: Optional[AM] = None
    ) -> Optional[T]:
        """Find entity by ID with partition key asynchronously."""
        cache_key = self._get_cache_key(
            "find_by_id_with_partition_key", id=id, partition_key=partition_key
        )

        # Try cache first
        cached_result = await self._get_from_cache(cache_key)
        if cached_result is not None:
            await self._check_authorization("read", cached_result, context)
            return cached_result

        async with self._with_circuit_breaker("find_by_id_with_partition_key"):
            await self._check_authorization("read", None, context)

            # Delegate to sync method in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self._thread_pool, self.find_by_id_with_partition_key, id, partition_key
            )

            # Cache the result
            if result is not None:
                await self._put_in_cache(cache_key, result)

            return result

    async def delete_by_id_with_partition_key_async(
        self, id: ID, partition_key: str, context: Optional[AM] = None
    ) -> None:
        """Delete entity by ID with partition key asynchronously."""
        async with self._with_circuit_breaker("delete_by_id_with_partition_key"):
            await self._check_authorization("delete", None, context)

            # Delegate to sync method in thread pool
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self._thread_pool,
                self.delete_by_id_with_partition_key,
                id,
                partition_key,
            )

            # Remove from cache
            cache_key = self._get_cache_key(
                "find_by_id_with_partition_key", id=id, partition_key=partition_key
            )
            async with self._cache_lock:
                self._cache.pop(cache_key, None)

    async def find_all_with_partition_key_async(
        self, partition_key: str, context: Optional[AM] = None
    ) -> AsyncGenerator[T, None]:
        """Find all entities with partition key asynchronously as a stream."""
        async with self._with_circuit_breaker("find_all_with_partition_key"):
            await self._check_authorization("read", None, context)

            # Delegate to sync method in thread pool
            loop = asyncio.get_event_loop()
            entities = await loop.run_in_executor(
                self._thread_pool,
                lambda: list(self.find_all_with_partition_key(partition_key)),
            )

            # Stream results
            for entity in entities:
                await self._check_authorization("read", entity, context)
                yield entity

    async def filter_async(
        self, properties: Dict[str, Any], context: Optional[AM] = None
    ) -> AsyncGenerator[T, None]:
        """Filter entities by properties asynchronously as a stream."""
        cache_key = self._get_cache_key("filter", **properties)

        # Try cache first
        cached_result = await self._get_from_cache(cache_key)
        if cached_result is not None:
            for entity in cached_result:
                await self._check_authorization("read", entity, context)
                yield entity
            return

        async with self._with_circuit_breaker("filter"):
            await self._check_authorization("read", None, context)

            # Delegate to sync method in thread pool
            loop = asyncio.get_event_loop()
            entities = await loop.run_in_executor(
                self._thread_pool, self.filter, properties
            )

            # Cache and stream results
            filtered_entities = []
            for entity in entities:
                await self._check_authorization("read", entity, context)
                filtered_entities.append(entity)
                yield entity

            # Cache the filtered results
            await self._put_in_cache(
                cache_key, filtered_entities, ttl=120
            )  # Shorter TTL for filters

    # Health and monitoring methods

    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status."""
        cache_size = len(self._cache)

        return {
            "status": (
                "healthy" if self._circuit_breaker.state != "OPEN" else "degraded"
            ),
            "circuit_breaker": {
                "state": self._circuit_breaker.state,
                "failure_count": self._circuit_breaker.failure_count,
                "last_failure_time": self._circuit_breaker.last_failure_time,
            },
            "cache": {
                "enabled": self._enable_caching,
                "size": cache_size,
                "hits": self._metrics.cache_hits,
                "misses": self._metrics.cache_misses,
                "hit_ratio": self._metrics.cache_hits
                / max(1, self._metrics.cache_hits + self._metrics.cache_misses),
            },
            "metrics": {
                "operation_counts": dict(self._metrics.operation_counts),
                "average_latencies": self._metrics.average_latencies,
                "error_counts": dict(self._metrics.error_counts),
            },
            "thread_pool": {
                "active_threads": getattr(self._thread_pool, "_threads", 0)
            },
        }

    async def clear_cache(self):
        """Clear all cached data."""
        async with self._cache_lock:
            self._cache.clear()

    async def reset_circuit_breaker(self):
        """Reset circuit breaker to closed state."""
        self._circuit_breaker.state = "CLOSED"
        self._circuit_breaker.failure_count = 0
        self._circuit_breaker.half_open_calls = 0

    async def shutdown(self):
        """Shutdown the repository and cleanup resources."""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        self._thread_pool.shutdown(wait=True)

    # Backward compatibility: sync wrapper methods

    def save_sync(self, entity: T, context: Optional[AM] = None) -> T:
        """Sync wrapper for save_async."""
        return asyncio.run(self.save_async(entity, context))

    def find_by_id_sync(self, id: ID, context: Optional[AM] = None) -> Optional[T]:
        """Sync wrapper for find_by_id_async."""
        return asyncio.run(self.find_by_id_async(id, context))

    def find_all_sync(self, context: Optional[AM] = None) -> List[T]:
        """Sync wrapper for find_all_async."""

        async def _collect():
            return [entity async for entity in self.find_all_async(context)]

        return asyncio.run(_collect())

    def delete_sync(self, entity: T, context: Optional[AM] = None) -> None:
        """Sync wrapper for delete_async."""
        asyncio.run(self.delete_async(entity, context))

    def filter_sync(
        self, properties: Dict[str, Any], context: Optional[AM] = None
    ) -> List[T]:
        """Sync wrapper for filter_async."""

        async def _collect():
            return [entity async for entity in self.filter_async(properties, context)]

        return asyncio.run(_collect())

    # Abstract methods that subclasses must implement (original sync API)

    @abstractmethod
    def save(self, entity: T) -> T:
        """Save an entity."""
        pass

    @abstractmethod
    def find_by_id(self, id: ID) -> Optional[T]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def find_all(self) -> Iterable[T]:
        """Find all entities."""
        pass

    @abstractmethod
    def delete(self, entity: T) -> None:
        """Delete an entity."""
        pass

    @abstractmethod
    def delete_by_id(self, id: ID) -> None:
        """Delete entity by ID."""
        pass

    @abstractmethod
    def exists_by_id(self, id: ID) -> bool:
        """Check if entity exists by ID."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Count all entities."""
        pass

    @abstractmethod
    def save_all(self, entities: Iterable[T]) -> Iterable[T]:
        """Save multiple entities."""
        pass

    @abstractmethod
    def find_by_id_with_partition_key(self, id: ID, partition_key: str) -> Optional[T]:
        """Find entity by ID with partition key."""
        pass

    @abstractmethod
    def delete_by_id_with_partition_key(self, id: ID, partition_key: str) -> None:
        """Delete entity by ID with partition key."""
        pass

    @abstractmethod
    def find_all_with_partition_key(self, partition_key: str) -> Iterable[T]:
        """Find all entities with partition key."""
        pass

    @abstractmethod
    def filter(self, properties: Dict[str, Any]) -> List[T]:
        """Filter entities by properties."""
        pass


# Example implementation that gracefully degrades without Cosmos SDK
class MockReactiveAuthorizationCosmosRepository(
    ReactiveAuthorizationCosmosRepository[AM, T, ID]
):
    """
    Mock implementation for testing and graceful degradation without Cosmos SDK.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._storage: Dict[ID, T] = {}

    def save(self, entity: T) -> T:
        """Save an entity."""
        if hasattr(entity, "id"):
            self._storage[entity.id] = entity
        return entity

    def find_by_id(self, id: ID) -> Optional[T]:
        """Find entity by ID."""
        return self._storage.get(id)

    def find_all(self) -> Iterable[T]:
        """Find all entities."""
        return list(self._storage.values())

    def delete(self, entity: T) -> None:
        """Delete an entity."""
        if hasattr(entity, "id") and entity.id in self._storage:
            del self._storage[entity.id]

    def delete_by_id(self, id: ID) -> None:
        """Delete entity by ID."""
        self._storage.pop(id, None)

    def exists_by_id(self, id: ID) -> bool:
        """Check if entity exists by ID."""
        return id in self._storage

    def count(self) -> int:
        """Count all entities."""
        return len(self._storage)

    def save_all(self, entities: Iterable[T]) -> Iterable[T]:
        """Save multiple entities."""
        saved = []
        for entity in entities:
            saved.append(self.save(entity))
        return saved

    def find_by_id_with_partition_key(self, id: ID, partition_key: str) -> Optional[T]:
        """Find entity by ID with partition key."""
        # In mock implementation, ignore partition key
        return self.find_by_id(id)

    def delete_by_id_with_partition_key(self, id: ID, partition_key: str) -> None:
        """Delete entity by ID with partition key."""
        # In mock implementation, ignore partition key
        self.delete_by_id(id)

    def find_all_with_partition_key(self, partition_key: str) -> Iterable[T]:
        """Find all entities with partition key."""
        # In mock implementation, return all entities
        return self.find_all()

    def filter(self, properties: Dict[str, Any]) -> List[T]:
        """Filter entities by properties."""
        # Simple property matching for mock implementation
        results = []
        for entity in self._storage.values():
            match = True
            for key, value in properties.items():
                if not hasattr(entity, key) or getattr(entity, key) != value:
                    match = False
                    break
            if match:
                results.append(entity)
        return results
