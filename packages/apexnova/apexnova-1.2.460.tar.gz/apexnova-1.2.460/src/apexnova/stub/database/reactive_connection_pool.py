"""
Modern reactive database connection pool and management system.

Features:
- Reactive connection pooling with asyncio
- Connection health monitoring and validation
- Transaction management with coroutines
- Query execution with prepared statements
- Connection lifecycle management
- Pool metrics and monitoring
- Automatic connection recovery
- Batch operation support
- Query result streaming
"""

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, AsyncIterator, TypeVar
from contextlib import asynccontextmanager
import threading
from collections import deque

# For database connectivity, we'll use a generic interface
# In production, you'd use specific drivers like asyncpg, aiomysql, etc.
try:
    import asyncpg  # PostgreSQL async driver

    HAS_ASYNCPG = True
except ImportError:
    HAS_ASYNCPG = False

logger = logging.getLogger(__name__)

T = TypeVar("T")


class PoolState(Enum):
    """Connection pool state."""

    STARTING = "STARTING"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"


@dataclass
class DatabaseConfig:
    """Database connection configuration."""

    url: str
    username: str
    password: str
    driver_name: str
    min_pool_size: int = 5
    max_pool_size: int = 20
    connection_timeout: timedelta = field(default_factory=lambda: timedelta(seconds=30))
    idle_timeout: timedelta = field(default_factory=lambda: timedelta(minutes=10))
    max_lifetime: timedelta = field(default_factory=lambda: timedelta(minutes=30))
    validation_query: str = "SELECT 1"
    validation_timeout: timedelta = field(default_factory=lambda: timedelta(seconds=5))
    leak_detection_threshold: timedelta = field(
        default_factory=lambda: timedelta(seconds=60)
    )
    enable_health_checks: bool = True
    health_check_interval: timedelta = field(
        default_factory=lambda: timedelta(minutes=1)
    )


@dataclass
class PooledConnection:
    """Connection wrapper with metadata."""

    connection: Any  # Generic connection object
    id: str
    created_at: datetime = field(default_factory=datetime.now)
    last_used: datetime = field(default_factory=datetime.now)
    use_count: int = 0
    is_healthy: bool = True

    @property
    def age(self) -> timedelta:
        """Get connection age."""
        return datetime.now() - self.created_at

    @property
    def idle_time(self) -> timedelta:
        """Get idle time."""
        return datetime.now() - self.last_used

    def mark_used(self) -> "PooledConnection":
        """Mark connection as used."""
        self.last_used = datetime.now()
        self.use_count += 1
        return self

    def mark_unhealthy(self) -> "PooledConnection":
        """Mark connection as unhealthy."""
        self.is_healthy = False
        return self


@dataclass
class PoolMetrics:
    """Connection pool metrics."""

    active_connections: int = 0
    idle_connections: int = 0
    total_connections: int = 0
    connections_created: int = 0
    connections_destroyed: int = 0
    connections_leaked: int = 0
    connections_failed: int = 0
    average_connection_time: timedelta = timedelta()
    average_query_time: timedelta = timedelta()
    pool_utilization: float = 0.0
    health_checks_passed: int = 0
    health_checks_failed: int = 0


@dataclass
class QueryResult:
    """Query result wrapper."""

    rows: List[Dict[str, Any]]
    affected_rows: int = 0
    execution_time: timedelta = timedelta()
    metadata: "QueryMetadata" = None


@dataclass
class QueryMetadata:
    """Query execution metadata."""

    query: str
    parameters: List[Any]
    execution_time: timedelta
    connection_id: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TransactionContext:
    """Transaction context."""

    connection: PooledConnection
    isolation_level: str
    is_read_only: bool = False
    start_time: datetime = field(default_factory=datetime.now)


# Custom exceptions
class ConnectionPoolException(Exception):
    """Base connection pool exception."""

    pass


class ConnectionLeakException(ConnectionPoolException):
    """Connection leak detected."""

    pass


class QueryExecutionException(Exception):
    """Query execution failed."""

    pass


