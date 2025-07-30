"""
ReactiveSerializationEngine - Modern reactive serialization with multiple format support

This module provides a comprehensive reactive serialization engine with support for:
- Multiple formats: JSON, Protobuf, Binary, XML, YAML, CBOR, Avro
- Streaming operations with async/await
- Caching with TTL expiration
- Compression and checksum verification
- Performance metrics and monitoring
- Type safety and comprehensive error handling
"""

import asyncio
import json
import pickle
import hashlib
import time
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Union,
    TypeVar,
    Generic,
    AsyncIterator,
    Callable,
    Type,
)
from concurrent.futures import ThreadPoolExecutor

try:
    from .compression_service import CompressionService, CompressionType
    from .checksum_service import ChecksumService, ChecksumType
except ImportError:
    # Fallback for direct execution
    from compression_service import CompressionService, CompressionType
    from checksum_service import ChecksumService, ChecksumType

# Type variables
T = TypeVar("T")
R = TypeVar("R")

# Setup logging
logger = logging.getLogger(__name__)


class SerializationFormat(Enum):
    """Supported serialization formats with MIME types"""

    JSON = ("json", "application/json")
    PROTOBUF = ("proto", "application/x-protobuf")
    BINARY = ("bin", "application/octet-stream")
    XML = ("xml", "application/xml")
    YAML = ("yaml", "application/yaml")
    CBOR = ("cbor", "application/cbor")
    AVRO = ("avro", "application/avro")

    def __init__(self, extension: str, mime_type: str):
        self.extension = extension
        self.mime_type = mime_type


