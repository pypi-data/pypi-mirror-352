"""
Reactive Application Insights Service

Advanced Application Insights integration with reactive patterns, supporting:
- Circuit breaker pattern for resilience
- Batch processing with backpressure handling
- Health monitoring and metrics collection
- Event streaming and real-time telemetry
- Feature flag integration and caching
"""

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import (
    Any,
    AsyncIterator,
    Dict,
    List,
    Optional,
    Callable,
    Union,
)
import threading
from collections import deque
import logging
import uuid
import json

from ..core.result import Result
from ..core.error import StubError
from ..model.authorization_context import AuthorizationContext

logger = logging.getLogger(__name__)


class TelemetryEventType(Enum):
    """Types of telemetry events."""

    EVENT = "event"
    EXCEPTION = "exception"
    TRACE = "trace"
    REQUEST = "request"
    DEPENDENCY = "dependency"
    METRIC = "metric"
    PAGE_VIEW = "page_view"


class CircuitBreakerState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, rejecting requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class HealthStatus(Enum):
    """Health status indicators."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class ApplicationInsightsTelemetryEvent:
    """Telemetry event for Application Insights."""

    event_type: TelemetryEventType
    name: str
    properties: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Union[int, float]] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: Optional[str] = None
    authorization_context: Optional[AuthorizationContext] = None
    severity_level: str = "information"

    # Request-specific fields
    duration_ms: Optional[float] = None
    response_code: Optional[str] = None
    success: Optional[bool] = None
    url: Optional[str] = None

    # Exception-specific fields
    exception: Optional[Exception] = None
    operation: Optional[str] = None

    # Dependency-specific fields
    dependency_type: Optional[str] = None
    dependency_data: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "event_type": self.event_type.value,
            "name": self.name,
            "properties": self.properties,
            "metrics": self.metrics,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "severity_level": self.severity_level,
        }

        # Add type-specific fields if present
        if self.duration_ms is not None:
            result["duration_ms"] = self.duration_ms
        if self.response_code is not None:
            result["response_code"] = self.response_code
        if self.success is not None:
            result["success"] = self.success
        if self.url is not None:
            result["url"] = self.url
        if self.exception is not None:
            result["exception"] = str(self.exception)
        if self.operation is not None:
            result["operation"] = self.operation
        if self.dependency_type is not None:
            result["dependency_type"] = self.dependency_type
        if self.dependency_data is not None:
            result["dependency_data"] = self.dependency_data

        return result


@dataclass
class CircuitBreakerStats:
    """Statistics for circuit breaker."""

    state: CircuitBreakerState
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    total_requests: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": (
                self.last_failure_time.isoformat() if self.last_failure_time else None
            ),
            "last_success_time": (
                self.last_success_time.isoformat() if self.last_success_time else None
            ),
            "total_requests": self.total_requests,
            "success_rate": self.success_count / max(self.total_requests, 1),
        }


@dataclass
class HealthInfo:
    """Health information."""

    status: HealthStatus
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    dependencies: Dict[str, HealthStatus] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "message": self.message,
            "details": self.details,
            "dependencies": {k: v.value for k, v in self.dependencies.items()},
        }


@dataclass
class ReactiveApplicationInsightsConfig:
    """Configuration for reactive Application Insights service."""

    enabled: bool = True
    service_name: str = "unknown-service"
    instrumentation_key: str = ""
    connection_string: str = ""

    # Batch processing
    batch_size: int = 100
    flush_interval_seconds: float = 30.0
    max_buffer_size: int = 10000
    max_retries: int = 3
    retry_delay_seconds: float = 1.0

    # Circuit breaker
    circuit_breaker_enabled: bool = True
    failure_threshold: int = 5
    recovery_timeout_seconds: float = 60.0
    call_timeout_seconds: float = 10.0
    minimum_throughput: int = 10

    # Health checks
    enable_health_checks: bool = True
    health_check_interval_seconds: float = 30.0

    # Feature flags
    enable_feature_flag_caching: bool = True
    feature_flag_cache_ttl_seconds: float = 300.0  # 5 minutes

    # Performance
    enable_metrics_aggregation: bool = True
    metrics_aggregation_window_seconds: float = 60.0


class PerformanceTimer:
    """Performance timer for automatic metric tracking."""

    def __init__(
        self,
        operation_name: str,
        metadata: Optional[Dict[str, Any]] = None,
        callback: Optional[Callable] = None,
    ):
        self.operation_name = operation_name
        self.metadata = metadata or {}
        self.callback = callback
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    def __enter__(self):
        """Start timing."""
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timing and report."""
        self.end_time = time.time()

        if self.start_time and self.callback:
            duration = self.end_time - self.start_time
            self.callback(
                {
                    "operation_name": self.operation_name,
                    "duration_ms": duration * 1000,
                    "success": exc_type is None,
                    "metadata": self.metadata,
                }
            )

    async def __aenter__(self):
        """Async context manager entry."""
        return self.__enter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        self.__exit__(exc_type, exc_val, exc_tb)


