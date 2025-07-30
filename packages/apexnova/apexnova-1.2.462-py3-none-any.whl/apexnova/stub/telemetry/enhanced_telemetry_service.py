"""
Enhanced Telemetry Service for Python Stub Implementation

Provides high-level telemetry service with advanced monitoring, custom metrics,
and performance tracking. Includes operation tracking, business event monitoring,
and comprehensive exception handling with context.
"""

import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar, Generic
from uuid import uuid4

from .reactive_telemetry_collector import ReactiveTelemetryCollector
from .reactive_application_insights_service import ReactiveApplicationInsightsService


T = TypeVar("T")


@dataclass
class MetricAggregator:
    """Aggregates metrics with statistical calculations"""

    count: int = 0
    sum: float = 0.0
    min: float = float("inf")
    max: float = float("-inf")
    last_updated: datetime = field(default_factory=datetime.now)

    @property
    def average(self) -> float:
        """Calculate average value"""
        return self.sum / self.count if self.count > 0 else 0.0

    def update(self, value: float) -> None:
        """Update aggregator with new value"""
        self.count += 1
        self.sum += value
        self.min = min(self.min, value)
        self.max = max(self.max, value)
        self.last_updated = datetime.now()


@dataclass
class AuthorizationContext:
    """Authorization context for telemetry enrichment"""

    id: str
    roles: List[str] = field(default_factory=list)
    actor: str = ""
    device: str = ""
    location: str = ""
    user_agent: str = ""
    tier: str = ""
    account_id: str = ""
    client_request_id: str = ""
    ip_address: str = ""
    request_time: datetime = field(default_factory=datetime.now)


@dataclass
class OperationMetrics:
    """Metrics for operation tracking"""

    operation_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    operation_id: str = field(default_factory=lambda: str(uuid4()))


@dataclass
class BatchOperationResult:
    """Result of batch operation processing"""

    batch_name: str
    total_items: int
    success_count: int
    failure_count: int
    duration_ms: float
    start_time: datetime
    end_time: datetime
    errors: List[str] = field(default_factory=list)


