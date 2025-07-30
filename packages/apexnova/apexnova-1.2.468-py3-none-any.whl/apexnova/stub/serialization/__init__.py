"""
ApexNova Serialization Module

Provides reactive serialization capabilities with multiple format support,
compression, checksums, caching, and streaming operations.
"""

from .reactive_serialization_engine import (
    ReactiveSerializationEngine,
    ReactiveSerializationEngineBuilder,
    SerializationFormat,
    SerializationError,
    FormatNotSupportedError,
    CompressionError,
    ChecksumError,
    CacheError,
    SerializationResult,
    SerializationMetrics,
    SerializationConfig,
    CacheEntry,
    get_default_engine,
    serialize,
    deserialize,
)

from .compression_service import (
    CompressionService,
    CompressionType,
)

from .checksum_service import (
    ChecksumService,
    ChecksumType,
)

__all__ = [
    # Main engine and builder
    "ReactiveSerializationEngine",
    "ReactiveSerializationEngineBuilder",
    # Enums
    "SerializationFormat",
    "CompressionType",
    "ChecksumType",
    # Error types
    "SerializationError",
    "FormatNotSupportedError",
    "CompressionError",
    "ChecksumError",
    "CacheError",
    # Data types
    "SerializationResult",
    "SerializationMetrics",
    "SerializationConfig",
    "CacheEntry",
    # Services
    "CompressionService",
    "ChecksumService",
    # Convenience functions
    "get_default_engine",
    "serialize",
    "deserialize",
]
