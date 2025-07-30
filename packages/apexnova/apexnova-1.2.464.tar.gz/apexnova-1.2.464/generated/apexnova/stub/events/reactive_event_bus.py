"""
Reactive Event Bus Implementation

A modern reactive event bus with asyncio and type-safe event handling.
Features:
- Type-safe event publishing and subscribing
- Backpressure handling and buffering strategies
- Event replay and persistence
- Dead letter queue for failed events
- Event filtering and transformation
- Metrics and monitoring
- Retry mechanisms with exponential backoff
"""

import asyncio
import time
import uuid
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import (
    Any,
    AsyncIterator,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Protocol,
    Type,
    TypeVar,
    Union,
    runtime_checkable,
)
import logging
from concurrent.futures import ThreadPoolExecutor

# Type variables
T = TypeVar("T", bound="Event")
R = TypeVar("R")


# Event severity enumeration
class EventSeverity(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# Base event interface
@runtime_checkable
class Event(Protocol):
    """Base event interface that all events must implement"""

    id: str
    timestamp: datetime
    metadata: Dict[str, Any]


@dataclass(frozen=True)
class DomainEvent:
    """Domain event for business logic events"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    aggregate_id: str = ""
    aggregate_type: str = ""
    event_type: str = ""
    version: int = 0
    payload: Any = None


@dataclass(frozen=True)
class SystemEvent:
    """System event for infrastructure and operational events"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: str = ""
    event_type: str = ""
    severity: EventSeverity = EventSeverity.INFO
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)


# Event handler interfaces
class EventHandler(ABC, Generic[T]):
    """Abstract base class for event handlers"""

    @abstractmethod
    async def handle(self, event: T) -> bool:
        """Handle the event. Return True for success, False for failure."""
        pass

    @property
    def handler_name(self) -> str:
        return self.__class__.__name__


class EventProjection(ABC, Generic[T, R]):
    """Abstract base class for event projections"""

    @abstractmethod
    async def project(self, event: T) -> Optional[R]:
        """Project the event to a read model. Return None if projection fails."""
        pass

    @property
    def projection_name(self) -> str:
        return self.__class__.__name__


# Configuration classes
@dataclass
class RetryConfig:
    """Retry configuration for failed event processing"""

    max_attempts: int = 3
    initial_delay: timedelta = timedelta(seconds=1)
    max_delay: timedelta = timedelta(seconds=30)
    backoff_multiplier: float = 2.0


@dataclass
class SubscriptionConfig:
    """Configuration for event subscriptions"""

    buffer_size: int = 1000
    retry_config: RetryConfig = field(default_factory=RetryConfig)
    dead_letter_enabled: bool = True
    metrics_enabled: bool = True


@dataclass
class EventBusConfig:
    """Configuration for the event bus"""

    buffer_size: int = 10000
    replay_buffer_size: int = 1000
    dead_letter_buffer_size: int = 1000
    metrics_collection_interval: timedelta = timedelta(seconds=30)
    enable_event_persistence: bool = False
    enable_circuit_breaker: bool = True


# Metrics and monitoring
@dataclass
class EventBusMetrics:
    """Event bus metrics for monitoring"""

    events_published: int = 0
    events_processed: int = 0
    events_failed: int = 0
    events_in_dead_letter: int = 0
    active_subscriptions: int = 0
    average_processing_time: timedelta = timedelta()
    p95_processing_time: timedelta = timedelta()
    p99_processing_time: timedelta = timedelta()
    throughput_per_second: float = 0.0
    error_rate: float = 0.0


@dataclass
class DeadLetterEvent:
    """Wrapper for events that failed processing"""

    original_event: Event
    failure_reason: str
    failure_count: int
    last_attempt: datetime
    subscription: str


# Event filter and transformer
class EventFilter(Protocol, Generic[T]):
    """Protocol for event filtering"""

    async def matches(self, event: T) -> bool: ...


class EventTransformer(Protocol, Generic[T, R]):
    """Protocol for event transformation"""

    async def transform(self, event: T) -> Optional[R]: ...


