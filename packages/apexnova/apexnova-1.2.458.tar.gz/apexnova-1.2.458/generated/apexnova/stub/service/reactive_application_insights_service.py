"""Modern async/reactive Azure Application Insights service."""

from __future__ import annotations

import asyncio
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Dict, Optional, Any, AsyncGenerator, List, Protocol, Union
from datetime import datetime, timedelta
import logging
import weakref
from concurrent.futures import ThreadPoolExecutor

try:
    from azure.monitor.opentelemetry import configure_azure_monitor  # type: ignore

    azure_monitor_available = True
except ImportError:
    azure_monitor_available = False
    configure_azure_monitor = None  # type: ignore

try:
    from opentelemetry import trace, metrics  # type: ignore
    from opentelemetry.trace import Status, StatusCode  # type: ignore

    opentelemetry_available = True
except ImportError:
    opentelemetry_available = False
    trace = None  # type: ignore
    metrics = None  # type: ignore
    Status = None  # type: ignore
    StatusCode = None  # type: ignore

# Type checking imports
if hasattr(__builtins__, "TYPE_CHECKING"):
    from apexnova.stub.authorization_context_pb2 import AuthorizationContext


logger = logging.getLogger(__name__)


@dataclass
class TelemetryConfig:
    """Configuration for reactive telemetry service."""

    service_name: str = "reactive-python-service"
    batch_size: int = 50
    flush_interval_seconds: float = 5.0
    enable_metrics_aggregation: bool = True
    enable_circuit_breaker: bool = True
    max_queue_size: int = 10000
    enable_streaming: bool = True
    circuit_breaker_threshold: int = 5
    rate_limit_per_second: float = 1000.0


@dataclass
class MetricAggregation:
    """Aggregated metrics data."""

    count: int = 0
    sum: float = 0.0
    min: float = float("inf")
    max: float = float("-inf")
    avg: float = 0.0
    last_updated: datetime = None

    def update(self, value: float) -> None:
        """Update aggregation with new value."""
        self.count += 1
        self.sum += value
        self.min = min(self.min, value)
        self.max = max(self.max, value)
        self.avg = self.sum / self.count
        self.last_updated = datetime.now()


@dataclass
class TelemetryEvent:
    """Base telemetry event."""

    name: str
    timestamp: datetime
    properties: Dict[str, Any]
    authorization_context: Optional["AuthorizationContext"] = None


class EventStream(Protocol):
    """Protocol for event streaming."""

    async def emit(self, event: TelemetryEvent) -> None:
        """Emit an event to the stream."""
        ...

    async def __aiter__(self) -> AsyncGenerator[TelemetryEvent, None]:
        """Async iterator for events."""
        ...


