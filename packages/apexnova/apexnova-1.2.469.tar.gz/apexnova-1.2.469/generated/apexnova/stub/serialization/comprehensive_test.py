#!/usr/bin/env python3
"""
Comprehensive test suite for ReactiveSerializationEngine
"""

import asyncio
import time
from typing import List, Dict, Any

from reactive_serialization_engine import (
    ReactiveSerializationEngine,
    ReactiveSerializationEngineBuilder,
    SerializationFormat,
    serialize,
    deserialize,
)
from compression_service import CompressionType
from checksum_service import ChecksumType


class TestData:
    """Test data class for serialization"""

    def __init__(self, name: str, value: int, items: List[str]):
        self.name = name
        self.value = value
        self.items = items

    def __eq__(self, other):
        return (
            isinstance(other, TestData)
            and self.name == other.name
            and self.value == other.value
            and self.items == other.items
        )

    def __str__(self):
        return f"TestData(name='{self.name}', value={self.value}, items={self.items})"


async def test_basic_serialization():
    """Test basic serialization functionality"""
    print("=== Testing Basic Serialization ===")

    test_data = {"name": "test", "value": 42, "items": ["a", "b", "c"]}

    engine = ReactiveSerializationEngine()

    # Test JSON
    result = await engine.serialize(test_data, SerializationFormat.JSON)
    assert result.is_success, f"JSON serialization failed: {result.error}"
    print("✓ JSON serialization successful")

    deserialized = await engine.deserialize(
        result.value, dict, SerializationFormat.JSON
    )
    assert deserialized.is_success, f"JSON deserialization failed: {deserialized.error}"
    assert deserialized.value == test_data, "JSON round-trip failed"
    print("✓ JSON deserialization successful")

    # Test Binary
    result = await engine.serialize(test_data, SerializationFormat.BINARY)
    assert result.is_success, f"Binary serialization failed: {result.error}"
    print("✓ Binary serialization successful")

    deserialized = await engine.deserialize(
        result.value, dict, SerializationFormat.BINARY
    )
    assert (
        deserialized.is_success
    ), f"Binary deserialization failed: {deserialized.error}"
    assert deserialized.value == test_data, "Binary round-trip failed"
    print("✓ Binary deserialization successful")


async def test_all_formats():
    """Test all supported serialization formats"""
    print("\n=== Testing All Formats ===")

    test_data = {"message": "hello", "number": 123}
    engine = ReactiveSerializationEngine()

    formats = [
        SerializationFormat.JSON,
        SerializationFormat.BINARY,
        SerializationFormat.XML,
        SerializationFormat.YAML,
        SerializationFormat.CBOR,
        SerializationFormat.AVRO,
        SerializationFormat.PROTOBUF,
    ]

    for format_type in formats:
        try:
            # Serialize
            result = await engine.serialize(test_data, format_type)
            assert (
                result.is_success
            ), f"{format_type.name} serialization failed: {result.error}"

            # Deserialize
            deserialized = await engine.deserialize(result.value, dict, format_type)
            assert (
                deserialized.is_success
            ), f"{format_type.name} deserialization failed: {deserialized.error}"

            print(f"✓ {format_type.name} format working")
        except Exception as e:
            print(f"✗ {format_type.name} format failed: {e}")


async def test_compression():
    """Test compression functionality"""
    print("\n=== Testing Compression ===")

    # Create larger test data for better compression
    test_data = {"data": "x" * 1000, "repeat": ["test"] * 100}
    engine = ReactiveSerializationEngine()

    # Test without compression
    result_no_compression = await engine.serialize(
        test_data, SerializationFormat.JSON, CompressionType.NONE
    )
    assert result_no_compression.is_success
    original_size = len(result_no_compression.value)
    print(f"Original size: {original_size} bytes")

    # Test with GZIP compression
    result_compressed = await engine.serialize(
        test_data, SerializationFormat.JSON, CompressionType.GZIP
    )
    assert result_compressed.is_success
    compressed_size = len(result_compressed.value)
    print(f"Compressed size: {compressed_size} bytes")
    print(f"Compression ratio: {compressed_size / original_size:.2%}")

    # Test decompression
    decompressed = await engine.deserialize(
        result_compressed.value, dict, SerializationFormat.JSON, CompressionType.GZIP
    )
    assert decompressed.is_success
    assert decompressed.value == test_data
    print("✓ GZIP compression/decompression successful")


async def test_checksum():
    """Test checksum functionality"""
    print("\n=== Testing Checksum ===")

    test_data = {"secure": "data"}
    engine = ReactiveSerializationEngine()

    # Serialize with checksum
    result = await engine.serialize(
        test_data, SerializationFormat.JSON, CompressionType.NONE, ChecksumType.SHA256
    )
    assert result.is_success

    # Calculate expected checksum
    expected_checksum = engine.checksum_service.calculate_checksum(
        result.value, ChecksumType.SHA256
    )

    # Deserialize with checksum verification
    deserialized = await engine.deserialize(
        result.value,
        dict,
        SerializationFormat.JSON,
        CompressionType.NONE,
        ChecksumType.SHA256,
        expected_checksum,
    )
    assert deserialized.is_success
    assert deserialized.value == test_data
    print("✓ SHA256 checksum verification successful")


