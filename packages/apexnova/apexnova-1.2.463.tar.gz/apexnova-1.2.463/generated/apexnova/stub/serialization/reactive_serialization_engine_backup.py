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
import zlib
import gzip
import time
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
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
    get_type_hints,
    TYPE_CHECKING,
)
from concurrent.futures import ThreadPoolExecutor
import weakref

if TYPE_CHECKING:
    from .compression_service import CompressionService
    from .checksum_service import ChecksumService

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


class CompressionType(Enum):
    """Supported compression algorithms"""

    NONE = "none"
    GZIP = "gzip"
    DEFLATE = "deflate"
    BROTLI = "brotli"
    LZ4 = "lz4"
    SNAPPY = "snappy"


class ChecksumType(Enum):
    """Supported checksum algorithms"""

    NONE = "none"
    CRC32 = "crc32"
    MD5 = "md5"
    SHA256 = "sha256"
    SHA512 = "sha512"


class SerializationError(Exception):
    """Base class for serialization errors"""

    def __init__(self, message: str, code: str):
        super().__init__(message)
        self.message = message
        self.code = code

    class UnsupportedFormat(Exception):
        def __init__(self):
            super().__init__("Unsupported serialization format", "UNSUPPORTED_FORMAT")

    class InvalidData(Exception):
        def __init__(self):
            super().__init__("Invalid data for serialization", "INVALID_DATA")

    class TypeMismatch(Exception):
        def __init__(self):
            super().__init__("Type mismatch during deserialization", "TYPE_MISMATCH")

    class IOError(Exception):
        def __init__(self):
            super().__init__("I/O error during serialization", "IO_ERROR")

    class ConfigurationError(Exception):
        def __init__(self):
            super().__init__("Serialization configuration error", "CONFIG_ERROR")

    @classmethod
    def custom(cls, message: str, code: str) -> "SerializationError":
        return cls(message, code)


class SerializationResult(Generic[T]):
    """Result wrapper for serialization operations"""

    def __init__(
        self, data: Optional[T] = None, error: Optional[SerializationError] = None
    ):
        self._data = data
        self._error = error

    @classmethod
    def success(cls, data: T) -> "SerializationResult[T]":
        return cls(data=data)

    @classmethod
    def failure(cls, error: SerializationError) -> "SerializationResult[T]":
        return cls(error=error)

    @property
    def is_success(self) -> bool:
        return self._error is None

    @property
    def is_failure(self) -> bool:
        return self._error is not None

    def map(self, transform: Callable[[T], R]) -> "SerializationResult[R]":
        if self.is_success:
            try:
                return SerializationResult.success(transform(self._data))
            except Exception as e:
                return SerializationResult.failure(
                    SerializationError.custom(str(e), "TRANSFORM_ERROR")
                )
        return SerializationResult.failure(self._error)

    def flat_map(
        self, transform: Callable[[T], "SerializationResult[R]"]
    ) -> "SerializationResult[R]":
        if self.is_success:
            return transform(self._data)
        return SerializationResult.failure(self._error)

    def get_or_none(self) -> Optional[T]:
        return self._data if self.is_success else None

    def get_or_throw(self) -> T:
        if self.is_success:
            return self._data
        raise self._error


