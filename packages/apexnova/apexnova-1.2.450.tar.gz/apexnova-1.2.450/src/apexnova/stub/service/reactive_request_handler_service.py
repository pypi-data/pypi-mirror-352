"""Reactive request handler service with async/reactive patterns."""

import asyncio
import time
from dataclasses import dataclass, field
from typing import (
    TypeVar,
    Callable,
    Optional,
    Any,
    Dict,
    List,
    AsyncGenerator,
    Union,
    Coroutine,
    Type,
    DefaultDict,
)
import logging
from collections import defaultdict
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor

# Conditional imports for graceful degradation
try:
    from apexnova.stub.authorization_context_pb2 import AuthorizationContext
    from apexnova.stub.response_pb2 import ResponseStatus

    _HAS_PROTOBUF = True
except ImportError:
    # Mock types for graceful degradation
    AuthorizationContext = Any
    ResponseStatus = Any
    _HAS_PROTOBUF = False

from .reactive_application_insights_service import ReactiveApplicationInsightsService
from ..feature.context.feature_targeting_context import FeatureTargetingContext

T = TypeVar("T")
R = TypeVar("R")

logger = logging.getLogger(__name__)


@dataclass
class RequestMetrics:
    """Request processing metrics."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_duration: float = 0.0
    min_duration: float = float("inf")
    max_duration: float = 0.0
    error_counts: DefaultDict[str, int] = field(
        default_factory=lambda: defaultdict(int)
    )
    status_code_counts: DefaultDict[str, int] = field(
        default_factory=lambda: defaultdict(int)
    )

    def record_request(
        self, duration: float, success: bool, status_code: str, error_type: str = None
    ):
        """Record request metrics."""
        self.total_requests += 1

        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
            if error_type:
                self.error_counts[error_type] += 1

        self.status_code_counts[status_code] += 1

        # Update duration statistics
        self.min_duration = min(self.min_duration, duration)
        self.max_duration = max(self.max_duration, duration)
        self.average_duration = (
            self.average_duration * (self.total_requests - 1) + duration
        ) / self.total_requests

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        return self.successful_requests / max(1, self.total_requests)


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
class RequestContext:
    """Enhanced request context with reactive features."""

    request_id: str
    authorization_context: Optional[AuthorizationContext]
    feature_context: Optional[FeatureTargetingContext]
    start_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

    @property
    def duration(self) -> float:
        """Get current request duration in seconds."""
        return time.time() - self.start_time


class ReactiveRequestHandlerService:
    """
    Reactive request handler service with async/reactive patterns,
    circuit breaker, metrics, and comprehensive monitoring.
    """

    def __init__(
        self,
        application_insights_service: ReactiveApplicationInsightsService,
        feature_targeting_context_accessor: Optional[Any] = None,
        max_concurrent_requests: int = 100,
        circuit_breaker_failure_threshold: int = 5,
        circuit_breaker_recovery_timeout: int = 60,
        thread_pool_size: int = 20,
        enable_detailed_metrics: bool = True,
        request_timeout: float = 30.0,
    ):
        """
        Initialize reactive request handler service.

        Args:
            application_insights_service: Reactive telemetry service
            feature_targeting_context_accessor: Accessor for feature targeting context
            max_concurrent_requests: Maximum concurrent requests
            circuit_breaker_failure_threshold: Circuit breaker failure threshold
            circuit_breaker_recovery_timeout: Circuit breaker recovery timeout
            thread_pool_size: Thread pool size for blocking operations
            enable_detailed_metrics: Whether to enable detailed metrics
            request_timeout: Request timeout in seconds
        """
        self.application_insights_service = application_insights_service
        self.feature_targeting_context_accessor = feature_targeting_context_accessor

        # Async concurrency control
        self._semaphore = asyncio.Semaphore(max_concurrent_requests)
        self._request_timeout = request_timeout

        # Circuit breaker for fault tolerance
        self._circuit_breaker = CircuitBreakerState(
            failure_threshold=circuit_breaker_failure_threshold,
            recovery_timeout=circuit_breaker_recovery_timeout,
        )

        # Thread pool for blocking operations
        self._thread_pool = ThreadPoolExecutor(max_workers=thread_pool_size)

        # Metrics
        self._enable_detailed_metrics = enable_detailed_metrics
        self._metrics = RequestMetrics()
        self._active_requests: Dict[str, RequestContext] = {}
        self._metrics_lock = asyncio.Lock()

        # Request tracking
        self._request_counter = 0
        self._request_streams: Dict[str, asyncio.Queue] = {}

    def _generate_request_id(self) -> str:
        """Generate unique request ID."""
        self._request_counter += 1
        return f"req_{int(time.time())}_{self._request_counter}"

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

    async def _record_success(self, operation: str):
        """Record successful operation."""
        if self._circuit_breaker.state == "HALF_OPEN":
            self._circuit_breaker.half_open_calls += 1
            if (
                self._circuit_breaker.half_open_calls
                >= self._circuit_breaker.half_open_max_calls
            ):
                self._circuit_breaker.state = "CLOSED"
                self._circuit_breaker.failure_count = 0
                logger.info(f"Circuit breaker closed for operation: {operation}")

    async def _record_failure(self, operation: str, error: Exception):
        """Record failed operation."""
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
        try:
            await self._check_circuit_breaker(operation)
            yield
            await self._record_success(operation)
        except Exception as e:
            await self._record_failure(operation, e)
            raise

    async def _create_request_context(
        self,
        authorization_context: Optional[AuthorizationContext],
        request: T,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RequestContext:
        """Create enhanced request context."""
        request_id = self._generate_request_id()

        # Create feature targeting context if accessor is available
        feature_context = None
        if self.feature_targeting_context_accessor and authorization_context:
            try:
                feature_context = FeatureTargetingContext(authorization_context)
                self.feature_targeting_context_accessor.set_local_context(
                    feature_context
                )
            except Exception as e:
                logger.warning(f"Failed to set feature context: {e}")

        return RequestContext(
            request_id=request_id,
            authorization_context=authorization_context,
            feature_context=feature_context,
            start_time=time.time(),
            metadata=metadata or {},
            tags=[],
        )

    async def _cleanup_request_context(self, context: RequestContext):
        """Cleanup request context."""
        if self.feature_targeting_context_accessor:
            try:
                self.feature_targeting_context_accessor.clear_targeting_context()
            except Exception as e:
                logger.warning(f"Failed to clear feature context: {e}")

        # Remove from active requests
        self._active_requests.pop(context.request_id, None)

    async def handle_request_with_context_async(
        self,
        authorization_context: Optional[AuthorizationContext],
        service_call: Callable[[T, Any], Union[None, Coroutine[Any, Any, None]]],
        request: T,
        response_observer: Any,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Handle a gRPC request asynchronously with authorization context and telemetry.

        Args:
            authorization_context: The authorization context
            service_call: The service method to call (can be sync or async)
            request: The request object
            response_observer: The response observer
            metadata: Optional request metadata
        """
        # Create request context
        context = await self._create_request_context(
            authorization_context, request, metadata
        )
        self._active_requests[context.request_id] = context

        async with self._semaphore:
            async with self._with_circuit_breaker("handle_request"):
                try:
                    # Apply timeout
                    await asyncio.wait_for(
                        self._execute_service_call(
                            service_call, request, response_observer, context
                        ),
                        timeout=self._request_timeout,
                    )

                    # Track successful request
                    duration_ms = int(context.duration * 1000)
                    request_name = (
                        type(request).__name__ if request else "UnknownRequest"
                    )

                    await self.application_insights_service.track_request_async(
                        request_name=request_name,
                        duration_millis=duration_ms,
                        response_code="200",
                        success=True,
                        authorization_context=authorization_context,
                        properties={"request_id": context.request_id},
                    )

                    # Update metrics
                    if self._enable_detailed_metrics:
                        async with self._metrics_lock:
                            self._metrics.record_request(context.duration, True, "200")

                except asyncio.TimeoutError:
                    await self._handle_timeout(context, request, authorization_context)
                except Exception as exception:
                    await self._handle_exception(
                        exception, context, request, authorization_context
                    )
                finally:
                    await self._cleanup_request_context(context)
                    await self._complete_response(response_observer)

    async def _execute_service_call(
        self,
        service_call: Callable[[T, Any], Union[None, Coroutine[Any, Any, None]]],
        request: T,
        response_observer: Any,
        context: RequestContext,
    ):
        """Execute service call (sync or async)."""
        if asyncio.iscoroutinefunction(service_call):
            # Async service call
            await service_call(request, response_observer)
        else:
            # Sync service call - run in thread pool
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self._thread_pool, service_call, request, response_observer
            )

    async def _handle_timeout(
        self,
        context: RequestContext,
        request: T,
        authorization_context: Optional[AuthorizationContext],
    ):
        """Handle request timeout."""
        duration_ms = int(context.duration * 1000)
        request_name = type(request).__name__ if request else "UnknownRequest"

        await self.application_insights_service.track_request_async(
            request_name=request_name,
            duration_millis=duration_ms,
            response_code="408",
            success=False,
            authorization_context=authorization_context,
            properties={"request_id": context.request_id, "error": "timeout"},
        )

        # Update metrics
        if self._enable_detailed_metrics:
            async with self._metrics_lock:
                self._metrics.record_request(
                    context.duration, False, "408", "TimeoutError"
                )

        logger.warning(
            f"Request {context.request_id} timed out after {context.duration:.2f}s"
        )

    async def _handle_exception(
        self,
        exception: Exception,
        context: RequestContext,
        request: T,
        authorization_context: Optional[AuthorizationContext],
    ):
        """Handle request exception."""
        duration_ms = int(context.duration * 1000)
        request_name = type(request).__name__ if request else "UnknownRequest"

        await self.application_insights_service.track_request_async(
            request_name=request_name,
            duration_millis=duration_ms,
            response_code="500",
            success=False,
            authorization_context=authorization_context,
            properties={"request_id": context.request_id},
        )

        # Handle the exception with detailed tracking
        response_status = await self.handle_exception_async(
            exception, request_name, authorization_context, context.request_id
        )

        # Update metrics
        if self._enable_detailed_metrics:
            async with self._metrics_lock:
                error_type = type(exception).__name__
                response_code = self._get_response_code_from_exception(exception)
                self._metrics.record_request(
                    context.duration, False, response_code, error_type
                )

    async def _complete_response(self, response_observer: Any):
        """Complete the response safely."""
        try:
            if hasattr(response_observer, "on_completed"):
                if asyncio.iscoroutinefunction(response_observer.on_completed):
                    await response_observer.on_completed()
                else:
                    # Run sync method in thread pool
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(
                        self._thread_pool, response_observer.on_completed
                    )
        except Exception as e:
            logger.warning(f"Failed to complete response: {e}")

    async def handle_exception_async(
        self,
        exception: Exception,
        operation: str,
        authorization_context: Optional[AuthorizationContext] = None,
        request_id: Optional[str] = None,
    ) -> Optional[ResponseStatus]:
        """
        Handle an exception asynchronously by logging it and returning appropriate response status.

        Args:
            exception: The exception that occurred
            operation: The operation name where the exception occurred
            authorization_context: Optional authorization context
            request_id: Optional request ID

        Returns:
            ResponseStatus corresponding to the exception type
        """
        # Track the exception with additional properties
        exception_type = type(exception).__name__
        properties = {"operation": operation, "typeName": exception_type}

        if request_id:
            properties["request_id"] = request_id

        # Send the exception to Application Insights
        await self.application_insights_service.track_exception_async(
            exception=exception,
            authorization_context=authorization_context,
            properties=properties,
        )

        # Return appropriate response status
        return self.get_response_status(exception)

    def get_response_status(self, exception: Exception) -> Optional[ResponseStatus]:
        """
        Get the appropriate response status for an exception.

        Args:
            exception: The exception to map to a response status

        Returns:
            ResponseStatus corresponding to the exception type
        """
        if not _HAS_PROTOBUF:
            return None

        # Note: ResponseStatus enum usage would need runtime import handling
        # For now, returning None as placeholder for graceful degradation
        if isinstance(exception, PermissionError):
            return None  # ResponseStatus.RESPONSE_STATUS_PERMISSION_DENIED
        elif isinstance(exception, ValueError):
            return None  # ResponseStatus.RESPONSE_STATUS_INVALID_ARGUMENT
        elif isinstance(exception, AttributeError):
            return None  # ResponseStatus.RESPONSE_STATUS_BAD_REQUEST
        elif isinstance(exception, KeyError) or isinstance(exception, LookupError):
            return None  # ResponseStatus.RESPONSE_STATUS_NOT_FOUND
        elif isinstance(exception, RuntimeError):
            return None  # ResponseStatus.RESPONSE_STATUS_INTERNAL_ERROR
        elif isinstance(exception, asyncio.TimeoutError):
            return None  # ResponseStatus.RESPONSE_STATUS_TIMEOUT
        else:
            return None  # ResponseStatus.RESPONSE_STATUS_UNKNOWN

    def _get_response_code_from_exception(self, exception: Exception) -> str:
        """Get HTTP-like response code from exception."""
        if isinstance(exception, PermissionError):
            return "403"
        elif isinstance(exception, ValueError):
            return "400"
        elif isinstance(exception, AttributeError):
            return "400"
        elif isinstance(exception, KeyError) or isinstance(exception, LookupError):
            return "404"
        elif isinstance(exception, asyncio.TimeoutError):
            return "408"
        elif isinstance(exception, RuntimeError):
            return "500"
        else:
            return "500"

    async def get_request_metrics_stream(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Get real-time request metrics as a stream."""
        while True:
            async with self._metrics_lock:
                metrics_snapshot = {
                    "timestamp": time.time(),
                    "total_requests": self._metrics.total_requests,
                    "successful_requests": self._metrics.successful_requests,
                    "failed_requests": self._metrics.failed_requests,
                    "success_rate": self._metrics.success_rate,
                    "average_duration": self._metrics.average_duration,
                    "min_duration": (
                        self._metrics.min_duration
                        if self._metrics.min_duration != float("inf")
                        else 0
                    ),
                    "max_duration": self._metrics.max_duration,
                    "active_requests": len(self._active_requests),
                    "circuit_breaker_state": self._circuit_breaker.state,
                    "error_counts": dict(self._metrics.error_counts),
                    "status_code_counts": dict(self._metrics.status_code_counts),
                }

            yield metrics_snapshot
            await asyncio.sleep(1)  # Emit metrics every second

    async def get_active_requests(self) -> List[Dict[str, Any]]:
        """Get information about currently active requests."""
        return [
            {
                "request_id": context.request_id,
                "duration": context.duration,
                "start_time": context.start_time,
                "metadata": context.metadata,
                "tags": context.tags,
            }
            for context in self._active_requests.values()
        ]

    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status."""
        async with self._metrics_lock:
            return {
                "status": (
                    "healthy" if self._circuit_breaker.state != "OPEN" else "degraded"
                ),
                "circuit_breaker": {
                    "state": self._circuit_breaker.state,
                    "failure_count": self._circuit_breaker.failure_count,
                    "last_failure_time": self._circuit_breaker.last_failure_time,
                },
                "metrics": {
                    "total_requests": self._metrics.total_requests,
                    "success_rate": self._metrics.success_rate,
                    "average_duration": self._metrics.average_duration,
                    "active_requests": len(self._active_requests),
                },
                "thread_pool": {
                    "active_threads": getattr(self._thread_pool, "_threads", 0)
                },
            }

    async def reset_circuit_breaker(self):
        """Reset circuit breaker to closed state."""
        self._circuit_breaker.state = "CLOSED"
        self._circuit_breaker.failure_count = 0
        self._circuit_breaker.half_open_calls = 0

    async def reset_metrics(self):
        """Reset all metrics."""
        async with self._metrics_lock:
            self._metrics = RequestMetrics()

    async def shutdown(self):
        """Shutdown the service and cleanup resources."""
        # Cancel all active requests
        for context in self._active_requests.values():
            await self._cleanup_request_context(context)

        self._active_requests.clear()
        self._thread_pool.shutdown(wait=True)

    # Backward compatibility: sync wrapper methods

    def handle_request_with_context(
        self,
        authorization_context: Optional[AuthorizationContext],
        service_call: Callable[[T, Any], None],
        request: T,
        response_observer: Any,
    ) -> None:
        """
        Sync wrapper for handle_request_with_context_async.

        Handle a gRPC request with authorization context and telemetry.

        Args:
            authorization_context: The authorization context
            service_call: The service method to call
            request: The request object
            response_observer: The response observer
        """
        asyncio.run(
            self.handle_request_with_context_async(
                authorization_context, service_call, request, response_observer
            )
        )

    def handle_exception(
        self,
        exception: Exception,
        operation: str,
        authorization_context: Optional[AuthorizationContext] = None,
    ) -> Optional[ResponseStatus]:
        """
        Sync wrapper for handle_exception_async.

        Handle an exception by logging it and returning appropriate response status.

        Args:
            exception: The exception that occurred
            operation: The operation name where the exception occurred
            authorization_context: Optional authorization context

        Returns:
            ResponseStatus corresponding to the exception type
        """
        return asyncio.run(
            self.handle_exception_async(exception, operation, authorization_context)
        )


# Example usage demonstrating reactive patterns
class ExampleUsage:
    """Example usage of ReactiveRequestHandlerService."""

    def __init__(self):
        # Create reactive application insights service
        self.app_insights = ReactiveApplicationInsightsService()

        # Create reactive request handler
        self.request_handler = ReactiveRequestHandlerService(
            application_insights_service=self.app_insights,
            max_concurrent_requests=50,
            enable_detailed_metrics=True,
        )

    async def example_async_request_handling(self):
        """Example of async request handling."""

        async def example_service_call(request, response_observer):
            # Simulate async work
            await asyncio.sleep(0.1)
            if hasattr(response_observer, "on_next"):
                response_observer.on_next(f"Processed: {request}")

        # Handle request asynchronously
        await self.request_handler.handle_request_with_context_async(
            authorization_context=None,
            service_call=example_service_call,
            request="test_request",
            response_observer=None,
        )

    async def monitor_real_time_metrics(self):
        """Example of monitoring real-time metrics."""
        async for metrics in self.request_handler.get_request_metrics_stream():
            print(f"Metrics: {metrics}")
            # In real usage, you might send this to a monitoring system
            if metrics["total_requests"] > 100:
                break
