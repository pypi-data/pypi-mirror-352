#!/usr/bin/env python3
"""Minimal test for imports"""

try:
    print("Testing imports...")

    # Test individual imports
    import asyncio

    print("✓ asyncio imported")

    import json

    print("✓ json imported")

    import pickle

    print("✓ pickle imported")

    from typing import Any, Dict, List, Optional, Union, TypeVar, Generic

    print("✓ typing imports work")

    from enum import Enum

    print("✓ enum imported")

    # Test custom imports
    try:
        from compression_service import CompressionService, CompressionType

        print("✓ compression_service imported")
    except ImportError as e:
        print(f"⚠ compression_service import failed: {e}")

    try:
        from checksum_service import ChecksumService, ChecksumType

        print("✓ checksum_service imported")
    except ImportError as e:
        print(f"⚠ checksum_service import failed: {e}")

    # Test the main module
    try:
        from reactive_serialization_engine import SerializationFormat

        print("✓ SerializationFormat imported successfully")
    except Exception as e:
        print(f"❌ reactive_serialization_engine import failed: {e}")
        import traceback

        traceback.print_exc()

    print("Import test completed!")

except Exception as e:
    print(f"❌ General error: {e}")
    import traceback

    traceback.print_exc()
