"""
Reactive Telemetry Collector

Modern telemetry and metrics collection system with reactive patterns, supporting:
- Multiple metric types (counters, gauges, histograms, timers)
- Real-time streaming with backpressure handling
- Metric aggregation and caching
- Batch processing and export
- Performance monitoring and health checks
"""

import asyncio
import time
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import (
    Any,
    AsyncIterator,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    TypeVar,
    Union,
    Tuple,
)
import threading
from concurrent.futures import ThreadPoolExecutor
import logging
import statistics
import weakref

from ..core.result import Result
from ..core.error import StubError
from ..model.authorization_context import AuthorizationContext

logger = logging.getLogger(__name__)

T = TypeVar("T")


class MetricType(Enum):
    """Types of telemetry metrics."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    SUMMARY = "summary"


@dataclass
class TelemetryMetric:
    """Base telemetry metric."""

    name: str
    value: Union[int, float]
    metric_type: MetricType
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary representation."""
        return {
            "name": self.name,
            "value": self.value,
            "type": self.metric_type.value,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags,
            "metadata": self.metadata,
        }


@dataclass
class TelemetryEvent:
    """Telemetry event for tracking occurrences."""

    name: str
    properties: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    severity: str = "info"
    correlation_id: Optional[str] = None
    authorization_context: Optional[AuthorizationContext] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary representation."""
        return {
            "name": self.name,
            "properties": self.properties,
            "timestamp": self.timestamp.isoformat(),
            "severity": self.severity,
            "correlation_id": self.correlation_id,
        }


class MetricAggregator:
    """Aggregates metrics over time windows."""

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.values: deque = deque(maxlen=window_size)
        self.lock = threading.Lock()

    def add_value(self, value: Union[int, float]) -> None:
        """Add a value to the aggregator."""
        with self.lock:
            self.values.append((time.time(), value))

    def get_stats(self) -> Dict[str, float]:
        """Get aggregated statistics."""
        with self.lock:
            if not self.values:
                return {
                    "count": 0,
                    "sum": 0.0,
                    "min": 0.0,
                    "max": 0.0,
                    "mean": 0.0,
                    "median": 0.0,
                }

            values_only = [v for _, v in self.values]
            return {
                "count": len(values_only),
                "sum": sum(values_only),
                "min": min(values_only),
                "max": max(values_only),
                "mean": statistics.mean(values_only),
                "median": statistics.median(values_only),
            }

    def reset(self) -> None:
        """Reset the aggregator."""
        with self.lock:
            self.values.clear()


class TelemetryCounter:
    """Thread-safe counter metric."""

    def __init__(self, name: str, tags: Optional[Dict[str, str]] = None):
        self.name = name
        self.tags = tags or {}
        self._value = 0
        self._lock = threading.Lock()

    def increment(self, amount: Union[int, float] = 1) -> None:
        """Increment the counter."""
        with self._lock:
            self._value += amount

    def get_value(self) -> Union[int, float]:
        """Get current counter value."""
        with self._lock:
            return self._value

    def reset(self) -> None:
        """Reset counter to zero."""
        with self._lock:
            self._value = 0

    def to_metric(self) -> TelemetryMetric:
        """Convert to TelemetryMetric."""
        return TelemetryMetric(
            name=self.name,
            value=self.get_value(),
            metric_type=MetricType.COUNTER,
            tags=self.tags,
        )


class TelemetryGauge:
    """Thread-safe gauge metric."""

    def __init__(self, name: str, tags: Optional[Dict[str, str]] = None):
        self.name = name
        self.tags = tags or {}
        self._value = 0.0
        self._lock = threading.Lock()

    def set_value(self, value: Union[int, float]) -> None:
        """Set the gauge value."""
        with self._lock:
            self._value = float(value)

    def increment(self, amount: Union[int, float] = 1) -> None:
        """Increment the gauge."""
        with self._lock:
            self._value += amount

    def decrement(self, amount: Union[int, float] = 1) -> None:
        """Decrement the gauge."""
        with self._lock:
            self._value -= amount

    def get_value(self) -> float:
        """Get current gauge value."""
        with self._lock:
            return self._value

    def to_metric(self) -> TelemetryMetric:
        """Convert to TelemetryMetric."""
        return TelemetryMetric(
            name=self.name,
            value=self.get_value(),
            metric_type=MetricType.GAUGE,
            tags=self.tags,
        )


class TelemetryHistogram:
    """Histogram metric for tracking value distributions."""

    def __init__(
        self,
        name: str,
        buckets: Optional[List[float]] = None,
        tags: Optional[Dict[str, str]] = None,
    ):
        self.name = name
        self.tags = tags or {}
        self.buckets = buckets or [0.1, 0.5, 1.0, 2.5, 5.0, 10.0, float("inf")]
        self.bucket_counts = [0] * len(self.buckets)
        self.sum = 0.0
        self.count = 0
        self._lock = threading.Lock()

    def observe(self, value: Union[int, float]) -> None:
        """Record an observation."""
        with self._lock:
            self.sum += value
            self.count += 1

            # Find the appropriate bucket
            for i, bucket in enumerate(self.buckets):
                if value <= bucket:
                    self.bucket_counts[i] += 1

    def get_stats(self) -> Dict[str, Any]:
        """Get histogram statistics."""
        with self._lock:
            return {
                "count": self.count,
                "sum": self.sum,
                "buckets": dict(zip(self.buckets, self.bucket_counts)),
                "mean": self.sum / self.count if self.count > 0 else 0.0,
            }

    def reset(self) -> None:
        """Reset histogram."""
        with self._lock:
            self.bucket_counts = [0] * len(self.buckets)
            self.sum = 0.0
            self.count = 0

    def to_metric(self) -> TelemetryMetric:
        """Convert to TelemetryMetric."""
        return TelemetryMetric(
            name=self.name,
            value=self.get_stats(),
            metric_type=MetricType.HISTOGRAM,
            tags=self.tags,
        )


class TelemetryTimer:
    """Timer metric for measuring duration."""

    def __init__(self, name: str, tags: Optional[Dict[str, str]] = None):
        self.name = name
        self.tags = tags or {}
        self.histogram = TelemetryHistogram(f"{name}_duration", tags=tags)
        self._start_time: Optional[float] = None

    def __enter__(self):
        """Start timing."""
        self._start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timing and record duration."""
        if self._start_time is not None:
            duration = time.time() - self._start_time
            self.histogram.observe(duration)

    def time_callable(self, func: Callable[[], T]) -> Tuple[T, float]:
        """Time a callable and return result with duration."""
        start_time = time.time()
        try:
            result = func()
            return result, time.time() - start_time
        finally:
            duration = time.time() - start_time
            self.histogram.observe(duration)

    async def time_async_callable(self, func: Callable[[], T]) -> Tuple[T, float]:
        """Time an async callable and return result with duration."""
        start_time = time.time()
        try:
            result = await func()
            return result, time.time() - start_time
        finally:
            duration = time.time() - start_time
            self.histogram.observe(duration)

    def get_stats(self) -> Dict[str, Any]:
        """Get timer statistics."""
        return self.histogram.get_stats()

    def to_metric(self) -> TelemetryMetric:
        """Convert to TelemetryMetric."""
        return TelemetryMetric(
            name=self.name,
            value=self.get_stats(),
            metric_type=MetricType.TIMER,
            tags=self.tags,
        )