# Main reactive event bus implementation
class ReactiveEventBus:
    """
    Main reactive event bus implementation with comprehensive features
    """

    def __init__(self, config: EventBusConfig = None):
        self.config = config or EventBusConfig()
        self.logger = logging.getLogger(self.__class__.__name__)

        # Core components
        self._event_queue = asyncio.Queue(maxsize=self.config.buffer_size)
        self._subscriptions: Dict[str, "SubscriptionManager"] = {}
        self._replay_buffer: deque = deque(maxlen=self.config.replay_buffer_size)
        self._dead_letter_queue: deque = deque(
            maxlen=self.config.dead_letter_buffer_size
        )
        self._lock = asyncio.Lock()

        # Metrics
        self._events_published = 0
        self._events_processed = 0
        self._events_failed = 0
        self._processing_times: List[float] = []

        # Control flags
        self._running = False
        self._processing_task: Optional[asyncio.Task] = None
        self._metrics_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the event bus processing"""
        if self._running:
            return

        self._running = True
        self._processing_task = asyncio.create_task(self._process_events())

        if self.config.metrics_collection_interval.total_seconds() > 0:
            self._metrics_task = asyncio.create_task(self._collect_metrics())

        self.logger.info("Reactive event bus started")

    async def stop(self):
        """Stop the event bus processing"""
        self._running = False

        if self._processing_task:
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass

        if self._metrics_task:
            self._metrics_task.cancel()
            try:
                await self._metrics_task
            except asyncio.CancelledError:
                pass

        # Close all subscriptions
        for subscription in self._subscriptions.values():
            await subscription.close()

        self.logger.info("Reactive event bus stopped")

    async def publish(self, event: Event) -> bool:
        """Publish an event to the bus"""
        try:
            await self._event_queue.put(event)
            self._events_published += 1
            return True
        except Exception as e:
            self.logger.error(f"Failed to publish event {event.id}: {e}")
            return False

    async def publish_batch(self, events: List[Event]) -> List[bool]:
        """Publish multiple events"""
        results = []
        for event in events:
            result = await self.publish(event)
            results.append(result)
        return results

    async def subscribe(
        self,
        subscriber_name: str,
        event_type: Type[T],
        handler: Callable[[T], bool],
        config: SubscriptionConfig = None,
    ) -> "SubscriptionManager":
        """Subscribe to events of a specific type"""
        config = config or SubscriptionConfig()

        subscription = SubscriptionManager(
            subscriber_name=subscriber_name,
            event_type=event_type,
            config=config,
            handler=handler,
            event_bus=self,
        )

        self._subscriptions[subscriber_name] = subscription
        await subscription.start()

        self.logger.info(f"Subscribed {subscriber_name} to {event_type.__name__}")
        return subscription

    async def subscribe_with_filter(
        self,
        subscriber_name: str,
        event_type: Type[T],
        event_filter: EventFilter[T],
        handler: Callable[[T], bool],
        config: SubscriptionConfig = None,
    ) -> "SubscriptionManager":
        """Subscribe with event filtering"""

        async def filtered_handler(event: T) -> bool:
            if await event_filter.matches(event):
                return await handler(event)
            return True  # Skip event, consider it handled

        return await self.subscribe(
            subscriber_name, event_type, filtered_handler, config
        )

    async def subscribe_with_transform(
        self,
        subscriber_name: str,
        event_type: Type[T],
        transformer: EventTransformer[T, R],
        handler: Callable[[R], bool],
        config: SubscriptionConfig = None,
    ) -> "SubscriptionManager":
        """Subscribe with event transformation"""

        async def transform_handler(event: T) -> bool:
            transformed = await transformer.transform(event)
            if transformed is not None:
                return await handler(transformed)
            return True  # Skip event if transformation returns None

        return await self.subscribe(
            subscriber_name, event_type, transform_handler, config
        )

    async def create_projection(
        self,
        projection_name: str,
        event_type: Type[T],
        projection: EventProjection[T, R],
        config: SubscriptionConfig = None,
    ) -> AsyncIterator[R]:
        """Create a projection from events"""
        results = asyncio.Queue()

        async def projection_handler(event: T) -> bool:
            try:
                result = await projection.project(event)
                if result is not None:
                    await results.put(result)
                return True
            except Exception as e:
                self.logger.error(f"Projection {projection_name} failed: {e}")
                return False

        await self.subscribe(projection_name, event_type, projection_handler, config)

        # Yield projection results
        while True:
            try:
                result = await asyncio.wait_for(results.get(), timeout=1.0)
                yield result
            except asyncio.TimeoutError:
                if not self._running:
                    break

    async def replay_events(
        self, subscriber_name: str, from_timestamp: Optional[datetime] = None
    ) -> AsyncIterator[Event]:
        """Replay events for a subscriber"""
        async with self._lock:
            events_to_replay = []

            for event in self._replay_buffer:
                if from_timestamp is None or event.timestamp >= from_timestamp:
                    events_to_replay.append(event)

        for event in events_to_replay:
            yield event

    async def get_dead_letter_events(self) -> AsyncIterator[DeadLetterEvent]:
        """Get dead letter events"""
        for dead_letter_event in self._dead_letter_queue:
            yield dead_letter_event

    async def retry_dead_letter_events(
        self, filter_func: Optional[Callable[[DeadLetterEvent], bool]] = None
    ) -> int:
        """Retry dead letter events"""
        events_to_retry = []

        for dead_letter_event in list(self._dead_letter_queue):
            if filter_func is None or filter_func(dead_letter_event):
                events_to_retry.append(dead_letter_event)
                self._dead_letter_queue.remove(dead_letter_event)

        retried_count = 0
        for dead_letter_event in events_to_retry:
            success = await self.publish(dead_letter_event.original_event)
            if success:
                retried_count += 1
            else:
                # Put back in dead letter queue
                self._dead_letter_queue.append(dead_letter_event)

        return retried_count

    async def get_metrics(self) -> EventBusMetrics:
        """Get current event bus metrics"""
        async with self._lock:
            avg_processing_time = (
                timedelta(
                    milliseconds=sum(self._processing_times)
                    / len(self._processing_times)
                )
                if self._processing_times
                else timedelta()
            )

            sorted_times = sorted(self._processing_times)
            p95_time = (
                timedelta(milliseconds=sorted_times[int(len(sorted_times) * 0.95)])
                if sorted_times
                else timedelta()
            )
            p99_time = (
                timedelta(milliseconds=sorted_times[int(len(sorted_times) * 0.99)])
                if sorted_times
                else timedelta()
            )

            total_events = self._events_processed + self._events_failed
            error_rate = self._events_failed / total_events if total_events > 0 else 0.0

            return EventBusMetrics(
                events_published=self._events_published,
                events_processed=self._events_processed,
                events_failed=self._events_failed,
                events_in_dead_letter=len(self._dead_letter_queue),
                active_subscriptions=len(self._subscriptions),
                average_processing_time=avg_processing_time,
                p95_processing_time=p95_time,
                p99_processing_time=p99_time,
                error_rate=error_rate,
            )

    async def unsubscribe(self, subscriber_name: str) -> bool:
        """Unsubscribe a subscriber"""
        subscription = self._subscriptions.pop(subscriber_name, None)
        if subscription:
            await subscription.close()
            self.logger.info(f"Unsubscribed {subscriber_name}")
            return True
        return False

    # Private methods
    async def _process_events(self):
        """Main event processing loop"""
        while self._running:
            try:
                event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)

                # Add to replay buffer
                async with self._lock:
                    self._replay_buffer.append(event)

                # Distribute to subscriptions
                await self._distribute_event(event)

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error processing events: {e}")

    async def _distribute_event(self, event: Event):
        """Distribute event to all matching subscriptions"""
        tasks = []

        for subscription in self._subscriptions.values():
            if subscription.can_handle(event):
                task = asyncio.create_task(subscription.process_event(event))
                tasks.append(task)

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _collect_metrics(self):
        """Collect and cleanup metrics periodically"""
        while self._running:
            try:
                await asyncio.sleep(
                    self.config.metrics_collection_interval.total_seconds()
                )

                # Clean up old processing times (keep only last 1000)
                async with self._lock:
                    if len(self._processing_times) > 1000:
                        self._processing_times = self._processing_times[-1000:]

            except Exception as e:
                self.logger.error(f"Error collecting metrics: {e}")


# Subscription manager
class SubscriptionManager:
    """Manages individual event subscriptions"""

    def __init__(
        self,
        subscriber_name: str,
        event_type: Type[Event],
        config: SubscriptionConfig,
        handler: Callable[[Event], bool],
        event_bus: ReactiveEventBus,
    ):
        self.subscriber_name = subscriber_name
        self.event_type = event_type
        self.config = config
        self.handler = handler
        self.event_bus = event_bus
        self.logger = logging.getLogger(f"{self.__class__.__name__}({subscriber_name})")

        self._active = False
        self._event_queue = asyncio.Queue(maxsize=config.buffer_size)
        self._processing_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the subscription processing"""
        if self._active:
            return

        self._active = True
        self._processing_task = asyncio.create_task(self._process_subscription_events())
        self.logger.info(f"Started subscription for {self.event_type.__name__}")

    async def close(self):
        """Close the subscription"""
        self._active = False

        if self._processing_task:
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass

        self.logger.info("Subscription closed")

    def can_handle(self, event: Event) -> bool:
        """Check if this subscription can handle the event"""
        return self._active and isinstance(event, self.event_type)

    async def process_event(self, event: Event):
        """Process an event through this subscription"""
        if not self._active:
            return

        try:
            await self._event_queue.put(event)
        except asyncio.QueueFull:
            self.logger.warning(f"Subscription queue full for {self.subscriber_name}")

    async def _process_subscription_events(self):
        """Process events in this subscription"""
        while self._active:
            try:
                event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)
                await self._handle_event_with_retry(event)

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error processing subscription events: {e}")

    async def _handle_event_with_retry(self, event: Event):
        """Handle event with retry logic"""
        start_time = time.time()

        for attempt in range(self.config.retry_config.max_attempts):
            try:
                success = await self.handler(event)

                if success:
                    self.event_bus._events_processed += 1
                    processing_time = (time.time() - start_time) * 1000  # milliseconds

                    async with self.event_bus._lock:
                        self.event_bus._processing_times.append(processing_time)

                    return
                else:
                    raise Exception("Handler returned False")

            except Exception as e:
                if attempt == self.config.retry_config.max_attempts - 1:
                    # Final attempt failed
                    self.event_bus._events_failed += 1

                    if self.config.dead_letter_enabled:
                        dead_letter_event = DeadLetterEvent(
                            original_event=event,
                            failure_reason=str(e),
                            failure_count=attempt + 1,
                            last_attempt=datetime.now(),
                            subscription=self.subscriber_name,
                        )
                        self.event_bus._dead_letter_queue.append(dead_letter_event)

                    self.logger.error(
                        f"Event {event.id} failed after {attempt + 1} attempts: {e}"
                    )
                    return
                else:
                    # Calculate backoff delay
                    delay = min(
                        self.config.retry_config.initial_delay.total_seconds()
                        * (self.config.retry_config.backoff_multiplier**attempt),
                        self.config.retry_config.max_delay.total_seconds(),
                    )
                    await asyncio.sleep(delay)