class ReactiveConnectionPool:
    """
    Reactive database connection pool.

    This is a generic implementation that can be adapted for different database drivers.
    """

    def __init__(self, config: DatabaseConfig):
        """
        Initialize connection pool.

        Args:
            config: Database configuration
        """
        self.config = config
        self.pool_state = PoolState.STARTING

        # Connection management
        self.available_connections: asyncio.Queue[PooledConnection] = asyncio.Queue(
            maxsize=config.max_pool_size
        )
        self.active_connections: Dict[str, PooledConnection] = {}
        self.all_connections: Dict[str, PooledConnection] = {}

        # Metrics
        self.connections_created = 0
        self.connections_destroyed = 0
        self.connections_leaked = 0
        self.connections_failed = 0
        self.health_checks_passed = 0
        self.health_checks_failed = 0
        self.connection_times: deque[float] = deque(maxlen=1000)
        self.query_times: deque[float] = deque(maxlen=1000)

        # Synchronization
        self._lock = asyncio.Lock()
        self._creation_semaphore = asyncio.Semaphore(config.max_pool_size)

        # Background tasks
        self._tasks: List[asyncio.Task] = []

        logger.info(
            f"Initializing connection pool with min={config.min_pool_size}, max={config.max_pool_size}"
        )

    async def initialize(self) -> None:
        """Initialize the connection pool."""
        try:
            # Create initial connections
            initial_connections = []
            for _ in range(self.config.min_pool_size):
                conn = await self._create_connection()
                if conn:
                    initial_connections.append(conn)

            # Add to available pool
            for conn in initial_connections:
                await self.available_connections.put(conn)

            self.pool_state = PoolState.RUNNING
            logger.info(
                f"Connection pool initialized with {len(initial_connections)} connections"
            )

            # Start background tasks
            if self.config.enable_health_checks:
                self._tasks.append(asyncio.create_task(self._health_check_task()))
            self._tasks.append(asyncio.create_task(self._maintenance_task()))
            self._tasks.append(asyncio.create_task(self._leak_detection_task()))

        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            self.pool_state = PoolState.STOPPED
            raise ConnectionPoolException(f"Pool initialization failed: {e}")

    async def get_connection(self) -> PooledConnection:
        """Get a connection from the pool."""
        if self.pool_state != PoolState.RUNNING:
            raise ConnectionPoolException("Connection pool is not running")

        start_time = time.time()

        try:
            # Try to get an available connection with timeout
            try:
                connection = await asyncio.wait_for(
                    self.available_connections.get(),
                    timeout=self.config.connection_timeout.total_seconds(),
                )
            except asyncio.TimeoutError:
                # Try to create a new connection if pool not full
                connection = await self._create_connection()
                if not connection:
                    raise ConnectionPoolException(
                        "Unable to obtain connection within timeout"
                    )

            # Validate connection health
            if not await self._is_connection_healthy(connection):
                await self._destroy_connection(connection)
                return await self.get_connection()  # Recursive call

            # Mark as active
            connection = connection.mark_used()
            async with self._lock:
                self.active_connections[connection.id] = connection
                self.all_connections[connection.id] = connection

            # Record metrics
            connection_time = time.time() - start_time
            async with self._lock:
                self.connection_times.append(connection_time)

            return connection

        except Exception as e:
            self.connections_failed += 1
            raise ConnectionPoolException(f"Failed to get connection: {e}")

    async def return_connection(self, connection: PooledConnection) -> None:
        """Return a connection to the pool."""
        async with self._lock:
            self.active_connections.pop(connection.id, None)

        if (
            await self._is_connection_healthy(connection)
            and self.pool_state == PoolState.RUNNING
        ):
            try:
                await self.available_connections.put(connection)
            except:
                # Queue might be full or closed
                await self._destroy_connection(connection)
        else:
            await self._destroy_connection(connection)

    @asynccontextmanager
    async def connection(self):
        """Context manager for connection usage."""
        conn = await self.get_connection()
        try:
            yield conn.connection
        finally:
            await self.return_connection(conn)

    @asynccontextmanager
    async def transaction(
        self, isolation_level: str = "READ COMMITTED", read_only: bool = False
    ):
        """
        Context manager for transactions.

        Args:
            isolation_level: Transaction isolation level
            read_only: Whether transaction is read-only
        """
        conn = await self.get_connection()

        # This is a generic implementation
        # Specific database drivers would have their own transaction APIs
        try:
            # Start transaction (implementation depends on driver)
            if hasattr(conn.connection, "transaction"):
                async with conn.connection.transaction():
                    yield TransactionContext(conn, isolation_level, read_only)
            else:
                # Fallback for drivers without context manager support
                await self._begin_transaction(
                    conn.connection, isolation_level, read_only
                )
                try:
                    yield TransactionContext(conn, isolation_level, read_only)
                    await self._commit_transaction(conn.connection)
                except Exception:
                    await self._rollback_transaction(conn.connection)
                    raise
        finally:
            await self.return_connection(conn)

    async def execute_query(
        self, query: str, parameters: Optional[List[Any]] = None
    ) -> QueryResult:
        """
        Execute a query and return results.

        Args:
            query: SQL query
            parameters: Query parameters

        Returns:
            Query result
        """
        parameters = parameters or []
        start_time = time.time()

        async with self.connection() as conn:
            rows = await self._execute_query_internal(conn, query, parameters)

            execution_time = timedelta(seconds=time.time() - start_time)
            async with self._lock:
                self.query_times.append(execution_time.total_seconds())

            return QueryResult(
                rows=rows,
                execution_time=execution_time,
                metadata=QueryMetadata(
                    query=query,
                    parameters=parameters,
                    execution_time=execution_time,
                    connection_id="unknown",
                ),
            )

    async def execute_update(
        self, query: str, parameters: Optional[List[Any]] = None
    ) -> int:
        """
        Execute an update query.

        Args:
            query: SQL query
            parameters: Query parameters

        Returns:
            Number of affected rows
        """
        parameters = parameters or []
        start_time = time.time()

        async with self.connection() as conn:
            affected_rows = await self._execute_update_internal(conn, query, parameters)

            execution_time = time.time() - start_time
            async with self._lock:
                self.query_times.append(execution_time)

            return affected_rows

    async def execute_batch(
        self, query: str, parameters_list: List[List[Any]]
    ) -> List[int]:
        """
        Execute batch operations.

        Args:
            query: SQL query
            parameters_list: List of parameter sets

        Returns:
            List of affected rows for each operation
        """
        results = []

        async with self.connection() as conn:
            for parameters in parameters_list:
                affected_rows = await self._execute_update_internal(
                    conn, query, parameters
                )
                results.append(affected_rows)

        return results

    async def execute_query_stream(
        self, query: str, parameters: Optional[List[Any]] = None, fetch_size: int = 1000
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream query results for large datasets.

        Args:
            query: SQL query
            parameters: Query parameters
            fetch_size: Number of rows to fetch at a time

        Yields:
            Row dictionaries
        """
        parameters = parameters or []

        async with self.connection() as conn:
            # This is a generic implementation
            # Specific drivers would have their own streaming APIs
            async for row in self._execute_query_stream_internal(
                conn, query, parameters, fetch_size
            ):
                yield row

    async def get_metrics(self) -> PoolMetrics:
        """Get pool metrics."""
        async with self._lock:
            total_connections = len(self.all_connections)
            active_count = len(self.active_connections)
            idle_count = total_connections - active_count

            avg_connection_time = (
                timedelta(
                    seconds=sum(self.connection_times) / len(self.connection_times)
                )
                if self.connection_times
                else timedelta()
            )

            avg_query_time = (
                timedelta(seconds=sum(self.query_times) / len(self.query_times))
                if self.query_times
                else timedelta()
            )

            utilization = (
                active_count / self.config.max_pool_size
                if self.config.max_pool_size > 0
                else 0.0
            )

            return PoolMetrics(
                active_connections=active_count,
                idle_connections=idle_count,
                total_connections=total_connections,
                connections_created=self.connections_created,
                connections_destroyed=self.connections_destroyed,
                connections_leaked=self.connections_leaked,
                connections_failed=self.connections_failed,
                average_connection_time=avg_connection_time,
                average_query_time=avg_query_time,
                pool_utilization=utilization,
                health_checks_passed=self.health_checks_passed,
                health_checks_failed=self.health_checks_failed,
            )

    async def is_healthy(self) -> bool:
        """Check if pool is healthy."""
        if self.pool_state != PoolState.RUNNING:
            return False

        healthy_connections = sum(
            1 for conn in self.all_connections.values() if conn.is_healthy
        )
        return healthy_connections >= self.config.min_pool_size

    async def shutdown(self) -> None:
        """Shutdown the connection pool."""
        logger.info("Shutting down connection pool...")
        self.pool_state = PoolState.STOPPING

        # Cancel background tasks
        for task in self._tasks:
            task.cancel()

        # Wait for tasks to complete
        await asyncio.gather(*self._tasks, return_exceptions=True)

        # Close all connections
        connections_to_close = list(self.all_connections.values())
        for connection in connections_to_close:
            await self._destroy_connection(connection)

        self.active_connections.clear()
        self.all_connections.clear()

        self.pool_state = PoolState.STOPPED
        logger.info("Connection pool shutdown complete")

    # Private methods
    async def _create_connection(self) -> Optional[PooledConnection]:
        """Create a new connection."""
        async with self._creation_semaphore:
            if len(self.all_connections) >= self.config.max_pool_size:
                return None

            try:
                # This is where you'd create the actual database connection
                # For example, with asyncpg:
                # connection = await asyncpg.connect(...)

                # For this generic implementation, we'll create a mock connection
                connection = await self._create_raw_connection()

                pooled_connection = PooledConnection(
                    connection=connection, id=f"conn-{uuid.uuid4()}"
                )

                async with self._lock:
                    self.all_connections[pooled_connection.id] = pooled_connection
                    self.connections_created += 1

                logger.debug(f"Created new connection: {pooled_connection.id}")
                return pooled_connection

            except Exception as e:
                self.connections_failed += 1
                logger.error(f"Failed to create connection: {e}")
                return None

    async def _destroy_connection(self, connection: PooledConnection) -> None:
        """Destroy a connection."""
        try:
            # Close the actual database connection
            await self._close_raw_connection(connection.connection)

            async with self._lock:
                self.all_connections.pop(connection.id, None)
                self.active_connections.pop(connection.id, None)
                self.connections_destroyed += 1

            logger.debug(f"Destroyed connection: {connection.id}")

        except Exception as e:
            logger.error(f"Failed to destroy connection {connection.id}: {e}")

    async def _is_connection_healthy(self, connection: PooledConnection) -> bool:
        """Check if connection is healthy."""
        try:
            # Execute validation query
            await asyncio.wait_for(
                self._execute_validation_query(connection.connection),
                timeout=self.config.validation_timeout.total_seconds(),
            )
            return True
        except Exception as e:
            logger.warning(f"Connection health check failed for {connection.id}: {e}")
            return False

    # Database-specific methods (to be implemented for specific drivers)
    async def _create_raw_connection(self) -> Any:
        """Create raw database connection (driver-specific)."""
        # This would be implemented for specific database drivers
        # For example, with asyncpg:
        # return await asyncpg.connect(
        #     host=self.config.host,
        #     port=self.config.port,
        #     user=self.config.username,
        #     password=self.config.password,
        #     database=self.config.database
        # )

        # Mock implementation
        class MockConnection:
            async def execute(self, query, *args):
                return []

            async def fetch(self, query, *args):
                return []

            async def close(self):
                pass

        return MockConnection()

    async def _close_raw_connection(self, connection: Any) -> None:
        """Close raw database connection (driver-specific)."""
        if hasattr(connection, "close"):
            await connection.close()

    async def _execute_validation_query(self, connection: Any) -> None:
        """Execute validation query (driver-specific)."""
        if hasattr(connection, "execute"):
            await connection.execute(self.config.validation_query)

    async def _execute_query_internal(
        self, connection: Any, query: str, parameters: List[Any]
    ) -> List[Dict[str, Any]]:
        """Execute query and return rows (driver-specific)."""
        if hasattr(connection, "fetch"):
            rows = await connection.fetch(query, *parameters)
            # Convert to list of dicts (implementation depends on driver)
            return [dict(row) for row in rows] if rows else []
        return []

    async def _execute_update_internal(
        self, connection: Any, query: str, parameters: List[Any]
    ) -> int:
        """Execute update and return affected rows (driver-specific)."""
        if hasattr(connection, "execute"):
            result = await connection.execute(query, *parameters)
            # Extract affected rows count (implementation depends on driver)
            return 0
        return 0

    async def _execute_query_stream_internal(
        self, connection: Any, query: str, parameters: List[Any], fetch_size: int
    ) -> AsyncIterator[Dict[str, Any]]:
        """Stream query results (driver-specific)."""
        # Mock implementation
        rows = await self._execute_query_internal(connection, query, parameters)
        for row in rows:
            yield row

    async def _begin_transaction(
        self, connection: Any, isolation_level: str, read_only: bool
    ) -> None:
        """Begin transaction (driver-specific)."""
        pass

    async def _commit_transaction(self, connection: Any) -> None:
        """Commit transaction (driver-specific)."""
        pass

    async def _rollback_transaction(self, connection: Any) -> None:
        """Rollback transaction (driver-specific)."""
        pass

    # Background tasks
    async def _health_check_task(self) -> None:
        """Periodic health check task."""
        while self.pool_state == PoolState.RUNNING:
            try:
                await asyncio.sleep(self.config.health_check_interval.total_seconds())
                await self._perform_health_checks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check task error: {e}")

    async def _maintenance_task(self) -> None:
        """Connection maintenance task."""
        while self.pool_state == PoolState.RUNNING:
            try:
                await asyncio.sleep(60)  # Run every minute
                await self._perform_maintenance()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Maintenance task error: {e}")

    async def _leak_detection_task(self) -> None:
        """Connection leak detection task."""
        while self.pool_state == PoolState.RUNNING:
            try:
                await asyncio.sleep(
                    self.config.leak_detection_threshold.total_seconds()
                )
                await self._detect_leaked_connections()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Leak detection task error: {e}")

    async def _perform_health_checks(self) -> None:
        """Perform health checks on all connections."""
        connections_to_check = list(self.all_connections.values())

        for connection in connections_to_check:
            if await self._is_connection_healthy(connection):
                self.health_checks_passed += 1
            else:
                self.health_checks_failed += 1
                connection.mark_unhealthy()

                # Remove from active connections if unhealthy
                async with self._lock:
                    self.active_connections.pop(connection.id, None)

                await self._destroy_connection(connection)

    async def _perform_maintenance(self) -> None:
        """Perform connection maintenance."""
        now = datetime.now()
        connections_to_remove = []

        for connection in self.all_connections.values():
            # Remove connections that have exceeded max lifetime
            if connection.age > self.config.max_lifetime:
                connections_to_remove.append(connection)
            # Remove idle connections that have exceeded idle timeout
            elif (
                connection.idle_time > self.config.idle_timeout
                and len(self.all_connections) > self.config.min_pool_size
            ):
                connections_to_remove.append(connection)

        for connection in connections_to_remove:
            await self._destroy_connection(connection)

    async def _detect_leaked_connections(self) -> None:
        """Detect potentially leaked connections."""
        now = datetime.now()
        leak_threshold = now - self.config.leak_detection_threshold

        for connection in self.active_connections.values():
            if connection.last_used < leak_threshold:
                logger.warning(f"Potential connection leak detected: {connection.id}")
                self.connections_leaked += 1


class ConnectionPoolBuilder:
    """Builder for creating connection pools."""

    def __init__(self):
        """Initialize builder."""
        self._config = DatabaseConfig("", "", "", "")

    def config(
        self, url: str, username: str, password: str, driver_name: str
    ) -> "ConnectionPoolBuilder":
        """Set database configuration."""
        self._config.url = url
        self._config.username = username
        self._config.password = password
        self._config.driver_name = driver_name
        return self

    def pool_size(self, min_size: int, max_size: int) -> "ConnectionPoolBuilder":
        """Set pool size."""
        self._config.min_pool_size = min_size
        self._config.max_pool_size = max_size
        return self

    def timeouts(
        self, connection: timedelta, idle: timedelta, max_lifetime: timedelta
    ) -> "ConnectionPoolBuilder":
        """Set timeout configuration."""
        self._config.connection_timeout = connection
        self._config.idle_timeout = idle
        self._config.max_lifetime = max_lifetime
        return self

    def validation(self, query: str, timeout: timedelta) -> "ConnectionPoolBuilder":
        """Set validation configuration."""
        self._config.validation_query = query
        self._config.validation_timeout = timeout
        return self

    def health_checks(
        self, enabled: bool, interval: timedelta
    ) -> "ConnectionPoolBuilder":
        """Set health check configuration."""
        self._config.enable_health_checks = enabled
        self._config.health_check_interval = interval
        return self

    def build(self) -> ReactiveConnectionPool:
        """Build connection pool."""
        return ReactiveConnectionPool(self._config)


def connection_pool(
    builder_fn: Callable[[ConnectionPoolBuilder], None],
) -> ReactiveConnectionPool:
    """
    DSL function to create connection pool.

    Example:
        pool = connection_pool(lambda b: b
            .config("postgresql://localhost/db", "user", "pass", "postgresql")
            .pool_size(5, 20)
            .health_checks(True, timedelta(minutes=1))
        )
    """
    builder = ConnectionPoolBuilder()
    builder_fn(builder)
    return builder.build()


# Extension functions for easier usage
async def query_for_object(
    pool: ReactiveConnectionPool,
    query: str,
    parameters: Optional[List[Any]] = None,
    mapper: Optional[Callable[[Dict[str, Any]], T]] = None,
) -> Optional[T]:
    """Query for single object."""
    result = await pool.execute_query(query, parameters)
    if result.rows:
        row = result.rows[0]
        return mapper(row) if mapper else row
    return None


async def query_for_list(
    pool: ReactiveConnectionPool,
    query: str,
    parameters: Optional[List[Any]] = None,
    mapper: Optional[Callable[[Dict[str, Any]], T]] = None,
) -> List[T]:
    """Query for list of objects."""
    result = await pool.execute_query(query, parameters)
    if mapper:
        return [mapper(row) for row in result.rows]
    return result.rows
