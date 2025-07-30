"""
Reactive Observability Collector

Distributed tracing and observability framework with reactive patterns, supporting:
- Distributed tracing with span management
- Context propagation across service boundaries
- Trace sampling and filtering
- Real-time trace streaming
- Performance metrics and analysis
"""

import asyncio
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import (
    Any,
    AsyncIterator,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Union,
    Callable,
)
import threading
from concurrent.futures import ThreadPoolExecutor
import logging
import json
from contextvars import ContextVar

from ..core.result import Result
from ..core.error import StubError
from ..model.authorization_context import AuthorizationContext

logger = logging.getLogger(__name__)

# Context variable for distributed tracing
current_trace_context: ContextVar[Optional["TraceContext"]] = ContextVar(
    "current_trace_context", default=None
)
current_span_context: ContextVar[Optional["SpanContext"]] = ContextVar(
    "current_span_context", default=None
)


class SpanKind(Enum):
    """Types of spans."""

    INTERNAL = "internal"
    SERVER = "server"
    CLIENT = "client"
    PRODUCER = "producer"
    CONSUMER = "consumer"


class SpanStatus(Enum):
    """Span completion status."""

    OK = "ok"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class SpanContext:
    """Context for a single span."""

    span_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_span_id: Optional[str] = None
    baggage: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "span_id": self.span_id,
            "trace_id": self.trace_id,
            "parent_span_id": self.parent_span_id,
            "baggage": self.baggage,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SpanContext":
        """Create from dictionary representation."""
        return cls(
            span_id=data.get("span_id", str(uuid.uuid4())),
            trace_id=data.get("trace_id", str(uuid.uuid4())),
            parent_span_id=data.get("parent_span_id"),
            baggage=data.get("baggage", {}),
        )


@dataclass
class TraceContext:
    """Context for an entire trace."""

    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    service_name: str = "unknown"
    operation_name: str = "unknown"
    correlation_id: Optional[str] = None
    authorization_context: Optional[AuthorizationContext] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "trace_id": self.trace_id,
            "service_name": self.service_name,
            "operation_name": self.operation_name,
            "correlation_id": self.correlation_id,
            "metadata": self.metadata,
        }