# Concrete base implementations
class BaseEventHandler(EventHandler[T]):
    """Base implementation for event handlers"""

    async def handle(self, event: T) -> bool:
        try:
            await self.do_handle(event)
            return True
        except Exception:
            return False

    @abstractmethod
    async def do_handle(self, event: T):
        """Implement the actual event handling logic"""
        pass


class BaseEventProjection(EventProjection[T, R]):
    """Base implementation for event projections"""

    async def project(self, event: T) -> Optional[R]:
        try:
            return await self.do_project(event)
        except Exception:
            return None

    @abstractmethod
    async def do_project(self, event: T) -> R:
        """Implement the actual projection logic"""
        pass


# Builder and DSL support
class EventBusConfigBuilder:
    """Builder for event bus configuration"""

    def __init__(self):
        self._buffer_size = 10000
        self._replay_buffer_size = 1000
        self._dead_letter_buffer_size = 1000
        self._metrics_collection_interval = timedelta(seconds=30)
        self._enable_event_persistence = False
        self._enable_circuit_breaker = True

    def buffer_size(self, size: int) -> "EventBusConfigBuilder":
        self._buffer_size = size
        return self

    def replay_buffer_size(self, size: int) -> "EventBusConfigBuilder":
        self._replay_buffer_size = size
        return self

    def dead_letter_buffer_size(self, size: int) -> "EventBusConfigBuilder":
        self._dead_letter_buffer_size = size
        return self

    def metrics_collection_interval(
        self, interval: timedelta
    ) -> "EventBusConfigBuilder":
        self._metrics_collection_interval = interval
        return self

    def enable_event_persistence(self, enable: bool) -> "EventBusConfigBuilder":
        self._enable_event_persistence = enable
        return self

    def enable_circuit_breaker(self, enable: bool) -> "EventBusConfigBuilder":
        self._enable_circuit_breaker = enable
        return self

    def build(self) -> EventBusConfig:
        return EventBusConfig(
            buffer_size=self._buffer_size,
            replay_buffer_size=self._replay_buffer_size,
            dead_letter_buffer_size=self._dead_letter_buffer_size,
            metrics_collection_interval=self._metrics_collection_interval,
            enable_event_persistence=self._enable_event_persistence,
            enable_circuit_breaker=self._enable_circuit_breaker,
        )


