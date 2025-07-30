#!/usr/bin/env python3
"""
Simple demo of ReactiveSerializationEngine streaming features
"""

import asyncio
from typing import AsyncIterator
from datetime import datetime

from reactive_serialization_engine import (
    ReactiveSerializationEngine,
    SerializationFormat,
)


async def simple_streaming_demo():
    """Simple streaming demo"""
    print("=== Simple Streaming Demo ===")

    engine = ReactiveSerializationEngine()

    # Create test data
    test_data = [{"id": i, "timestamp": datetime.now().isoformat()} for i in range(3)]

    print("📤 Serializing items...")
    for i, item in enumerate(test_data):
        result = await engine.serialize(item, SerializationFormat.JSON)
        if result.is_success:
            print(f"   Item {i}: {len(result.value)} bytes")
        else:
            print(f"   Error: {result.error}")

    # Test metrics
    metrics = engine.get_metrics()
    if metrics:
        print(f"📊 Total operations: {metrics.operations_count}")
        print(f"📊 Total bytes: {metrics.total_bytes_serialized}")

    await engine.close()
    print("✓ Demo completed")


if __name__ == "__main__":
    asyncio.run(simple_streaming_demo())