class SerializationError(Exception):
    """Base exception for serialization errors"""

    def __init__(
        self,
        message: str,
        format_type: Optional[SerializationFormat] = None,
        original_error: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.format_type = format_type
        self.original_error = original_error
        self.timestamp = datetime.now()


class FormatNotSupportedError(SerializationError):
    """Raised when a format is not supported"""

    pass


class CompressionError(SerializationError):
    """Raised when compression/decompression fails"""

    pass


class ChecksumError(SerializationError):
    """Raised when checksum verification fails"""

    pass


class CacheError(SerializationError):
    """Raised when cache operations fail"""

    pass


class SerializationResult(Generic[T]):
    """
    Monadic wrapper for serialization results with comprehensive error handling
    """

    def __init__(
        self, value: Optional[T] = None, error: Optional[SerializationError] = None
    ):
        if value is not None and error is not None:
            raise ValueError("SerializationResult cannot have both value and error")
        if value is None and error is None:
            raise ValueError("SerializationResult must have either value or error")

        self._value = value
        self._error = error

    @classmethod
    def success(cls, value: T) -> "SerializationResult[T]":
        """Create a successful result"""
        return cls(value=value)

    @classmethod
    def failure(cls, error: SerializationError) -> "SerializationResult[Any]":
        """Create a failed result"""
        return cls(error=error)

    @property
    def is_success(self) -> bool:
        """Check if result is successful"""
        return self._error is None

    @property
    def is_failure(self) -> bool:
        """Check if result is a failure"""
        return self._error is not None

    @property
    def value(self) -> T:
        """Get the value or raise error"""
        if self._error is not None:
            raise self._error
        if self._value is None:
            raise ValueError("SerializationResult has no value")
        return self._value

    @property
    def error(self) -> Optional[SerializationError]:
        """Get the error if any"""
        return self._error

    def map(self, func: Callable[[T], R]) -> "SerializationResult[R]":
        """Transform the value if successful"""
        if self.is_failure:
            return SerializationResult.failure(self._error)  # type: ignore
        try:
            if self._value is None:
                raise ValueError("Cannot map on None value")
            return SerializationResult.success(func(self._value))
        except Exception as e:
            return SerializationResult.failure(
                SerializationError(f"Map operation failed: {str(e)}", original_error=e)
            )

    def flat_map(
        self, func: Callable[[T], "SerializationResult[R]"]
    ) -> "SerializationResult[R]":
        """Flatmap operation for chaining results"""
        if self.is_failure:
            return SerializationResult.failure(self._error)  # type: ignore
        try:
            if self._value is None:
                raise ValueError("Cannot flatmap on None value")
            return func(self._value)
        except Exception as e:
            return SerializationResult.failure(
                SerializationError(
                    f"FlatMap operation failed: {str(e)}", original_error=e
                )
            )

    def or_else(self, default: T) -> T:
        """Get value or default"""
        if self.is_success and self._value is not None:
            return self._value
        return default

    def __bool__(self) -> bool:
        return self.is_success


@dataclass
class SerializationMetrics:
    """Metrics for serialization operations"""

    operations_count: int = 0
    total_bytes_serialized: int = 0
    total_bytes_deserialized: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    compression_ratio: float = 0.0
    total_serialization_time: float = 0.0
    total_deserialization_time: float = 0.0
    errors_count: int = 0

    def add_serialization(
        self, bytes_count: int, time_taken: float, compression_ratio: float = 1.0
    ):
        """Add serialization metrics"""
        self.operations_count += 1
        self.total_bytes_serialized += bytes_count
        self.total_serialization_time += time_taken
        self.compression_ratio = (self.compression_ratio + compression_ratio) / 2

    def add_deserialization(self, bytes_count: int, time_taken: float):
        """Add deserialization metrics"""
        self.total_bytes_deserialized += bytes_count
        self.total_deserialization_time += time_taken

    def add_cache_hit(self):
        """Record cache hit"""
        self.cache_hits += 1

    def add_cache_miss(self):
        """Record cache miss"""
        self.cache_misses += 1

    def add_error(self):
        """Record error"""
        self.errors_count += 1

    @property
    def cache_hit_ratio(self) -> float:
        """Calculate cache hit ratio"""
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0


@dataclass
class SerializationConfig:
    """Configuration for serialization engine"""

    default_format: SerializationFormat = SerializationFormat.JSON
    compression_type: CompressionType = CompressionType.NONE
    checksum_type: ChecksumType = ChecksumType.NONE
    cache_enabled: bool = True
    cache_max_size: int = 1000
    cache_ttl_seconds: int = 3600
    enable_metrics: bool = True
    max_concurrent_operations: int = 100
    streaming_chunk_size: int = 8192
    thread_pool_size: int = 4
    type_checking_enabled: bool = True


@dataclass
class CacheEntry:
    """Cache entry with TTL"""

    data: bytes
    format_type: SerializationFormat
    created_at: datetime
    ttl_seconds: int
    compression_type: CompressionType = CompressionType.NONE
    checksum_type: ChecksumType = ChecksumType.NONE
    checksum_value: Optional[str] = None

    @property
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        return datetime.now() - self.created_at > timedelta(seconds=self.ttl_seconds)


class ReactiveSerializationEngine:
    """
    Modern reactive serialization engine with comprehensive features
    """

    def __init__(self, config: Optional[SerializationConfig] = None):
        self.config = config or SerializationConfig()
        self.metrics = SerializationMetrics() if self.config.enable_metrics else None
        self._cache: Dict[str, CacheEntry] = {}
        self._type_registry: Dict[str, Type[Any]] = {}
        self._serializers: Dict[
            SerializationFormat, Callable[[Any], Union[str, bytes]]
        ] = {}
        self._deserializers: Dict[SerializationFormat, Callable[..., Any]] = {}
        self._semaphore = asyncio.Semaphore(self.config.max_concurrent_operations)
        self._executor = ThreadPoolExecutor(max_workers=self.config.thread_pool_size)
        self._cache_cleanup_task: Optional[asyncio.Task[None]] = None

        # Initialize services
        self.compression_service = CompressionService()
        self.checksum_service = ChecksumService()

        # Register default serializers
        self._register_default_serializers()

        # Start cache cleanup if needed
        if self.config.cache_enabled:
            self._start_cache_cleanup()

    def _register_default_serializers(self):
        """Register default serializers for supported formats"""
        # JSON
        self._serializers[SerializationFormat.JSON] = json.dumps
        self._deserializers[SerializationFormat.JSON] = json.loads

        # Binary (pickle)
        self._serializers[SerializationFormat.BINARY] = pickle.dumps
        self._deserializers[SerializationFormat.BINARY] = pickle.loads

        # XML - basic implementation
        def xml_serialize(obj: Any) -> str:
            """Basic XML serialization"""
            if isinstance(obj, dict):
                xml_parts = ["<root>"]
                for key, value in obj.items():
                    xml_parts.append(f"<{key}>{value}</{key}>")
                xml_parts.append("</root>")
                return "".join(xml_parts)
            else:
                return f"<root>{obj}</root>"

        def xml_deserialize(xml_str: str) -> Any:
            """Basic XML deserialization - returns string for now"""
            # This is a simplified implementation
            # In production, use proper XML parsing library like lxml or xml.etree
            return xml_str.replace("<root>", "").replace("</root>", "").strip()

        self._serializers[SerializationFormat.XML] = xml_serialize
        self._deserializers[SerializationFormat.XML] = xml_deserialize

        # YAML - basic implementation using JSON-like format
        def yaml_serialize(obj: Any) -> str:
            """Basic YAML-like serialization"""
            if isinstance(obj, dict):
                lines = []
                for key, value in obj.items():
                    if isinstance(value, str):
                        lines.append(f"{key}: '{value}'")
                    else:
                        lines.append(f"{key}: {value}")
                return "\n".join(lines)
            else:
                return str(obj)

        def yaml_deserialize(yaml_str: str) -> Any:
            """Basic YAML-like deserialization"""
            # Simplified implementation - in production use PyYAML
            result = {}
            for line in yaml_str.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip().strip("'\"")
                    result[key] = value
            return result if result else yaml_str

        self._serializers[SerializationFormat.YAML] = yaml_serialize
        self._deserializers[SerializationFormat.YAML] = yaml_deserialize

        # CBOR - placeholder (would need cbor2 library in production)
        def cbor_serialize(obj: Any) -> bytes:
            """CBOR serialization fallback to JSON bytes"""
            logger.warning("CBOR not available, falling back to JSON")
            return json.dumps(obj).encode("utf-8")

        def cbor_deserialize(data: bytes) -> Any:
            """CBOR deserialization fallback from JSON bytes"""
            logger.warning("CBOR not available, falling back to JSON")
            return json.loads(data.decode("utf-8"))

        self._serializers[SerializationFormat.CBOR] = cbor_serialize
        self._deserializers[SerializationFormat.CBOR] = cbor_deserialize

        # Avro - placeholder (would need avro library in production)
        def avro_serialize(obj: Any) -> bytes:
            """Avro serialization fallback to JSON bytes"""
            logger.warning("Avro not available, falling back to JSON")
            return json.dumps(obj).encode("utf-8")

        def avro_deserialize(data: bytes) -> Any:
            """Avro deserialization fallback from JSON bytes"""
            logger.warning("Avro not available, falling back to JSON")
            return json.loads(data.decode("utf-8"))

        self._serializers[SerializationFormat.AVRO] = avro_serialize
        self._deserializers[SerializationFormat.AVRO] = avro_deserialize

        # Protobuf - placeholder (would need protobuf library in production)
        def protobuf_serialize(obj: Any) -> bytes:
            """Protobuf serialization fallback to binary"""
            logger.warning("Protobuf not available, falling back to pickle")
            return pickle.dumps(obj)

        def protobuf_deserialize(data: bytes) -> Any:
            """Protobuf deserialization fallback from binary"""
            logger.warning("Protobuf not available, falling back to pickle")
            return pickle.loads(data)

        self._serializers[SerializationFormat.PROTOBUF] = protobuf_serialize
        self._deserializers[SerializationFormat.PROTOBUF] = protobuf_deserialize

    def _start_cache_cleanup(self):
        """Start background cache cleanup task"""

        async def cleanup_task():
            while True:
                try:
                    await asyncio.sleep(300)  # Check every 5 minutes
                    await self._cleanup_expired_cache_entries()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Cache cleanup error: {e}")

        self._cache_cleanup_task = asyncio.create_task(cleanup_task())

    async def _cleanup_expired_cache_entries(self):
        """Remove expired cache entries"""
        expired_keys = [key for key, entry in self._cache.items() if entry.is_expired]
        for key in expired_keys:
            del self._cache[key]
        logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")

    def register_type(self, type_name: str, type_class: Type[Any]):
        """Register a type for polymorphic serialization"""
        self._type_registry[type_name] = type_class

    def register_serializer(
        self,
        format_type: SerializationFormat,
        serializer: Callable[[Any], Union[str, bytes]],
        deserializer: Callable[..., Any],
    ):
        """Register custom serializer/deserializer for a format"""
        self._serializers[format_type] = serializer
        self._deserializers[format_type] = deserializer

    def _generate_cache_key(
        self,
        obj: Any,
        format_type: SerializationFormat,
        compression: CompressionType,
        checksum: ChecksumType,
    ) -> str:
        """Generate cache key for object"""
        try:
            # Try to use object hash first
            obj_hash = hash(obj)
        except TypeError:
            # If object is not hashable, use its string representation
            obj_hash = hash(str(obj))

        obj_hash_str = hashlib.md5(str(obj_hash).encode()).hexdigest()
        return f"{obj_hash_str}_{format_type.name}_{compression.name}_{checksum.name}"

    async def serialize(
        self,
        obj: object,
        format_type: Optional[SerializationFormat] = None,
        compression: Optional[CompressionType] = None,
        checksum: Optional[ChecksumType] = None,
    ) -> SerializationResult[bytes]:
        """
        Serialize object to bytes with optional compression and checksum
        """
        format_type = format_type or self.config.default_format
        compression = compression or self.config.compression_type
        checksum = checksum or self.config.checksum_type

        async with self._semaphore:
            try:
                start_time = time.time()
                cache_key = self._generate_cache_key(
                    obj, format_type, compression, checksum
                )

                # Check cache first
                if self.config.cache_enabled:
                    cached_entry = self._cache.get(cache_key)
                    if cached_entry and not cached_entry.is_expired:
                        if self.metrics:
                            self.metrics.add_cache_hit()
                        return SerializationResult.success(cached_entry.data)
                    elif self.metrics:
                        self.metrics.add_cache_miss()

                # Serialize object
                if format_type not in self._serializers:
                    return SerializationResult.failure(
                        FormatNotSupportedError(
                            f"Format {format_type} not supported", format_type
                        )
                    )

                serializer = self._serializers[format_type]

                # Run serialization in thread pool for blocking operations
                loop = asyncio.get_event_loop()
                serialized_data = await loop.run_in_executor(
                    self._executor, serializer, obj
                )

                # Convert to bytes if needed
                if isinstance(serialized_data, str):
                    data_bytes = serialized_data.encode("utf-8")
                else:
                    data_bytes = serialized_data

                # Apply compression
                if compression != CompressionType.NONE:
                    compressed_data = self.compression_service.compress(
                        data_bytes, compression
                    )
                    data_bytes = compressed_data

                # Calculate checksum
                checksum_value = None
                if checksum != ChecksumType.NONE:
                    checksum_value = self.checksum_service.calculate_checksum(
                        data_bytes, checksum
                    )

                # Update metrics
                end_time = time.time()
                if self.metrics:
                    compression_ratio = (
                        len(data_bytes) / len(serialized_data)
                        if compression != CompressionType.NONE
                        else 1.0
                    )
                    self.metrics.add_serialization(
                        len(data_bytes), end_time - start_time, compression_ratio
                    )

                # Cache result
                if self.config.cache_enabled:
                    cache_entry = CacheEntry(
                        data=data_bytes,
                        format_type=format_type,
                        created_at=datetime.now(),
                        ttl_seconds=self.config.cache_ttl_seconds,
                        compression_type=compression,
                        checksum_type=checksum,
                        checksum_value=checksum_value,
                    )
                    self._cache[cache_key] = cache_entry

                    # Limit cache size
                    if len(self._cache) > self.config.cache_max_size:
                        # Remove oldest entry
                        oldest_key = min(
                            self._cache.keys(), key=lambda k: self._cache[k].created_at
                        )
                        del self._cache[oldest_key]

                return SerializationResult.success(data_bytes)

            except Exception as e:
                if self.metrics:
                    self.metrics.add_error()
                return SerializationResult.failure(
                    SerializationError(
                        f"Serialization failed: {str(e)}", format_type, e
                    )
                )

    async def deserialize(
        self,
        data: bytes,
        target_type: Type[T],
        format_type: Optional[SerializationFormat] = None,
        compression: Optional[CompressionType] = None,
        checksum: Optional[ChecksumType] = None,
        expected_checksum: Optional[str] = None,
    ) -> SerializationResult[T]:
        """
        Deserialize bytes to object with optional decompression and checksum verification
        """
        format_type = format_type or self.config.default_format
        compression = compression or self.config.compression_type
        checksum = checksum or self.config.checksum_type

        async with self._semaphore:
            try:
                start_time = time.time()

                # Verify checksum if provided
                if checksum != ChecksumType.NONE and expected_checksum:
                    if not self.checksum_service.verify_checksum(
                        data, checksum, expected_checksum
                    ):
                        return SerializationResult.failure(
                            ChecksumError(f"Checksum verification failed", format_type)
                        )

                # Decompress if needed
                if compression != CompressionType.NONE:
                    decompressed_data = self.compression_service.decompress(
                        data, compression
                    )
                    data = decompressed_data

                # Deserialize
                if format_type not in self._deserializers:
                    return SerializationResult.failure(
                        FormatNotSupportedError(
                            f"Format {format_type} not supported", format_type
                        )
                    )

                deserializer = self._deserializers[format_type]

                # Handle string formats
                if format_type in [
                    SerializationFormat.JSON,
                    SerializationFormat.XML,
                    SerializationFormat.YAML,
                ]:
                    data_str = data.decode("utf-8")
                    loop = asyncio.get_event_loop()
                    obj = await loop.run_in_executor(
                        self._executor, deserializer, data_str
                    )
                else:
                    loop = asyncio.get_event_loop()
                    obj = await loop.run_in_executor(self._executor, deserializer, data)

                # Type checking
                if self.config.type_checking_enabled and not isinstance(
                    obj, target_type
                ):
                    logger.warning(
                        f"Deserialized object type {type(obj)} doesn't match expected {target_type}"
                    )

                # Update metrics
                end_time = time.time()
                if self.metrics:
                    self.metrics.add_deserialization(len(data), end_time - start_time)

                return SerializationResult.success(obj)

            except Exception as e:
                if self.metrics:
                    self.metrics.add_error()
                return SerializationResult.failure(
                    SerializationError(
                        f"Deserialization failed: {str(e)}", format_type, e
                    )
                )

    async def serialize_batch(
        self,
        objects: List[T],
        format_type: Optional[SerializationFormat] = None,
        compression: Optional[CompressionType] = None,
        checksum: Optional[ChecksumType] = None,
    ) -> List[SerializationResult[bytes]]:
        """Serialize multiple objects in parallel"""
        tasks = [
            self.serialize(obj, format_type, compression, checksum) for obj in objects
        ]
        return await asyncio.gather(*tasks)

    async def deserialize_batch(
        self,
        data_list: List[bytes],
        target_type: Type[T],
        format_type: Optional[SerializationFormat] = None,
        compression: Optional[CompressionType] = None,
        checksum: Optional[ChecksumType] = None,
    ) -> List[SerializationResult[T]]:
        """Deserialize multiple byte arrays in parallel"""
        tasks = [
            self.deserialize(data, target_type, format_type, compression, checksum)
            for data in data_list
        ]
        return await asyncio.gather(*tasks)

    async def serialize_stream(
        self,
        objects: AsyncIterator[T],
        format_type: Optional[SerializationFormat] = None,
        compression: Optional[CompressionType] = None,
        checksum: Optional[ChecksumType] = None,
    ) -> AsyncIterator[SerializationResult[bytes]]:
        """Serialize objects from an async stream"""
        async for obj in objects:
            yield await self.serialize(obj, format_type, compression, checksum)

    async def deserialize_stream(
        self,
        data_stream: AsyncIterator[bytes],
        target_type: Type[T],
        format_type: Optional[SerializationFormat] = None,
        compression: Optional[CompressionType] = None,
        checksum: Optional[ChecksumType] = None,
    ) -> AsyncIterator[SerializationResult[T]]:
        """Deserialize objects from a byte stream"""
        async for data in data_stream:
            yield await self.deserialize(
                data, target_type, format_type, compression, checksum
            )

    async def serialize_to_file(
        self,
        obj: object,
        file_path: str,
        format_type: Optional[SerializationFormat] = None,
        compression: Optional[CompressionType] = None,
        checksum: Optional[ChecksumType] = None,
    ) -> SerializationResult[str]:
        """Serialize object and save to file"""
        result = await self.serialize(obj, format_type, compression, checksum)
        if result.is_failure:
            if result.error is not None:
                return SerializationResult.failure(result.error)
            else:
                return SerializationResult.failure(
                    SerializationError("Serialization failed with unknown error")
                )

        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self._executor, lambda: open(file_path, "wb").write(result.value)
            )
            return SerializationResult.success(file_path)
        except Exception as e:
            return SerializationResult.failure(
                SerializationError(
                    f"Failed to write file {file_path}: {str(e)}", original_error=e
                )
            )

    async def deserialize_from_file(
        self,
        file_path: str,
        target_type: Type[T],
        format_type: Optional[SerializationFormat] = None,
        compression: Optional[CompressionType] = None,
        checksum: Optional[ChecksumType] = None,
        expected_checksum: Optional[str] = None,
    ) -> SerializationResult[T]:
        """Load and deserialize object from file"""
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                self._executor, lambda: open(file_path, "rb").read()
            )
            return await self.deserialize(
                data, target_type, format_type, compression, checksum, expected_checksum
            )
        except Exception as e:
            return SerializationResult.failure(
                SerializationError(
                    f"Failed to read file {file_path}: {str(e)}", original_error=e
                )
            )

    def clear_cache(self):
        """Clear all cache entries"""
        self._cache.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "size": len(self._cache),
            "max_size": self.config.cache_max_size,
            "hit_ratio": self.metrics.cache_hit_ratio if self.metrics else 0.0,
        }

    def get_metrics(self) -> Optional[SerializationMetrics]:
        """Get performance metrics"""
        return self.metrics

    async def close(self):
        """Clean up resources"""
        if self._cache_cleanup_task:
            self._cache_cleanup_task.cancel()
            try:
                await self._cache_cleanup_task
            except asyncio.CancelledError:
                pass

        self._executor.shutdown(wait=True)

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ):
        # Create a new event loop if none exists for cleanup
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            # Schedule cleanup
            loop.create_task(self.close())
        else:
            # Run cleanup
            loop.run_until_complete(self.close())


