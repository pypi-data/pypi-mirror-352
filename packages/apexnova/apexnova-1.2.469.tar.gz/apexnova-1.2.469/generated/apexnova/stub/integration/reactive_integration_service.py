"""Reactive integration service combining all reactive components with async/reactive patterns."""

import asyncio
import time
from dataclasses import dataclass, field
from typing import (
    Dict,
    Any,
    Optional,
    List,
    AsyncGenerator,
    Union,
    TypeVar,
    Generic,
    Callable,
    Type,
    Tuple,
)
import logging
from collections import defaultdict
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor

# Import reactive components
from ..service.reactive_application_insights_service import (
    ReactiveApplicationInsightsService,
)
from ..service.reactive_request_handler_service import ReactiveRequestHandlerService
from ..repository.reactive_gremlin_authorization_repository import (
    ReactiveGremlinAuthorizationRepository,
)
from ..repository.reactive_authorization_cosmos_repository import (
    ReactiveAuthorizationCosmosRepository,
)
from ..security.reactive_secret_util import ReactiveSecretUtil, JWTToken

# Conditional imports for graceful degradation
try:
    from apexnova.stub.authorization_context_pb2 import AuthorizationContext
    from apexnova.stub.response_pb2 import ResponseStatus

    _HAS_PROTOBUF = True
except ImportError:
    AuthorizationContext = Any
    ResponseStatus = Any
    _HAS_PROTOBUF = False

from ..model.base_model import IBaseModel

T = TypeVar("T", bound=IBaseModel)
AM = TypeVar("AM")
ID = TypeVar("ID")

logger = logging.getLogger(__name__)


@dataclass
class IntegrationMetrics:
    """Integration service metrics."""

    service_health: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    operation_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    error_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    average_latencies: Dict[str, float] = field(default_factory=dict)
    active_connections: int = 0

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


@dataclass
class CircuitBreakerState:
    """Circuit breaker state for fault tolerance."""

    failure_count: int = 0
    last_failure_time: float = 0
    state: str = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    failure_threshold: int = 10
    recovery_timeout: int = 120  # 2 minutes for integration service
    half_open_max_calls: int = 5
    half_open_calls: int = 0


@dataclass
class ServiceConfiguration:
    """Configuration for reactive services."""

    max_concurrent_operations: int = 100
    enable_caching: bool = True
    cache_ttl: int = 300
    circuit_breaker_failure_threshold: int = 10
    circuit_breaker_recovery_timeout: int = 120
    thread_pool_size: int = 20
    enable_detailed_metrics: bool = True
    request_timeout: float = 30.0
    jwt_expiry_seconds: int = 3600