class EventBusBuilder:
    """Builder for reactive event bus"""

    def __init__(self):
        self._config: Optional[EventBusConfig] = None

    def config(
        self, config_builder: Callable[[EventBusConfigBuilder], EventBusConfigBuilder]
    ) -> "EventBusBuilder":
        builder = EventBusConfigBuilder()
        self._config = config_builder(builder).build()
        return self

    def build(self) -> ReactiveEventBus:
        return ReactiveEventBus(config=self._config)


# DSL function
def event_bus(
    config_builder: Optional[
        Callable[[EventBusConfigBuilder], EventBusConfigBuilder]
    ] = None,
) -> ReactiveEventBus:
    """Create an event bus using DSL"""
    builder = EventBusBuilder()
    if config_builder:
        builder.config(config_builder)
    return builder.build()


# Extension functions for common patterns
async def publish_event(event_bus: ReactiveEventBus, event: Event) -> bool:
    """Convenience function to publish an event"""
    return await event_bus.publish(event)


async def subscribe_to_events(
    event_bus: ReactiveEventBus,
    subscriber_name: str,
    event_type: Type[T],
    handler: Callable[[T], None],
) -> "SubscriptionManager":
    """Convenience function to subscribe to events"""

    async def wrapper_handler(event: T) -> bool:
        try:
            await handler(event)
            return True
        except Exception:
            return False

    return await event_bus.subscribe(subscriber_name, event_type, wrapper_handler)
