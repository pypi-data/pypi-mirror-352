"""
Event Sourcing Implementation with CQRS Pattern

This module provides a comprehensive event sourcing system with:
- Event Store for aggregate persistence
- Aggregate Root base class
- CQRS (Command Query Responsibility Segregation) pattern
- Event Bus for domain events
- Projection system for read models
- In-memory and extensible storage implementations
"""

import asyncio
import uuid
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
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
)
import logging
import json
from concurrent.futures import ThreadPoolExecutor

# Type variables
T = TypeVar("T", bound="AggregateRoot")
E = TypeVar("E", bound="DomainEvent")
C = TypeVar("C", bound="Command")
Q = TypeVar("Q", bound="Query")
R = TypeVar("R")


# Base event interface for event sourcing
@dataclass(frozen=True)
class DomainEvent:
    """Base domain event for event sourcing"""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    aggregate_id: str = ""
    event_type: str = ""
    version: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, str] = field(default_factory=dict)
    data: Any = None


# Concrete event implementation
@dataclass(frozen=True)
class Event(DomainEvent):
    """Concrete event implementation"""

    pass


# Result type for operations
class Result(Generic[T]):
    """Result type for operation results"""

    def __init__(self, success: bool, data: T = None, error: Exception = None):
        self._success = success
        self._data = data
        self._error = error

    @property
    def is_success(self) -> bool:
        return self._success

    @property
    def is_failure(self) -> bool:
        return not self._success

    @property
    def data(self) -> T:
        if not self._success:
            raise self._error
        return self._data

    @property
    def error(self) -> Exception:
        return self._error

    @classmethod
    def success(cls, data: T = None) -> "Result[T]":
        return cls(True, data)

    @classmethod
    def failure(cls, error: Exception) -> "Result[T]":
        return cls(False, error=error)


# Event store interface
class EventStore(ABC):
    """Abstract interface for event storage"""

    @abstractmethod
    async def save_events(
        self, aggregate_id: str, events: List[DomainEvent], expected_version: int
    ) -> Result[None]:
        """Save events for an aggregate"""
        pass

    @abstractmethod
    async def get_events(
        self, aggregate_id: str, from_version: int = 0
    ) -> Result[List[DomainEvent]]:
        """Get events for an aggregate"""
        pass

    @abstractmethod
    async def get_all_events(
        self, from_timestamp: Optional[datetime] = None
    ) -> AsyncIterator[DomainEvent]:
        """Get all events in the store"""
        pass


# Event handler interface for domain events
class EventHandler(ABC, Generic[E]):
    """Abstract event handler for domain events"""

    @abstractmethod
    async def handle(self, event: E):
        """Handle the domain event"""
        pass

    @abstractmethod
    def can_handle(self, event: DomainEvent) -> bool:
        """Check if this handler can handle the event"""
        pass


# Event bus for domain events
class EventBus:
    """Event bus for publishing and subscribing to domain events"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._handlers: Dict[str, List[EventHandler]] = defaultdict(list)
        self._event_queue = asyncio.Queue()
        self._running = False
        self._processing_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the event bus"""
        if self._running:
            return

        self._running = True
        self._processing_task = asyncio.create_task(self._process_events())
        self.logger.info("Event bus started")

    async def stop(self):
        """Stop the event bus"""
        self._running = False

        if self._processing_task:
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass

        self.logger.info("Event bus stopped")

    def subscribe(self, event_type: str, handler: EventHandler[E]):
        """Subscribe a handler to an event type"""
        self._handlers[event_type].append(handler)
        self.logger.info(f"Subscribed handler for event type: {event_type}")

    async def publish(self, event: DomainEvent):
        """Publish a domain event"""
        self.logger.debug(
            f"Publishing event: {event.event_type} for aggregate: {event.aggregate_id}"
        )
        await self._event_queue.put(event)

    async def publish_batch(self, events: List[DomainEvent]):
        """Publish multiple domain events"""
        for event in events:
            await self._event_queue.put(event)

    async def _process_events(self):
        """Process events from the queue"""
        while self._running:
            try:
                event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)
                await self._process_event(event)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error processing events: {e}")

    async def _process_event(self, event: DomainEvent):
        """Process a single event"""
        event_handlers = self._handlers.get(event.event_type, [])

        for handler in event_handlers:
            try:
                if handler.can_handle(event):
                    await handler.handle(event)
            except Exception as e:
                self.logger.error(f"Error handling event {event.event_type}: {e}")