@dataclass
class Span:
    """Represents a span in distributed tracing."""

    context: SpanContext
    operation_name: str
    kind: SpanKind = SpanKind.INTERNAL
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = None
    status: SpanStatus = SpanStatus.OK
    tags: Dict[str, Any] = field(default_factory=dict)
    events: List[Dict[str, Any]] = field(default_factory=list)
    duration_ms: Optional[float] = None
    error: Optional[Exception] = None

    def finish(self, status: Optional[SpanStatus] = None) -> None:
        """Finish the span."""
        self.end_time = datetime.now(timezone.utc)
        if status:
            self.status = status

        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            self.duration_ms = delta.total_seconds() * 1000

    def set_tag(self, key: str, value: Any) -> None:
        """Set a tag on the span."""
        self.tags[key] = value

    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Add an event to the span."""
        event = {
            "name": name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "attributes": attributes or {},
        }
        self.events.append(event)

    def set_error(self, error: Exception) -> None:
        """Set error information on the span."""
        self.error = error
        self.status = SpanStatus.ERROR
        self.set_tag("error", True)
        self.set_tag("error.type", type(error).__name__)
        self.set_tag("error.message", str(error))

    def to_dict(self) -> Dict[str, Any]:
        """Convert span to dictionary representation."""
        return {
            "context": self.context.to_dict(),
            "operation_name": self.operation_name,
            "kind": self.kind.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": self.duration_ms,
            "status": self.status.value,
            "tags": self.tags,
            "events": self.events,
            "error": str(self.error) if self.error else None,
        }


class SpanBuilder:
    """Builder for creating spans with configuration."""

    def __init__(self, operation_name: str, tracer: "ReactiveObservabilityCollector"):
        self.operation_name = operation_name
        self.tracer = tracer
        self.kind = SpanKind.INTERNAL
        self.tags: Dict[str, Any] = {}
        self.parent_span_context: Optional[SpanContext] = None
        self.start_time: Optional[datetime] = None

    def with_kind(self, kind: SpanKind) -> "SpanBuilder":
        """Set the span kind."""
        self.kind = kind
        return self

    def with_tag(self, key: str, value: Any) -> "SpanBuilder":
        """Add a tag to the span."""
        self.tags[key] = value
        return self

    def with_tags(self, tags: Dict[str, Any]) -> "SpanBuilder":
        """Add multiple tags to the span."""
        self.tags.update(tags)
        return self

    def with_parent(self, parent_context: SpanContext) -> "SpanBuilder":
        """Set the parent span context."""
        self.parent_span_context = parent_context
        return self

    def with_start_time(self, start_time: datetime) -> "SpanBuilder":
        """Set custom start time."""
        self.start_time = start_time
        return self

    def start(self) -> Span:
        """Start the span."""
        # Create span context
        if self.parent_span_context:
            span_context = SpanContext(
                trace_id=self.parent_span_context.trace_id,
                parent_span_id=self.parent_span_context.span_id,
                baggage=self.parent_span_context.baggage.copy(),
            )
        else:
            span_context = SpanContext()

        # Create span
        span = Span(
            context=span_context,
            operation_name=self.operation_name,
            kind=self.kind,
            start_time=self.start_time or datetime.now(timezone.utc),
            tags=self.tags.copy(),
        )

        # Register with tracer
        self.tracer._register_span(span)

        return span


@dataclass
class TracingConfig:
    """Configuration for tracing system."""

    enabled: bool = True
    service_name: str = "unknown-service"
    sampling_rate: float = 1.0  # 1.0 = 100% sampling
    max_spans_per_trace: int = 1000
    max_trace_duration_seconds: float = 300.0  # 5 minutes
    batch_size: int = 100
    flush_interval_seconds: float = 10.0
    max_queue_size: int = 10000
    enable_automatic_instrumentation: bool = True
    export_timeout_seconds: float = 30.0


class SpanProcessor(ABC):
    """Abstract base class for span processors."""

    @abstractmethod
    async def on_start(self, span: Span, parent_context: Optional[SpanContext]) -> None:
        """Called when a span starts."""
        pass

    @abstractmethod
    async def on_end(self, span: Span) -> None:
        """Called when a span ends."""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the processor."""
        pass


