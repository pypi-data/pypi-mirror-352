"""
Enhanced authorization model with reactive programming, advanced caching, and comprehensive observability.
"""

import asyncio
import logging
import time
from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, AsyncIterator, Generic, TypeVar
from collections import deque
import hashlib
import json

from ..core.result import Result
from .authorization_rule import AuthorizationRule
from .authorization_status import AuthorizationStatus
from .model.base_authorization_model import BaseAuthorizationModel

logger = logging.getLogger(__name__)

T = TypeVar("T")


class BreakerState(Enum):
    """Circuit breaker states."""

    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


@dataclass
class AuthorizationMetric:
    """Metrics for authorization operations."""

    total_checks: int = 0
    pass_count: int = 0
    fail_count: int = 0
    average_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    recent_latencies: deque = field(default_factory=lambda: deque(maxlen=1000))
    last_updated: datetime = field(default_factory=datetime.now)

    def add_latency(self, latency_ms: float) -> None:
        """Add a latency measurement and update percentiles."""
        self.recent_latencies.append(latency_ms)
        self._update_percentiles()

    def _update_percentiles(self) -> None:
        """Update percentile calculations."""
        if self.recent_latencies:
            sorted_latencies = sorted(self.recent_latencies)
            size = len(sorted_latencies)
            self.p95_latency_ms = sorted_latencies[min(int(size * 0.95), size - 1)]
            self.p99_latency_ms = sorted_latencies[min(int(size * 0.99), size - 1)]


@dataclass
class CachedResult:
    """Cached authorization result."""

    result: AuthorizationStatus
    timestamp: datetime
    ttl: timedelta = field(default_factory=lambda: timedelta(minutes=5))
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        return datetime.now() > self.timestamp + self.ttl

    def remaining_ttl(self) -> timedelta:
        """Get remaining time to live."""
        expiry = self.timestamp + self.ttl
        return expiry - datetime.now() if expiry > datetime.now() else timedelta(0)