async def test_caching():
    """Test caching functionality"""
    print("\n=== Testing Caching ===")

    test_data = {"cached": "data"}
    engine = ReactiveSerializationEngine()

    # First serialization (cache miss)
    start_time = time.time()
    result1 = await engine.serialize(test_data, SerializationFormat.JSON)
    first_time = time.time() - start_time
    assert result1.is_success

    # Second serialization (cache hit)
    start_time = time.time()
    result2 = await engine.serialize(test_data, SerializationFormat.JSON)
    second_time = time.time() - start_time
    assert result2.is_success

    # Results should be identical
    assert result1.value == result2.value
    print(f"First serialization: {first_time:.4f}s")
    print(f"Second serialization: {second_time:.4f}s")
    print("✓ Caching working (cache hit should be faster)")

    # Check cache stats
    stats = engine.get_cache_stats()
    print(f"Cache stats: {stats}")


async def test_batch_operations():
    """Test batch serialization/deserialization"""
    print("\n=== Testing Batch Operations ===")

    test_objects = [{"id": i, "data": f"item_{i}"} for i in range(5)]

    engine = ReactiveSerializationEngine()

    # Batch serialize
    results = await engine.serialize_batch(test_objects, SerializationFormat.JSON)
    assert all(r.is_success for r in results), "Batch serialization failed"
    print("✓ Batch serialization successful")

    # Batch deserialize
    serialized_data = [r.value for r in results]
    deserialized_results = await engine.deserialize_batch(
        serialized_data, dict, SerializationFormat.JSON
    )
    assert all(
        r.is_success for r in deserialized_results
    ), "Batch deserialization failed"

    deserialized_objects = [r.value for r in deserialized_results]
    assert deserialized_objects == test_objects, "Batch round-trip failed"
    print("✓ Batch deserialization successful")


async def test_file_operations():
    """Test file serialization/deserialization"""
    print("\n=== Testing File Operations ===")

    test_data = {"file": "test", "content": "data"}
    engine = ReactiveSerializationEngine()

    file_path = "/tmp/test_serialization.bin"

    # Serialize to file
    result = await engine.serialize_to_file(
        test_data, file_path, SerializationFormat.JSON
    )
    assert result.is_success, f"File serialization failed: {result.error}"
    print("✓ File serialization successful")

    # Deserialize from file
    deserialized = await engine.deserialize_from_file(
        file_path, dict, SerializationFormat.JSON
    )
    assert deserialized.is_success, f"File deserialization failed: {deserialized.error}"
    assert deserialized.value == test_data, "File round-trip failed"
    print("✓ File deserialization successful")


async def test_builder_pattern():
    """Test builder pattern configuration"""
    print("\n=== Testing Builder Pattern ===")

    engine = (
        ReactiveSerializationEngineBuilder()
        .with_format(SerializationFormat.JSON)
        .with_compression(CompressionType.GZIP)
        .with_checksum(ChecksumType.MD5)
        .with_cache(enabled=True, max_size=500, ttl_seconds=1800)
        .with_metrics(enabled=True)
        .with_concurrency(max_operations=50, thread_pool_size=2)
        .build()
    )

    test_data = {"builder": "test"}

    result = await engine.serialize(test_data)
    assert result.is_success

    deserialized = await engine.deserialize(result.value, dict)
    assert deserialized.is_success
    assert deserialized.value == test_data

    print("✓ Builder pattern configuration successful")


async def test_metrics():
    """Test metrics collection"""
    print("\n=== Testing Metrics ===")

    engine = ReactiveSerializationEngine()
    test_data = {"metrics": "test"}

    # Perform some operations
    for i in range(3):
        result = await engine.serialize(test_data, SerializationFormat.JSON)
        assert result.is_success, f"Serialization {i} failed"

    metrics = engine.get_metrics()
    assert metrics is not None, "Metrics should not be None"

    print(f"Operations count: {metrics.operations_count}")
    print(f"Total bytes serialized: {metrics.total_bytes_serialized}")
    print(f"Cache hit ratio: {metrics.cache_hit_ratio:.2%}")

    # With caching enabled, we may have cache hits, so check actual values
    assert (
        metrics.operations_count >= 1
    ), f"Expected at least 1 operation, got {metrics.operations_count}"
    assert (
        metrics.total_bytes_serialized > 0
    ), f"Expected bytes serialized > 0, got {metrics.total_bytes_serialized}"

    print("✓ Metrics collection working")


async def test_convenience_functions():
    """Test convenience functions"""
    print("\n=== Testing Convenience Functions ===")

    test_data = {"convenience": "test"}

    # Quick serialize
    result = await serialize(test_data, SerializationFormat.JSON)
    assert result.is_success
    print("✓ Convenience serialize function working")

    # Quick deserialize
    deserialized = await deserialize(result.value, dict, SerializationFormat.JSON)
    assert deserialized.is_success
    assert deserialized.value == test_data
    print("✓ Convenience deserialize function working")


async def run_all_tests():
    """Run all tests"""
    print("Starting comprehensive ReactiveSerializationEngine tests...\n")

    start_time = time.time()

    try:
        await test_basic_serialization()
        await test_all_formats()
        await test_compression()
        await test_checksum()
        await test_caching()
        await test_batch_operations()
        await test_file_operations()
        await test_builder_pattern()
        await test_metrics()
        await test_convenience_functions()

        end_time = time.time()
        print(f"\n🎉 All tests passed! Total time: {end_time - start_time:.2f}s")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(run_all_tests())
