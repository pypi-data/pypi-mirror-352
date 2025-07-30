#!/usr/bin/env python3
"""Direct test for ReactiveSerializationEngine"""
import asyncio
import sys
import os


async def main():
    try:
        # Direct import since we're in the same directory
        from reactive_serialization_engine import (
            ReactiveSerializationEngine,
            SerializationFormat,
            SerializationConfig,
        )

        print("ReactiveSerializationEngine imported successfully!")

        # Create engine
        engine = ReactiveSerializationEngine()
        print("Engine created successfully!")

        # Test simple serialization
        test_data = {"hello": "world", "number": 42, "list": [1, 2, 3]}
        print(f"Test data: {test_data}")

        formats_to_test = [
            SerializationFormat.JSON,
            SerializationFormat.BINARY,
            SerializationFormat.XML,
            SerializationFormat.YAML,
        ]

        for format_type in formats_to_test:
            print(f"\n--- Testing {format_type.name} ---")

            # Serialize
            result = await engine.serialize(test_data, format_type)
            if result.is_success:
                print(
                    f"✓ {format_type.name} serialization successful: {len(result.value)} bytes"
                )

                # Deserialize
                deserialize_result = await engine.deserialize(
                    result.value, dict, format_type
                )
                if deserialize_result.is_success:
                    print(
                        f"✓ {format_type.name} deserialization successful: {deserialize_result.value}"
                    )
                    matches = deserialize_result.value == test_data
                    print(f"  Data matches: {matches}")
                    if not matches:
                        print(f"  Original: {test_data}")
                        print(f"  Restored: {deserialize_result.value}")
                else:
                    print(
                        f"✗ {format_type.name} deserialization failed: {deserialize_result.error}"
                    )
            else:
                print(f"✗ {format_type.name} serialization failed: {result.error}")

        # Test metrics
        metrics = engine.get_metrics()
        print(f"\n--- Metrics ---")
        print(f"Total operations: {metrics.total_operations}")
        print(f"Successful operations: {metrics.successful_operations}")
        print(f"Failed operations: {metrics.failed_operations}")
        print(f"Cache hits: {metrics.cache_hits}")
        print(f"Cache misses: {metrics.cache_misses}")

        await engine.close()
        print("\n✓ Test completed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