# In-memory event store implementation
class InMemoryEventStore(EventStore):
    """In-memory implementation of event store"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._events: Dict[str, List[DomainEvent]] = defaultdict(list)
        self._versions: Dict[str, int] = defaultdict(int)
        self._lock = asyncio.Lock()

    async def save_events(
        self, aggregate_id: str, events: List[DomainEvent], expected_version: int
    ) -> Result[None]:
        """Save events for an aggregate with optimistic concurrency"""
        try:
            async with self._lock:
                current_version = self._versions[aggregate_id]

                if current_version != expected_version:
                    return Result.failure(
                        Exception(
                            f"Expected version {expected_version} but was {current_version}"
                        )
                    )

                aggregate_events = self._events[aggregate_id]

                for event in events:
                    # Create versioned event
                    versioned_event = Event(
                        event_id=event.event_id,
                        aggregate_id=aggregate_id,
                        event_type=event.event_type,
                        version=current_version + 1,
                        timestamp=event.timestamp,
                        metadata=event.metadata,
                        data=event.data,
                    )
                    aggregate_events.append(versioned_event)
                    current_version += 1

                self._versions[aggregate_id] = current_version

            self.logger.debug(
                f"Saved {len(events)} events for aggregate {aggregate_id}"
            )
            return Result.success()

        except Exception as e:
            self.logger.error(
                f"Failed to save events for aggregate {aggregate_id}: {e}"
            )
            return Result.failure(e)

    async def get_events(
        self, aggregate_id: str, from_version: int = 0
    ) -> Result[List[DomainEvent]]:
        """Get events for an aggregate"""
        try:
            aggregate_events = self._events.get(aggregate_id, [])
            filtered_events = [e for e in aggregate_events if e.version >= from_version]
            return Result.success(filtered_events)
        except Exception as e:
            self.logger.error(f"Failed to get events for aggregate {aggregate_id}: {e}")
            return Result.failure(e)

    async def get_all_events(
        self, from_timestamp: Optional[datetime] = None
    ) -> AsyncIterator[DomainEvent]:
        """Get all events in the store"""
        all_events = []
        for events in self._events.values():
            all_events.extend(events)

        # Sort by timestamp
        all_events.sort(key=lambda e: e.timestamp)

        for event in all_events:
            if from_timestamp is None or event.timestamp >= from_timestamp:
                yield event


# Aggregate root base class
class AggregateRoot(ABC):
    """Base class for aggregate roots in event sourcing"""

    def __init__(self, aggregate_id: str):
        self.id = aggregate_id
        self._uncommitted_events: List[DomainEvent] = []
        self.version = 0

    def apply_event(self, event: DomainEvent):
        """Apply an event to the aggregate"""
        if isinstance(event, Event):
            versioned_event = Event(
                event_id=event.event_id,
                aggregate_id=self.id,
                event_type=event.event_type,
                version=self.version + 1,
                timestamp=event.timestamp,
                metadata=event.metadata,
                data=event.data,
            )
        else:
            versioned_event = Event(
                aggregate_id=self.id,
                event_type=event.event_type,
                version=self.version + 1,
                timestamp=datetime.now(),
                metadata=event.metadata,
                data=event,
            )

        self._uncommitted_events.append(versioned_event)
        self.version += 1
        self.handle_event(event)

    @abstractmethod
    def handle_event(self, event: DomainEvent):
        """Handle an event to update aggregate state"""
        pass

    def get_uncommitted_events(self) -> List[DomainEvent]:
        """Get uncommitted events"""
        return self._uncommitted_events.copy()

    def clear_uncommitted_events(self):
        """Clear uncommitted events"""
        self._uncommitted_events.clear()

    def load_from_history(self, events: List[DomainEvent]):
        """Load aggregate from event history"""
        for event in events:
            self.handle_event(event)
            self.version = event.version


# Repository pattern for aggregates
class EventSourcedRepository(ABC, Generic[T]):
    """Abstract repository for event-sourced aggregates"""

    def __init__(self, event_store: EventStore, event_bus: EventBus):
        self.event_store = event_store
        self.event_bus = event_bus
        self.logger = logging.getLogger(self.__class__.__name__)

    async def save(self, aggregate: T) -> Result[None]:
        """Save an aggregate"""
        events = aggregate.get_uncommitted_events()
        if not events:
            return Result.success()

        save_result = await self.event_store.save_events(
            aggregate.id, events, aggregate.version - len(events)
        )

        if save_result.is_success:
            aggregate.clear_uncommitted_events()

            # Publish events to event bus
            for event in events:
                await self.event_bus.publish(event)

            self.logger.info(
                f"Saved and published {len(events)} events for aggregate {aggregate.id}"
            )
            return Result.success()
        else:
            return save_result

    async def get_by_id(self, aggregate_id: str) -> Result[Optional[T]]:
        """Get an aggregate by ID"""
        events_result = await self.event_store.get_events(aggregate_id)

        if events_result.is_failure:
            return Result.failure(events_result.error)

        events = events_result.data
        if not events:
            return Result.success(None)

        try:
            aggregate = self.create_aggregate(aggregate_id)
            aggregate.load_from_history(events)
            return Result.success(aggregate)
        except Exception as e:
            self.logger.error(f"Failed to create aggregate {aggregate_id}: {e}")
            return Result.failure(e)

    @abstractmethod
    def create_aggregate(self, aggregate_id: str) -> T:
        """Create a new aggregate instance"""
        pass


# CQRS Pattern Implementation


# Command interface
class Command(ABC):
    """Base interface for commands"""

    command_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)


# Query interface
class Query(ABC, Generic[R]):
    """Base interface for queries"""

    query_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)


# Command handler interface
class CommandHandler(ABC, Generic[C, R]):
    """Abstract command handler"""

    @abstractmethod
    async def handle(self, command: C) -> Result[R]:
        """Handle the command"""
        pass

    @abstractmethod
    def can_handle(self, command: Command) -> bool:
        """Check if this handler can handle the command"""
        pass


# Query handler interface
class QueryHandler(ABC, Generic[Q, R]):
    """Abstract query handler"""

    @abstractmethod
    async def handle(self, query: Q) -> Result[R]:
        """Handle the query"""
        pass

    @abstractmethod
    def can_handle(self, query: Query) -> bool:
        """Check if this handler can handle the query"""
        pass


# CQRS Bus for commands and queries
class CQRSBus:
    """Bus for handling commands and queries"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._command_handlers: Dict[str, CommandHandler] = {}
        self._query_handlers: Dict[str, QueryHandler] = {}

    def register_command_handler(
        self, command_type: str, handler: CommandHandler[C, R]
    ):
        """Register a command handler"""
        self._command_handlers[command_type] = handler
        self.logger.info(f"Registered command handler for: {command_type}")

    def register_query_handler(self, query_type: str, handler: QueryHandler[Q, R]):
        """Register a query handler"""
        self._query_handlers[query_type] = handler
        self.logger.info(f"Registered query handler for: {query_type}")

    async def execute_command(self, command: C) -> Result[R]:
        """Execute a command"""
        command_type = command.__class__.__name__
        handler = self._command_handlers.get(command_type)

        if handler and handler.can_handle(command):
            try:
                self.logger.debug(f"Executing command: {command_type}")
                return await handler.handle(command)
            except Exception as e:
                self.logger.error(f"Error executing command {command_type}: {e}")
                return Result.failure(e)
        else:
            error = Exception(f"No handler found for command: {command_type}")
            return Result.failure(error)

    async def execute_query(self, query: Q) -> Result[R]:
        """Execute a query"""
        query_type = query.__class__.__name__
        handler = self._query_handlers.get(query_type)

        if handler and handler.can_handle(query):
            try:
                self.logger.debug(f"Executing query: {query_type}")
                return await handler.handle(query)
            except Exception as e:
                self.logger.error(f"Error executing query {query_type}: {e}")
                return Result.failure(e)
        else:
            error = Exception(f"No handler found for query: {query_type}")
            return Result.failure(error)


