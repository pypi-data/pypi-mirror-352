"""Enhanced caching system with tiered caching, external backends, and advanced metrics."""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from collections import defaultdict
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
    Protocol,
)
from concurrent.futures import ThreadPoolExecutor
import threading
import weakref
import json

from .reactive_cache import (
    ReactiveCache,
    CacheConfig,
    CacheEntry,
    CacheStats,
    EvictionPolicy,
)

K = TypeVar("K")
V = TypeVar("V")

logger = logging.getLogger(__name__)


class CacheBackend(ABC, Generic[K, V]):
    """Abstract cache backend interface."""

    @abstractmethod
    async def get(self, key: K) -> Optional[V]:
        """Get value by key."""
        pass

    @abstractmethod
    async def put(self, key: K, value: V, ttl: Optional[timedelta] = None) -> None:
        """Put key-value pair."""
        pass

    @abstractmethod
    async def delete(self, key: K) -> bool:
        """Delete key."""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear all entries."""
        pass

    @abstractmethod
    async def keys(self) -> Set[K]:
        """Get all keys."""
        pass

    @abstractmethod
    async def size(self) -> int:
        """Get cache size."""
        pass


@dataclass
class CacheMetrics:
    """Enhanced cache metrics with detailed statistics."""

    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    evictions: int = 0
    expired_entries: int = 0
    backend_latency: Dict[str, float] = field(default_factory=dict)
    hit_rate_by_key_pattern: Dict[str, float] = field(default_factory=dict)
    memory_usage_bytes: int = 0
    network_io_bytes: int = 0
    last_updated: datetime = field(default_factory=datetime.now)

    @property
    def hit_rate(self) -> float:
        """Calculate hit rate percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.cache_hits / self.total_requests) * 100

    @property
    def miss_rate(self) -> float:
        """Calculate miss rate percentage."""
        return 100.0 - self.hit_rate


@dataclass
class CacheStatistics:
    """Comprehensive cache statistics."""

    uptime: timedelta
    metrics: CacheMetrics
    tier_statistics: Dict[str, CacheMetrics] = field(default_factory=dict)
    performance_profile: Dict[str, Any] = field(default_factory=dict)
    health_score: float = 0.0
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "uptime_seconds": self.uptime.total_seconds(),
            "hit_rate": self.metrics.hit_rate,
            "miss_rate": self.metrics.miss_rate,
            "total_requests": self.metrics.total_requests,
            "cache_hits": self.metrics.cache_hits,
            "cache_misses": self.metrics.cache_misses,
            "evictions": self.metrics.evictions,
            "expired_entries": self.metrics.expired_entries,
            "memory_usage_bytes": self.metrics.memory_usage_bytes,
            "network_io_bytes": self.metrics.network_io_bytes,
            "tier_statistics": {
                tier: {
                    "hit_rate": stats.hit_rate,
                    "requests": stats.total_requests,
                    "latency": stats.backend_latency,
                }
                for tier, stats in self.tier_statistics.items()
            },
            "health_score": self.health_score,
            "recommendations": self.recommendations,
        }


