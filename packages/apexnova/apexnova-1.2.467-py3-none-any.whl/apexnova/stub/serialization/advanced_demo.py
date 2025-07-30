#!/usr/bin/env python3
"""
Advanced features and streaming capabilities for ReactiveSerializationEngine
"""

import asyncio
import json
from typing import AsyncIterator, List, Dict, Any
from datetime import datetime

from reactive_serialization_engine import (
    ReactiveSerializationEngine,
    SerializationFormat,
    ReactiveSerializationEngineBuilder,
)
from compression_service import CompressionType
from checksum_service import ChecksumType


async def demo_streaming_operations():
    """Demonstrate streaming serialization capabilities"""
    print("=== Streaming Operations Demo ===")

    engine = ReactiveSerializationEngine()

    # Create a stream of data
    async def data_generator():
        for i in range(5):
            yield {
                "id": i,
                "timestamp": datetime.now().isoformat(),
                "data": f"stream_item_{i}",
            }
            await asyncio.sleep(0.1)  # Simulate real streaming

    print("📤 Streaming serialization...")
    serialized_count = 0
    async for result in engine.serialize_stream(
        data_generator(), SerializationFormat.JSON
    ):
        if result.is_success:
            serialized_count += 1
            print(f"   Serialized item {serialized_count}: {len(result.value)} bytes")
        else:
            print(f"   ❌ Serialization failed: {result.error}")

    print(f"✓ Streamed {serialized_count} items successfully")


async def demo_advanced_caching():
    """Demonstrate advanced caching features"""
    print("\n=== Advanced Caching Demo ===")

    # Configure engine with custom cache settings
    engine = (
        ReactiveSerializationEngineBuilder()
        .with_cache(enabled=True, max_size=3, ttl_seconds=2)
        .with_metrics(enabled=True)
        .build()
    )

    # Test cache overflow
    print("🗄️ Testing cache overflow...")
    test_objects = [{"cache_test": i, "data": f"object_{i}"} for i in range(5)]

    for i, obj in enumerate(test_objects):
        result = await engine.serialize(obj, SerializationFormat.JSON)
        assert result.is_success
        stats = engine.get_cache_stats()
        print(f"   Object {i}: Cache size = {stats['size']}/{stats['max_size']}")

    # Test TTL expiration
    print("⏰ Testing TTL expiration...")
    result = await engine.serialize({"ttl_test": "data"}, SerializationFormat.JSON)
    print(f"   Cached item, size: {engine.get_cache_stats()['size']}")

    print("   Waiting for TTL expiration...")
    await asyncio.sleep(3)

    # Trigger cache cleanup
    await engine._cleanup_expired_cache_entries()
    print(f"   After cleanup, size: {engine.get_cache_stats()['size']}")

    await engine.close()


async def demo_compression_comparison():
    """Demonstrate compression effectiveness across formats"""
    print("\n=== Compression Comparison Demo ===")

    # Create test data with good compression potential
    large_data = {
        "repeated_field": "x" * 500,
        "array": ["item"] * 100,
        "nested": {"level1": {"level2": {"data": "repeated_string " * 50}}},
    }

    engine = ReactiveSerializationEngine()

    formats = [SerializationFormat.JSON, SerializationFormat.BINARY]
    compressions = [CompressionType.NONE, CompressionType.GZIP, CompressionType.ZLIB]

    print("📊 Compression effectiveness:")
    print(f"{'Format':<10} {'Compression':<12} {'Size (bytes)':<12} {'Ratio':<8}")
    print("-" * 50)

    baseline_size = None

    for format_type in formats:
        for compression in compressions:
            result = await engine.serialize(large_data, format_type, compression)
            if result.is_success:
                size = len(result.value)
                if baseline_size is None:
                    baseline_size = size
                    ratio = "100%"
                else:
                    ratio = f"{(size / baseline_size) * 100:.1f}%"

                print(
                    f"{format_type.name:<10} {compression.name:<12} {size:<12} {ratio:<8}"
                )


async def demo_error_handling():
    """Demonstrate comprehensive error handling"""
    print("\n=== Error Handling Demo ===")

    engine = ReactiveSerializationEngine()

    # Test invalid data
    print("🚫 Testing error scenarios...")

    # Non-serializable object
    class NonSerializable:
        def __init__(self):
            self.func = lambda x: x  # Functions can't be JSON serialized

    result = await engine.serialize(NonSerializable(), SerializationFormat.JSON)
    if result.is_failure:
        print(f"   ✓ Caught expected error: {result.error}")

    # Invalid checksum
    valid_data = b'{"test": "data"}'
    result = await engine.deserialize(
        valid_data,
        dict,
        SerializationFormat.JSON,
        checksum=ChecksumType.SHA256,
        expected_checksum="invalid_checksum",
    )
    if result.is_failure:
        print(f"   ✓ Caught checksum error: {result.error}")

    # Non-existent file
    result = await engine.deserialize_from_file(
        "/non/existent/file.json", dict, SerializationFormat.JSON
    )
    if result.is_failure:
        print(f"   ✓ Caught file error: {result.error}")