# Event projections for read models
class Projection(ABC):
    """Abstract base class for event projections"""

    @abstractmethod
    async def handle(self, event: DomainEvent):
        """Handle an event to update the projection"""
        pass

    @abstractmethod
    def get_projection_name(self) -> str:
        """Get the name of this projection"""
        pass


# Projection manager
class ProjectionManager:
    """Manages event projections for read models"""

    def __init__(self, event_bus: EventBus, event_store: EventStore):
        self.event_bus = event_bus
        self.event_store = event_store
        self.logger = logging.getLogger(self.__class__.__name__)
        self._projections: List[Projection] = []

    def register(self, projection: Projection):
        """Register a projection"""
        self._projections.append(projection)
        self.logger.info(f"Registered projection: {projection.get_projection_name()}")

    async def rebuild(
        self, projection: Projection, from_timestamp: Optional[datetime] = None
    ):
        """Rebuild a specific projection"""
        self.logger.info(f"Rebuilding projection: {projection.get_projection_name()}")

        async for event in self.event_store.get_all_events(from_timestamp):
            try:
                await projection.handle(event)
            except Exception as e:
                self.logger.error(
                    f"Error rebuilding projection {projection.get_projection_name()}: {e}"
                )

    async def rebuild_all(self, from_timestamp: Optional[datetime] = None):
        """Rebuild all projections"""
        for projection in self._projections:
            await self.rebuild(projection, from_timestamp)


