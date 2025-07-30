#!/usr/bin/env python3
"""
ApexNova Integration Example - ReactiveSerializationEngine
Demonstrates integration with the broader ApexNova reactive modernization project
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

from reactive_serialization_engine import (
    ReactiveSerializationEngine,
    ReactiveSerializationEngineBuilder,
    SerializationFormat,
)
from compression_service import CompressionType
from checksum_service import ChecksumType


# Example ApexNova domain models
@dataclass
class User:
    """ApexNova User entity"""

    id: str
    username: str
    email: str
    created_at: datetime
    permissions: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {**asdict(self), "created_at": self.created_at.isoformat()}


@dataclass
class MarketData:
    """ApexNova Market entity"""

    symbol: str
    price: float
    volume: int
    timestamp: datetime
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {**asdict(self), "timestamp": self.timestamp.isoformat()}


@dataclass
class Notification:
    """ApexNova Notification entity"""

    id: str
    user_id: str
    type: str
    title: str
    message: str
    priority: str
    sent_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {**asdict(self), "sent_at": self.sent_at.isoformat()}


class ApexNovaReactiveSerializer:
    """
    ApexNova-specific reactive serialization service
    Demonstrates integration patterns for the modernization project
    """

    def __init__(self):
        # Production-optimized configuration
        self.engine = (
            ReactiveSerializationEngineBuilder()
            .with_format(SerializationFormat.JSON)  # Default for API compatibility
            .with_compression(CompressionType.GZIP)  # Reduce network overhead
            .with_checksum(ChecksumType.SHA256)  # Ensure data integrity
            .with_cache(enabled=True, max_size=10000, ttl_seconds=3600)  # 1-hour cache
            .with_metrics(enabled=True)  # Monitor performance
            .with_concurrency(
                max_operations=200, thread_pool_size=16
            )  # High throughput
            .build()
        )

    async def serialize_user(self, user: User) -> bytes:
        """Serialize user entity for storage/transmission"""
        result = await self.engine.serialize(
            user.to_dict(),
            SerializationFormat.JSON,
            CompressionType.GZIP,
            ChecksumType.SHA256,
        )

        if result.is_failure:
            raise Exception(f"User serialization failed: {result.error}")

        return result.value

    async def deserialize_user(
        self, data: bytes, expected_checksum: Optional[str] = None
    ) -> User:
        """Deserialize user entity from storage/transmission"""
        result = await self.engine.deserialize(
            data,
            dict,
            SerializationFormat.JSON,
            CompressionType.GZIP,
            ChecksumType.SHA256,
            expected_checksum,
        )

        if result.is_failure:
            raise Exception(f"User deserialization failed: {result.error}")

        user_data = result.value
        return User(
            id=user_data["id"],
            username=user_data["username"],
            email=user_data["email"],
            created_at=datetime.fromisoformat(user_data["created_at"]),
            permissions=user_data["permissions"],
        )

    async def serialize_market_data_stream(
        self, market_data_stream
    ) -> AsyncIterator[bytes]:
        """Serialize streaming market data for real-time processing"""

        async def data_transformer():
            async for market_data in market_data_stream:
                yield market_data.to_dict()

        async for result in self.engine.serialize_stream(
            data_transformer(), SerializationFormat.JSON, CompressionType.GZIP
        ):
            if result.is_success:
                yield result.value
            else:
                # Log error but continue processing stream
                print(f"Market data serialization error: {result.error}")

    async def batch_serialize_notifications(
        self, notifications: List[Notification]
    ) -> List[bytes]:
        """Batch serialize notifications for efficient processing"""
        notification_dicts = [notification.to_dict() for notification in notifications]

        results = await self.engine.serialize_batch(
            notification_dicts, SerializationFormat.JSON, CompressionType.GZIP
        )

        # Filter successful results and log errors
        successful_data = []
        for i, result in enumerate(results):
            if result.is_success:
                successful_data.append(result.value)
            else:
                print(f"Notification {i} serialization failed: {result.error}")

        return successful_data

    async def persist_to_cache(
        self,
        key: str,
        data: Any,
        format_type: SerializationFormat = SerializationFormat.JSON,
    ):
        """Persist data to cache with ApexNova-specific logic"""
        result = await self.engine.serialize(data, format_type, CompressionType.GZIP)

        if result.is_success:
            # In production, this would integrate with Redis/Hazelcast
            print(f"Cache stored: {key} -> {len(result.value)} bytes (compressed)")
            return True
        else:
            print(f"Cache store failed for {key}: {result.error}")
            return False

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get ApexNova-specific performance metrics"""
        metrics = self.engine.get_metrics()
        cache_stats = self.engine.get_cache_stats()

        if not metrics:
            return {"error": "Metrics not available"}

        return {
            "serialization": {
                "operations_count": metrics.operations_count,
                "total_bytes_serialized": metrics.total_bytes_serialized,
                "total_bytes_deserialized": metrics.total_bytes_deserialized,
                "avg_serialization_time": (
                    metrics.total_serialization_time / metrics.operations_count
                    if metrics.operations_count > 0
                    else 0
                ),
                "avg_deserialization_time": (
                    metrics.total_deserialization_time / metrics.operations_count
                    if metrics.operations_count > 0
                    else 0
                ),
                "compression_ratio": metrics.compression_ratio,
                "error_count": metrics.errors_count,
            },
            "cache": {
                "size": cache_stats["size"],
                "max_size": cache_stats["max_size"],
                "hit_ratio": metrics.cache_hit_ratio,
                "hits": metrics.cache_hits,
                "misses": metrics.cache_misses,
            },
        }

    async def health_check(self) -> Dict[str, Any]:
        """ApexNova health check endpoint"""
        try:
            # Test basic functionality
            test_data = {"health_check": True, "timestamp": datetime.now().isoformat()}
            result = await self.engine.serialize(test_data, SerializationFormat.JSON)

            if result.is_success:
                # Test round-trip
                deserialized = await self.engine.deserialize(
                    result.value, dict, SerializationFormat.JSON
                )
                if deserialized.is_success:
                    return {
                        "status": "healthy",
                        "serialization": "ok",
                        "deserialization": "ok",
                        "metrics": await self.get_performance_metrics(),
                    }

            return {"status": "degraded", "error": "Serialization test failed"}

        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def close(self):
        """Clean up resources"""
        await self.engine.close()