async def demo_performance_monitoring():
    """Demonstrate performance monitoring and metrics"""
    print("\n=== Performance Monitoring Demo ===")

    engine = ReactiveSerializationEngine()

    # Perform various operations
    test_data = {"performance": "test", "data": list(range(100))}

    print("📈 Running performance test...")

    # Serialize multiple times with different formats
    for format_type in [SerializationFormat.JSON, SerializationFormat.BINARY]:
        for i in range(10):
            await engine.serialize(test_data, format_type)

    metrics = engine.get_metrics()
    if metrics:
        print(f"📊 Performance Metrics:")
        print(f"   Total operations: {metrics.operations_count}")
        print(f"   Bytes serialized: {metrics.total_bytes_serialized}")
        print(
            f"   Avg serialization time: {metrics.total_serialization_time / metrics.operations_count:.4f}s"
        )
        print(f"   Cache hit ratio: {metrics.cache_hit_ratio:.1%}")
        print(f"   Compression ratio: {metrics.compression_ratio:.2f}")
        print(f"   Error count: {metrics.errors_count}")


async def demo_custom_serializers():
    """Demonstrate custom serializer registration"""
    print("\n=== Custom Serializers Demo ===")

    engine = ReactiveSerializationEngine()

    # Define a custom format (CSV-like)
    def csv_serialize(obj: Any) -> str:
        if isinstance(obj, list) and all(isinstance(item, dict) for item in obj):
            if not obj:
                return ""
            headers = list(obj[0].keys())
            lines = [",".join(headers)]
            for item in obj:
                lines.append(",".join(str(item.get(h, "")) for h in headers))
            return "\n".join(lines)
        return str(obj)

    def csv_deserialize(csv_str: str) -> List[Dict[str, str]]:
        lines = csv_str.strip().split("\n")
        if len(lines) < 2:
            return []
        headers = lines[0].split(",")
        result = []
        for line in lines[1:]:
            values = line.split(",")
            result.append(dict(zip(headers, values)))
        return result

    # Register custom serializer
    engine.register_serializer(SerializationFormat.XML, csv_serialize, csv_deserialize)

    # Test custom serialization
    test_data = [
        {"name": "Alice", "age": "30", "city": "New York"},
        {"name": "Bob", "age": "25", "city": "London"},
    ]

    result = await engine.serialize(test_data, SerializationFormat.XML)
    if result.is_success:
        print("📝 Custom CSV serialization:")
        print(result.value.decode("utf-8"))

        # Test deserialization
        deserialized = await engine.deserialize(
            result.value, list, SerializationFormat.XML
        )
        if deserialized.is_success:
            print("✓ Custom deserialization successful:")
            print(f"   {deserialized.value}")


async def demo_reactive_patterns():
    """Demonstrate reactive programming patterns"""
    print("\n=== Reactive Patterns Demo ===")

    engine = ReactiveSerializationEngine()

    # Chain operations using monadic patterns
    test_data = {"reactive": "data", "value": 42}

    # Serialize, then transform the result
    result = await engine.serialize(test_data, SerializationFormat.JSON)

    # Use map to transform successful results
    transformed = result.map(lambda data: data.decode("utf-8").upper())

    if transformed.is_success:
        print("🔄 Monadic transformation successful")
        print(f"   Original length: {len(result.value)}")
        print(f"   Transformed (uppercase): {transformed.value[:50]}...")

    # Use flat_map for chaining operations
    async def deserialize_and_modify(data: bytes):
        deserialized = await engine.deserialize(data, dict, SerializationFormat.JSON)
        return deserialized.map(lambda obj: {**obj, "modified": True})

    chained_result = await result.flat_map(lambda data: deserialize_and_modify(data))

    if chained_result.is_success:
        print("🔗 Monadic chaining successful")
        print(f"   Result: {chained_result.value}")


async def run_advanced_demos():
    """Run all advanced feature demonstrations"""
    print("🚀 ReactiveSerializationEngine Advanced Features Demo\n")

    try:
        await demo_streaming_operations()
        await demo_advanced_caching()
        await demo_compression_comparison()
        await demo_error_handling()
        await demo_performance_monitoring()
        await demo_custom_serializers()
        await demo_reactive_patterns()

        print("\n🎉 All advanced demos completed successfully!")

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(run_advanced_demos())