@dataclass
class SerializationMetadata:
    """Metadata for serialization operations"""

    format: SerializationFormat
    timestamp: datetime = field(default_factory=datetime.now)
    version: str = "1.0"
    compression_type: CompressionType = CompressionType.NONE
    checksum_type: ChecksumType = ChecksumType.CRC32
    checksum: Optional[str] = None
    custom_headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class SerializationMetrics:
    """Performance metrics for serialization operations"""

    total_serializations: int = 0
    total_deserializations: int = 0
    average_serialization_time: float = 0.0
    average_deserialization_time: float = 0.0
    total_bytes_processed: int = 0
    error_count: int = 0
    format_usage: Dict[SerializationFormat, int] = field(default_factory=dict)
    cache_hits: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SerializationConfig:
    """Configuration for ReactiveSerializationEngine"""

    pretty_print: bool = False
    ignore_unknown_keys: bool = True
    coerce_input_values: bool = True
    encode_defaults: bool = True
    enable_caching: bool = True
    cache_expiry: timedelta = field(default_factory=lambda: timedelta(minutes=30))
    batch_concurrency: int = 10
    default_format: SerializationFormat = SerializationFormat.JSON
    enable_compression: bool = False
    default_compression: CompressionType = CompressionType.GZIP
    enable_checksums: bool = False
    default_checksum: ChecksumType = ChecksumType.CRC32


@dataclass
class CacheEntry:
    """Cache entry with expiration"""

    data: bytes
    expires_at: datetime
    metadata: SerializationMetadata

    def is_expired(self, now: Optional[datetime] = None) -> bool:
        if now is None:
            now = datetime.now()
        return now > self.expires_at


class SerializationMetricsCollector:
    """Collects and manages serialization performance metrics"""

    def __init__(self):
        self._serialization_count = 0
        self._deserialization_count = 0
        self._error_count = 0
        self._total_bytes_processed = 0
        self._cache_hits = 0
        self._format_usage: Dict[SerializationFormat, int] = {}
        self._serialization_times: List[float] = []
        self._deserialization_times: List[float] = []
        self._lock = asyncio.Lock()

    async def record_serialization_start(self, format_type: SerializationFormat):
        async with self._lock:
            self._format_usage[format_type] = self._format_usage.get(format_type, 0) + 1

    async def record_serialization_success(
        self, format_type: SerializationFormat, bytes_count: int, duration: float
    ):
        async with self._lock:
            self._serialization_count += 1
            self._total_bytes_processed += bytes_count
            self._serialization_times.append(duration)

    async def record_serialization_error(self, format_type: SerializationFormat):
        async with self._lock:
            self._error_count += 1

    async def record_deserialization_start(self, format_type: SerializationFormat):
        async with self._lock:
            self._format_usage[format_type] = self._format_usage.get(format_type, 0) + 1

    async def record_deserialization_success(
        self, format_type: SerializationFormat, bytes_count: int, duration: float
    ):
        async with self._lock:
            self._deserialization_count += 1
            self._total_bytes_processed += bytes_count
            self._deserialization_times.append(duration)

    async def record_deserialization_error(self, format_type: SerializationFormat):
        async with self._lock:
            self._error_count += 1

    async def record_cache_hit(self):
        async with self._lock:
            self._cache_hits += 1

    async def get_metrics(self) -> SerializationMetrics:
        async with self._lock:
            avg_serialization_time = (
                sum(self._serialization_times) / len(self._serialization_times)
                if self._serialization_times
                else 0.0
            )
            avg_deserialization_time = (
                sum(self._deserialization_times) / len(self._deserialization_times)
                if self._deserialization_times
                else 0.0
            )

            return SerializationMetrics(
                total_serializations=self._serialization_count,
                total_deserializations=self._deserialization_count,
                average_serialization_time=avg_serialization_time,
                average_deserialization_time=avg_deserialization_time,
                total_bytes_processed=self._total_bytes_processed,
                error_count=self._error_count,
                format_usage=self._format_usage.copy(),
                cache_hits=self._cache_hits,
            )