async def demo_apexnova_integration():
    """Demonstrate ApexNova integration patterns"""
    print("🚀 ApexNova ReactiveSerializationEngine Integration Demo")
    print("=" * 60)

    serializer = ApexNovaReactiveSerializer()

    try:
        # Demo 1: User entity serialization
        print("\n👤 User Entity Serialization")
        user = User(
            id="user_123",
            username="alex_nova",
            email="alex@apexnova.com",
            created_at=datetime.now(),
            permissions=["read", "write", "admin"],
        )

        serialized_user = await serializer.serialize_user(user)
        print(f"   Serialized user: {len(serialized_user)} bytes")

        deserialized_user = await serializer.deserialize_user(serialized_user)
        print(f"   Deserialized user: {deserialized_user.username}")

        # Demo 2: Market data streaming
        print("\n📈 Market Data Streaming")

        async def mock_market_stream():
            for i in range(5):
                yield MarketData(
                    symbol=f"APEX{i}",
                    price=100.0 + i,
                    volume=1000 * (i + 1),
                    timestamp=datetime.now(),
                    metadata={"exchange": "NYSE", "session": "regular"},
                )
                await asyncio.sleep(0.1)

        stream_count = 0
        async for serialized_data in serializer.serialize_market_data_stream(
            mock_market_stream()
        ):
            stream_count += 1
            print(
                f"   Streamed market data {stream_count}: {len(serialized_data)} bytes"
            )

        # Demo 3: Batch notification processing
        print("\n🔔 Batch Notification Processing")
        notifications = [
            Notification(
                id=f"notif_{i}",
                user_id="user_123",
                type="market_alert",
                title=f"Alert {i}",
                message=f"Market update message {i}",
                priority="high" if i % 2 == 0 else "normal",
                sent_at=datetime.now(),
            )
            for i in range(3)
        ]

        batch_results = await serializer.batch_serialize_notifications(notifications)
        print(f"   Batch processed {len(batch_results)} notifications")

        # Demo 4: Cache integration
        print("\n🗄️ Cache Integration")
        cache_data = {
            "user_preferences": {"theme": "dark", "notifications": True},
            "last_login": datetime.now().isoformat(),
        }

        cache_success = await serializer.persist_to_cache("user_123_prefs", cache_data)
        print(f"   Cache operation: {'success' if cache_success else 'failed'}")

        # Demo 5: Performance monitoring
        print("\n📊 Performance Monitoring")
        metrics = await serializer.get_performance_metrics()
        print(f"   Operations: {metrics['serialization']['operations_count']}")
        print(f"   Cache hit ratio: {metrics['cache']['hit_ratio']:.1%}")
        print(
            f"   Avg serialization time: {metrics['serialization']['avg_serialization_time']*1000:.2f}ms"
        )

        # Demo 6: Health check
        print("\n🏥 Health Check")
        health = await serializer.health_check()
        print(f"   Status: {health['status']}")
        print(f"   Serialization: {health.get('serialization', 'unknown')}")

        print("\n✅ ApexNova integration demo completed successfully!")

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        raise

    finally:
        await serializer.close()


async def demo_microservice_pattern():
    """Demonstrate microservice integration pattern"""
    print("\n🔧 Microservice Integration Pattern")
    print("-" * 40)

    # Simulate microservice communication
    serializer = ApexNovaReactiveSerializer()

    # Service A sends data to Service B
    service_a_data = {
        "service": "user_management",
        "operation": "user_created",
        "payload": {"user_id": "user_456", "timestamp": datetime.now().isoformat()},
        "metadata": {"version": "1.0", "correlation_id": "corr_123"},
    }

    # Serialize for inter-service communication
    result = await serializer.engine.serialize(
        service_a_data, SerializationFormat.JSON, CompressionType.GZIP
    )

    if result.is_success:
        print(f"   Microservice message: {len(result.value)} bytes")

        # Service B receives and processes
        deserialized = await serializer.engine.deserialize(
            result.value, dict, SerializationFormat.JSON, CompressionType.GZIP
        )

        if deserialized.is_success:
            message = deserialized.value
            print(f"   Service B received: {message['operation']}")
            print(f"   Correlation ID: {message['metadata']['correlation_id']}")

    await serializer.close()


if __name__ == "__main__":

    async def main():
        await demo_apexnova_integration()
        await demo_microservice_pattern()
        print("\n🎉 All ApexNova integration demos completed!")

    asyncio.run(main())