class ReactiveSerializationEngineBuilder:
    """Builder pattern for creating configured ReactiveSerializationEngine instances"""

    def __init__(self):
        self.config = SerializationConfig()

    def with_format(
        self, format_type: SerializationFormat
    ) -> "ReactiveSerializationEngineBuilder":
        self.config.default_format = format_type
        return self

    def with_compression(
        self, compression_type: CompressionType
    ) -> "ReactiveSerializationEngineBuilder":
        self.config.compression_type = compression_type
        return self

    def with_checksum(
        self, checksum_type: ChecksumType
    ) -> "ReactiveSerializationEngineBuilder":
        self.config.checksum_type = checksum_type
        return self

    def with_cache(
        self, enabled: bool = True, max_size: int = 1000, ttl_seconds: int = 3600
    ) -> "ReactiveSerializationEngineBuilder":
        self.config.cache_enabled = enabled
        self.config.cache_max_size = max_size
        self.config.cache_ttl_seconds = ttl_seconds
        return self

    def with_metrics(
        self, enabled: bool = True
    ) -> "ReactiveSerializationEngineBuilder":
        self.config.enable_metrics = enabled
        return self

    def with_concurrency(
        self, max_operations: int = 100, thread_pool_size: int = 4
    ) -> "ReactiveSerializationEngineBuilder":
        self.config.max_concurrent_operations = max_operations
        self.config.thread_pool_size = thread_pool_size
        return self

    def with_streaming(
        self, chunk_size: int = 8192
    ) -> "ReactiveSerializationEngineBuilder":
        self.config.streaming_chunk_size = chunk_size
        return self

    def with_type_checking(
        self, enabled: bool = True
    ) -> "ReactiveSerializationEngineBuilder":
        self.config.type_checking_enabled = enabled
        return self

    def build(self) -> ReactiveSerializationEngine:
        return ReactiveSerializationEngine(self.config)


# Global default engine instance
_default_engine: Optional[ReactiveSerializationEngine] = None
_default_engine_lock = asyncio.Lock()


async def get_default_engine() -> ReactiveSerializationEngine:
    """Get or create the default global serialization engine"""
    global _default_engine
    if _default_engine is None:
        async with _default_engine_lock:
            if _default_engine is None:
                _default_engine = ReactiveSerializationEngine()
    return _default_engine


# Convenience functions for quick serialization
async def serialize(
    obj: object, format_type: SerializationFormat = SerializationFormat.JSON
) -> SerializationResult[bytes]:
    """Quick serialize using default engine"""
    engine = await get_default_engine()
    return await engine.serialize(obj, format_type)


async def deserialize(
    data: bytes,
    target_type: Type[T],
    format_type: SerializationFormat = SerializationFormat.JSON,
) -> SerializationResult[T]:
    """Quick deserialize using default engine"""
    engine = await get_default_engine()
    return await engine.deserialize(data, target_type, format_type)
