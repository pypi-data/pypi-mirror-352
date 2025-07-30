"""Modern reactive caching system with TTL, eviction policies, and monitoring."""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import (
    Any,
    AsyncGenerator,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Set,
    TypeVar,
    Union,
    Tuple,
    Coroutine,
)
from concurrent.futures import ThreadPoolExecutor
import threading
import weakref

K = TypeVar("K")
V = TypeVar("V")

logger = logging.getLogger(__name__)


class EvictionPolicy(Enum):
    """Cache eviction policies."""

    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In, First Out
    TTL = "ttl"  # Time To Live based
    CUSTOM = "custom"  # Custom comparator


@dataclass
class CacheEntry(Generic[V]):
    """Cache entry with metadata."""

    value: V
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    ttl: Optional[timedelta] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        """Check if entry is expired."""
        if self.ttl is None:
            return False
        return datetime.now() > self.created_at + self.ttl

    def mark_accessed(self) -> "CacheEntry[V]":
        """Mark entry as accessed and return self."""
        self.last_accessed = datetime.now()
        self.access_count += 1
        return self

    def age(self) -> timedelta:
        """Get age of the entry."""
        return datetime.now() - self.created_at

    def time_since_last_access(self) -> timedelta:
        """Get time since last access."""
        return datetime.now() - self.last_accessed


@dataclass
class CacheConfig:
    """Cache configuration."""

    max_size: int = 1000
    default_ttl: Optional[timedelta] = None
    eviction_policy: EvictionPolicy = EvictionPolicy.LRU
    enable_metrics: bool = True
    cleanup_interval: timedelta = timedelta(minutes=1)
    refresh_ahead_factor: float = 0.8  # Refresh when 80% of TTL has elapsed


@dataclass
class CacheStats:
    """Cache statistics."""

    size: int
    hit_count: int
    miss_count: int
    eviction_count: int
    load_count: int
    average_load_time: timedelta
    expired_entries: int
    memory_usage_bytes: int

    @property
    def hit_rate(self) -> float:
        """Calculate hit rate."""
        total = self.hit_count + self.miss_count
        return self.hit_count / total if total > 0 else 0.0


class CacheEvent(Generic[K, V]):
    """Base class for cache events."""

    def __init__(self, key: K, timestamp: Optional[datetime] = None):
        self.key = key
        self.timestamp = timestamp or datetime.now()


class CacheEventHit(CacheEvent[K, V]):
    """Cache hit event."""

    def __init__(self, key: K, value: V, timestamp: Optional[datetime] = None):
        super().__init__(key, timestamp)
        self.value = value


class CacheEventMiss(CacheEvent[K, V]):
    """Cache miss event."""

    pass


class CacheEventPut(CacheEvent[K, V]):
    """Cache put event."""

    def __init__(
        self,
        key: K,
        value: V,
        ttl: Optional[timedelta] = None,
        timestamp: Optional[datetime] = None,
    ):
        super().__init__(key, timestamp)
        self.value = value
        self.ttl = ttl


class CacheEventEvicted(CacheEvent[K, V]):
    """Cache eviction event."""

    def __init__(
        self, key: K, value: V, reason: str, timestamp: Optional[datetime] = None
    ):
        super().__init__(key, timestamp)
        self.value = value
        self.reason = reason


class CacheEventExpired(CacheEvent[K, V]):
    """Cache expiration event."""

    def __init__(self, key: K, value: V, timestamp: Optional[datetime] = None):
        super().__init__(key, timestamp)
        self.value = value