# Example implementations


@dataclass
class ExampleDomainEvent(DomainEvent):
    """Example domain event"""

    name: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)


class ExampleEventHandler(EventHandler[ExampleDomainEvent]):
    """Example event handler"""

    async def handle(self, event: ExampleDomainEvent):
        # Handle the event
        logging.info(f"Handling event: {event.name}")

    def can_handle(self, event: DomainEvent) -> bool:
        return isinstance(event, ExampleDomainEvent)


class ExampleAggregate(AggregateRoot):
    """Example aggregate root"""

    def __init__(self, aggregate_id: str):
        super().__init__(aggregate_id)
        self.name = ""
        self.data = {}

    def handle_event(self, event: DomainEvent):
        """Handle events to update aggregate state"""
        if isinstance(event, ExampleDomainEvent):
            self.name = event.name
            self.data.update(event.payload)


class ExampleRepository(EventSourcedRepository[ExampleAggregate]):
    """Example repository"""

    def create_aggregate(self, aggregate_id: str) -> ExampleAggregate:
        return ExampleAggregate(aggregate_id)


@dataclass
class ExampleCommand(Command):
    """Example command"""

    name: str = ""
    data: Dict[str, Any] = field(default_factory=dict)


class ExampleCommandHandler(CommandHandler[ExampleCommand, str]):
    """Example command handler"""

    async def handle(self, command: ExampleCommand) -> Result[str]:
        # Process the command
        return Result.success(f"Processed command: {command.name}")

    def can_handle(self, command: Command) -> bool:
        return isinstance(command, ExampleCommand)


@dataclass
class ExampleQuery(Query[List[str]]):
    """Example query"""

    filter_criteria: str = ""


class ExampleQueryHandler(QueryHandler[ExampleQuery, List[str]]):
    """Example query handler"""

    async def handle(self, query: ExampleQuery) -> Result[List[str]]:
        # Process the query
        return Result.success(["result1", "result2"])

    def can_handle(self, query: Query) -> bool:
        return isinstance(query, ExampleQuery)


class ExampleProjection(Projection):
    """Example projection"""

    def __init__(self):
        self.data: Dict[str, Any] = {}

    async def handle(self, event: DomainEvent):
        """Update projection based on event"""
        if isinstance(event, ExampleDomainEvent):
            self.data[event.aggregate_id] = {
                "name": event.name,
                "timestamp": event.timestamp,
                "payload": event.payload,
            }

    def get_projection_name(self) -> str:
        return "ExampleProjection"