class BatchProcessor:
    """Batch processor for telemetry events."""

    def __init__(self, config: ReactiveApplicationInsightsConfig):
        self.config = config
        self.events_buffer: deque = deque(maxlen=config.max_buffer_size)
        self.metrics_buffer: deque = deque(maxlen=config.max_buffer_size)
        self.is_running = False
        self._flush_task: Optional[asyncio.Task] = None
        self._lock = threading.RLock()

    async def start(self) -> None:
        """Start the batch processor."""
        if self.is_running:
            return

        self.is_running = True
        self._flush_task = asyncio.create_task(self._periodic_flush())
        logger.info("Batch processor started")

    async def stop(self) -> None:
        """Stop the batch processor."""
        if not self.is_running:
            return

        self.is_running = False

        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass

        # Final flush
        await self.flush()
        logger.info("Batch processor stopped")

    def add_event(self, event: ApplicationInsightsTelemetryEvent) -> None:
        """Add an event to the buffer."""
        with self._lock:
            self.events_buffer.append(event)

    def add_metric(self, metric: Dict[str, Any]) -> None:
        """Add a metric to the buffer."""
        with self._lock:
            self.metrics_buffer.append(metric)

    async def flush(self) -> Result[None]:
        """Flush all buffered data."""
        try:
            events_to_flush = []
            metrics_to_flush = []

            with self._lock:
                events_to_flush = list(self.events_buffer)
                metrics_to_flush = list(self.metrics_buffer)
                self.events_buffer.clear()
                self.metrics_buffer.clear()

            # Process in batches
            if events_to_flush:
                await self._process_events_batch(events_to_flush)

            if metrics_to_flush:
                await self._process_metrics_batch(metrics_to_flush)

            return Result.success(None)

        except Exception as e:
            logger.error(f"Failed to flush batch data: {e}")
            return Result.failure(StubError("BATCH_FLUSH_ERROR", str(e)))

    async def _periodic_flush(self) -> None:
        """Periodic flush background task."""
        while self.is_running:
            try:
                await self.flush()
                await asyncio.sleep(self.config.flush_interval_seconds)
            except Exception as e:
                logger.error(f"Error in periodic flush: {e}")
                await asyncio.sleep(5)  # Backoff on error

    async def _process_events_batch(
        self, events: List[ApplicationInsightsTelemetryEvent]
    ) -> None:
        """Process a batch of events."""
        for i in range(0, len(events), self.config.batch_size):
            batch = events[i : i + self.config.batch_size]
            await self._send_events_to_app_insights(batch)

    async def _process_metrics_batch(self, metrics: List[Dict[str, Any]]) -> None:
        """Process a batch of metrics."""
        for i in range(0, len(metrics), self.config.batch_size):
            batch = metrics[i : i + self.config.batch_size]
            await self._send_metrics_to_app_insights(batch)

    async def _send_events_to_app_insights(
        self, events: List[ApplicationInsightsTelemetryEvent]
    ) -> None:
        """Send events to Application Insights (mock implementation)."""
        logger.info(f"Sending {len(events)} events to Application Insights")
        # Mock network call
        await asyncio.sleep(0.1)

        # Simulate occasional failures for testing
        if time.time() % 100 < 5:  # 5% failure rate
            raise Exception("Simulated Application Insights API failure")

    async def _send_metrics_to_app_insights(
        self, metrics: List[Dict[str, Any]]
    ) -> None:
        """Send metrics to Application Insights (mock implementation)."""
        logger.info(f"Sending {len(metrics)} metrics to Application Insights")
        # Mock network call
        await asyncio.sleep(0.1)