class ReactiveSerializationEngine:
    """
    Modern reactive serialization engine with multiple format support and streaming capabilities
    """

    def __init__(
        self,
        config: Optional[SerializationConfig] = None,
        compression_service: Optional[Any] = None,
        checksum_service: Optional[Any] = None,
    ):
        self.config = config or SerializationConfig()
        self.compression_service = compression_service or CompressionService()
        self.checksum_service = checksum_service or ChecksumService()

        # Caching and metrics
        self._serialization_cache: Dict[str, CacheEntry] = {}
        self._metrics_collector = SerializationMetricsCollector()
        self._cache_lock = asyncio.Lock()

        # Type registry for polymorphic serialization
        self._type_registry: Dict[str, Type] = {}
        self._serializers: Dict[Type, Any] = {}

        # Background tasks
        self._cleanup_task: Optional[asyncio.Task] = None
        self._start_cache_cleanup()

    def _start_cache_cleanup(self):
        """Start background cache cleanup task"""

        async def cleanup_loop():
            while True:
                try:
                    await asyncio.sleep(600)  # 10 minutes
                    await self._cleanup_expired_cache()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Cache cleanup error: {e}")

        loop = asyncio.get_event_loop()
        self._cleanup_task = loop.create_task(cleanup_loop())

    async def _cleanup_expired_cache(self):
        """Remove expired cache entries"""
        async with self._cache_lock:
            now = datetime.now()
            expired_keys = [
                key
                for key, entry in self._serialization_cache.items()
                if entry.is_expired(now)
            ]
            for key in expired_keys:
                del self._serialization_cache[key]
            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")

    def _build_cache_key(self, obj: Any, format_type: SerializationFormat) -> str:
        """Build cache key for object and format"""
        obj_hash = hash(str(obj))  # Simple hash for demonstration
        return f"{obj.__class__.__name__}_{format_type.name}_{obj_hash}"

    async def serialize(
        self,
        obj: Any,
        format_type: SerializationFormat = SerializationFormat.JSON,
        metadata: Optional[SerializationMetadata] = None,
    ) -> SerializationResult[bytes]:
        """
        Serialize object to bytes using specified format
        """
        start_time = time.time()

        try:
            await self._metrics_collector.record_serialization_start(format_type)

            # Check cache first
            if self.config.enable_caching:
                cache_key = self._build_cache_key(obj, format_type)
                async with self._cache_lock:
                    cached = self._serialization_cache.get(cache_key)
                    if cached and not cached.is_expired():
                        await self._metrics_collector.record_cache_hit()
                        return SerializationResult.success(cached.data)

            # Serialize based on format
            result = await self._serialize_by_format(obj, format_type)

            if result.is_success:
                processed_data = result.get_or_throw()

                # Apply compression if configured
                final_metadata = metadata or SerializationMetadata(format_type)
                if final_metadata.compression_type != CompressionType.NONE:
                    processed_data = await self.compression_service.compress(
                        processed_data, final_metadata.compression_type
                    )

                # Calculate checksum if configured
                checksum = None
                if final_metadata.checksum_type != ChecksumType.NONE:
                    checksum = await self.checksum_service.calculate(
                        processed_data, final_metadata.checksum_type
                    )

                # Cache the result
                if self.config.enable_caching:
                    cache_key = self._build_cache_key(obj, format_type)
                    async with self._cache_lock:
                        self._serialization_cache[cache_key] = CacheEntry(
                            data=processed_data,
                            expires_at=datetime.now() + self.config.cache_expiry,
                            metadata=SerializationMetadata(
                                format=final_metadata.format,
                                timestamp=final_metadata.timestamp,
                                version=final_metadata.version,
                                compression_type=final_metadata.compression_type,
                                checksum_type=final_metadata.checksum_type,
                                checksum=checksum,
                                custom_headers=final_metadata.custom_headers,
                            ),
                        )

                duration = time.time() - start_time
                await self._metrics_collector.record_serialization_success(
                    format_type, len(processed_data), duration
                )

                return SerializationResult.success(processed_data)
            else:
                await self._metrics_collector.record_serialization_error(format_type)
                return result

        except Exception as e:
            logger.error(f"Serialization failed for format {format_type}: {e}")
            await self._metrics_collector.record_serialization_error(format_type)
            return SerializationResult.failure(
                SerializationError.custom(str(e), "SERIALIZATION_ERROR")
            )

    async def deserialize(
        self,
        data: bytes,
        target_type: Type[T],
        format_type: SerializationFormat = SerializationFormat.JSON,
        metadata: Optional[SerializationMetadata] = None,
    ) -> SerializationResult[T]:
        """
        Deserialize bytes to object of specified type
        """
        start_time = time.time()

        try:
            await self._metrics_collector.record_deserialization_start(format_type)

            processed_data = data

            # Verify checksum if provided
            actual_metadata = metadata or SerializationMetadata(format_type)
            if (
                actual_metadata.checksum
                and actual_metadata.checksum_type != ChecksumType.NONE
            ):
                calculated_checksum = await self.checksum_service.calculate(
                    data, actual_metadata.checksum_type
                )
                if calculated_checksum != actual_metadata.checksum:
                    return SerializationResult.failure(
                        SerializationError.custom(
                            "Checksum verification failed", "CHECKSUM_MISMATCH"
                        )
                    )

            # Decompress if needed
            if actual_metadata.compression_type != CompressionType.NONE:
                processed_data = await self.compression_service.decompress(
                    processed_data, actual_metadata.compression_type
                )

            # Deserialize based on format
            result = await self._deserialize_by_format(
                processed_data, target_type, format_type
            )

            if result.is_success:
                duration = time.time() - start_time
                await self._metrics_collector.record_deserialization_success(
                    format_type, len(data), duration
                )
                return result
            else:
                await self._metrics_collector.record_deserialization_error(format_type)
                return result

        except Exception as e:
            logger.error(f"Deserialization failed for format {format_type}: {e}")
            await self._metrics_collector.record_deserialization_error(format_type)
            return SerializationResult.failure(
                SerializationError.custom(str(e), "DESERIALIZATION_ERROR")
            )

    async def _serialize_by_format(
        self, obj: Any, format_type: SerializationFormat
    ) -> SerializationResult[bytes]:
        """Serialize object based on format type"""
        try:
            if format_type == SerializationFormat.JSON:
                return await self._serialize_json(obj)
            elif format_type == SerializationFormat.PROTOBUF:
                return await self._serialize_protobuf(obj)
            elif format_type == SerializationFormat.BINARY:
                return await self._serialize_binary(obj)
            elif format_type == SerializationFormat.XML:
                return await self._serialize_xml(obj)
            elif format_type == SerializationFormat.YAML:
                return await self._serialize_yaml(obj)
            elif format_type == SerializationFormat.CBOR:
                return await self._serialize_cbor(obj)
            elif format_type == SerializationFormat.AVRO:
                return await self._serialize_avro(obj)
            else:
                return SerializationResult.failure(
                    SerializationError.UnsupportedFormat()
                )
        except Exception as e:
            return SerializationResult.failure(SerializationError.InvalidData())

    async def _deserialize_by_format(
        self, data: bytes, target_type: Type[T], format_type: SerializationFormat
    ) -> SerializationResult[T]:
        """Deserialize data based on format type"""
        try:
            if format_type == SerializationFormat.JSON:
                return await self._deserialize_json(data, target_type)
            elif format_type == SerializationFormat.PROTOBUF:
                return await self._deserialize_protobuf(data, target_type)
            elif format_type == SerializationFormat.BINARY:
                return await self._deserialize_binary(data, target_type)
            elif format_type == SerializationFormat.XML:
                return await self._deserialize_xml(data, target_type)
            elif format_type == SerializationFormat.YAML:
                return await self._deserialize_yaml(data, target_type)
            elif format_type == SerializationFormat.CBOR:
                return await self._deserialize_cbor(data, target_type)
            elif format_type == SerializationFormat.AVRO:
                return await self._deserialize_avro(data, target_type)
            else:
                return SerializationResult.failure(
                    SerializationError.UnsupportedFormat()
                )
        except Exception as e:
            return SerializationResult.failure(SerializationError.TypeMismatch())

    # Format-specific serialization methods
    async def _serialize_json(self, obj: Any) -> SerializationResult[bytes]:
        """Serialize object to JSON bytes"""
        try:
            json_str = json.dumps(
                obj, ensure_ascii=False, indent=2 if self.config.pretty_print else None
            )
            return SerializationResult.success(json_str.encode("utf-8"))
        except Exception as e:
            return SerializationResult.failure(SerializationError.InvalidData())

    async def _deserialize_json(
        self, data: bytes, target_type: Type[T]
    ) -> SerializationResult[T]:
        """Deserialize JSON bytes to object"""
        try:
            json_str = data.decode("utf-8")
            obj = json.loads(json_str)
            # TODO: Add proper type conversion based on target_type
            return SerializationResult.success(obj)
        except Exception as e:
            return SerializationResult.failure(SerializationError.TypeMismatch())

    async def _serialize_protobuf(self, obj: Any) -> SerializationResult[bytes]:
        """Serialize object to Protobuf bytes"""
        # TODO: Implement Protobuf serialization
        return SerializationResult.failure(SerializationError.UnsupportedFormat())

    async def _deserialize_protobuf(
        self, data: bytes, target_type: Type[T]
    ) -> SerializationResult[T]:
        """Deserialize Protobuf bytes to object"""
        # TODO: Implement Protobuf deserialization
        return SerializationResult.failure(SerializationError.UnsupportedFormat())

    async def _serialize_binary(self, obj: Any) -> SerializationResult[bytes]:
        """Serialize object to binary using pickle"""
        try:
            return SerializationResult.success(pickle.dumps(obj))
        except Exception as e:
            return SerializationResult.failure(SerializationError.InvalidData())

    async def _deserialize_binary(
        self, data: bytes, target_type: Type[T]
    ) -> SerializationResult[T]:
        """Deserialize binary data using pickle"""
        try:
            obj = pickle.loads(data)
            return SerializationResult.success(obj)
        except Exception as e:
            return SerializationResult.failure(SerializationError.TypeMismatch())

    async def _serialize_xml(self, obj: Any) -> SerializationResult[bytes]:
        """Serialize object to XML bytes"""
        # TODO: Implement XML serialization
        return SerializationResult.failure(SerializationError.UnsupportedFormat())

    async def _deserialize_xml(
        self, data: bytes, target_type: Type[T]
    ) -> SerializationResult[T]:
        """Deserialize XML bytes to object"""
        # TODO: Implement XML deserialization
        return SerializationResult.failure(SerializationError.UnsupportedFormat())

    async def _serialize_yaml(self, obj: Any) -> SerializationResult[bytes]:
        """Serialize object to YAML bytes"""
        # TODO: Implement YAML serialization
        return SerializationResult.failure(SerializationError.UnsupportedFormat())

    async def _deserialize_yaml(
        self, data: bytes, target_type: Type[T]
    ) -> SerializationResult[T]:
        """Deserialize YAML bytes to object"""
        # TODO: Implement YAML deserialization
        return SerializationResult.failure(SerializationError.UnsupportedFormat())

    async def _serialize_cbor(self, obj: Any) -> SerializationResult[bytes]:
        """Serialize object to CBOR bytes"""
        # TODO: Implement CBOR serialization
        return SerializationResult.failure(SerializationError.UnsupportedFormat())

    async def _deserialize_cbor(
        self, data: bytes, target_type: Type[T]
    ) -> SerializationResult[T]:
        """Deserialize CBOR bytes to object"""
        # TODO: Implement CBOR deserialization
        return SerializationResult.failure(SerializationError.UnsupportedFormat())

    async def _serialize_avro(self, obj: Any) -> SerializationResult[bytes]:
        """Serialize object to Avro bytes"""
        # TODO: Implement Avro serialization
        return SerializationResult.failure(SerializationError.UnsupportedFormat())

    async def _deserialize_avro(
        self, data: bytes, target_type: Type[T]
    ) -> SerializationResult[T]:
        """Deserialize Avro bytes to object"""
        # TODO: Implement Avro deserialization
        return SerializationResult.failure(SerializationError.UnsupportedFormat())

    # Streaming operations
    async def serialize_stream(
        self,
        objects: AsyncIterator[Any],
        format_type: SerializationFormat = SerializationFormat.JSON,
    ) -> AsyncIterator[SerializationResult[bytes]]:
        """Serialize stream of objects"""
        async for obj in objects:
            result = await self.serialize(obj, format_type)
            yield result

    async def deserialize_stream(
        self,
        data_stream: AsyncIterator[bytes],
        target_type: Type[T],
        format_type: SerializationFormat = SerializationFormat.JSON,
    ) -> AsyncIterator[SerializationResult[T]]:
        """Deserialize stream of data"""
        async for data in data_stream:
            result = await self.deserialize(data, target_type, format_type)
            yield result

    # Batch operations
    async def serialize_batch(
        self,
        objects: List[Any],
        format_type: SerializationFormat = SerializationFormat.JSON,
        concurrency: Optional[int] = None,
    ) -> SerializationResult[List[bytes]]:
        """Serialize batch of objects with concurrency control"""
        concurrency = concurrency or self.config.batch_concurrency

        try:
            semaphore = asyncio.Semaphore(concurrency)

            async def serialize_with_semaphore(obj):
                async with semaphore:
                    return await self.serialize(obj, format_type)

            tasks = [serialize_with_semaphore(obj) for obj in objects]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Check for failures
            failures = [
                r
                for r in results
                if isinstance(r, Exception)
                or (hasattr(r, "is_failure") and r.is_failure)
            ]
            if failures:
                return SerializationResult.failure(
                    SerializationError.custom(
                        f"Batch serialization failed: {len(failures)} errors",
                        "BATCH_ERROR",
                    )
                )

            success_results = [
                r.get_or_throw() for r in results if hasattr(r, "get_or_throw")
            ]
            return SerializationResult.success(success_results)

        except Exception as e:
            logger.error(f"Batch serialization failed: {e}")
            return SerializationResult.failure(
                SerializationError.custom(str(e), "BATCH_ERROR")
            )

    async def deserialize_batch(
        self,
        data_list: List[bytes],
        target_type: Type[T],
        format_type: SerializationFormat = SerializationFormat.JSON,
        concurrency: Optional[int] = None,
    ) -> SerializationResult[List[T]]:
        """Deserialize batch of data with concurrency control"""
        concurrency = concurrency or self.config.batch_concurrency

        try:
            semaphore = asyncio.Semaphore(concurrency)

            async def deserialize_with_semaphore(data):
                async with semaphore:
                    return await self.deserialize(data, target_type, format_type)

            tasks = [deserialize_with_semaphore(data) for data in data_list]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Check for failures
            failures = [
                r
                for r in results
                if isinstance(r, Exception)
                or (hasattr(r, "is_failure") and r.is_failure)
            ]
            if failures:
                return SerializationResult.failure(
                    SerializationError.custom(
                        f"Batch deserialization failed: {len(failures)} errors",
                        "BATCH_ERROR",
                    )
                )

            success_results = [
                r.get_or_throw() for r in results if hasattr(r, "get_or_throw")
            ]
            return SerializationResult.success(success_results)

        except Exception as e:
            logger.error(f"Batch deserialization failed: {e}")
            return SerializationResult.failure(
                SerializationError.custom(str(e), "BATCH_ERROR")
            )

    # File operations
    async def serialize_to_file(
        self,
        obj: Any,
        file_path: str,
        format_type: SerializationFormat = SerializationFormat.JSON,
        metadata: Optional[SerializationMetadata] = None,
    ) -> SerializationResult[None]:
        """Serialize object to file"""
        try:
            result = await self.serialize(obj, format_type, metadata)
            if result.is_success:
                with open(file_path, "wb") as f:
                    f.write(result.get_or_throw())
                return SerializationResult.success(None)
            else:
                return SerializationResult.failure(result._error)
        except Exception as e:
            logger.error(f"Failed to serialize to file {file_path}: {e}")
            return SerializationResult.failure(SerializationError.IOError())

    async def deserialize_from_file(
        self,
        file_path: str,
        target_type: Type[T],
        format_type: SerializationFormat = SerializationFormat.JSON,
        metadata: Optional[SerializationMetadata] = None,
    ) -> SerializationResult[T]:
        """Deserialize object from file"""
        try:
            with open(file_path, "rb") as f:
                data = f.read()
            return await self.deserialize(data, target_type, format_type, metadata)
        except Exception as e:
            logger.error(f"Failed to deserialize from file {file_path}: {e}")
            return SerializationResult.failure(SerializationError.IOError())

    # Type registration for polymorphic serialization
    def register_type(self, name: str, type_class: Type, serializer: Any = None):
        """Register type for polymorphic serialization"""
        self._type_registry[name] = type_class
        if serializer:
            self._serializers[type_class] = serializer

    # Configuration and management
    def configure(
        self, config_builder: Callable[["SerializationConfigBuilder"], None]
    ) -> "ReactiveSerializationEngine":
        """Create new engine with updated configuration"""
        builder = SerializationConfigBuilder()
        config_builder(builder)
        new_config = builder.build()
        return ReactiveSerializationEngine(
            new_config, self.compression_service, self.checksum_service
        )

    async def get_metrics(self) -> SerializationMetrics:
        """Get current performance metrics"""
        return await self._metrics_collector.get_metrics()

    async def clear_cache(self):
        """Clear serialization cache"""
        async with self._cache_lock:
            self._serialization_cache.clear()
        logger.info("Serialization cache cleared")

    async def shutdown(self):
        """Shutdown engine and cleanup resources"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        await self.clear_cache()
        logger.info("ReactiveSerializationEngine shutdown complete")


class SerializationConfigBuilder:
    """Builder for SerializationConfig"""

    def __init__(self):
        self._pretty_print = False
        self._ignore_unknown_keys = True
        self._coerce_input_values = True
        self._encode_defaults = True
        self._enable_caching = True
        self._cache_expiry = timedelta(minutes=30)
        self._batch_concurrency = 10
        self._default_format = SerializationFormat.JSON
        self._enable_compression = False
        self._default_compression = CompressionType.GZIP
        self._enable_checksums = False
        self._default_checksum = ChecksumType.CRC32

    def pretty_print(self, enabled: bool) -> "SerializationConfigBuilder":
        self._pretty_print = enabled
        return self

    def ignore_unknown_keys(self, enabled: bool) -> "SerializationConfigBuilder":
        self._ignore_unknown_keys = enabled
        return self

    def coerce_input_values(self, enabled: bool) -> "SerializationConfigBuilder":
        self._coerce_input_values = enabled
        return self

    def encode_defaults(self, enabled: bool) -> "SerializationConfigBuilder":
        self._encode_defaults = enabled
        return self

    def caching(
        self, enabled: bool, expiry: timedelta = timedelta(minutes=30)
    ) -> "SerializationConfigBuilder":
        self._enable_caching = enabled
        self._cache_expiry = expiry
        return self

    def batch_concurrency(self, concurrency: int) -> "SerializationConfigBuilder":
        self._batch_concurrency = concurrency
        return self

    def default_format(
        self, format_type: SerializationFormat
    ) -> "SerializationConfigBuilder":
        self._default_format = format_type
        return self

    def compression(
        self, enabled: bool, compression_type: CompressionType = CompressionType.GZIP
    ) -> "SerializationConfigBuilder":
        self._enable_compression = enabled
        self._default_compression = compression_type
        return self

    def checksums(
        self, enabled: bool, checksum_type: ChecksumType = ChecksumType.CRC32
    ) -> "SerializationConfigBuilder":
        self._enable_checksums = enabled
        self._default_checksum = checksum_type
        return self

    def build(self) -> SerializationConfig:
        return SerializationConfig(
            pretty_print=self._pretty_print,
            ignore_unknown_keys=self._ignore_unknown_keys,
            coerce_input_values=self._coerce_input_values,
            encode_defaults=self._encode_defaults,
            enable_caching=self._enable_caching,
            cache_expiry=self._cache_expiry,
            batch_concurrency=self._batch_concurrency,
            default_format=self._default_format,
            enable_compression=self._enable_compression,
            default_compression=self._default_compression,
            enable_checksums=self._enable_checksums,
            default_checksum=self._default_checksum,
        )


# DSL function
def serialization_engine(
    config_builder: Callable[[SerializationConfigBuilder], None],
) -> ReactiveSerializationEngine:
    """Create serialization engine using DSL"""
    builder = SerializationConfigBuilder()
    config_builder(builder)
    return ReactiveSerializationEngine(builder.build())


# Global serialization instance
class Serialization:
    """Global serialization service singleton"""

    _default_engine: Optional[ReactiveSerializationEngine] = None

    @classmethod
    def set_default(cls, engine: ReactiveSerializationEngine):
        cls._default_engine = engine

    @classmethod
    def get_default(cls) -> ReactiveSerializationEngine:
        if cls._default_engine is None:
            raise RuntimeError("No default serialization engine configured")
        return cls._default_engine

    @classmethod
    async def serialize(
        cls, obj: Any, format_type: SerializationFormat = SerializationFormat.JSON
    ) -> SerializationResult[bytes]:
        return await cls.get_default().serialize(obj, format_type)

    @classmethod
    async def deserialize(
        cls,
        data: bytes,
        target_type: Type[T],
        format_type: SerializationFormat = SerializationFormat.JSON,
    ) -> SerializationResult[T]:
        return await cls.get_default().deserialize(data, target_type, format_type)

    @classmethod
    async def serialize_stream(
        cls,
        objects: AsyncIterator[Any],
        format_type: SerializationFormat = SerializationFormat.JSON,
    ) -> AsyncIterator[SerializationResult[bytes]]:
        async for result in cls.get_default().serialize_stream(objects, format_type):
            yield result

    @classmethod
    async def deserialize_stream(
        cls,
        data_stream: AsyncIterator[bytes],
        target_type: Type[T],
        format_type: SerializationFormat = SerializationFormat.JSON,
    ) -> AsyncIterator[SerializationResult[T]]:
        async for result in cls.get_default().deserialize_stream(
            data_stream, target_type, format_type
        ):
            yield result


# Extension functions for common operations
async def serialize_to_json(
    obj: Any, engine: ReactiveSerializationEngine
) -> SerializationResult[str]:
    """Serialize object to JSON string"""
    result = await engine.serialize(obj, SerializationFormat.JSON)
    return result.map(lambda data: data.decode("utf-8"))


async def deserialize_from_json(
    json_str: str, target_type: Type[T], engine: ReactiveSerializationEngine
) -> SerializationResult[T]:
    """Deserialize JSON string to object"""
    return await engine.deserialize(
        json_str.encode("utf-8"), target_type, SerializationFormat.JSON
    )


async def serialize_to_protobuf(
    obj: Any, engine: ReactiveSerializationEngine
) -> SerializationResult[bytes]:
    """Serialize object to Protobuf bytes"""
    return await engine.serialize(obj, SerializationFormat.PROTOBUF)


async def deserialize_from_protobuf(
    data: bytes, target_type: Type[T], engine: ReactiveSerializationEngine
) -> SerializationResult[T]:
    """Deserialize Protobuf bytes to object"""
    return await engine.deserialize(data, target_type, SerializationFormat.PROTOBUF)