class ReactiveCache(Generic[K, V]):
    """Enhanced reactive cache implementation with async support."""

    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        self._cache: Dict[K, CacheEntry[V]] = {}
        self._lock = asyncio.Lock()

        # Metrics
        self._hit_count = 0
        self._miss_count = 0
        self._eviction_count = 0
        self._load_count = 0
        self._total_load_time = timedelta()

        # Event handling
        self._event_handlers: List[Callable[[CacheEvent], None]] = []

        # Background cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None
        self._start_cleanup()

    async def get(self, key: K) -> Optional[V]:
        """Get value by key with reactive support."""
        async with self._lock:
            entry = self._cache.get(key)

            if entry is not None and not entry.is_expired():
                self._hit_count += 1
                self._emit_event(CacheEventHit(key, entry.value))
                entry.mark_accessed()
                return entry.value
            else:
                self._miss_count += 1
                self._emit_event(CacheEventMiss(key))

                # Remove expired entry
                if entry is not None and entry.is_expired():
                    del self._cache[key]
                    self._emit_event(CacheEventExpired(key, entry.value))

                return None

    async def get_or_put(
        self,
        key: K,
        loader: Callable[[], Coroutine[Any, Any, V]],
        ttl: Optional[timedelta] = None,
    ) -> V:
        """Get or compute value with refresh-ahead pattern."""
        async with self._lock:
            entry = self._cache.get(key)

            if entry is not None and not entry.is_expired():
                self._hit_count += 1
                self._emit_event(CacheEventHit(key, entry.value))

                # Check if refresh-ahead is needed
                should_refresh_ahead = False
                if entry.ttl is not None:
                    elapsed_ratio = (
                        entry.age().total_seconds() / entry.ttl.total_seconds()
                    )
                    should_refresh_ahead = (
                        elapsed_ratio >= self.config.refresh_ahead_factor
                    )

                if should_refresh_ahead:
                    # Async refresh in background
                    asyncio.create_task(self._refresh_entry(key, loader, ttl))

                entry.mark_accessed()
                return entry.value

            else:
                self._miss_count += 1
                self._load_count += 1
                self._emit_event(CacheEventMiss(key))

                start_time = datetime.now()
                value = await loader()
                load_time = datetime.now() - start_time
                self._total_load_time += load_time

                await self.put(key, value, ttl)
                return value

    async def put(self, key: K, value: V, ttl: Optional[timedelta] = None) -> None:
        """Put value into cache."""
        async with self._lock:
            # Check if eviction is needed
            if len(self._cache) >= self.config.max_size:
                await self._evict_entries(1)

            effective_ttl = ttl or self.config.default_ttl
            entry = CacheEntry(value=value, ttl=effective_ttl)
            self._cache[key] = entry
            self._emit_event(CacheEventPut(key, value, effective_ttl))

    async def put_all(
        self, entries: Dict[K, V], ttl: Optional[timedelta] = None
    ) -> None:
        """Put multiple values efficiently."""
        for key, value in entries.items():
            await self.put(key, value, ttl)

    async def remove(self, key: K) -> Optional[V]:
        """Remove entry from cache."""
        async with self._lock:
            entry = self._cache.pop(key, None)
            if entry is not None:
                self._emit_event(CacheEventEvicted(key, entry.value, "Manual removal"))
                return entry.value
            return None

    async def clear(self) -> None:
        """Clear all entries."""
        async with self._lock:
            self._cache.clear()

    async def contains_key(self, key: K) -> bool:
        """Check if key exists and is not expired."""
        async with self._lock:
            entry = self._cache.get(key)
            return entry is not None and not entry.is_expired()

    async def keys(self) -> Set[K]:
        """Get all keys currently in cache."""
        async with self._lock:
            return set(self._cache.keys())

    def size(self) -> int:
        """Get cache size."""
        return len(self._cache)

    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        expired_count = sum(1 for entry in self._cache.values() if entry.is_expired())
        avg_load_time = (
            self._total_load_time / self._load_count
            if self._load_count > 0
            else timedelta()
        )

        return CacheStats(
            size=len(self._cache),
            hit_count=self._hit_count,
            miss_count=self._miss_count,
            eviction_count=self._eviction_count,
            load_count=self._load_count,
            average_load_time=avg_load_time,
            expired_entries=expired_count,
            memory_usage_bytes=self._estimate_memory_usage(),
        )

    async def events(self) -> AsyncGenerator[CacheEvent, None]:
        """Get event stream for monitoring."""
        # This would require a more sophisticated event streaming implementation
        # For now, just yield events as they come
        yield  # Placeholder

    def add_event_handler(self, handler: Callable[[CacheEvent], None]) -> None:
        """Add event handler."""
        self._event_handlers.append(handler)

    def remove_event_handler(self, handler: Callable[[CacheEvent], None]) -> None:
        """Remove event handler."""
        if handler in self._event_handlers:
            self._event_handlers.remove(handler)

    async def _refresh_entry(
        self,
        key: K,
        loader: Callable[[], Coroutine[Any, Any, V]],
        ttl: Optional[timedelta],
    ) -> None:
        """Refresh cache entry in background."""
        try:
            value = await loader()
            await self.put(key, value, ttl)
        except Exception as e:
            logger.warning(f"Failed to refresh cache entry for key: {key}", exc_info=e)

    async def _evict_entries(self, count: int) -> None:
        """Evict entries based on eviction policy."""
        if not self._cache:
            return

        entries_to_evict = []

        if self.config.eviction_policy == EvictionPolicy.LRU:
            entries_to_evict = sorted(
                self._cache.items(), key=lambda x: x[1].last_accessed
            )[:count]
        elif self.config.eviction_policy == EvictionPolicy.LFU:
            entries_to_evict = sorted(
                self._cache.items(), key=lambda x: x[1].access_count
            )[:count]
        elif self.config.eviction_policy == EvictionPolicy.FIFO:
            entries_to_evict = sorted(
                self._cache.items(), key=lambda x: x[1].created_at
            )[:count]
        elif self.config.eviction_policy == EvictionPolicy.TTL:
            entries_to_evict = [
                (key, entry) for key, entry in self._cache.items() if entry.is_expired()
            ]

        for key, entry in entries_to_evict:
            if key in self._cache:
                del self._cache[key]
                self._eviction_count += 1
                self._emit_event(
                    CacheEventEvicted(
                        key,
                        entry.value,
                        f"Eviction policy: {self.config.eviction_policy}",
                    )
                )

    async def _perform_cleanup(self) -> None:
        """Perform periodic cleanup of expired entries."""
        async with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items() if entry.is_expired()
            ]

            for key in expired_keys:
                entry = self._cache.pop(key, None)
                if entry is not None:
                    self._emit_event(CacheEventExpired(key, entry.value))

            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")

    def _start_cleanup(self) -> None:
        """Start background cleanup task."""

        async def cleanup_loop():
            while True:
                try:
                    await asyncio.sleep(self.config.cleanup_interval.total_seconds())
                    await self._perform_cleanup()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error("Error in cache cleanup", exc_info=e)

        self._cleanup_task = asyncio.create_task(cleanup_loop())

    def _emit_event(self, event: CacheEvent) -> None:
        """Emit cache event to handlers."""
        for handler in self._event_handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error in cache event handler: {e}")

    def _estimate_memory_usage(self) -> int:
        """Rough estimation of memory usage."""
        # Simple estimation - would need actual profiling for accuracy
        return len(self._cache) * 128  # Estimate 128 bytes per entry

    def shutdown(self) -> None:
        """Shutdown cache and cleanup resources."""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
        self._cache.clear()


