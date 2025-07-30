"""Modern reactive Gremlin authorization repository with async/await patterns."""

from __future__ import annotations

import asyncio
import time
from collections import defaultdict, deque
from typing import Dict, Optional, Any, AsyncGenerator, List, TypeVar, Generic, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import weakref
from concurrent.futures import ThreadPoolExecutor
from abc import ABC, abstractmethod

try:
    from gremlinpython.driver.driver_remote_connection import DriverRemoteConnection  # type: ignore
    from gremlinpython.process.anonymous_traversal import traversal  # type: ignore

    gremlin_available = True
except ImportError:
    gremlin_available = False
    DriverRemoteConnection = None  # type: ignore
    traversal = None  # type: ignore

from apexnova.stub.model.base_element import IBaseElement

# Type variables
T = TypeVar("T", bound=IBaseElement)
ID = TypeVar("ID")
AM = TypeVar("AM")  # Authorization model

logger = logging.getLogger(__name__)


@dataclass
class RepositoryConfig:
    """Configuration for reactive repository."""

    max_concurrent_operations: int = 10
    batch_size: int = 100
    query_timeout_seconds: float = 30.0
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60
    metrics_window_seconds: int = 300
    cache_ttl_seconds: int = 3600
    connection_pool_size: int = 5


@dataclass
class BatchResult:
    """Result of a batch operation."""

    successful_count: int
    failed_count: int
    total_count: int
    errors: List[str]
    successful_items: List[T]
    failed_items: List[T]


@dataclass
class RepositoryMetrics:
    """Repository operation metrics."""

    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    average_duration_ms: float = 0.0
    circuit_breaker_open: bool = False
    cache_hit_rate: float = 0.0
    last_updated: datetime = datetime.now()


