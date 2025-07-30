"""Database module for ApexNova stub."""

from .database_configuration import DatabaseConfiguration
from .reactive_connection_pool import (
    DatabaseConfig,
    PooledConnection,
    PoolState,
    PoolMetrics,
    QueryResult,
    QueryMetadata,
    TransactionContext,
    ConnectionPoolException,
    ConnectionLeakException,
    QueryExecutionException,
    ReactiveConnectionPool,
    ConnectionPoolBuilder,
    connection_pool,
)

__all__ = [
    # Database Configuration
    "DatabaseConfiguration",
    # Reactive Connection Pool
    "DatabaseConfig",
    "PooledConnection",
    "PoolState",
    "PoolMetrics",
    "QueryResult",
    "QueryMetadata",
    "TransactionContext",
    "ConnectionPoolException",
    "ConnectionLeakException",
    "QueryExecutionException",
    "ReactiveConnectionPool",
    "ConnectionPoolBuilder",
    "connection_pool",
]