class ReactiveIntegrationService(Generic[AM, T, ID]):
    """
    Reactive integration service that orchestrates all reactive components
    with comprehensive monitoring, circuit breaking, and health management.
    """

    def __init__(
        self,
        config: Optional[ServiceConfiguration] = None,
        application_insights_service: Optional[
            ReactiveApplicationInsightsService
        ] = None,
        request_handler_service: Optional[ReactiveRequestHandlerService] = None,
        gremlin_repository: Optional[ReactiveGremlinAuthorizationRepository] = None,
        cosmos_repository: Optional[ReactiveAuthorizationCosmosRepository] = None,
        secret_util: Optional[ReactiveSecretUtil] = None,
    ):
        """
        Initialize reactive integration service.

        Args:
            config: Service configuration
            application_insights_service: Optional pre-configured telemetry service
            request_handler_service: Optional pre-configured request handler
            gremlin_repository: Optional pre-configured Gremlin repository
            cosmos_repository: Optional pre-configured Cosmos repository
            secret_util: Optional pre-configured security utilities
        """
        self._config = config or ServiceConfiguration()

        # Initialize or use provided services
        self._app_insights = application_insights_service or ReactiveApplicationInsightsService(
            max_concurrent_operations=self._config.max_concurrent_operations,
            enable_caching=self._config.enable_caching,
            cache_ttl=self._config.cache_ttl,
            circuit_breaker_failure_threshold=self._config.circuit_breaker_failure_threshold,
            circuit_breaker_recovery_timeout=self._config.circuit_breaker_recovery_timeout,
            thread_pool_size=self._config.thread_pool_size,
        )

        self._request_handler = request_handler_service or ReactiveRequestHandlerService(
            application_insights_service=self._app_insights,
            max_concurrent_requests=self._config.max_concurrent_operations,
            circuit_breaker_failure_threshold=self._config.circuit_breaker_failure_threshold,
            circuit_breaker_recovery_timeout=self._config.circuit_breaker_recovery_timeout,
            thread_pool_size=self._config.thread_pool_size,
            enable_detailed_metrics=self._config.enable_detailed_metrics,
            request_timeout=self._config.request_timeout,
        )

        self._secret_util = secret_util or ReactiveSecretUtil(
            default_jwt_expiry=self._config.jwt_expiry_seconds,
            max_concurrent_operations=self._config.max_concurrent_operations,
            enable_caching=self._config.enable_caching,
            cache_ttl=self._config.cache_ttl,
            circuit_breaker_failure_threshold=self._config.circuit_breaker_failure_threshold,
            circuit_breaker_recovery_timeout=self._config.circuit_breaker_recovery_timeout,
            thread_pool_size=self._config.thread_pool_size,
        )

        # Optional repositories (can be provided later)
        self._gremlin_repo = gremlin_repository
        self._cosmos_repo = cosmos_repository

        # Integration service state
        self._circuit_breaker = CircuitBreakerState(
            failure_threshold=self._config.circuit_breaker_failure_threshold,
            recovery_timeout=self._config.circuit_breaker_recovery_timeout,
        )

        # Metrics and monitoring
        self._metrics = IntegrationMetrics()
        self._metrics_lock = asyncio.Lock()

        # Health monitoring task
        self._health_task: Optional[asyncio.Task] = None
        self._start_health_monitoring()

    def _start_health_monitoring(self):
        """Start background health monitoring task."""
        if self._health_task is None or self._health_task.done():
            self._health_task = asyncio.create_task(self._monitor_health_periodically())

    async def _monitor_health_periodically(self):
        """Periodically monitor health of all services."""
        while True:
            try:
                await asyncio.sleep(30)  # Check health every 30 seconds
                await self._update_service_health()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"Health monitoring error: {e}")

    async def _update_service_health(self):
        """Update health status of all services."""
        async with self._metrics_lock:
            try:
                self._metrics.service_health["app_insights"] = (
                    await self._app_insights.get_health_status()
                )
                self._metrics.service_health["request_handler"] = (
                    await self._request_handler.get_health_status()
                )
                self._metrics.service_health["secret_util"] = (
                    await self._secret_util.get_health_status()
                )

                if self._gremlin_repo:
                    self._metrics.service_health["gremlin_repo"] = (
                        await self._gremlin_repo.get_health_status()
                    )

                if self._cosmos_repo:
                    self._metrics.service_health["cosmos_repo"] = (
                        await self._cosmos_repo.get_health_status()
                    )

            except Exception as e:
                logger.warning(f"Failed to update service health: {e}")

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
                logger.info(
                    f"Integration circuit breaker half-open for operation: {operation}"
                )
            else:
                raise RuntimeError(
                    f"Integration circuit breaker open for operation: {operation}"
                )

        elif self._circuit_breaker.state == "HALF_OPEN":
            if (
                self._circuit_breaker.half_open_calls
                >= self._circuit_breaker.half_open_max_calls
            ):
                raise RuntimeError(
                    f"Integration circuit breaker half-open limit exceeded: {operation}"
                )

    async def _record_success(self, operation: str, latency: float):
        """Record successful operation."""
        async with self._metrics_lock:
            self._metrics.record_operation(operation, latency, success=True)

        if self._circuit_breaker.state == "HALF_OPEN":
            self._circuit_breaker.half_open_calls += 1
            if (
                self._circuit_breaker.half_open_calls
                >= self._circuit_breaker.half_open_max_calls
            ):
                self._circuit_breaker.state = "CLOSED"
                self._circuit_breaker.failure_count = 0
                logger.info(
                    f"Integration circuit breaker closed for operation: {operation}"
                )

    async def _record_failure(self, operation: str, latency: float, error: Exception):
        """Record failed operation."""
        async with self._metrics_lock:
            self._metrics.record_operation(operation, latency, success=False)

        self._circuit_breaker.failure_count += 1
        self._circuit_breaker.last_failure_time = time.time()

        if (
            self._circuit_breaker.failure_count
            >= self._circuit_breaker.failure_threshold
        ):
            self._circuit_breaker.state = "OPEN"
            logger.warning(
                f"Integration circuit breaker opened for operation: {operation} due to: {error}"
            )

    @asynccontextmanager
    async def _with_circuit_breaker(self, operation: str):
        """Context manager for circuit breaker pattern."""
        start_time = time.time()

        try:
            await self._check_circuit_breaker(operation)
            yield

            latency = time.time() - start_time
            await self._record_success(operation, latency)

        except Exception as e:
            latency = time.time() - start_time
            await self._record_failure(operation, latency, e)
            raise

    # Repository Management

    def set_gremlin_repository(
        self, repository: ReactiveGremlinAuthorizationRepository
    ):
        """Set the Gremlin repository."""
        self._gremlin_repo = repository

    def set_cosmos_repository(self, repository: ReactiveAuthorizationCosmosRepository):
        """Set the Cosmos repository."""
        self._cosmos_repo = repository

    # Integrated Operations

    async def authenticate_and_authorize_async(
        self,
        token: str,
        secret_key: str,
        required_permissions: Optional[List[str]] = None,
    ) -> Tuple[Dict[str, Any], AuthorizationContext]:
        """
        Authenticate JWT token and create authorization context.

        Args:
            token: JWT token
            secret_key: Secret key for verification
            required_permissions: Required permissions

        Returns:
            Tuple of (payload, authorization_context)
        """
        async with self._with_circuit_breaker("authenticate_and_authorize"):
            # Verify JWT token
            payload = await self._secret_util.verify_jwt_async(token, secret_key)

            # Create authorization context (simplified - would be more complex in real implementation)
            auth_context = self._create_authorization_context(
                payload, required_permissions
            )

            # Track authentication event
            await self._app_insights.track_event_async(
                event_name="user_authenticated",
                properties={
                    "user_id": payload.get("user_id"),
                    "permissions": required_permissions or [],
                },
            )

            return payload, auth_context

    def _create_authorization_context(
        self, payload: Dict[str, Any], required_permissions: Optional[List[str]]
    ) -> AuthorizationContext:
        """Create authorization context from JWT payload."""
        # Placeholder implementation - would create proper protobuf object
        # In real implementation, this would construct the actual AuthorizationContext
        return payload  # Return payload as mock authorization context

    async def process_authenticated_request_async(
        self,
        token: str,
        secret_key: str,
        service_call: Callable[[T, Any], Union[None, asyncio.coroutines.Coroutine]],
        request: T,
        response_observer: Any,
        required_permissions: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Process an authenticated request end-to-end.

        Args:
            token: JWT token
            secret_key: Secret key
            service_call: Service method to call
            request: Request object
            response_observer: Response observer
            required_permissions: Required permissions
            metadata: Optional metadata
        """
        async with self._with_circuit_breaker("process_authenticated_request"):
            try:
                # Authenticate and authorize
                payload, auth_context = await self.authenticate_and_authorize_async(
                    token, secret_key, required_permissions
                )

                # Process request with authorization context
                await self._request_handler.handle_request_with_context_async(
                    authorization_context=auth_context,
                    service_call=service_call,
                    request=request,
                    response_observer=response_observer,
                    metadata=metadata,
                )

            except Exception as e:
                # Handle authentication/authorization failures
                await self._app_insights.track_exception_async(
                    exception=e,
                    properties={
                        "operation": "process_authenticated_request",
                        "request_type": (
                            type(request).__name__ if request else "unknown"
                        ),
                    },
                )
                raise

    async def secure_data_operation_async(
        self,
        operation: str,
        entity: Optional[T] = None,
        entity_id: Optional[ID] = None,
        auth_context: Optional[AM] = None,
        use_gremlin: bool = False,
        use_cosmos: bool = False,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Perform secure data operation with proper authorization.

        Args:
            operation: Operation type (create, read, update, delete, filter)
            entity: Entity object (for create/update/delete)
            entity_id: Entity ID (for read/delete by ID)
            auth_context: Authorization context
            use_gremlin: Whether to use Gremlin repository
            use_cosmos: Whether to use Cosmos repository
            properties: Properties for filtering

        Returns:
            Operation result
        """
        async with self._with_circuit_breaker("secure_data_operation"):
            repo = None

            if use_gremlin and self._gremlin_repo:
                repo = self._gremlin_repo
            elif use_cosmos and self._cosmos_repo:
                repo = self._cosmos_repo
            else:
                raise ValueError("No repository configured for operation")

            # Track data operation
            await self._app_insights.track_event_async(
                event_name="data_operation",
                properties={
                    "operation": operation,
                    "repository_type": "gremlin" if use_gremlin else "cosmos",
                    "entity_type": type(entity).__name__ if entity else "unknown",
                },
            )

            # Perform operation based on type
            if operation == "create" and entity:
                return await repo.save_async(entity, auth_context)
            elif operation == "read" and entity_id:
                return await repo.find_by_id_async(entity_id, auth_context)
            elif operation == "update" and entity:
                return await repo.save_async(entity, auth_context)
            elif operation == "delete" and entity:
                await repo.delete_async(entity, auth_context)
                return None
            elif operation == "delete_by_id" and entity_id:
                await repo.delete_by_id_async(entity_id, auth_context)
                return None
            elif operation == "filter" and properties:
                results = []
                async for item in repo.filter_async(properties, auth_context):
                    results.append(item)
                return results
            elif operation == "find_all":
                results = []
                async for item in repo.find_all_async(auth_context):
                    results.append(item)
                return results
            else:
                raise ValueError(f"Unsupported operation: {operation}")

    async def batch_secure_operations_async(
        self, operations: List[Dict[str, Any]], auth_context: Optional[AM] = None
    ) -> List[Tuple[bool, Any, Optional[str]]]:
        """
        Perform multiple secure operations in batch.

        Args:
            operations: List of operation specifications
            auth_context: Authorization context

        Returns:
            List of (success, result, error) tuples
        """
        async with self._with_circuit_breaker("batch_secure_operations"):
            results = []

            # Process operations with limited concurrency
            semaphore = asyncio.Semaphore(10)  # Limit concurrent operations

            async def process_operation(op):
                async with semaphore:
                    try:
                        result = await self.secure_data_operation_async(
                            auth_context=auth_context, **op
                        )
                        return (True, result, None)
                    except Exception as e:
                        logger.warning(f"Batch operation failed: {e}")
                        return (False, None, str(e))

            # Execute all operations concurrently
            tasks = [process_operation(op) for op in operations]
            results = await asyncio.gather(*tasks)

            # Track batch operation
            success_count = sum(1 for success, _, _ in results if success)
            await self._app_insights.track_event_async(
                event_name="batch_operations",
                properties={
                    "total_operations": len(operations),
                    "successful_operations": success_count,
                    "failed_operations": len(operations) - success_count,
                },
            )

            return results

    # Token Management

    async def refresh_token_async(
        self,
        expired_token: str,
        secret_key: str,
        new_expiry_seconds: Optional[int] = None,
    ) -> JWTToken:
        """
        Refresh an expired JWT token.

        Args:
            expired_token: Expired JWT token
            secret_key: Secret key
            new_expiry_seconds: New expiry time

        Returns:
            New JWT token
        """
        async with self._with_circuit_breaker("refresh_token"):
            new_token = await self._secret_util.refresh_jwt_async(
                expired_token, secret_key, new_expiry_seconds
            )

            # Track token refresh
            await self._app_insights.track_event_async(
                event_name="token_refreshed",
                properties={
                    "new_expiry": new_token.expires_at,
                    "algorithm": new_token.header.get("alg", "unknown"),
                },
            )

            return new_token

    async def generate_service_token_async(
        self,
        service_name: str,
        permissions: List[str],
        secret_key: str,
        expiry_seconds: Optional[int] = None,
    ) -> JWTToken:
        """
        Generate a service-to-service JWT token.

        Args:
            service_name: Name of the service
            permissions: List of permissions
            secret_key: Secret key
            expiry_seconds: Token expiry

        Returns:
            JWT token for service
        """
        async with self._with_circuit_breaker("generate_service_token"):
            payload = {
                "service_name": service_name,
                "permissions": permissions,
                "token_type": "service",
            }

            token = await self._secret_util.generate_jwt_async(
                payload=payload, secret_key=secret_key, expiry_seconds=expiry_seconds
            )

            # Track service token generation
            await self._app_insights.track_event_async(
                event_name="service_token_generated",
                properties={
                    "service_name": service_name,
                    "permissions_count": len(permissions),
                },
            )

            return token

    # Monitoring and Health

    async def get_integration_metrics_stream(
        self,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Get real-time integration metrics as a stream."""
        while True:
            async with self._metrics_lock:
                metrics_snapshot = {
                    "timestamp": time.time(),
                    "circuit_breaker_state": self._circuit_breaker.state,
                    "operation_counts": dict(self._metrics.operation_counts),
                    "error_counts": dict(self._metrics.error_counts),
                    "average_latencies": self._metrics.average_latencies,
                    "service_health": self._metrics.service_health,
                    "active_connections": self._metrics.active_connections,
                }

            yield metrics_snapshot
            await asyncio.sleep(2)  # Emit metrics every 2 seconds

    async def get_comprehensive_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status of all components."""
        await self._update_service_health()

        async with self._metrics_lock:
            return {
                "status": (
                    "healthy" if self._circuit_breaker.state != "OPEN" else "degraded"
                ),
                "integration_circuit_breaker": {
                    "state": self._circuit_breaker.state,
                    "failure_count": self._circuit_breaker.failure_count,
                    "last_failure_time": self._circuit_breaker.last_failure_time,
                },
                "service_health": self._metrics.service_health,
                "configuration": {
                    "max_concurrent_operations": self._config.max_concurrent_operations,
                    "enable_caching": self._config.enable_caching,
                    "cache_ttl": self._config.cache_ttl,
                    "request_timeout": self._config.request_timeout,
                },
                "repositories": {
                    "gremlin_configured": self._gremlin_repo is not None,
                    "cosmos_configured": self._cosmos_repo is not None,
                },
                "integration_metrics": {
                    "operation_counts": dict(self._metrics.operation_counts),
                    "error_counts": dict(self._metrics.error_counts),
                    "average_latencies": self._metrics.average_latencies,
                },
            }

    async def reset_all_circuit_breakers(self):
        """Reset all circuit breakers across all services."""
        self._circuit_breaker.state = "CLOSED"
        self._circuit_breaker.failure_count = 0
        self._circuit_breaker.half_open_calls = 0

        await self._app_insights.reset_circuit_breaker()
        await self._request_handler.reset_circuit_breaker()
        await self._secret_util.reset_circuit_breaker()

        if self._gremlin_repo:
            await self._gremlin_repo.reset_circuit_breaker()

        if self._cosmos_repo:
            await self._cosmos_repo.reset_circuit_breaker()

    async def clear_all_caches(self):
        """Clear all caches across all services."""
        await self._app_insights.clear_cache()
        await self._secret_util.clear_cache()

        if self._gremlin_repo:
            await self._gremlin_repo.clear_cache()

        if self._cosmos_repo:
            await self._cosmos_repo.clear_cache()

    async def shutdown(self):
        """Shutdown all services and cleanup resources."""
        # Cancel health monitoring
        if self._health_task and not self._health_task.done():
            self._health_task.cancel()
            try:
                await self._health_task
            except asyncio.CancelledError:
                pass

        # Shutdown all services
        await self._app_insights.shutdown()
        await self._request_handler.shutdown()
        await self._secret_util.shutdown()

        if self._gremlin_repo:
            await self._gremlin_repo.shutdown()

        if self._cosmos_repo:
            await self._cosmos_repo.shutdown()

    # Backward compatibility: sync wrapper methods

    def authenticate_and_authorize(
        self,
        token: str,
        secret_key: str,
        required_permissions: Optional[List[str]] = None,
    ) -> Tuple[Dict[str, Any], AuthorizationContext]:
        """Sync wrapper for authenticate_and_authorize_async."""
        return asyncio.run(
            self.authenticate_and_authorize_async(
                token, secret_key, required_permissions
            )
        )

    def process_authenticated_request(
        self,
        token: str,
        secret_key: str,
        service_call: Callable[[T, Any], None],
        request: T,
        response_observer: Any,
        required_permissions: Optional[List[str]] = None,
    ) -> None:
        """Sync wrapper for process_authenticated_request_async."""
        asyncio.run(
            self.process_authenticated_request_async(
                token,
                secret_key,
                service_call,
                request,
                response_observer,
                required_permissions,
            )
        )

    def get_health_status(self) -> Dict[str, Any]:
        """Sync wrapper for get_comprehensive_health_status."""
        return asyncio.run(self.get_comprehensive_health_status())


# Example usage demonstrating complete reactive integration
class ExampleIntegrationUsage:
    """Example usage of ReactiveIntegrationService."""

    def __init__(self):
        # Create integration service with all components
        self.integration = ReactiveIntegrationService(
            config=ServiceConfiguration(
                max_concurrent_operations=100, enable_detailed_metrics=True
            )
        )

    async def example_complete_workflow(self):
        """Example of complete reactive workflow."""
        # Generate service token
        secret_key = await self.integration._secret_util.generate_secret_key_async()
        service_token = await self.integration.generate_service_token_async(
            service_name="example_service",
            permissions=["read", "write"],
            secret_key=secret_key,
        )

        print(f"Generated service token: {service_token.token}")

        # Authenticate and process request
        async def example_service_call(request, response_observer):
            # Simulate some async work
            await asyncio.sleep(0.1)
            return {"result": f"processed {request}"}

        await self.integration.process_authenticated_request_async(
            token=service_token.token,
            secret_key=secret_key,
            service_call=example_service_call,
            request="test_request",
            response_observer=None,
            required_permissions=["read"],
        )

    async def monitor_integration_health(self):
        """Example of monitoring integration health."""
        async for metrics in self.integration.get_integration_metrics_stream():
            print(f"Integration metrics: {metrics}")
            if metrics["operation_counts"].get("process_authenticated_request", 0) > 5:
                break

        # Get comprehensive health status
        health = await self.integration.get_comprehensive_health_status()
        print(f"Health status: {health}")


if __name__ == "__main__":
    # Example usage
    example = ExampleIntegrationUsage()
    asyncio.run(example.example_complete_workflow())