class ReactiveApplicationInsightsService:
    """
    Modern reactive Application Insights service with async/await patterns.

    Features:
    - Async telemetry operations with proper backpressure handling
    - Event streaming with asyncio.Queue
    - Circuit breaker pattern for resilience
    - Batch processing for performance
    - Metrics aggregation with reactive streams
    - Graceful degradation when Azure services unavailable
    - Memory-efficient event buffering
    """

    def __init__(
        self,
        connection_string: Optional[str] = None,
        feature_manager: Optional[Any] = None,
        config: Optional[TelemetryConfig] = None,
    ):
        """Initialize reactive telemetry service."""
        self.config = config or TelemetryConfig()
        self.feature_manager = feature_manager
        self.enabled = False
        self.tracer: Optional[Any] = None
        self.meter: Optional[Any] = None

        # Async components
        self._event_queue: asyncio.Queue[TelemetryEvent] = asyncio.Queue(
            maxsize=self.config.max_queue_size
        )
        self._batch_buffer: List[TelemetryEvent] = []
        self._metrics_aggregation: Dict[str, MetricAggregation] = defaultdict(
            MetricAggregation
        )
        self._event_streams: weakref.WeakSet = weakref.WeakSet()

        # Circuit breaker state
        self._circuit_breaker_failures = 0
        self._circuit_breaker_open = False
        self._circuit_breaker_last_failure = None

        # Background tasks
        self._background_tasks: List[asyncio.Task] = []
        self._shutdown_event = asyncio.Event()

        # Thread pool for blocking operations
        self._thread_pool = ThreadPoolExecutor(
            max_workers=2, thread_name_prefix="telemetry"
        )

        # Initialize Azure components
        self._initialize_azure_components(connection_string)

        # Start background processing
        asyncio.create_task(self._start_background_tasks())

    def _initialize_azure_components(self, connection_string: Optional[str]) -> None:
        """Initialize Azure Application Insights components."""
        if (
            not connection_string
            or not azure_monitor_available
            or not opentelemetry_available
        ):
            logger.warning(
                "Azure Application Insights not available - running in mock mode"
            )
            return

        try:
            configure_azure_monitor(connection_string=connection_string)  # type: ignore
            self.tracer = trace.get_tracer(self.config.service_name)  # type: ignore
            self.meter = metrics.get_meter(self.config.service_name)  # type: ignore
            self.enabled = True
            logger.info("Azure Application Insights initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Azure Application Insights: {e}")
            self.enabled = False

    async def _start_background_tasks(self) -> None:
        """Start background processing tasks."""
        self._background_tasks = [
            asyncio.create_task(self._batch_processor()),
            asyncio.create_task(self._metrics_aggregator()),
            asyncio.create_task(self._event_distributor()),
        ]

    async def _batch_processor(self) -> None:
        """Process events in batches for better performance."""
        while not self._shutdown_event.is_set():
            try:
                # Wait for events or timeout
                events_batch: List[TelemetryEvent] = []

                # Collect events up to batch size or timeout
                deadline = time.time() + self.config.flush_interval_seconds

                while (
                    len(events_batch) < self.config.batch_size
                    and time.time() < deadline
                ):
                    try:
                        timeout = deadline - time.time()
                        if timeout <= 0:
                            break

                        event = await asyncio.wait_for(
                            self._event_queue.get(), timeout=timeout
                        )
                        events_batch.append(event)
                    except asyncio.TimeoutError:
                        break

                if events_batch:
                    await self._process_events_batch(events_batch)

            except Exception as e:
                logger.error(f"Error in batch processor: {e}")
                await asyncio.sleep(1)  # Back off on error

    async def _process_events_batch(self, events: List[TelemetryEvent]) -> None:
        """Process a batch of telemetry events."""
        if not self.enabled or self._circuit_breaker_open:
            return

        try:
            # Use thread pool for potentially blocking telemetry operations
            await asyncio.get_event_loop().run_in_executor(
                self._thread_pool, self._send_telemetry_batch, events
            )

            # Reset circuit breaker on success
            self._circuit_breaker_failures = 0
            self._circuit_breaker_open = False

        except Exception as e:
            logger.error(f"Failed to process telemetry batch: {e}")
            await self._handle_circuit_breaker_failure()

    def _send_telemetry_batch(self, events: List[TelemetryEvent]) -> None:
        """Send telemetry batch (runs in thread pool)."""
        if not self.tracer:
            return

        for event in events:
            try:
                with self.tracer.start_span(event.name) as span:
                    # Add properties as attributes
                    for key, value in event.properties.items():
                        span.set_attribute(key, str(value))

                    # Add authorization context
                    if event.authorization_context:
                        auth_props = self._extract_authorization_context(
                            event.authorization_context
                        )
                        for key, value in auth_props.items():
                            span.set_attribute(f"auth.{key}", value)

                    span.set_status(Status(StatusCode.OK))  # type: ignore

            except Exception as e:
                logger.error(f"Failed to send individual telemetry event: {e}")

    async def _handle_circuit_breaker_failure(self) -> None:
        """Handle circuit breaker failure logic."""
        self._circuit_breaker_failures += 1
        self._circuit_breaker_last_failure = time.time()

        if self._circuit_breaker_failures >= self.config.circuit_breaker_threshold:
            self._circuit_breaker_open = True
            logger.warning("Telemetry circuit breaker opened due to failures")

            # Auto-recovery after timeout
            await asyncio.sleep(30)  # 30 second timeout
            self._circuit_breaker_open = False
            self._circuit_breaker_failures = 0
            logger.info("Telemetry circuit breaker reset")

    async def _metrics_aggregator(self) -> None:
        """Aggregate metrics in background."""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(1)  # Aggregate every second

                # Update metrics aggregations
                current_time = datetime.now()

                # Clean up old metrics (older than 1 hour)
                cutoff_time = current_time - timedelta(hours=1)
                to_remove = [
                    key
                    for key, metric in self._metrics_aggregation.items()
                    if metric.last_updated and metric.last_updated < cutoff_time
                ]

                for key in to_remove:
                    del self._metrics_aggregation[key]

            except Exception as e:
                logger.error(f"Error in metrics aggregator: {e}")

    async def _event_distributor(self) -> None:
        """Distribute events to registered streams."""
        async for event in self._stream_events():
            # Distribute to all registered streams
            for stream in list(self._event_streams):
                try:
                    await stream.emit(event)
                except Exception as e:
                    logger.error(f"Failed to emit event to stream: {e}")

    def _extract_authorization_context(
        self, authorization_context: "AuthorizationContext"
    ) -> Dict[str, str]:
        """Extract authorization context properties."""
        try:
            return {
                "service": self.config.service_name,
                "userId": authorization_context.id,
                "requestTime": str(authorization_context.request_time),
                "ipAddress": authorization_context.ip_address,
                "clientRequestId": authorization_context.client_request_id,
                "accountId": authorization_context.account_id,
            }
        except Exception:
            return {"service": self.config.service_name}

    async def track_event_async(
        self,
        event_name: str,
        authorization_context: Optional["AuthorizationContext"] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Track an event asynchronously."""
        event = TelemetryEvent(
            name=event_name,
            timestamp=datetime.now(),
            properties=properties or {},
            authorization_context=authorization_context,
        )

        try:
            # Non-blocking queue put with timeout
            await asyncio.wait_for(self._event_queue.put(event), timeout=1.0)
        except asyncio.TimeoutError:
            logger.warning(f"Telemetry queue full, dropping event: {event_name}")

    def track_event(
        self,
        event_name: str,
        authorization_context: Optional["AuthorizationContext"] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Track an event (sync wrapper for async method)."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # In async context, schedule coroutine
                asyncio.create_task(
                    self.track_event_async(
                        event_name, authorization_context, properties
                    )
                )
            else:
                # Not in async context, run directly
                loop.run_until_complete(
                    self.track_event_async(
                        event_name, authorization_context, properties
                    )
                )
        except RuntimeError:
            # No event loop, create one
            asyncio.run(
                self.track_event_async(event_name, authorization_context, properties)
            )

    async def track_events_batch_async(self, events: List[Dict[str, Any]]) -> None:
        """Track multiple events in batch."""
        for event_data in events:
            await self.track_event_async(
                event_data.get("name", "unknown"),
                event_data.get("authorization_context"),
                event_data.get("properties", {}),
            )

    async def track_metric_async(
        self,
        metric_name: str,
        value: float,
        properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Track a metric value."""
        # Update aggregation
        self._metrics_aggregation[metric_name].update(value)

        # Track as event too
        await self.track_event_async(
            f"metric.{metric_name}",
            properties={**(properties or {}), "value": value, "metric_type": "custom"},
        )

    async def track_exception_async(
        self,
        exception: Exception,
        authorization_context: Optional["AuthorizationContext"] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Track an exception asynchronously."""
        exception_properties = {
            **(properties or {}),
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
        }

        await self.track_event_async(
            "exception", authorization_context, exception_properties
        )

    def track_exception(
        self,
        exception: Exception,
        authorization_context: Optional["AuthorizationContext"] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Track an exception (sync wrapper)."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(
                    self.track_exception_async(
                        exception, authorization_context, properties
                    )
                )
            else:
                loop.run_until_complete(
                    self.track_exception_async(
                        exception, authorization_context, properties
                    )
                )
        except RuntimeError:
            asyncio.run(
                self.track_exception_async(exception, authorization_context, properties)
            )

    async def _stream_events(self) -> AsyncGenerator[TelemetryEvent, None]:
        """Stream events as they are processed."""
        processed_events: asyncio.Queue[TelemetryEvent] = asyncio.Queue()

        # Create a copy of the event queue for streaming
        async def event_copier():
            while True:
                try:
                    # Get events from main queue and copy to stream queue
                    event = await self._event_queue.get()
                    await processed_events.put(event)
                    await self._event_queue.put(event)  # Put back for processing
                except Exception as e:
                    logger.error(f"Error in event copier: {e}")

        # Start copier task
        copier_task = asyncio.create_task(event_copier())

        try:
            while True:
                event = await processed_events.get()
                yield event
        finally:
            copier_task.cancel()

    async def get_event_stream(self) -> AsyncGenerator[TelemetryEvent, None]:
        """Get a stream of telemetry events."""
        async for event in self._stream_events():
            yield event

    async def get_metrics_stream(
        self,
    ) -> AsyncGenerator[Dict[str, MetricAggregation], None]:
        """Get a stream of aggregated metrics."""
        while not self._shutdown_event.is_set():
            yield dict(self._metrics_aggregation)
            await asyncio.sleep(self.config.flush_interval_seconds)

    def get_health_status(self) -> Dict[str, Any]:
        """Get service health status."""
        return {
            "enabled": self.enabled,
            "circuit_breaker_open": self._circuit_breaker_open,
            "queue_size": self._event_queue.qsize(),
            "metrics_count": len(self._metrics_aggregation),
            "background_tasks_running": len(
                [t for t in self._background_tasks if not t.done()]
            ),
            "failures": self._circuit_breaker_failures,
        }

    @asynccontextmanager
    async def span_context(
        self, operation_name: str, properties: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Any, None]:
        """Create an async context manager for spans."""
        start_time = time.time()

        try:
            await self.track_event_async(
                f"{operation_name}.start",
                properties={**(properties or {}), "operation": operation_name},
            )

            yield operation_name

            # Track success
            duration = time.time() - start_time
            await self.track_metric_async(
                f"{operation_name}.duration",
                duration * 1000,  # Convert to milliseconds
                properties,
            )

        except Exception as e:
            # Track failure
            await self.track_exception_async(e, properties=properties)
            raise
        finally:
            await self.track_event_async(
                f"{operation_name}.end",
                properties={**(properties or {}), "operation": operation_name},
            )

    async def shutdown(self) -> None:
        """Gracefully shutdown the service."""
        logger.info("Shutting down reactive telemetry service...")

        # Signal shutdown
        self._shutdown_event.set()

        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()

        # Wait for tasks to complete
        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)

        # Process remaining events
        remaining_events = []
        while not self._event_queue.empty():
            try:
                event = self._event_queue.get_nowait()
                remaining_events.append(event)
            except asyncio.QueueEmpty:
                break

        if remaining_events:
            await self._process_events_batch(remaining_events)

        # Shutdown thread pool
        self._thread_pool.shutdown(wait=True)

        logger.info("Reactive telemetry service shutdown complete")