class CacheBuilder(Generic[K, V]):
    """Builder for fluent cache configuration."""

    def __init__(self):
        self._max_size = 1000
        self._default_ttl: Optional[timedelta] = None
        self._eviction_policy = EvictionPolicy.LRU
        self._enable_metrics = True
        self._cleanup_interval = timedelta(minutes=1)
        self._refresh_ahead_factor = 0.8

    def max_size(self, size: int) -> "CacheBuilder[K, V]":
        """Set maximum cache size."""
        self._max_size = size
        return self

    def default_ttl(self, ttl: timedelta) -> "CacheBuilder[K, V]":
        """Set default TTL."""
        self._default_ttl = ttl
        return self

    def eviction_policy(self, policy: EvictionPolicy) -> "CacheBuilder[K, V]":
        """Set eviction policy."""
        self._eviction_policy = policy
        return self

    def enable_metrics(self, enable: bool) -> "CacheBuilder[K, V]":
        """Enable/disable metrics."""
        self._enable_metrics = enable
        return self

    def cleanup_interval(self, interval: timedelta) -> "CacheBuilder[K, V]":
        """Set cleanup interval."""
        self._cleanup_interval = interval
        return self

    def refresh_ahead_factor(self, factor: float) -> "CacheBuilder[K, V]":
        """Set refresh ahead factor."""
        self._refresh_ahead_factor = factor
        return self

    def build(self) -> ReactiveCache[K, V]:
        """Build the cache."""
        config = CacheConfig(
            max_size=self._max_size,
            default_ttl=self._default_ttl,
            eviction_policy=self._eviction_policy,
            enable_metrics=self._enable_metrics,
            cleanup_interval=self._cleanup_interval,
            refresh_ahead_factor=self._refresh_ahead_factor,
        )
        return ReactiveCache(config)