class EnhancedTelemetryService:
    """
    Enhanced telemetry service with advanced monitoring, custom metrics, and performance tracking.

    Provides comprehensive telemetry capabilities including:
    - Operation tracking with automatic timing
    - Custom performance metrics with aggregation
    - Business event tracking
    - Exception tracking with context
    - Batch operation monitoring
    - Dependency call tracking
    """

    def __init__(
        self,
        telemetry_collector: Optional[ReactiveTelemetryCollector] = None,
        application_insights_service: Optional[
            ReactiveApplicationInsightsService
        ] = None,
        thread_pool_size: int = 10,
    ):
        self.logger = logging.getLogger(__name__)
        self.telemetry_collector = telemetry_collector or ReactiveTelemetryCollector()
        self.application_insights_service = (
            application_insights_service or ReactiveApplicationInsightsService()
        )

        # Metric aggregators and counters
        self.custom_metrics: Dict[str, MetricAggregator] = {}
        self.operation_counters: Dict[str, int] = {}

        # Thread pool for async operations
        self.executor = ThreadPoolExecutor(max_workers=thread_pool_size)

        # Service state
        self.is_started = False

        self.logger.info("Enhanced Telemetry Service initialized")

    async def start(self) -> None:
        """Start the enhanced telemetry service"""
        if self.is_started:
            return

        await self.telemetry_collector.start()
        self.is_started = True
        self.logger.info("Enhanced Telemetry Service started")

    async def stop(self) -> None:
        """Stop the enhanced telemetry service"""
        if not self.is_started:
            return

        await self.telemetry_collector.stop()
        self.executor.shutdown(wait=True)
        self.is_started = False
        self.logger.info("Enhanced Telemetry Service stopped")

    def track_performance_metric(
        self,
        metric_name: str,
        value: float,
        properties: Optional[Dict[str, str]] = None,
        authorization_context: Optional[AuthorizationContext] = None,
    ) -> None:
        """
        Track custom performance metrics with aggregation.

        Args:
            metric_name: Name of the metric
            value: Metric value
            properties: Additional properties
            authorization_context: Authorization context for enrichment
        """
        # Update local aggregator
        if metric_name not in self.custom_metrics:
            self.custom_metrics[metric_name] = MetricAggregator()

        self.custom_metrics[metric_name].update(value)

        # Build enriched properties
        enriched_properties = self._build_properties(
            properties or {}, authorization_context
        )

        # Send to telemetry collector
        asyncio.create_task(
            self._track_metric_async(metric_name, value, enriched_properties)
        )

        self.logger.debug(f"Tracked performance metric: {metric_name} = {value}")

    @asynccontextmanager
    async def track_operation(
        self,
        operation_name: str,
        properties: Optional[Dict[str, str]] = None,
        authorization_context: Optional[AuthorizationContext] = None,
    ):
        """
        Context manager for tracking operation duration with automatic calculation.

        Args:
            operation_name: Name of the operation
            properties: Additional properties
            authorization_context: Authorization context for enrichment

        Yields:
            OperationMetrics: Metrics object for the operation
        """
        operation_id = str(uuid4())
        start_time = datetime.now()

        # Increment operation counter
        self.operation_counters[operation_name] = (
            self.operation_counters.get(operation_name, 0) + 1
        )

        metrics = OperationMetrics(
            operation_name=operation_name,
            start_time=start_time,
            operation_id=operation_id,
            properties=properties or {},
        )

        self.logger.debug(f"Starting operation: {operation_name} [ID: {operation_id}]")

        try:
            yield metrics

            # Operation completed successfully
            end_time = datetime.now()
            duration_ms = (end_time - start_time).total_seconds() * 1000

            metrics.end_time = end_time
            metrics.duration_ms = duration_ms
            metrics.success = True

            await self._track_operation_complete(metrics, authorization_context)

            self.logger.debug(
                f"Operation completed successfully: {operation_name} [ID: {operation_id}] "
                f"in {duration_ms:.2f}ms"
            )

        except Exception as exception:
            # Operation failed
            end_time = datetime.now()
            duration_ms = (end_time - start_time).total_seconds() * 1000

            metrics.end_time = end_time
            metrics.duration_ms = duration_ms
            metrics.success = False
            metrics.error_message = str(exception)

            await self._track_operation_complete(metrics, authorization_context)
            await self.track_exception(
                exception, operation_name, properties, authorization_context
            )

            self.logger.error(
                f"Operation failed: {operation_name} [ID: {operation_id}] "
                f"after {duration_ms:.2f}ms - {exception}"
            )

            raise

    async def track_exception(
        self,
        exception: Exception,
        operation: Optional[str] = None,
        properties: Optional[Dict[str, str]] = None,
        authorization_context: Optional[AuthorizationContext] = None,
    ) -> None:
        """
        Enhanced exception tracking with context.

        Args:
            exception: The exception to track
            operation: Operation where exception occurred
            properties: Additional properties
            authorization_context: Authorization context for enrichment
        """
        enriched_properties = self._build_properties(
            properties or {}, authorization_context
        )

        if operation:
            enriched_properties["operation"] = operation

        enriched_properties.update(
            {
                "exception_type": type(exception).__name__,
                "exception_message": str(exception),
                "timestamp": datetime.now().isoformat(),
            }
        )

        # Track stack trace for severe exceptions
        if isinstance(exception, (RuntimeError, SystemError)):
            import traceback

            stack_trace = traceback.format_exc()
            enriched_properties["stack_trace"] = stack_trace[:8192]  # Limit size

        # Send to Application Insights
        await self.application_insights_service.track_event(
            {
                "name": "Exception",
                "properties": enriched_properties,
                "measurements": {},
                "userId": authorization_context.id if authorization_context else None,
                "sessionId": enriched_properties.get("session_id"),
                "requestId": enriched_properties.get("client_request_id"),
            }
        )

        # Track exception count metric
        self.track_performance_metric(
            "exception_count", 1.0, enriched_properties, authorization_context
        )

        self.logger.error(
            f"Exception tracked: {type(exception).__name__} - {exception}"
        )

    async def track_dependency(
        self,
        dependency_name: str,
        command_name: str,
        start_time: datetime,
        duration: timedelta,
        success: bool,
        properties: Optional[Dict[str, str]] = None,
        authorization_context: Optional[AuthorizationContext] = None,
    ) -> None:
        """
        Track dependency calls with timing.

        Args:
            dependency_name: Name of the dependency
            command_name: Command or operation name
            start_time: When the call started
            duration: Duration of the call
            success: Whether the call was successful
            properties: Additional properties
            authorization_context: Authorization context for enrichment
        """
        enriched_properties = self._build_properties(
            properties or {}, authorization_context
        )
        enriched_properties.update(
            {
                "dependency_name": dependency_name,
                "command_name": command_name,
                "success": str(success),
                "duration_ms": str(duration.total_seconds() * 1000),
                "start_time": start_time.isoformat(),
            }
        )

        # Send to Application Insights
        await self.application_insights_service.track_event(
            {
                "name": "DependencyCall",
                "properties": enriched_properties,
                "measurements": {
                    "duration_ms": duration.total_seconds() * 1000,
                    "success": 1.0 if success else 0.0,
                },
                "userId": authorization_context.id if authorization_context else None,
                "sessionId": enriched_properties.get("session_id"),
                "requestId": enriched_properties.get("client_request_id"),
            }
        )

        self.logger.debug(
            f"Dependency call tracked: {dependency_name}.{command_name} - {success}"
        )

    async def track_business_event(
        self,
        event_name: str,
        properties: Optional[Dict[str, str]] = None,
        metrics: Optional[Dict[str, float]] = None,
        authorization_context: Optional[AuthorizationContext] = None,
    ) -> None:
        """
        Track business events with rich context.

        Args:
            event_name: Name of the business event
            properties: Event properties
            metrics: Event metrics
            authorization_context: Authorization context for enrichment
        """
        enriched_properties = self._build_properties(
            properties or {}, authorization_context
        )
        enriched_properties["event_type"] = "business_event"

        # Send to Application Insights
        await self.application_insights_service.track_event(
            {
                "name": event_name,
                "properties": enriched_properties,
                "measurements": metrics or {},
                "userId": authorization_context.id if authorization_context else None,
                "sessionId": enriched_properties.get("session_id"),
                "requestId": enriched_properties.get("client_request_id"),
            }
        )

        self.logger.info(f"Business event tracked: {event_name}")

    async def track_page_view(
        self,
        page_name: str,
        url: Optional[str] = None,
        duration: Optional[timedelta] = None,
        properties: Optional[Dict[str, str]] = None,
        authorization_context: Optional[AuthorizationContext] = None,
    ) -> None:
        """
        Track page views for web applications.

        Args:
            page_name: Name of the page
            url: Page URL
            duration: Time spent on page
            properties: Additional properties
            authorization_context: Authorization context for enrichment
        """
        enriched_properties = self._build_properties(
            properties or {}, authorization_context
        )
        enriched_properties["page_name"] = page_name

        if url:
            enriched_properties["url"] = url

        measurements = {}
        if duration:
            measurements["duration_ms"] = duration.total_seconds() * 1000

        # Send to Application Insights
        await self.application_insights_service.track_event(
            {
                "name": "PageView",
                "properties": enriched_properties,
                "measurements": measurements,
                "userId": authorization_context.id if authorization_context else None,
                "sessionId": enriched_properties.get("session_id"),
                "requestId": enriched_properties.get("client_request_id"),
            }
        )

        self.logger.debug(f"Page view tracked: {page_name}")

    async def track_batch_operation(
        self,
        batch_name: str,
        items: List[Any],
        processor: Callable[[Any], Any],
        properties: Optional[Dict[str, str]] = None,
        authorization_context: Optional[AuthorizationContext] = None,
        max_concurrency: int = 10,
    ) -> BatchOperationResult:
        """
        Track batch operation with detailed metrics.

        Args:
            batch_name: Name of the batch operation
            items: Items to process
            processor: Processing function for each item
            properties: Additional properties
            authorization_context: Authorization context for enrichment
            max_concurrency: Maximum concurrent processing

        Returns:
            BatchOperationResult: Results of batch processing
        """
        start_time = datetime.now()
        success_count = 0
        failure_count = 0
        errors = []

        async with self.track_operation(
            f"batch_{batch_name}", properties, authorization_context
        ):
            # Process items with concurrency control
            semaphore = asyncio.Semaphore(max_concurrency)

            async def process_item(item: Any) -> bool:
                async with semaphore:
                    try:
                        if asyncio.iscoroutinefunction(processor):
                            await processor(item)
                        else:
                            # Run sync function in thread pool
                            await asyncio.get_event_loop().run_in_executor(
                                self.executor, processor, item
                            )
                        return True
                    except Exception as e:
                        errors.append(str(e))
                        await self.track_exception(
                            e,
                            "batch_item_processing",
                            properties,
                            authorization_context,
                        )
                        return False

            # Process all items concurrently
            results = await asyncio.gather(
                *[process_item(item) for item in items], return_exceptions=True
            )

            # Count successes and failures
            for result in results:
                if isinstance(result, Exception):
                    failure_count += 1
                elif result:
                    success_count += 1
                else:
                    failure_count += 1

        end_time = datetime.now()
        duration_ms = (end_time - start_time).total_seconds() * 1000

        # Track batch metrics
        self.track_performance_metric(
            f"{batch_name}_batch_size",
            float(len(items)),
            properties,
            authorization_context,
        )
        self.track_performance_metric(
            f"{batch_name}_success_count",
            float(success_count),
            properties,
            authorization_context,
        )
        self.track_performance_metric(
            f"{batch_name}_failure_count",
            float(failure_count),
            properties,
            authorization_context,
        )
        self.track_performance_metric(
            f"{batch_name}_batch_duration_ms",
            duration_ms,
            properties,
            authorization_context,
        )

        result = BatchOperationResult(
            batch_name=batch_name,
            total_items=len(items),
            success_count=success_count,
            failure_count=failure_count,
            duration_ms=duration_ms,
            start_time=start_time,
            end_time=end_time,
            errors=errors,
        )

        self.logger.info(
            f"Batch operation '{batch_name}' completed: {success_count} succeeded, "
            f"{failure_count} failed in {duration_ms:.2f}ms"
        )

        return result

    def get_metrics_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get aggregated metrics for monitoring"""
        return {
            name: {
                "count": aggregator.count,
                "sum": aggregator.sum,
                "average": aggregator.average,
                "min": aggregator.min,
                "max": aggregator.max,
                "last_updated": aggregator.last_updated.isoformat(),
            }
            for name, aggregator in self.custom_metrics.items()
        }

    def get_operation_counters(self) -> Dict[str, int]:
        """Get operation counters"""
        return self.operation_counters.copy()

    def clear_metrics(self) -> None:
        """Clear all metrics (useful for testing)"""
        self.custom_metrics.clear()
        self.operation_counters.clear()
        self.logger.debug("All metrics cleared")

    async def flush(self) -> None:
        """Flush telemetry immediately"""
        await self.telemetry_collector.flush()
        await self.application_insights_service.flush()
        self.logger.debug("Telemetry flushed")

    async def _track_operation_complete(
        self,
        metrics: OperationMetrics,
        authorization_context: Optional[AuthorizationContext],
    ) -> None:
        """Track operation completion with detailed metrics"""
        properties = self._build_properties(metrics.properties, authorization_context)
        properties.update(
            {
                "operation": metrics.operation_name,
                "success": str(metrics.success),
                "duration_ms": str(metrics.duration_ms or 0),
                "operation_id": metrics.operation_id,
            }
        )

        if metrics.error_message:
            properties["error_message"] = metrics.error_message

        # Track as custom event
        await self.application_insights_service.track_event(
            {
                "name": "OperationCompleted",
                "properties": properties,
                "measurements": {
                    "duration_ms": metrics.duration_ms or 0,
                    "success": 1.0 if metrics.success else 0.0,
                },
                "userId": authorization_context.id if authorization_context else None,
                "sessionId": properties.get("session_id"),
                "requestId": properties.get("client_request_id"),
            }
        )

        # Track duration as metric
        if metrics.duration_ms is not None:
            self.track_performance_metric(
                f"{metrics.operation_name}_duration_ms",
                metrics.duration_ms,
                properties,
                authorization_context,
            )

        # Track success rate
        self.track_performance_metric(
            f"{metrics.operation_name}_success_rate",
            1.0 if metrics.success else 0.0,
            properties,
            authorization_context,
        )

    async def _track_metric_async(
        self, metric_name: str, value: float, properties: Dict[str, str]
    ) -> None:
        """Track metric asynchronously"""
        await self.telemetry_collector.track_metric(metric_name, value, properties)

    def _build_properties(
        self,
        properties: Dict[str, str],
        authorization_context: Optional[AuthorizationContext],
    ) -> Dict[str, str]:
        """Build enriched properties with authorization context"""
        result = properties.copy()

        if authorization_context:
            result.update(
                {
                    "user_id": authorization_context.id,
                    "roles": ",".join(authorization_context.roles),
                    "actor": authorization_context.actor,
                    "device": authorization_context.device,
                    "location": authorization_context.location,
                    "user_agent": authorization_context.user_agent,
                    "tier": authorization_context.tier,
                    "account_id": authorization_context.account_id,
                    "client_request_id": authorization_context.client_request_id,
                    "ip_address": authorization_context.ip_address,
                    "request_time": authorization_context.request_time.isoformat(),
                }
            )

        # Add default properties
        result["timestamp"] = datetime.now().isoformat()
        result["service"] = "enhanced_telemetry_service"

        return result