class BatchSpanProcessor(SpanProcessor):
    """Batch span processor for efficient export."""

    def __init__(self, config: TracingConfig):
        self.config = config
        self.spans_queue: asyncio.Queue = asyncio.Queue(maxsize=config.max_queue_size)
        self.is_running = False
        self._export_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Start the batch processor."""
        if self.is_running:
            return

        self.is_running = True
        self._export_task = asyncio.create_task(self._export_worker())

    async def shutdown(self) -> None:
        """Shutdown the batch processor."""
        if not self.is_running:
            return

        self.is_running = False

        if self._export_task:
            self._export_task.cancel()
            try:
                await self._export_task
            except asyncio.CancelledError:
                pass

        # Process remaining spans
        await self._export_batch(force=True)

    async def on_start(self, span: Span, parent_context: Optional[SpanContext]) -> None:
        """Called when a span starts."""
        # No action needed on start for batch processor
        pass

    async def on_end(self, span: Span) -> None:
        """Called when a span ends."""
        if not self.is_running:
            return

        try:
            await asyncio.wait_for(self.spans_queue.put(span), timeout=1.0)
        except asyncio.TimeoutError:
            logger.warning("Spans queue is full, dropping span")

    async def _export_worker(self) -> None:
        """Background worker for exporting spans."""
        while self.is_running:
            try:
                await asyncio.sleep(self.config.flush_interval_seconds)
                await self._export_batch()
            except Exception as e:
                logger.error(f"Error in span export worker: {e}")

    async def _export_batch(self, force: bool = False) -> None:
        """Export a batch of spans."""
        spans_to_export = []

        # Collect spans from queue
        try:
            while len(spans_to_export) < self.config.batch_size:
                span = await asyncio.wait_for(
                    self.spans_queue.get(), timeout=0.1 if not force else 1.0
                )
                spans_to_export.append(span)
        except asyncio.TimeoutError:
            # No more spans available
            pass

        if spans_to_export:
            await self._export_spans(spans_to_export)

    async def _export_spans(self, spans: List[Span]) -> None:
        """Export spans to backend."""
        logger.info(f"Exporting {len(spans)} spans")
        # Mock implementation - in real scenario, send to tracing backend
        await asyncio.sleep(0.1)


@dataclass
class ObservabilityMetrics:
    """Metrics for observability collector."""

    spans_created: int = 0
    spans_finished: int = 0
    traces_active: int = 0
    spans_dropped: int = 0
    export_errors: int = 0
    average_span_duration_ms: float = 0.0
    trace_processing_latency_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "spans_created": self.spans_created,
            "spans_finished": self.spans_finished,
            "traces_active": self.traces_active,
            "spans_dropped": self.spans_dropped,
            "export_errors": self.export_errors,
            "average_span_duration_ms": self.average_span_duration_ms,
            "trace_processing_latency_ms": self.trace_processing_latency_ms,
        }


class DistributedTracingManager:
    """Manager for distributed tracing context."""

    def __init__(self):
        self.active_traces: Dict[str, TraceContext] = {}
        self.active_spans: Dict[str, Span] = {}
        self._lock = threading.RLock()

    def start_trace(
        self,
        operation_name: str,
        service_name: str = "unknown",
        authorization_context: Optional[AuthorizationContext] = None,
    ) -> TraceContext:
        """Start a new trace."""
        trace_context = TraceContext(
            service_name=service_name,
            operation_name=operation_name,
            authorization_context=authorization_context,
        )

        with self._lock:
            self.active_traces[trace_context.trace_id] = trace_context

        # Set in context variables
        current_trace_context.set(trace_context)

        return trace_context

    def finish_trace(self, trace_id: str) -> None:
        """Finish a trace."""
        with self._lock:
            self.active_traces.pop(trace_id, None)

    def get_current_trace(self) -> Optional[TraceContext]:
        """Get current trace context."""
        return current_trace_context.get()

    def get_current_span(self) -> Optional[Span]:
        """Get current span context."""
        span_context = current_span_context.get()
        if span_context:
            with self._lock:
                return self.active_spans.get(span_context.span_id)
        return None

    def register_span(self, span: Span) -> None:
        """Register an active span."""
        with self._lock:
            self.active_spans[span.context.span_id] = span

        # Set in context variables
        current_span_context.set(span.context)

    def finish_span(self, span_id: str) -> None:
        """Finish a span."""
        with self._lock:
            span = self.active_spans.pop(span_id, None)
            if span:
                span.finish()


class ReactiveObservabilityCollector:
    """
    Reactive observability collector for distributed tracing.

    Features:
    - Distributed tracing with automatic context propagation
    - Span lifecycle management
    - Real-time trace streaming
    - Sampling and filtering
    - Performance metrics collection
    """

    def __init__(self, config: Optional[TracingConfig] = None):
        self.config = config or TracingConfig()
        self.tracing_manager = DistributedTracingManager()
        self.span_processor = BatchSpanProcessor(self.config)
        self.metrics = ObservabilityMetrics()
        self.is_running = False
        self._lock = threading.RLock()

        logger.info(
            f"ReactiveObservabilityCollector initialized with config: {self.config}"
        )

    async def start(self) -> None:
        """Start the observability collector."""
        if self.is_running:
            logger.warning("Observability collector is already running")
            return

        self.is_running = True
        logger.info("Starting reactive observability collector")

        # Start span processor
        await self.span_processor.start()

    async def stop(self) -> None:
        """Stop the observability collector."""
        if not self.is_running:
            return

        logger.info("Stopping reactive observability collector")
        self.is_running = False

        # Stop span processor
        await self.span_processor.shutdown()

    def create_span(self, operation_name: str) -> SpanBuilder:
        """Create a new span builder."""
        return SpanBuilder(operation_name, self)

    def start_trace(
        self,
        operation_name: str,
        service_name: Optional[str] = None,
        authorization_context: Optional[AuthorizationContext] = None,
    ) -> TraceContext:
        """Start a new trace."""
        return self.tracing_manager.start_trace(
            operation_name,
            service_name or self.config.service_name,
            authorization_context,
        )

    def get_current_span(self) -> Optional[Span]:
        """Get the current active span."""
        return self.tracing_manager.get_current_span()

    def get_current_trace(self) -> Optional[TraceContext]:
        """Get the current active trace."""
        return self.tracing_manager.get_current_trace()

    async def trace_operation(
        self, operation_name: str, func: Callable, *args, **kwargs
    ):
        """Trace an operation with automatic span management."""
        span = self.create_span(operation_name).start()

        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            span.set_tag("success", True)
            return result

        except Exception as e:
            span.set_error(e)
            raise
        finally:
            span.finish()
            await self._finish_span(span)

    def _register_span(self, span: Span) -> None:
        """Register a span with the collector."""
        if not self.config.enabled:
            return

        # Apply sampling
        if not self._should_sample():
            return

        self.tracing_manager.register_span(span)

        with self._lock:
            self.metrics.spans_created += 1

    async def _finish_span(self, span: Span) -> None:
        """Finish a span and process it."""
        if not self.config.enabled:
            return

        span.finish()

        # Update metrics
        with self._lock:
            self.metrics.spans_finished += 1
            if span.duration_ms:
                # Update average duration (simple moving average)
                current_avg = self.metrics.average_span_duration_ms
                count = self.metrics.spans_finished
                self.metrics.average_span_duration_ms = (
                    current_avg * (count - 1) + span.duration_ms
                ) / count

        # Process span
        await self.span_processor.on_end(span)

        # Cleanup
        self.tracing_manager.finish_span(span.context.span_id)

    def _should_sample(self) -> bool:
        """Determine if a span should be sampled."""
        if self.config.sampling_rate >= 1.0:
            return True
        if self.config.sampling_rate <= 0.0:
            return False

        import random

        return random.random() < self.config.sampling_rate

    async def get_traces_stream(self) -> AsyncIterator[List[Span]]:
        """Get streaming traces."""
        # This would normally stream completed traces
        # For now, it's a mock implementation
        while self.is_running:
            await asyncio.sleep(self.config.flush_interval_seconds)
            # In a real implementation, yield completed traces
            yield []

    def get_metrics(self) -> ObservabilityMetrics:
        """Get current observability metrics."""
        with self._lock:
            # Update active traces count
            self.metrics.traces_active = len(self.tracing_manager.active_traces)
            return ObservabilityMetrics(**self.metrics.__dict__)

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the observability collector."""
        metrics = self.get_metrics()

        return {
            "is_running": self.is_running,
            "service_name": self.config.service_name,
            "sampling_rate": self.config.sampling_rate,
            "metrics": metrics.to_dict(),
            "configuration": {
                "enabled": self.config.enabled,
                "max_spans_per_trace": self.config.max_spans_per_trace,
                "batch_size": self.config.batch_size,
                "flush_interval_seconds": self.config.flush_interval_seconds,
            },
        }

    # Context managers for easy span management
    def span(self, operation_name: str, **kwargs):
        """Context manager for creating and managing spans."""
        return SpanContextManager(self, operation_name, **kwargs)


class SpanContextManager:
    """Context manager for automatic span lifecycle management."""

    def __init__(
        self, collector: ReactiveObservabilityCollector, operation_name: str, **kwargs
    ):
        self.collector = collector
        self.operation_name = operation_name
        self.kwargs = kwargs
        self.span: Optional[Span] = None

    def __enter__(self) -> Span:
        """Start the span."""
        builder = self.collector.create_span(self.operation_name)

        # Apply any additional configuration
        for key, value in self.kwargs.items():
            if key == "kind":
                builder.with_kind(value)
            elif key == "tags":
                builder.with_tags(value)
            elif key == "parent":
                builder.with_parent(value)

        self.span = builder.start()
        return self.span

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Finish the span."""
        if self.span:
            if exc_type:
                self.span.set_error(exc_val)

            # Use asyncio to finish the span if we're in an async context
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self.collector._finish_span(self.span))
            except RuntimeError:
                # Not in async context - finish synchronously
                self.span.finish()

    async def __aenter__(self) -> Span:
        """Async context manager entry."""
        return self.__enter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.span:
            if exc_type:
                self.span.set_error(exc_val)

            await self.collector._finish_span(self.span)