def cache() -> CacheBuilder[Any, Any]:
    """Create a cache builder with fluent API."""
    return CacheBuilder()


class MultiLevelCache(Generic[K, V]):
    """Multi-level cache with L1 (memory) and L2 (distributed) support."""

    def __init__(
        self,
        l1_cache: ReactiveCache[K, V],
        l2_cache: Optional[ReactiveCache[K, V]] = None,
    ):
        self.l1_cache = l1_cache
        self.l2_cache = l2_cache

    async def get(self, key: K) -> Optional[V]:
        """Get from L1, then L2 if available."""
        # Try L1 first
        value = await self.l1_cache.get(key)
        if value is not None:
            return value

        # Try L2 if available
        if self.l2_cache:
            value = await self.l2_cache.get(key)
            if value is not None:
                # Promote to L1
                await self.l1_cache.put(key, value)
                return value

        return None

    async def put(self, key: K, value: V, ttl: Optional[timedelta] = None) -> None:
        """Put in both L1 and L2."""
        await self.l1_cache.put(key, value, ttl)
        if self.l2_cache:
            await self.l2_cache.put(key, value, ttl)

    async def remove(self, key: K) -> Optional[V]:
        """Remove from both levels."""
        l1_result = await self.l1_cache.remove(key)
        if self.l2_cache:
            await self.l2_cache.remove(key)
        return l1_result

    def get_combined_stats(self) -> Tuple[CacheStats, Optional[CacheStats]]:
        """Get stats from both cache levels."""
        return (
            self.l1_cache.get_stats(),
            self.l2_cache.get_stats() if self.l2_cache else None,
        )


class CacheWarmer(Generic[K, V]):
    """Cache warming utilities."""

    def __init__(self, cache: ReactiveCache[K, V]):
        self.cache = cache

    async def warm_up(
        self,
        keys: List[K],
        loader: Callable[[K], Coroutine[Any, Any, Optional[V]]],
        concurrency: int = 10,
        ttl: Optional[timedelta] = None,
    ) -> None:
        """Warm up cache with multiple keys concurrently."""
        semaphore = asyncio.Semaphore(concurrency)

        async def load_and_cache(key: K):
            async with semaphore:
                try:
                    value = await loader(key)
                    if value is not None:
                        await self.cache.put(key, value, ttl)
                except Exception as e:
                    logger.warning(f"Failed to warm cache for key: {key}", exc_info=e)

        await asyncio.gather(*[load_and_cache(key) for key in keys])


# Cache monitoring and health check
@dataclass
class CacheHealth:
    """Cache health status."""

    is_healthy: bool
    hit_rate: float
    memory_pressure: float
    expired_ratio: float
    recommendations: List[str]


class CacheMonitor(Generic[K, V]):
    """Cache monitoring and health check."""

    def __init__(self, cache: ReactiveCache[K, V]):
        self.cache = cache

    def health_check(self) -> CacheHealth:
        """Perform cache health check."""
        stats = self.cache.get_stats()

        return CacheHealth(
            is_healthy=stats.hit_rate > 0.7 and stats.size < 0.9 * 1000,
            hit_rate=stats.hit_rate,
            memory_pressure=stats.size / 1000,  # Normalize to max size
            expired_ratio=stats.expired_entries / max(stats.size, 1),
            recommendations=self._generate_recommendations(stats),
        )

    def _generate_recommendations(self, stats: CacheStats) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []

        if stats.hit_rate < 0.5:
            recommendations.append(
                "Low hit rate - consider increasing cache size or adjusting TTL"
            )

        if stats.expired_entries > stats.size * 0.2:
            recommendations.append(
                "High expired entry ratio - consider shorter cleanup intervals"
            )

        if stats.average_load_time > timedelta(milliseconds=100):
            recommendations.append(
                "High load times - consider implementing refresh-ahead strategy"
            )

        return recommendations