@dataclass
class TelemetryConfig:
    """Configuration for telemetry collector."""

    enabled: bool = True
    max_metrics_cache: int = 10000
    flush_interval_seconds: float = 30.0
    batch_size: int = 100
    max_retries: int = 3
    enable_aggregation: bool = True
    aggregation_window_size: int = 1000
    export_timeout_seconds: float = 10.0
    enable_health_checks: bool = True
    health_check_interval_seconds: float = 60.0


class MetricsRegistry:
    """Registry for managing metrics instances."""

    def __init__(self):
        self.counters: Dict[str, TelemetryCounter] = {}
        self.gauges: Dict[str, TelemetryGauge] = {}
        self.histograms: Dict[str, TelemetryHistogram] = {}
        self.timers: Dict[str, TelemetryTimer] = {}
        self.aggregators: Dict[str, MetricAggregator] = {}
        self._lock = threading.RLock()

    def get_or_create_counter(
        self, name: str, tags: Optional[Dict[str, str]] = None
    ) -> TelemetryCounter:
        """Get or create a counter metric."""
        key = f"{name}:{hash(str(sorted((tags or {}).items())))}"
        with self._lock:
            if key not in self.counters:
                self.counters[key] = TelemetryCounter(name, tags)
            return self.counters[key]

    def get_or_create_gauge(
        self, name: str, tags: Optional[Dict[str, str]] = None
    ) -> TelemetryGauge:
        """Get or create a gauge metric."""
        key = f"{name}:{hash(str(sorted((tags or {}).items())))}"
        with self._lock:
            if key not in self.gauges:
                self.gauges[key] = TelemetryGauge(name, tags)
            return self.gauges[key]

    def get_or_create_histogram(
        self,
        name: str,
        buckets: Optional[List[float]] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> TelemetryHistogram:
        """Get or create a histogram metric."""
        key = f"{name}:{hash(str(sorted((tags or {}).items())))}"
        with self._lock:
            if key not in self.histograms:
                self.histograms[key] = TelemetryHistogram(name, buckets, tags)
            return self.histograms[key]

    def get_or_create_timer(
        self, name: str, tags: Optional[Dict[str, str]] = None
    ) -> TelemetryTimer:
        """Get or create a timer metric."""
        key = f"{name}:{hash(str(sorted((tags or {}).items())))}"
        with self._lock:
            if key not in self.timers:
                self.timers[key] = TelemetryTimer(name, tags)
            return self.timers[key]

    def get_all_metrics(self) -> List[TelemetryMetric]:
        """Get all metrics as TelemetryMetric instances."""
        metrics = []
        with self._lock:
            # Add counters
            for counter in self.counters.values():
                metrics.append(counter.to_metric())

            # Add gauges
            for gauge in self.gauges.values():
                metrics.append(gauge.to_metric())

            # Add histograms
            for histogram in self.histograms.values():
                metrics.append(histogram.to_metric())

            # Add timers
            for timer in self.timers.values():
                metrics.append(timer.to_metric())

        return metrics

    def reset_all(self) -> None:
        """Reset all metrics."""
        with self._lock:
            for counter in self.counters.values():
                counter.reset()

            for histogram in self.histograms.values():
                histogram.reset()


class ReactiveTelemetryCollector:
    """
    Reactive telemetry collector with streaming capabilities.

    Features:
    - Real-time metric collection and streaming
    - Batch processing with backpressure handling
    - Metric aggregation and caching
    - Health monitoring and circuit breaker patterns
    - Export to multiple backends
    """

    def __init__(self, config: Optional[TelemetryConfig] = None):
        self.config = config or TelemetryConfig()
        self.registry = MetricsRegistry()
        self.events_buffer: deque = deque(maxlen=self.config.max_metrics_cache)
        self.metrics_buffer: deque = deque(maxlen=self.config.max_metrics_cache)
        self.is_running = False
        self.executor = ThreadPoolExecutor(max_workers=4)
        self._flush_task: Optional[asyncio.Task] = None
        self._health_task: Optional[asyncio.Task] = None
        self._lock = threading.RLock()

        # Performance metrics
        self.metrics_collected = TelemetryCounter("telemetry_metrics_collected")
        self.events_collected = TelemetryCounter("telemetry_events_collected")
        self.export_errors = TelemetryCounter("telemetry_export_errors")
        self.export_duration = TelemetryTimer("telemetry_export_duration")

        # Health status
        self.last_export_time = time.time()
        self.export_failure_count = 0

        logger.info(
            f"ReactiveTelemetryCollector initialized with config: {self.config}"
        )

    async def start(self) -> None:
        """Start the telemetry collector."""
        if self.is_running:
            logger.warning("Telemetry collector is already running")
            return

        self.is_running = True
        logger.info("Starting reactive telemetry collector")

        # Start background tasks
        self._flush_task = asyncio.create_task(self._periodic_flush())

        if self.config.enable_health_checks:
            self._health_task = asyncio.create_task(self._health_monitor())

    async def stop(self) -> None:
        """Stop the telemetry collector."""
        if not self.is_running:
            return

        logger.info("Stopping reactive telemetry collector")
        self.is_running = False

        # Cancel background tasks
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass

        if self._health_task:
            self._health_task.cancel()
            try:
                await self._health_task
            except asyncio.CancelledError:
                pass

        # Final flush
        await self.flush()

        # Shutdown executor
        self.executor.shutdown(wait=True)

    def collect_metric(self, metric: TelemetryMetric) -> None:
        """Collect a telemetry metric."""
        if not self.config.enabled:
            return

        with self._lock:
            self.metrics_buffer.append(metric)
            self.metrics_collected.increment()

        logger.debug(f"Collected metric: {metric.name} = {metric.value}")

    def collect_event(self, event: TelemetryEvent) -> None:
        """Collect a telemetry event."""
        if not self.config.enabled:
            return

        with self._lock:
            self.events_buffer.append(event)
            self.events_collected.increment()

        logger.debug(f"Collected event: {event.name}")

    def increment_counter(
        self,
        name: str,
        amount: Union[int, float] = 1,
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """Increment a counter metric."""
        counter = self.registry.get_or_create_counter(name, tags)
        counter.increment(amount)

    def set_gauge(
        self, name: str, value: Union[int, float], tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Set a gauge metric value."""
        gauge = self.registry.get_or_create_gauge(name, tags)
        gauge.set_value(value)

    def observe_histogram(
        self,
        name: str,
        value: Union[int, float],
        buckets: Optional[List[float]] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record a histogram observation."""
        histogram = self.registry.get_or_create_histogram(name, buckets, tags)
        histogram.observe(value)

    def time_operation(
        self, name: str, tags: Optional[Dict[str, str]] = None
    ) -> TelemetryTimer:
        """Create a timer for measuring operation duration."""
        return self.registry.get_or_create_timer(name, tags)

    async def get_metrics_stream(self) -> AsyncIterator[List[TelemetryMetric]]:
        """Get streaming metrics with backpressure handling."""
        while self.is_running:
            if self.metrics_buffer:
                with self._lock:
                    # Get batch of metrics
                    batch_size = min(len(self.metrics_buffer), self.config.batch_size)
                    batch = [self.metrics_buffer.popleft() for _ in range(batch_size)]

                if batch:
                    yield batch

            # Add registry metrics
            registry_metrics = self.registry.get_all_metrics()
            if registry_metrics:
                yield registry_metrics

            await asyncio.sleep(self.config.flush_interval_seconds)

    async def get_events_stream(self) -> AsyncIterator[List[TelemetryEvent]]:
        """Get streaming events with backpressure handling."""
        while self.is_running:
            if self.events_buffer:
                with self._lock:
                    # Get batch of events
                    batch_size = min(len(self.events_buffer), self.config.batch_size)
                    batch = [self.events_buffer.popleft() for _ in range(batch_size)]

                if batch:
                    yield batch

            await asyncio.sleep(self.config.flush_interval_seconds)

    async def flush(self) -> Result[None]:
        """Flush all buffered metrics and events."""
        try:
            with self.export_duration:
                # Export metrics
                if self.metrics_buffer:
                    with self._lock:
                        metrics_to_export = list(self.metrics_buffer)
                        self.metrics_buffer.clear()

                    # Add registry metrics
                    metrics_to_export.extend(self.registry.get_all_metrics())

                    await self._export_metrics(metrics_to_export)

                # Export events
                if self.events_buffer:
                    with self._lock:
                        events_to_export = list(self.events_buffer)
                        self.events_buffer.clear()

                    await self._export_events(events_to_export)

            self.last_export_time = time.time()
            self.export_failure_count = 0
            return Result.success(None)

        except Exception as e:
            self.export_errors.increment()
            self.export_failure_count += 1
            logger.error(f"Failed to flush telemetry data: {e}")
            return Result.failure(StubError("TELEMETRY_FLUSH_ERROR", str(e)))

    async def _export_metrics(self, metrics: List[TelemetryMetric]) -> None:
        """Export metrics to backend (mock implementation)."""
        logger.info(f"Exporting {len(metrics)} metrics")
        # In a real implementation, this would send to monitoring backend
        await asyncio.sleep(0.1)  # Simulate export time

    async def _export_events(self, events: List[TelemetryEvent]) -> None:
        """Export events to backend (mock implementation)."""
        logger.info(f"Exporting {len(events)} events")
        # In a real implementation, this would send to logging backend
        await asyncio.sleep(0.1)  # Simulate export time

    async def _periodic_flush(self) -> None:
        """Periodic flush background task."""
        while self.is_running:
            try:
                await self.flush()
                await asyncio.sleep(self.config.flush_interval_seconds)
            except Exception as e:
                logger.error(f"Error in periodic flush: {e}")
                await asyncio.sleep(5)  # Backoff on error

    async def _health_monitor(self) -> None:
        """Health monitoring background task."""
        while self.is_running:
            try:
                await self._check_health()
                await asyncio.sleep(self.config.health_check_interval_seconds)
            except Exception as e:
                logger.error(f"Error in health monitor: {e}")
                await asyncio.sleep(10)  # Backoff on error

    async def _check_health(self) -> None:
        """Check telemetry collector health."""
        current_time = time.time()
        time_since_export = current_time - self.last_export_time

        # Check if exports are failing
        if time_since_export > self.config.flush_interval_seconds * 3:
            logger.warning(f"No successful export in {time_since_export:.1f} seconds")

        if self.export_failure_count > 5:
            logger.error(f"High export failure count: {self.export_failure_count}")

        # Check buffer sizes
        with self._lock:
            metrics_buffer_size = len(self.metrics_buffer)
            events_buffer_size = len(self.events_buffer)

        if metrics_buffer_size > self.config.max_metrics_cache * 0.8:
            logger.warning(
                f"Metrics buffer nearly full: {metrics_buffer_size}/{self.config.max_metrics_cache}"
            )

        if events_buffer_size > self.config.max_metrics_cache * 0.8:
            logger.warning(
                f"Events buffer nearly full: {events_buffer_size}/{self.config.max_metrics_cache}"
            )

    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status."""
        current_time = time.time()

        with self._lock:
            metrics_buffer_size = len(self.metrics_buffer)
            events_buffer_size = len(self.events_buffer)

        return {
            "is_running": self.is_running,
            "last_export_time": self.last_export_time,
            "time_since_export": current_time - self.last_export_time,
            "export_failure_count": self.export_failure_count,
            "metrics_buffer_size": metrics_buffer_size,
            "events_buffer_size": events_buffer_size,
            "metrics_collected_total": self.metrics_collected.get_value(),
            "events_collected_total": self.events_collected.get_value(),
            "export_errors_total": self.export_errors.get_value(),
        }

    def __del__(self):
        """Cleanup when collector is destroyed."""
        if self.is_running:
            logger.warning("ReactiveTelemetryCollector destroyed while running")