class CircuitBreaker:
    """Circuit breaker implementation for resilience."""

    def __init__(self, config: ReactiveApplicationInsightsConfig):
        self.config = config
        self.stats = CircuitBreakerStats(state=CircuitBreakerState.CLOSED)
        self._lock = threading.RLock()

    def should_allow_request(self) -> bool:
        """Check if request should be allowed through."""
        if not self.config.circuit_breaker_enabled:
            return True

        with self._lock:
            if self.stats.state == CircuitBreakerState.CLOSED:
                return True
            elif self.stats.state == CircuitBreakerState.OPEN:
                # Check if recovery timeout has passed
                if (
                    self.stats.last_failure_time
                    and time.time() - self.stats.last_failure_time.timestamp()
                    > self.config.recovery_timeout_seconds
                ):
                    self.stats.state = CircuitBreakerState.HALF_OPEN
                    return True
                return False
            elif self.stats.state == CircuitBreakerState.HALF_OPEN:
                return True

        return False

    def record_success(self) -> None:
        """Record a successful operation."""
        with self._lock:
            self.stats.success_count += 1
            self.stats.total_requests += 1
            self.stats.last_success_time = datetime.now(timezone.utc)

            if self.stats.state == CircuitBreakerState.HALF_OPEN:
                # Recovery successful, close circuit
                self.stats.state = CircuitBreakerState.CLOSED
                self.stats.failure_count = 0

    def record_failure(self) -> None:
        """Record a failed operation."""
        with self._lock:
            self.stats.failure_count += 1
            self.stats.total_requests += 1
            self.stats.last_failure_time = datetime.now(timezone.utc)

            # Check if we should open the circuit
            if (
                self.stats.state
                in [CircuitBreakerState.CLOSED, CircuitBreakerState.HALF_OPEN]
                and self.stats.failure_count >= self.config.failure_threshold
                and self.stats.total_requests >= self.config.minimum_throughput
            ):
                self.stats.state = CircuitBreakerState.OPEN

    def get_stats(self) -> CircuitBreakerStats:
        """Get current circuit breaker statistics."""
        with self._lock:
            return CircuitBreakerStats(**self.stats.__dict__)