@dataclass
class AuthorizationEvent(Generic[T]):
    """Event emitted during authorization."""

    action: str
    context: Dict[str, Any]  # AuthorizationContext representation
    entity: T
    result: AuthorizationStatus
    duration: timedelta
    cache_hit: bool
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class CircuitBreakerState:
    """Circuit breaker state management."""

    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    state: BreakerState = BreakerState.CLOSED
    failure_threshold: int = 10
    timeout_duration: timedelta = field(default_factory=lambda: timedelta(minutes=1))

    def should_allow_request(self) -> bool:
        """Check if request should be allowed based on circuit breaker state."""
        if self.state == BreakerState.CLOSED:
            return True
        elif self.state == BreakerState.OPEN:
            if self.last_failure_time:
                return datetime.now() > self.last_failure_time + self.timeout_duration
            return True
        else:  # HALF_OPEN
            return True

    def on_success(self) -> None:
        """Handle successful request."""
        self.failure_count = 0
        self.state = BreakerState.CLOSED

    def on_failure(self) -> None:
        """Handle failed request."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        if self.failure_count >= self.failure_threshold:
            self.state = BreakerState.OPEN


@dataclass
class CacheStats:
    """Cache statistics."""

    total_entries: int
    active_entries: int
    expired_entries: int
    hit_ratio: float


class EnhancedAuthorizationModel(BaseAuthorizationModel[T], Generic[T]):
    """
    Modern authorization model with reactive programming, advanced caching, and comprehensive observability.
    """

    def __init__(self):
        """Initialize enhanced authorization model."""
        super().__init__()
        self._authorization_metrics: Dict[str, AuthorizationMetric] = {}
        self._cache: Dict[str, CachedResult] = {}
        self._authorization_events: List[AuthorizationEvent[T]] = []
        self._circuit_breaker_states: Dict[str, CircuitBreakerState] = {}
        self._event_listeners: List[Any] = []
        self._cache_hits = 0
        self._cache_misses = 0

    async def can_perform_action(
        self,
        action: str,
        context: Dict[str, Any],
        entity: T,
        use_cache: bool = True,
        use_circuit_breaker: bool = True,
    ) -> Result[bool]:
        """
        Reactive authorization check with Flow support.

        Args:
            action: The action to authorize
            context: Authorization context
            entity: The entity to check authorization for
            use_cache: Whether to use caching
            use_circuit_breaker: Whether to use circuit breaker pattern

        Returns:
            Result containing success/failure of authorization
        """
        start_time = time.time()
        cache_key = self._generate_cache_key(action, context, entity)

        # Circuit breaker check
        if use_circuit_breaker:
            breaker_state = self._circuit_breaker_states.setdefault(
                action, CircuitBreakerState()
            )
            if not breaker_state.should_allow_request():
                logger.warning(f"Circuit breaker is OPEN for action: {action}")
                return Result.failure(RuntimeError("Circuit breaker is OPEN"))

        try:
            # Check cache first if enabled
            if use_cache and cache_key in self._cache:
                cached = self._cache[cache_key]
                if not cached.is_expired():
                    duration = timedelta(seconds=time.time() - start_time)
                    result = cached.result == AuthorizationStatus.PASS
                    self._record_metric(action, cached.result, duration)
                    await self._emit_event(
                        action, context, entity, cached.result, duration, True
                    )
                    self._cache_hits += 1
                    return Result.success(result)
                else:
                    del self._cache[cache_key]  # Clean up expired cache

            self._cache_misses += 1

            # Evaluate rules
            rules = self._get_rules_for_action(action)
            result = await self._evaluate_rules_with_metrics(rules, context, entity)
            duration = timedelta(seconds=time.time() - start_time)

            # Cache the result
            if use_cache:
                self._cache[cache_key] = CachedResult(
                    result=result,
                    timestamp=datetime.now(),
                    metadata={"evaluated_rules": len(rules)},
                )

            self._record_metric(action, result, duration)
            await self._emit_event(action, context, entity, result, duration, False)

            # Update circuit breaker
            if use_circuit_breaker:
                self._circuit_breaker_states[action].on_success()

            logger.debug(
                f"Authorization check for action '{action}' completed in "
                f"{duration.total_seconds() * 1000:.2f}ms with result: {result}"
            )
            return Result.success(result == AuthorizationStatus.PASS)

        except Exception as e:
            duration = timedelta(seconds=time.time() - start_time)
            logger.error(
                f"Authorization check failed for action '{action}'", exc_info=True
            )

            # Update circuit breaker on failure
            if use_circuit_breaker:
                self._circuit_breaker_states[action].on_failure()

            return Result.failure(e)

    async def can_perform_action_batch(
        self,
        action: str,
        context: Dict[str, Any],
        entities: List[T],
        use_cache: bool = True,
        max_concurrency: int = 10,
    ) -> AsyncIterator[Tuple[T, Result[bool]]]:
        """
        Batch authorization with async iterator and parallel processing.

        Args:
            action: The action to authorize
            context: Authorization context
            entities: List of entities to check
            use_cache: Whether to use caching
            max_concurrency: Maximum concurrent checks

        Yields:
            Tuples of (entity, authorization result)
        """
        semaphore = asyncio.Semaphore(max_concurrency)

        async def check_with_semaphore(entity: T) -> Tuple[T, Result[bool]]:
            async with semaphore:
                result = await self.can_perform_action(
                    action, context, entity, use_cache
                )
                return entity, result

        # Create tasks for all entities
        tasks = [check_with_semaphore(entity) for entity in entities]

        # Process results as they complete
        for coro in asyncio.as_completed(tasks):
            yield await coro

    async def authorization_event_stream(self) -> AsyncIterator[AuthorizationEvent[T]]:
        """
        Stream authorization events for monitoring.

        Yields:
            Authorization events as they occur
        """
        # In a real implementation, this would be connected to an event bus
        # For now, we'll yield from the stored events
        for event in self._authorization_events:
            yield event

    def get_detailed_metrics(self) -> Dict[str, AuthorizationMetric]:
        """Get detailed authorization metrics with percentiles."""
        return self._authorization_metrics.copy()

    def get_cache_stats(self) -> CacheStats:
        """Get cache statistics."""
        total_entries = len(self._cache)
        expired_entries = sum(1 for entry in self._cache.values() if entry.is_expired())
        active_entries = total_entries - expired_entries

        total_requests = self._cache_hits + self._cache_misses
        hit_ratio = self._cache_hits / total_requests if total_requests > 0 else 0.0

        return CacheStats(
            total_entries=total_entries,
            active_entries=active_entries,
            expired_entries=expired_entries,
            hit_ratio=hit_ratio,
        )

    def cleanup_cache(self) -> None:
        """Clear expired cache entries."""
        expired_keys = [key for key, value in self._cache.items() if value.is_expired()]
        for key in expired_keys:
            del self._cache[key]
        logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")

    async def warmup_cache(
        self, actions: List[str], contexts: List[Dict[str, Any]], entities: List[T]
    ) -> None:
        """
        Warm up cache for frequently accessed entities.

        Args:
            actions: List of actions to cache
            contexts: List of contexts to cache
            entities: List of entities to cache
        """
        combinations = [
            (action, context, entity)
            for action in actions
            for context in contexts
            for entity in entities
        ]

        # Process combinations with limited concurrency
        semaphore = asyncio.Semaphore(50)

        async def warmup_entry(action: str, context: Dict[str, Any], entity: T):
            async with semaphore:
                await self.can_perform_action(
                    action, context, entity, use_cache=True, use_circuit_breaker=False
                )

        tasks = [
            warmup_entry(action, context, entity)
            for action, context, entity in combinations
        ]

        await asyncio.gather(*tasks)
        logger.info(f"Cache warmed up with {len(combinations)} entries")

    # Modern API methods
    async def can_read(self, context: Dict[str, Any], entity: T) -> bool:
        """Check if read action is allowed."""
        result = await self.can_perform_action("read", context, entity)
        return result.value if result.is_success else False

    async def can_create(self, context: Dict[str, Any], entity: T) -> bool:
        """Check if create action is allowed."""
        result = await self.can_perform_action("create", context, entity)
        return result.value if result.is_success else False

    async def can_update(self, context: Dict[str, Any], entity: T) -> bool:
        """Check if update action is allowed."""
        result = await self.can_perform_action("update", context, entity)
        return result.value if result.is_success else False

    async def can_delete(self, context: Dict[str, Any], entity: T) -> bool:
        """Check if delete action is allowed."""
        result = await self.can_perform_action("delete", context, entity)
        return result.value if result.is_success else False

    # Helper methods
    def _generate_cache_key(
        self, action: str, context: Dict[str, Any], entity: T
    ) -> str:
        """Generate cache key for authorization check."""
        # Create a stable string representation
        context_str = json.dumps(context, sort_keys=True)
        entity_str = str(hash(entity))
        key_str = f"{action}:{context_str}:{entity_str}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def _get_rules_for_action(self, action: str) -> List[AuthorizationRule[T]]:
        """Get rules for specific action."""
        action_lower = action.lower()
        if action_lower == "read":
            return self.get_read_rules()
        elif action_lower == "create":
            return self.get_create_rules()
        elif action_lower == "update":
            return self.get_update_rules()
        elif action_lower == "delete":
            return self.get_delete_rules()
        else:
            raise ValueError(f"Unknown action: {action}")

    async def _evaluate_rules_with_metrics(
        self, rules: List[AuthorizationRule[T]], context: Dict[str, Any], entity: T
    ) -> AuthorizationStatus:
        """Evaluate rules with metrics tracking."""
        for rule in rules:
            rule_start_time = time.time()
            result = rule.evaluate(context, entity)
            rule_duration = time.time() - rule_start_time

            logger.trace(
                f"Rule {rule.__class__.__name__} evaluated in "
                f"{rule_duration * 1000:.2f}ms with result: {result}"
            )

            if result != AuthorizationStatus.NEXT:
                return result

        return AuthorizationStatus.FAIL

    def _record_metric(
        self, action: str, result: AuthorizationStatus, duration: timedelta
    ) -> None:
        """Record authorization metrics."""
        metric = self._authorization_metrics.setdefault(action, AuthorizationMetric())
        metric.total_checks += 1

        if result == AuthorizationStatus.PASS:
            metric.pass_count += 1
        elif result == AuthorizationStatus.FAIL:
            metric.fail_count += 1

        # Update latency metrics
        latency_ms = duration.total_seconds() * 1000
        metric.average_latency_ms = (
            metric.average_latency_ms * (metric.total_checks - 1) + latency_ms
        ) / metric.total_checks
        metric.add_latency(latency_ms)

    async def _emit_event(
        self,
        action: str,
        context: Dict[str, Any],
        entity: T,
        result: AuthorizationStatus,
        duration: timedelta,
        cache_hit: bool,
    ) -> None:
        """Emit authorization event."""
        event = AuthorizationEvent(
            action=action,
            context=context,
            entity=entity,
            result=result,
            duration=duration,
            cache_hit=cache_hit,
        )
        self._authorization_events.append(event)

        # Notify listeners (if any)
        for listener in self._event_listeners:
            if asyncio.iscoroutinefunction(listener):
                await listener(event)
            else:
                listener(event)
