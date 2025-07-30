#!/usr/bin/env python3
"""Simple test for ReactiveSerializationEngine"""
import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))


async def main():
    try:
        from apexnova.stub.serialization.reactive_serialization_engine import (
            ReactiveSerializationEngine,
            SerializationFormat,
        )

        print("ReactiveSerializationEngine imported successfully!")

        # Create engine
        engine = ReactiveSerializationEngine()
        print("Engine created successfully!")

        # Test simple serialization
        test_data = {"hello": "world", "number": 42}
        print(f"Test data: {test_data}")

        # JSON serialization
        result = await engine.serialize(test_data, SerializationFormat.JSON)
        if result.is_success:
            print(f"✓ JSON serialization successful: {len(result.value)} bytes")
            print(f"  Content: {result.value.decode('utf-8')}")

            # Deserialize
            deserialize_result = await engine.deserialize(
                result.value, dict, SerializationFormat.JSON
            )
            if deserialize_result.is_success:
                print(f"✓ JSON deserialization successful: {deserialize_result.value}")
                print(f"  Data matches: {deserialize_result.value == test_data}")
            else:
                print(f"✗ JSON deserialization failed: {deserialize_result.error}")
        else:
            print(f"✗ JSON serialization failed: {result.error}")

        await engine.close()
        print("✓ Test completed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