class ReactiveApplicationInsightsService:
    """
    Reactive Application Insights service with advanced features.

    Features:
    - Reactive telemetry collection with streaming
    - Circuit breaker pattern for resilience
    - Batch processing with backpressure handling
    - Health monitoring and metrics
    - Feature flag integration and caching
    - Context correlation and enrichment
    """

    def __init__(self, config: Optional[ReactiveApplicationInsightsConfig] = None):
        self.config = config or ReactiveApplicationInsightsConfig()
        self.batch_processor = BatchProcessor(self.config)
        self.circuit_breaker = CircuitBreaker(self.config)
        self.is_running = False

        # Health monitoring
        self.health_status = HealthStatus.HEALTHY
        self._health_task: Optional[asyncio.Task] = None

        # Feature flag cache
        self.feature_flag_cache: Dict[str, Any] = {}
        self.feature_flag_cache_timestamps: Dict[str, float] = {}

        # Metrics aggregation
        self.metrics_aggregations: Dict[str, List[float]] = {}
        self._aggregation_lock = threading.RLock()

        # Performance metrics
        self.total_events = 0
        self.total_exceptions = 0
        self.total_requests = 0
        self.total_metrics = 0

        logger.info(
            f"ReactiveApplicationInsightsService initialized with config: {self.config}"
        )

    async def start(self) -> None:
        """Start the Application Insights service."""
        if self.is_running:
            logger.warning("Application Insights service is already running")
            return

        self.is_running = True
        logger.info("Starting reactive Application Insights service")

        # Start batch processor
        await self.batch_processor.start()

        # Start health monitoring
        if self.config.enable_health_checks:
            self._health_task = asyncio.create_task(self._health_monitor())

    async def stop(self) -> None:
        """Stop the Application Insights service."""
        if not self.is_running:
            return

        logger.info("Stopping reactive Application Insights service")
        self.is_running = False

        # Stop health monitoring
        if self._health_task:
            self._health_task.cancel()
            try:
                await self._health_task
            except asyncio.CancelledError:
                pass

        # Stop batch processor
        await self.batch_processor.stop()

    async def track_event(
        self,
        event_name: str,
        properties: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Union[int, float]]] = None,
        authorization_context: Optional[AuthorizationContext] = None,
        correlation_id: Optional[str] = None,
    ) -> Result[None]:
        """Track a telemetry event."""
        if not self.config.enabled or not self.circuit_breaker.should_allow_request():
            return Result.success(None)

        try:
            event = ApplicationInsightsTelemetryEvent(
                event_type=TelemetryEventType.EVENT,
                name=event_name,
                properties=properties or {},
                metrics=metrics or {},
                authorization_context=authorization_context,
                correlation_id=correlation_id,
            )

            self.batch_processor.add_event(event)
            self.total_events += 1
            self.circuit_breaker.record_success()

            return Result.success(None)

        except Exception as e:
            self.circuit_breaker.record_failure()
            logger.error(f"Failed to track event: {e}")
            return Result.failure(StubError("TRACK_EVENT_ERROR", str(e)))

    async def track_exception(
        self,
        exception: Exception,
        operation: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        authorization_context: Optional[AuthorizationContext] = None,
        correlation_id: Optional[str] = None,
    ) -> Result[None]:
        """Track an exception."""
        if not self.config.enabled or not self.circuit_breaker.should_allow_request():
            return Result.success(None)

        try:
            event = ApplicationInsightsTelemetryEvent(
                event_type=TelemetryEventType.EXCEPTION,
                name=type(exception).__name__,
                properties=properties or {},
                authorization_context=authorization_context,
                correlation_id=correlation_id,
                exception=exception,
                operation=operation,
                severity_level="error",
            )

            self.batch_processor.add_event(event)
            self.total_exceptions += 1
            self.circuit_breaker.record_success()

            return Result.success(None)

        except Exception as e:
            self.circuit_breaker.record_failure()
            logger.error(f"Failed to track exception: {e}")
            return Result.failure(StubError("TRACK_EXCEPTION_ERROR", str(e)))

    async def track_request(
        self,
        request_name: str,
        duration_ms: float,
        response_code: str,
        success: bool,
        url: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        authorization_context: Optional[AuthorizationContext] = None,
        correlation_id: Optional[str] = None,
    ) -> Result[None]:
        """Track a request."""
        if not self.config.enabled or not self.circuit_breaker.should_allow_request():
            return Result.success(None)

        try:
            # Generate URL if not provided
            if not url:
                url = f"https://{self.config.service_name}.apexnova.vc/{request_name}"

            event = ApplicationInsightsTelemetryEvent(
                event_type=TelemetryEventType.REQUEST,
                name=request_name,
                properties=properties or {},
                authorization_context=authorization_context,
                correlation_id=correlation_id,
                duration_ms=duration_ms,
                response_code=response_code,
                success=success,
                url=url,
            )

            self.batch_processor.add_event(event)
            self.total_requests += 1
            self.circuit_breaker.record_success()

            return Result.success(None)

        except Exception as e:
            self.circuit_breaker.record_failure()
            logger.error(f"Failed to track request: {e}")
            return Result.failure(StubError("TRACK_REQUEST_ERROR", str(e)))

    async def track_dependency(
        self,
        dependency_name: str,
        dependency_type: str,
        dependency_data: str,
        duration_ms: float,
        success: bool,
        result_code: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        authorization_context: Optional[AuthorizationContext] = None,
        correlation_id: Optional[str] = None,
    ) -> Result[None]:
        """Track a dependency call."""
        if not self.config.enabled or not self.circuit_breaker.should_allow_request():
            return Result.success(None)

        try:
            event = ApplicationInsightsTelemetryEvent(
                event_type=TelemetryEventType.DEPENDENCY,
                name=dependency_name,
                properties=properties or {},
                authorization_context=authorization_context,
                correlation_id=correlation_id,
                duration_ms=duration_ms,
                success=success,
                response_code=result_code,
                dependency_type=dependency_type,
                dependency_data=dependency_data,
            )

            self.batch_processor.add_event(event)
            self.circuit_breaker.record_success()

            return Result.success(None)

        except Exception as e:
            self.circuit_breaker.record_failure()
            logger.error(f"Failed to track dependency: {e}")
            return Result.failure(StubError("TRACK_DEPENDENCY_ERROR", str(e)))

    async def track_metric(
        self,
        metric_name: str,
        value: Union[int, float],
        properties: Optional[Dict[str, Any]] = None,
        authorization_context: Optional[AuthorizationContext] = None,
    ) -> Result[None]:
        """Track a custom metric."""
        if not self.config.enabled:
            return Result.success(None)

        try:
            metric = {
                "name": metric_name,
                "value": value,
                "properties": properties or {},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            # Add to aggregation if enabled
            if self.config.enable_metrics_aggregation:
                with self._aggregation_lock:
                    if metric_name not in self.metrics_aggregations:
                        self.metrics_aggregations[metric_name] = []
                    self.metrics_aggregations[metric_name].append(float(value))

            self.batch_processor.add_metric(metric)
            self.total_metrics += 1

            return Result.success(None)

        except Exception as e:
            logger.error(f"Failed to track metric: {e}")
            return Result.failure(StubError("TRACK_METRIC_ERROR", str(e)))

    def create_timer(
        self, operation_name: str, metadata: Optional[Dict[str, Any]] = None
    ) -> PerformanceTimer:
        """Create a performance timer."""
        return PerformanceTimer(
            operation_name,
            metadata,
            lambda metrics: asyncio.create_task(
                self.track_metric(
                    f"{operation_name}_duration_ms", metrics["duration_ms"], metadata
                )
            ),
        )

    async def flush(self) -> Result[None]:
        """Flush all pending telemetry data."""
        return await self.batch_processor.flush()

    async def get_event_stream(
        self,
    ) -> AsyncIterator[List[ApplicationInsightsTelemetryEvent]]:
        """Get streaming telemetry events."""
        # Mock implementation - in real scenario, this would stream live events
        while self.is_running:
            await asyncio.sleep(self.config.flush_interval_seconds)
            # In real implementation, yield batches of events
            yield []

    def get_circuit_breaker_stats(self) -> CircuitBreakerStats:
        """Get circuit breaker statistics."""
        return self.circuit_breaker.get_stats()

    def get_health_status(self) -> HealthInfo:
        """Get current health status."""
        dependencies = {
            "application_insights": self._check_app_insights_health(),
            "circuit_breaker": self._check_circuit_breaker_health(),
            "batch_processor": self._check_batch_processor_health(),
        }

        overall_status = self._calculate_overall_health(dependencies)

        return HealthInfo(
            status=overall_status,
            dependencies=dependencies,
            details={
                "total_events": self.total_events,
                "total_exceptions": self.total_exceptions,
                "total_requests": self.total_requests,
                "total_metrics": self.total_metrics,
                "circuit_breaker_stats": self.circuit_breaker.get_stats().to_dict(),
                "service_name": self.config.service_name,
            },
        )

    def _check_app_insights_health(self) -> HealthStatus:
        """Check Application Insights health."""
        # Mock health check - in real scenario, ping Application Insights API
        return HealthStatus.HEALTHY

    def _check_circuit_breaker_health(self) -> HealthStatus:
        """Check circuit breaker health."""
        stats = self.circuit_breaker.get_stats()
        if stats.state == CircuitBreakerState.CLOSED:
            return HealthStatus.HEALTHY
        elif stats.state == CircuitBreakerState.HALF_OPEN:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.UNHEALTHY

    def _check_batch_processor_health(self) -> HealthStatus:
        """Check batch processor health."""
        return (
            HealthStatus.HEALTHY
            if self.batch_processor.is_running
            else HealthStatus.UNHEALTHY
        )

    def _calculate_overall_health(
        self, dependencies: Dict[str, HealthStatus]
    ) -> HealthStatus:
        """Calculate overall health from dependencies."""
        statuses = list(dependencies.values())

        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY

    async def _health_monitor(self) -> None:
        """Health monitoring background task."""
        while self.is_running:
            try:
                health_info = self.get_health_status()
                self.health_status = health_info.status

                if health_info.status != HealthStatus.HEALTHY:
                    logger.warning(f"Health status: {health_info.status.value}")

                await asyncio.sleep(self.config.health_check_interval_seconds)
            except Exception as e:
                logger.error(f"Error in health monitor: {e}")
                await asyncio.sleep(10)  # Backoff on error