class ReactiveGremlinAuthorizationRepository(ABC, Generic[AM, T, ID]):
    """
    Modern reactive Gremlin authorization repository with async/await patterns.

    Features:
    - Async repository operations with proper backpressure handling
    - Circuit breaker pattern for resilience
    - Batch processing for performance
    - Query result streaming
    - Graceful degradation when Gremlin unavailable
    - Authorization checks on all operations
    - Memory-efficient caching with TTL
    """

    def __init__(
        self,
        authorization_model: AM,
        gremlin_endpoint: Optional[str] = None,
        element_type: Optional[type] = None,
        config: Optional[RepositoryConfig] = None,
    ):
        """Initialize reactive repository."""
        self.authorization_model = authorization_model
        self.element_type = element_type
        self.config = config or RepositoryConfig()
        self.enabled = False

        # Connection and traversal
        self.connection: Optional[Any] = None
        self.g: Optional[Any] = None

        # Async components
        self._semaphore = asyncio.Semaphore(self.config.max_concurrent_operations)
        self._thread_pool = ThreadPoolExecutor(
            max_workers=self.config.connection_pool_size
        )
        self._shutdown_event = asyncio.Event()
        self._background_tasks: List[asyncio.Task] = []

        # Circuit breaker
        self._circuit_breaker_failures = 0
        self._circuit_breaker_open = False
        self._circuit_breaker_last_failure = 0.0

        # Metrics and cache
        self._metrics = RepositoryMetrics()
        self._operation_cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        self._operation_durations = deque(maxlen=1000)

        # Stream management
        self._result_streams: weakref.WeakSet = weakref.WeakSet()

        # Initialize connection
        if gremlin_endpoint:
            asyncio.create_task(self._initialize_connection(gremlin_endpoint))

    async def _initialize_connection(self, endpoint: str) -> None:
        """Initialize Gremlin connection asynchronously."""
        if not gremlin_available:
            logger.warning(
                "Gremlin libraries not available, repository will operate in degraded mode"
            )
            return

        try:
            # Use thread pool for potentially blocking connection setup
            await asyncio.get_event_loop().run_in_executor(
                self._thread_pool, self._setup_gremlin_connection, endpoint
            )
            self.enabled = True
            logger.info("Gremlin connection established successfully")

        except Exception as e:
            logger.error(f"Failed to establish Gremlin connection: {e}")
            await self._handle_circuit_breaker_failure()

    def _setup_gremlin_connection(self, endpoint: str) -> None:
        """Setup Gremlin connection (runs in thread pool)."""
        self.connection = DriverRemoteConnection(endpoint, "g")
        self.g = traversal().withRemote(self.connection)

    async def _handle_circuit_breaker_failure(self) -> None:
        """Handle circuit breaker failure logic."""
        self._circuit_breaker_failures += 1
        self._circuit_breaker_last_failure = time.time()

        if self._circuit_breaker_failures >= self.config.circuit_breaker_threshold:
            self._circuit_breaker_open = True
            logger.warning(
                f"Circuit breaker opened after {self._circuit_breaker_failures} failures"
            )

    def _check_circuit_breaker(self) -> bool:
        """Check if circuit breaker should allow operations."""
        if not self._circuit_breaker_open:
            return True

        # Check if we should attempt to close the circuit breaker
        if (
            time.time() - self._circuit_breaker_last_failure
        ) > self.config.circuit_breaker_timeout:
            self._circuit_breaker_open = False
            self._circuit_breaker_failures = 0
            logger.info("Circuit breaker closed, attempting to resume operations")
            return True

        return False

    def _get_cache_key(self, operation: str, *args) -> str:
        """Generate cache key for operation."""
        return f"{operation}:{hash(str(args))}"

    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Get item from cache with TTL check."""
        if key not in self._cache_timestamps:
            return None

        age = datetime.now() - self._cache_timestamps[key]
        if age.total_seconds() > self.config.cache_ttl_seconds:
            del self._operation_cache[key]
            del self._cache_timestamps[key]
            return None

        return self._operation_cache.get(key)

    def _put_in_cache(self, key: str, value: Any) -> None:
        """Put item in cache with timestamp."""
        self._operation_cache[key] = value
        self._cache_timestamps[key] = datetime.now()

    async def _record_operation_metrics(
        self, operation: str, duration: float, success: bool
    ) -> None:
        """Record operation metrics."""
        self._metrics.total_operations += 1
        if success:
            self._metrics.successful_operations += 1
        else:
            self._metrics.failed_operations += 1

        self._operation_durations.append(duration)
        if self._operation_durations:
            self._metrics.average_duration_ms = sum(self._operation_durations) / len(
                self._operation_durations
            )

        self._metrics.last_updated = datetime.now()

    async def create_async(
        self, authorization_context: "AuthorizationContext", element: T
    ) -> T:
        """Create an element asynchronously."""
        if not self.authorization_model.can_create(authorization_context, element):
            raise PermissionError(
                "Permission Denied: You do not have permission to create this entity."
            )

        if not self._check_circuit_breaker():
            raise RuntimeError("Circuit breaker is open")

        start_time = time.time()

        async with self._semaphore:
            try:
                if not self.enabled or self.g is None:
                    raise RuntimeError("Gremlin connection not available")

                # Execute create operation in thread pool
                result = await asyncio.get_event_loop().run_in_executor(
                    self._thread_pool, self._create_vertex_sync, element
                )

                duration = (time.time() - start_time) * 1000
                await self._record_operation_metrics("create", duration, True)

                # Reset circuit breaker on success
                self._circuit_breaker_failures = 0
                self._circuit_breaker_open = False

                return result

            except Exception as e:
                duration = (time.time() - start_time) * 1000
                await self._record_operation_metrics("create", duration, False)
                await self._handle_circuit_breaker_failure()
                raise RuntimeError(f"Failed to create entity: {e}")

    def _create_vertex_sync(self, element: T) -> T:
        """Create vertex synchronously (runs in thread pool)."""
        query = self.g.addV(getattr(element, "type", "vertex"))
        query = query.property("id", element.id)
        query = query.property("label", getattr(element, "label", ""))

        # Add other properties
        for attr_name in dir(element):
            if not attr_name.startswith("_") and attr_name not in [
                "id",
                "label",
                "type",
            ]:
                attr_value = getattr(element, attr_name)
                if not callable(attr_value):
                    query = query.property(attr_name, attr_value)

        query.next()
        return element

    async def read_by_id_async(
        self, authorization_context: "AuthorizationContext", id: ID
    ) -> T:
        """Read an element by ID asynchronously."""
        # Check cache first
        cache_key = self._get_cache_key("read_by_id", id)
        cached = self._get_from_cache(cache_key)
        if cached:
            element = cached
            if self.authorization_model.can_read(authorization_context, element):
                return element
            else:
                raise PermissionError(
                    "Permission Denied: You do not have permission to read this entity."
                )

        if not self._check_circuit_breaker():
            raise RuntimeError("Circuit breaker is open")

        start_time = time.time()

        async with self._semaphore:
            try:
                if not self.enabled or self.g is None:
                    raise RuntimeError("Gremlin connection not available")

                # Execute read operation in thread pool
                element = await asyncio.get_event_loop().run_in_executor(
                    self._thread_pool, self._read_vertex_sync, id
                )

                if not self.authorization_model.can_read(
                    authorization_context, element
                ):
                    raise PermissionError(
                        "Permission Denied: You do not have permission to read this entity."
                    )

                # Cache the result
                self._put_in_cache(cache_key, element)

                duration = (time.time() - start_time) * 1000
                await self._record_operation_metrics("read_by_id", duration, True)

                # Reset circuit breaker on success
                self._circuit_breaker_failures = 0
                self._circuit_breaker_open = False

                return element

            except Exception as e:
                duration = (time.time() - start_time) * 1000
                await self._record_operation_metrics("read_by_id", duration, False)
                await self._handle_circuit_breaker_failure()
                if "Permission Denied" in str(e):
                    raise e
                raise RuntimeError(f"Failed to read entity: {e}")

    def _read_vertex_sync(self, id: ID) -> T:
        """Read vertex synchronously (runs in thread pool)."""
        try:
            vertex = self.g.V().hasId(str(id)).next()
            return self._vertex_to_element(vertex)
        except StopIteration:
            raise ValueError("No Such Item Exists")

    async def update_async(
        self, authorization_context: "AuthorizationContext", element: T
    ) -> T:
        """Update an element asynchronously."""
        if not self.authorization_model.can_update(authorization_context, element):
            raise PermissionError(
                "Permission Denied: You do not have permission to update this entity."
            )

        if not self._check_circuit_breaker():
            raise RuntimeError("Circuit breaker is open")

        start_time = time.time()

        async with self._semaphore:
            try:
                if not self.enabled or self.g is None:
                    raise RuntimeError("Gremlin connection not available")

                # Execute update operation in thread pool
                result = await asyncio.get_event_loop().run_in_executor(
                    self._thread_pool, self._update_vertex_sync, element
                )

                # Invalidate cache
                cache_key = self._get_cache_key("read_by_id", element.id)
                if cache_key in self._operation_cache:
                    del self._operation_cache[cache_key]
                    del self._cache_timestamps[cache_key]

                duration = (time.time() - start_time) * 1000
                await self._record_operation_metrics("update", duration, True)

                # Reset circuit breaker on success
                self._circuit_breaker_failures = 0
                self._circuit_breaker_open = False

                return result

            except Exception as e:
                duration = (time.time() - start_time) * 1000
                await self._record_operation_metrics("update", duration, False)
                await self._handle_circuit_breaker_failure()
                raise RuntimeError(f"Failed to update entity: {e}")

    def _update_vertex_sync(self, element: T) -> T:
        """Update vertex synchronously (runs in thread pool)."""
        query = self.g.V().hasId(element.id)

        # Update properties
        for attr_name in dir(element):
            if not attr_name.startswith("_") and attr_name not in ["id"]:
                attr_value = getattr(element, attr_name)
                if not callable(attr_value):
                    query = query.property(attr_name, attr_value)

        query.next()
        return element

    async def delete_async(
        self, authorization_context: "AuthorizationContext", element: T
    ) -> None:
        """Delete an element asynchronously."""
        if not self.authorization_model.can_delete(authorization_context, element):
            raise PermissionError(
                "Permission Denied: You do not have permission to delete this entity."
            )

        if not self._check_circuit_breaker():
            raise RuntimeError("Circuit breaker is open")

        start_time = time.time()

        async with self._semaphore:
            try:
                if not self.enabled or self.g is None:
                    raise RuntimeError("Gremlin connection not available")

                # Execute delete operation in thread pool
                await asyncio.get_event_loop().run_in_executor(
                    self._thread_pool, self._delete_vertex_sync, element.id
                )

                # Invalidate cache
                cache_key = self._get_cache_key("read_by_id", element.id)
                if cache_key in self._operation_cache:
                    del self._operation_cache[cache_key]
                    del self._cache_timestamps[cache_key]

                duration = (time.time() - start_time) * 1000
                await self._record_operation_metrics("delete", duration, True)

                # Reset circuit breaker on success
                self._circuit_breaker_failures = 0
                self._circuit_breaker_open = False

            except Exception as e:
                duration = (time.time() - start_time) * 1000
                await self._record_operation_metrics("delete", duration, False)
                await self._handle_circuit_breaker_failure()
                raise RuntimeError(f"Failed to delete entity: {e}")

    def _delete_vertex_sync(self, id: ID) -> None:
        """Delete vertex synchronously (runs in thread pool)."""
        self.g.V().hasId(str(id)).drop().iterate()

    async def filter_async(
        self,
        authorization_context: "AuthorizationContext",
        properties: Dict[str, Any],
        limit: Optional[int] = None,
    ) -> AsyncGenerator[T, None]:
        """Filter elements asynchronously with streaming results."""
        if not self._check_circuit_breaker():
            raise RuntimeError("Circuit breaker is open")

        start_time = time.time()

        async with self._semaphore:
            try:
                if not self.enabled or self.g is None:
                    raise RuntimeError("Gremlin connection not available")

                # Execute filter operation in thread pool
                vertices = await asyncio.get_event_loop().run_in_executor(
                    self._thread_pool, self._filter_vertices_sync, properties, limit
                )

                # Stream authorized results
                count = 0
                for vertex in vertices:
                    element = self._vertex_to_element(vertex)
                    if self.authorization_model.can_read(
                        authorization_context, element
                    ):
                        yield element
                        count += 1

                duration = (time.time() - start_time) * 1000
                await self._record_operation_metrics("filter", duration, True)

                # Reset circuit breaker on success
                self._circuit_breaker_failures = 0
                self._circuit_breaker_open = False

            except Exception as e:
                duration = (time.time() - start_time) * 1000
                await self._record_operation_metrics("filter", duration, False)
                await self._handle_circuit_breaker_failure()
                raise RuntimeError(f"Failed to filter entities: {e}")

    def _filter_vertices_sync(
        self, properties: Dict[str, Any], limit: Optional[int]
    ) -> List[Any]:
        """Filter vertices synchronously (runs in thread pool)."""
        query = self.g.V()

        # Add property filters
        for key, value in properties.items():
            query = query.has(key, value)

        if limit:
            query = query.limit(limit)

        return query.toList()

    async def batch_create_async(
        self, authorization_context: "AuthorizationContext", elements: List[T]
    ) -> BatchResult:
        """Create multiple elements in batches."""
        successful_items = []
        failed_items = []
        errors = []

        # Filter authorized elements
        authorized_elements = []
        for element in elements:
            if self.authorization_model.can_create(authorization_context, element):
                authorized_elements.append(element)
            else:
                failed_items.append(element)
                errors.append(f"Permission denied for element {element.id}")

        # Process in batches
        for i in range(0, len(authorized_elements), self.config.batch_size):
            batch = authorized_elements[i : i + self.config.batch_size]
            batch_tasks = [
                self.create_async(authorization_context, element) for element in batch
            ]

            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

            for element, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    failed_items.append(element)
                    errors.append(str(result))
                else:
                    successful_items.append(result)

        return BatchResult(
            successful_count=len(successful_items),
            failed_count=len(failed_items),
            total_count=len(elements),
            errors=errors,
            successful_items=successful_items,
            failed_items=failed_items,
        )

    async def get_metrics_stream(self) -> AsyncGenerator[RepositoryMetrics, None]:
        """Get a stream of repository metrics."""
        while not self._shutdown_event.is_set():
            # Calculate cache hit rate
            total_cache_ops = (
                len(self._operation_cache) + self._metrics.total_operations
            )
            cache_hits = len(self._operation_cache)
            self._metrics.cache_hit_rate = (
                cache_hits / total_cache_ops if total_cache_ops > 0 else 0.0
            )
            self._metrics.circuit_breaker_open = self._circuit_breaker_open

            yield self._metrics
            await asyncio.sleep(1)

    def get_health_status(self) -> Dict[str, Any]:
        """Get repository health status."""
        return {
            "enabled": self.enabled,
            "circuit_breaker_open": self._circuit_breaker_open,
            "connection_available": self.g is not None,
            "cache_size": len(self._operation_cache),
            "total_operations": self._metrics.total_operations,
            "success_rate": (
                self._metrics.successful_operations / self._metrics.total_operations
                if self._metrics.total_operations > 0
                else 0.0
            ),
            "average_duration_ms": self._metrics.average_duration_ms,
            "failures": self._circuit_breaker_failures,
        }

    def _vertex_to_element(self, vertex: Any) -> T:
        """Convert a Gremlin vertex to an element object."""
        if not self.element_type:
            raise RuntimeError("Element type not specified")

        # Extract vertex properties
        vertex_id = (
            getattr(vertex, "id", str(vertex)) if hasattr(vertex, "id") else str(vertex)
        )
        properties = {}

        if hasattr(vertex, "properties"):
            for prop_name, prop_value in vertex.properties.items():
                properties[prop_name] = prop_value

        # Create element with extracted properties
        try:
            return self.element_type(id=vertex_id, **properties)  # type: ignore
        except Exception:
            # Fallback to basic element creation
            return self.element_type(id=vertex_id)  # type: ignore

    # Sync wrapper methods for backward compatibility
    def create(self, authorization_context: "AuthorizationContext", element: T) -> T:
        """Create element (sync wrapper)."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # In async context, this will fail - user should use async method
                raise RuntimeError("Use create_async() in async context")
            else:
                return loop.run_until_complete(
                    self.create_async(authorization_context, element)
                )
        except RuntimeError:
            return asyncio.run(self.create_async(authorization_context, element))

    def read_by_id(self, authorization_context: "AuthorizationContext", id: ID) -> T:
        """Read by ID (sync wrapper)."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                raise RuntimeError("Use read_by_id_async() in async context")
            else:
                return loop.run_until_complete(
                    self.read_by_id_async(authorization_context, id)
                )
        except RuntimeError:
            return asyncio.run(self.read_by_id_async(authorization_context, id))

    def update(self, authorization_context: "AuthorizationContext", element: T) -> T:
        """Update element (sync wrapper)."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                raise RuntimeError("Use update_async() in async context")
            else:
                return loop.run_until_complete(
                    self.update_async(authorization_context, element)
                )
        except RuntimeError:
            return asyncio.run(self.update_async(authorization_context, element))

    def delete(self, authorization_context: "AuthorizationContext", element: T) -> None:
        """Delete element (sync wrapper)."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                raise RuntimeError("Use delete_async() in async context")
            else:
                loop.run_until_complete(
                    self.delete_async(authorization_context, element)
                )
        except RuntimeError:
            asyncio.run(self.delete_async(authorization_context, element))

    async def shutdown(self) -> None:
        """Gracefully shutdown the repository."""
        self._shutdown_event.set()

        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()

        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)

        # Close connection
        if self.connection:
            try:
                await asyncio.get_event_loop().run_in_executor(
                    self._thread_pool, self.connection.close
                )
            except Exception as e:
                logger.error(f"Error closing Gremlin connection: {e}")

        # Shutdown thread pool
        self._thread_pool.shutdown(wait=True)