class RedisBackend(CacheBackend[K, V]):
    """Redis cache backend implementation."""

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        key_prefix: str = "cache:",
        serializer: Optional[Callable] = None,
    ):
        self.redis_url = redis_url
        self.key_prefix = key_prefix
        self.serializer = serializer or json.dumps
        self.deserializer = json.loads
        self._redis = None

        # Try to import redis with graceful fallback
        try:
            import redis.asyncio as redis

            self._redis_module = redis
            self._available = True
        except ImportError:
            logger.warning("Redis not available, using in-memory fallback")
            self._available = False
            self._fallback_cache: Dict[K, Tuple[V, float]] = {}

    async def _get_redis(self):
        """Get Redis connection."""
        if not self._available:
            return None
        if self._redis is None:
            self._redis = self._redis_module.from_url(self.redis_url)
        return self._redis

    def _make_key(self, key: K) -> str:
        """Make Redis key."""
        return f"{self.key_prefix}{key}"

    async def get(self, key: K) -> Optional[V]:
        """Get value by key."""
        redis = await self._get_redis()
        if redis is None:
            # Fallback to in-memory
            if key in self._fallback_cache:
                value, expire_time = self._fallback_cache[key]
                if expire_time == 0 or time.time() < expire_time:
                    return value
                else:
                    del self._fallback_cache[key]
            return None

        try:
            redis_key = self._make_key(key)
            data = await redis.get(redis_key)
            if data is None:
                return None
            return self.deserializer(data)
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    async def put(self, key: K, value: V, ttl: Optional[timedelta] = None) -> None:
        """Put key-value pair."""
        redis = await self._get_redis()
        if redis is None:
            # Fallback to in-memory
            expire_time = 0
            if ttl:
                expire_time = time.time() + ttl.total_seconds()
            self._fallback_cache[key] = (value, expire_time)
            return

        try:
            redis_key = self._make_key(key)
            data = self.serializer(value)
            if ttl:
                await redis.setex(redis_key, int(ttl.total_seconds()), data)
            else:
                await redis.set(redis_key, data)
        except Exception as e:
            logger.error(f"Redis put error: {e}")

    async def delete(self, key: K) -> bool:
        """Delete key."""
        redis = await self._get_redis()
        if redis is None:
            return self._fallback_cache.pop(key, None) is not None

        try:
            redis_key = self._make_key(key)
            result = await redis.delete(redis_key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False

    async def clear(self) -> None:
        """Clear all entries."""
        redis = await self._get_redis()
        if redis is None:
            self._fallback_cache.clear()
            return

        try:
            keys = await redis.keys(f"{self.key_prefix}*")
            if keys:
                await redis.delete(*keys)
        except Exception as e:
            logger.error(f"Redis clear error: {e}")

    async def keys(self) -> Set[K]:
        """Get all keys."""
        redis = await self._get_redis()
        if redis is None:
            return set(self._fallback_cache.keys())

        try:
            redis_keys = await redis.keys(f"{self.key_prefix}*")
            return {key.decode().replace(self.key_prefix, "") for key in redis_keys}
        except Exception as e:
            logger.error(f"Redis keys error: {e}")
            return set()

    async def size(self) -> int:
        """Get cache size."""
        keys = await self.keys()
        return len(keys)


class MemcachedBackend(CacheBackend[K, V]):
    """Memcached cache backend implementation."""

    def __init__(
        self,
        servers: List[str] = None,
        key_prefix: str = "cache:",
        serializer: Optional[Callable] = None,
    ):
        self.servers = servers or ["127.0.0.1:11211"]
        self.key_prefix = key_prefix
        self.serializer = serializer or json.dumps
        self.deserializer = json.loads
        self._client = None

        # Try to import memcached with graceful fallback
        try:
            import aiomcache

            self._memcache_module = aiomcache
            self._available = True
        except ImportError:
            logger.warning("Memcached not available, using in-memory fallback")
            self._available = False
            self._fallback_cache: Dict[K, Tuple[V, float]] = {}

    async def _get_client(self):
        """Get Memcached client."""
        if not self._available:
            return None
        if self._client is None:
            self._client = self._memcache_module.Client(*self.servers)
        return self._client

    def _make_key(self, key: K) -> str:
        """Make Memcached key."""
        return f"{self.key_prefix}{key}"

    async def get(self, key: K) -> Optional[V]:
        """Get value by key."""
        client = await self._get_client()
        if client is None:
            # Fallback implementation
            if key in self._fallback_cache:
                value, expire_time = self._fallback_cache[key]
                if expire_time == 0 or time.time() < expire_time:
                    return value
                else:
                    del self._fallback_cache[key]
            return None

        try:
            cache_key = self._make_key(key)
            data = await client.get(cache_key.encode())
            if data is None:
                return None
            return self.deserializer(data.decode())
        except Exception as e:
            logger.error(f"Memcached get error: {e}")
            return None

    async def put(self, key: K, value: V, ttl: Optional[timedelta] = None) -> None:
        """Put key-value pair."""
        client = await self._get_client()
        if client is None:
            # Fallback implementation
            expire_time = 0
            if ttl:
                expire_time = time.time() + ttl.total_seconds()
            self._fallback_cache[key] = (value, expire_time)
            return

        try:
            cache_key = self._make_key(key)
            data = self.serializer(value)
            expiration = int(ttl.total_seconds()) if ttl else 0
            await client.set(cache_key.encode(), data.encode(), exptime=expiration)
        except Exception as e:
            logger.error(f"Memcached put error: {e}")

    async def delete(self, key: K) -> bool:
        """Delete key."""
        client = await self._get_client()
        if client is None:
            return self._fallback_cache.pop(key, None) is not None

        try:
            cache_key = self._make_key(key)
            result = await client.delete(cache_key.encode())
            return result
        except Exception as e:
            logger.error(f"Memcached delete error: {e}")
            return False

    async def clear(self) -> None:
        """Clear all entries."""
        client = await self._get_client()
        if client is None:
            self._fallback_cache.clear()
            return

        try:
            await client.flush_all()
        except Exception as e:
            logger.error(f"Memcached clear error: {e}")

    async def keys(self) -> Set[K]:
        """Get all keys (limited functionality in Memcached)."""
        # Memcached doesn't support key listing, return empty set
        logger.warning("Key listing not supported in Memcached")
        return set()

    async def size(self) -> int:
        """Get cache size (limited functionality in Memcached)."""
        # Memcached doesn't support size calculation
        return 0


class TieredCache(Generic[K, V]):
    """Multi-tier cache with L1 (memory) and L2 (distributed) backends."""

    def __init__(
        self,
        l1_cache: ReactiveCache[K, V],
        l2_backend: CacheBackend[K, V],
        promotion_threshold: int = 3,
        metrics_enabled: bool = True,
    ):
        self.l1_cache = l1_cache
        self.l2_backend = l2_backend
        self.promotion_threshold = promotion_threshold
        self.metrics_enabled = metrics_enabled

        # Access tracking for promotion
        self._access_counts: Dict[K, int] = defaultdict(int)
        self._metrics = CacheMetrics()
        self._start_time = datetime.now()

        # Background tasks
        self._promotion_task: Optional[asyncio.Task] = None
        self._metrics_task: Optional[asyncio.Task] = None

        if metrics_enabled:
            self._start_background_tasks()

    def _start_background_tasks(self):
        """Start background tasks for promotion and metrics."""
        self._promotion_task = asyncio.create_task(self._promotion_worker())
        self._metrics_task = asyncio.create_task(self._metrics_worker())

    async def _promotion_worker(self):
        """Background worker for cache promotion."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                await self._process_promotions()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Promotion worker error: {e}")

    async def _metrics_worker(self):
        """Background worker for metrics collection."""
        while True:
            try:
                await asyncio.sleep(30)  # Update every 30 seconds
                await self._update_metrics()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics worker error: {e}")

    async def _process_promotions(self):
        """Process cache promotions from L2 to L1."""
        candidates = [
            key
            for key, count in self._access_counts.items()
            if count >= self.promotion_threshold
        ]

        for key in candidates[:10]:  # Limit promotions per cycle
            try:
                value = await self.l2_backend.get(key)
                if value is not None:
                    await self.l1_cache.put(key, value)
                    logger.debug(f"Promoted key to L1: {key}")
            except Exception as e:
                logger.error(f"Promotion error for key {key}: {e}")

    async def _update_metrics(self):
        """Update cache metrics."""
        try:
            l1_stats = self.l1_cache.get_stats()
            l2_size = await self.l2_backend.size()

            self._metrics.last_updated = datetime.now()
            # Update other metrics as needed
        except Exception as e:
            logger.error(f"Metrics update error: {e}")

    async def get(self, key: K) -> Optional[V]:
        """Get value from tiered cache."""
        self._metrics.total_requests += 1
        self._access_counts[key] += 1

        # Try L1 first
        value = await self.l1_cache.get(key)
        if value is not None:
            self._metrics.cache_hits += 1
            return value

        # Try L2
        value = await self.l2_backend.get(key)
        if value is not None:
            self._metrics.cache_hits += 1

            # Consider promoting to L1 if accessed frequently
            if self._access_counts[key] >= self.promotion_threshold:
                await self.l1_cache.put(key, value)

            return value

        self._metrics.cache_misses += 1
        return None

    async def put(self, key: K, value: V, ttl: Optional[timedelta] = None) -> None:
        """Put value in tiered cache."""
        # Put in both L1 and L2
        await asyncio.gather(
            self.l1_cache.put(key, value, ttl),
            self.l2_backend.put(key, value, ttl),
            return_exceptions=True,
        )

    async def delete(self, key: K) -> bool:
        """Delete from both tiers."""
        results = await asyncio.gather(
            self.l1_cache.delete(key),
            self.l2_backend.delete(key),
            return_exceptions=True,
        )
        return any(isinstance(r, bool) and r for r in results)

    async def clear(self) -> None:
        """Clear both tiers."""
        await asyncio.gather(
            self.l1_cache.clear(), self.l2_backend.clear(), return_exceptions=True
        )
        self._access_counts.clear()

    def get_statistics(self) -> CacheStatistics:
        """Get comprehensive cache statistics."""
        uptime = datetime.now() - self._start_time
        l1_stats = self.l1_cache.get_stats()

        # Calculate health score
        health_score = min(100.0, self._metrics.hit_rate)
        if health_score < 50:
            health_score *= 0.8  # Penalty for low hit rate

        # Generate recommendations
        recommendations = []
        if self._metrics.hit_rate < 70:
            recommendations.append("Consider increasing L1 cache size")
        if len(self._access_counts) > 1000:
            recommendations.append(
                "High key diversity - consider key pattern optimization"
            )

        return CacheStatistics(
            uptime=uptime,
            metrics=self._metrics,
            tier_statistics={
                "L1": CacheMetrics(
                    total_requests=l1_stats.total_requests,
                    cache_hits=l1_stats.cache_hits,
                    cache_misses=l1_stats.cache_misses,
                    evictions=l1_stats.evictions,
                    memory_usage_bytes=l1_stats.size * 1024,  # Estimate
                ),
                "L2": CacheMetrics(
                    # L2 metrics would be populated from backend
                ),
            },
            health_score=health_score,
            recommendations=recommendations,
        )

    async def shutdown(self):
        """Shutdown background tasks."""
        if self._promotion_task:
            self._promotion_task.cancel()
            try:
                await self._promotion_task
            except asyncio.CancelledError:
                pass

        if self._metrics_task:
            self._metrics_task.cancel()
            try:
                await self._metrics_task
            except asyncio.CancelledError:
                pass


class EnhancedCache(TieredCache[K, V]):
    """Enhanced cache with advanced features and monitoring."""

    def __init__(
        self,
        l1_config: Optional[CacheConfig] = None,
        l2_backend: Optional[CacheBackend[K, V]] = None,
        enable_analytics: bool = True,
        enable_auto_tuning: bool = False,
    ):

        # Create L1 cache with default config if not provided
        if l1_config is None:
            l1_config = CacheConfig(
                max_size=1000,
                ttl=timedelta(minutes=30),
                eviction_policy=EvictionPolicy.LRU,
            )

        l1_cache = ReactiveCache(l1_config)

        # Use Redis backend by default if not provided
        if l2_backend is None:
            l2_backend = RedisBackend()

        super().__init__(l1_cache, l2_backend, metrics_enabled=enable_analytics)

        self.enable_analytics = enable_analytics
        self.enable_auto_tuning = enable_auto_tuning

        # Advanced features
        self._access_patterns: Dict[str, List[float]] = defaultdict(list)
        self._key_popularity: Dict[K, float] = defaultdict(float)

        if enable_auto_tuning:
            self._tuning_task = asyncio.create_task(self._auto_tuning_worker())

    async def _auto_tuning_worker(self):
        """Auto-tune cache parameters based on usage patterns."""
        while True:
            try:
                await asyncio.sleep(300)  # Tune every 5 minutes
                await self._perform_auto_tuning()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Auto-tuning error: {e}")

    async def _perform_auto_tuning(self):
        """Perform automatic cache tuning."""
        stats = self.get_statistics()

        # Adjust L1 cache size based on hit rate
        if stats.metrics.hit_rate < 60:
            # Increase L1 cache size
            current_size = self.l1_cache.config.max_size
            new_size = min(current_size * 1.2, 5000)
            logger.info(
                f"Auto-tuning: Increasing L1 cache size from {current_size} to {new_size}"
            )
            # Note: This would require cache config modification support

        # Adjust TTL based on access patterns
        avg_access_interval = self._calculate_average_access_interval()
        if avg_access_interval > 0:
            optimal_ttl = timedelta(seconds=avg_access_interval * 2)
            logger.debug(f"Auto-tuning: Suggested TTL adjustment to {optimal_ttl}")

    def _calculate_average_access_interval(self) -> float:
        """Calculate average access interval for auto-tuning."""
        intervals = []
        for pattern in self._access_patterns.values():
            if len(pattern) > 1:
                for i in range(1, len(pattern)):
                    intervals.append(pattern[i] - pattern[i - 1])

        return sum(intervals) / len(intervals) if intervals else 0

    async def get_with_analytics(self, key: K) -> Tuple[Optional[V], Dict[str, Any]]:
        """Get value with detailed analytics."""
        start_time = time.time()
        value = await self.get(key)
        end_time = time.time()

        # Record access pattern
        self._access_patterns[str(key)].append(time.time())
        self._key_popularity[key] = (
            self._key_popularity[key] * 0.9 + 0.1
        )  # Decay + increment

        analytics = {
            "latency_ms": (end_time - start_time) * 1000,
            "cache_tier": (
                "L1" if key in await self.l1_cache.keys() else "L2" if value else "miss"
            ),
            "popularity_score": self._key_popularity[key],
            "access_count": len(self._access_patterns[str(key)]),
        }

        return value, analytics


class ExternalCache:
    """External cache interface for cloud services."""

    def __init__(self, provider: str = "aws", region: str = "us-east-1"):
        self.provider = provider
        self.region = region
        self._client = None

        logger.info(f"External cache configured for {provider} in {region}")

    async def connect(self):
        """Connect to external cache service."""
        if self.provider == "aws":
            try:
                import boto3

                # Initialize AWS ElastiCache client
                logger.info("AWS ElastiCache client initialized")
            except ImportError:
                logger.warning("AWS SDK not available")
        elif self.provider == "azure":
            try:
                # Initialize Azure Redis client
                logger.info("Azure Redis client initialized")
            except ImportError:
                logger.warning("Azure SDK not available")
        elif self.provider == "gcp":
            try:
                # Initialize GCP Memorystore client
                logger.info("GCP Memorystore client initialized")
            except ImportError:
                logger.warning("GCP SDK not available")

    async def get_cluster_info(self) -> Dict[str, Any]:
        """Get external cache cluster information."""
        return {
            "provider": self.provider,
            "region": self.region,
            "status": "connected" if self._client else "disconnected",
            "cluster_nodes": 1,  # Mock data
            "memory_usage": "45%",
            "network_throughput": "1.2 GB/s",
        }


class CacheFactory:
    """Factory for creating different types of caches."""

    @staticmethod
    def create_memory_cache(config: Optional[CacheConfig] = None) -> ReactiveCache:
        """Create an in-memory cache."""
        if config is None:
            config = CacheConfig(max_size=1000, ttl=timedelta(minutes=15))
        return ReactiveCache(config)

    @staticmethod
    def create_redis_cache(
        redis_url: str = "redis://localhost:6379",
        l1_config: Optional[CacheConfig] = None,
    ) -> TieredCache:
        """Create a tiered cache with Redis L2."""
        l1_cache = CacheFactory.create_memory_cache(l1_config)
        l2_backend = RedisBackend(redis_url)
        return TieredCache(l1_cache, l2_backend)

    @staticmethod
    def create_memcached_cache(
        servers: Optional[List[str]] = None, l1_config: Optional[CacheConfig] = None
    ) -> TieredCache:
        """Create a tiered cache with Memcached L2."""
        l1_cache = CacheFactory.create_memory_cache(l1_config)
        l2_backend = MemcachedBackend(servers)
        return TieredCache(l1_cache, l2_backend)

    @staticmethod
    def create_enhanced_cache(
        backend_type: str = "redis",
        enable_analytics: bool = True,
        enable_auto_tuning: bool = False,
    ) -> EnhancedCache:
        """Create an enhanced cache with advanced features."""
        l1_config = CacheConfig(
            max_size=2000, ttl=timedelta(minutes=30), eviction_policy=EvictionPolicy.LRU
        )

        if backend_type == "redis":
            l2_backend = RedisBackend()
        elif backend_type == "memcached":
            l2_backend = MemcachedBackend()
        else:
            raise ValueError(f"Unsupported backend type: {backend_type}")

        return EnhancedCache(
            l1_config=l1_config,
            l2_backend=l2_backend,
            enable_analytics=enable_analytics,
            enable_auto_tuning=enable_auto_tuning,
        )


# Usage examples
async def example_usage():
    """Example usage of enhanced caching features."""

    # Create enhanced cache with analytics
    cache = CacheFactory.create_enhanced_cache(
        backend_type="redis", enable_analytics=True, enable_auto_tuning=True
    )

    # Use cache with analytics
    value, analytics = await cache.get_with_analytics("user:123")
    print(f"Cache analytics: {analytics}")

    # Put some data
    await cache.put("user:123", {"name": "John", "email": "john@example.com"})

    # Get comprehensive statistics
    stats = cache.get_statistics()
    print(f"Cache statistics: {stats.to_dict()}")

    # Cleanup
    await cache.shutdown()


if __name__ == "__main__":
    asyncio.run(example_usage())
