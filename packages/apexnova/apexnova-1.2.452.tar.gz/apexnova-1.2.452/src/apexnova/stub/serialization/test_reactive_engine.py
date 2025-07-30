#!/usr/bin/env python3
"""
Test script for ReactiveSerializationEngine
"""
import asyncio
import sys
from pathlib import Path

# Add the src directory to the path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from apexnova.stub.serialization.reactive_serialization_engine import (
    ReactiveSerializationEngine,
    SerializationFormat,
    ReactiveSerializationEngineBuilder,
)
from apexnova.stub.serialization.compression_service import CompressionType
from apexnova.stub.serialization.checksum_service import ChecksumType


async def test_basic_serialization():
    """Test basic serialization functionality"""
    print("Testing ReactiveSerializationEngine...")

    # Create engine with default settings
    engine = ReactiveSerializationEngine()

    # Test data
    test_data = {
        "name": "ApexNova",
        "version": "1.0.0",
        "features": ["reactive", "modern", "fast"],
        "active": True,
        "count": 42,
    }

    print(f"Original data: {test_data}")

    # Test JSON serialization
    print("\n1. Testing JSON serialization...")
    result = await engine.serialize(test_data, SerializationFormat.JSON)
    if result.is_success:
        print(f"✓ JSON serialization successful: {len(result.value)} bytes")

        # Test deserialization
        deserialize_result = await engine.deserialize(
            result.value, dict, SerializationFormat.JSON
        )
        if deserialize_result.is_success:
            print(f"✓ JSON deserialization successful: {deserialize_result.value}")
        else:
            print(f"✗ JSON deserialization failed: {deserialize_result.error}")
    else:
        print(f"✗ JSON serialization failed: {result.error}")

    # Test Binary serialization
    print("\n2. Testing Binary serialization...")
    result = await engine.serialize(test_data, SerializationFormat.BINARY)
    if result.is_success:
        print(f"✓ Binary serialization successful: {len(result.value)} bytes")

        # Test deserialization
        deserialize_result = await engine.deserialize(
            result.value, dict, SerializationFormat.BINARY
        )
        if deserialize_result.is_success:
            print(f"✓ Binary deserialization successful: {deserialize_result.value}")
        else:
            print(f"✗ Binary deserialization failed: {deserialize_result.error}")
    else:
        print(f"✗ Binary serialization failed: {result.error}")

    # Test XML serialization
    print("\n3. Testing XML serialization...")
    result = await engine.serialize(test_data, SerializationFormat.XML)
    if result.is_success:
        xml_str = result.value.decode("utf-8")
        print(f"✓ XML serialization successful:\n{xml_str}")

        # Test deserialization
        deserialize_result = await engine.deserialize(
            result.value, dict, SerializationFormat.XML
        )
        if deserialize_result.is_success:
            print(f"✓ XML deserialization successful")
        else:
            print(f"✗ XML deserialization failed: {deserialize_result.error}")
    else:
        print(f"✗ XML serialization failed: {result.error}")

    # Test YAML serialization
    print("\n4. Testing YAML serialization...")
    result = await engine.serialize(test_data, SerializationFormat.YAML)
    if result.is_success:
        yaml_str = result.value.decode("utf-8")
        print(f"✓ YAML serialization successful:\n{yaml_str}")
    else:
        print(f"✗ YAML serialization failed: {result.error}")

    await engine.close()
    print("\n✓ All tests completed!")


async def test_compression_and_checksum():
    """Test compression and checksum features"""
    print("\n\nTesting compression and checksum features...")

    engine = (
        ReactiveSerializationEngineBuilder()
        .with_compression(CompressionType.GZIP)
        .with_checksum(ChecksumType.MD5)
        .with_cache(enabled=True)
        .build()
    )

    test_data = "This is a test string that should compress well when repeated. " * 50

    print(f"Original data size: {len(test_data)} characters")

    # Serialize with compression and checksum
    result = await engine.serialize(
        test_data, SerializationFormat.JSON, CompressionType.GZIP, ChecksumType.MD5
    )

    if result.is_success:
        print(f"✓ Compressed serialization successful: {len(result.value)} bytes")

        # Deserialize
        deserialize_result = await engine.deserialize(
            result.value,
            str,
            SerializationFormat.JSON,
            CompressionType.GZIP,
            ChecksumType.MD5,
        )
        if deserialize_result.is_success:
            print(f"✓ Compressed deserialization successful")
            print(f"  Data matches: {deserialize_result.value == test_data}")
        else:
            print(f"✗ Compressed deserialization failed: {deserialize_result.error}")
    else:
        print(f"✗ Compressed serialization failed: {result.error}")

    # Test cache
    print("\nTesting cache...")
    cache_stats = engine.get_cache_stats()
    print(f"Cache stats: {cache_stats}")

    # Test metrics
    metrics = engine.get_metrics()
    if metrics:
        print(f"Operations count: {metrics.operations_count}")
        print(f"Cache hit ratio: {metrics.cache_hit_ratio:.2%}")

    await engine.close()


async def test_file_operations():
    """Test file serialization operations"""
    print("\n\nTesting file operations...")

    engine = ReactiveSerializationEngine()

    test_data = {
        "message": "Hello, ApexNova!",
        "timestamp": "2025-06-01T12:00:00Z",
        "metadata": {"source": "test", "version": "1.0"},
    }

    test_file = "/tmp/apexnova_test.json"

    # Serialize to file
    result = await engine.serialize_to_file(
        test_data, test_file, SerializationFormat.JSON
    )
    if result.is_success:
        print(f"✓ File serialization successful: {result.value}")

        # Deserialize from file
        deserialize_result = await engine.deserialize_from_file(
            test_file, dict, SerializationFormat.JSON
        )
        if deserialize_result.is_success:
            print(f"✓ File deserialization successful: {deserialize_result.value}")
        else:
            print(f"✗ File deserialization failed: {deserialize_result.error}")
    else:
        print(f"✗ File serialization failed: {result.error}")

    await engine.close()


async def main():
    """Run all tests"""
    try:
        await test_basic_serialization()
        await test_compression_and_checksum()
        await test_file_operations()
        print("\n🎉 All tests completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
