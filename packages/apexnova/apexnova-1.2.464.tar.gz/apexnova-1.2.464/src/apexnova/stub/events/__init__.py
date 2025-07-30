"""
ApexNova Reactive Events Module

This module provides a comprehensive reactive event system with:
- Reactive Event Bus with type-safe publishing and subscribing
- Event Sourcing with aggregate persistence
- CQRS (Command Query Responsibility Segregation) pattern
- Dead letter queue for failed events
- Event replay and persistence
- Backpressure handling and buffering
- Metrics and monitoring
- Event filtering and transformation
"""

from .reactive_event_bus import (
    # Core Event Types
    Event,
    DomainEvent,
    SystemEvent,
    EventSeverity,
    # Handler Types
    EventHandler,
    EventProjection,
    BaseEventHandler,
    BaseEventProjection,
    # Configuration
    SubscriptionConfig,
    RetryConfig,
    EventBusConfig,
    # Metrics and Monitoring
    EventBusMetrics,
    DeadLetterEvent,
    # Event Bus
    ReactiveEventBus,
    # Builder and DSL
    EventBusBuilder,
    EventBusConfigBuilder,
    event_bus,
    # Filters and Transformers
    EventFilter,
    EventTransformer,
)

from .event_sourcing import (
    # Event Sourcing Core
    EventStore,
    InMemoryEventStore,
    # Aggregate Root
    AggregateRoot,
    EventSourcedRepository,
    # CQRS Pattern
    Command,
    Query,
    CommandHandler,
    QueryHandler,
    CQRSBus,
    # Event Handling
    EventBus as EventSourcingBus,
    EventHandler as DomainEventHandler,
    # Projections
    Projection,
    ProjectionManager,
    # Event Types for Event Sourcing
    DomainEvent as EventSourcingDomainEvent,
    Event as EventSourcingEvent,
)

__all__ = [
    # Event Bus
    "Event",
    "DomainEvent",
    "SystemEvent",
    "EventSeverity",
    "EventHandler",
    "EventProjection",
    "BaseEventHandler",
    "BaseEventProjection",
    "SubscriptionConfig",
    "RetryConfig",
    "EventBusConfig",
    "EventBusMetrics",
    "DeadLetterEvent",
    "ReactiveEventBus",
    "EventBusBuilder",
    "EventBusConfigBuilder",
    "event_bus",
    "EventFilter",
    "EventTransformer",
    # Event Sourcing
    "EventStore",
    "InMemoryEventStore",
    "AggregateRoot",
    "EventSourcedRepository",
    "Command",
    "Query",
    "CommandHandler",
    "QueryHandler",
    "CQRSBus",
    "EventSourcingBus",
    "DomainEventHandler",
    "Projection",
    "ProjectionManager",
    "EventSourcingDomainEvent",
    "EventSourcingEvent",
]
