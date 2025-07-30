"""Reactive security utilities with async/reactive patterns for JWT and cryptographic operations."""

import asyncio
import time
import hashlib
import hmac
import base64
import json
from dataclasses import dataclass, field
from typing import (
    Dict,
    Any,
    Optional,
    List,
    Union,
    AsyncGenerator,
    Callable,
    TypeVar,
    Generic,
    Tuple,
)
import logging
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from collections import defaultdict
import secrets

# Conditional imports for graceful degradation
try:
    import jwt
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend

    _HAS_CRYPTO_LIBS = True
except ImportError:
    # Mock for graceful degradation
    jwt = None
    _HAS_CRYPTO_LIBS = False

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class CryptoMetrics:
    """Cryptographic operation metrics."""

    operation_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    average_latencies: Dict[str, float] = field(default_factory=dict)
    error_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    cache_hits: int = 0
    cache_misses: int = 0

    def record_operation(self, operation: str, latency: float, success: bool = True):
        """Record operation metrics."""
        self.operation_counts[operation] += 1
        current_avg = self.average_latencies.get(operation, 0)
        count = self.operation_counts[operation]
        self.average_latencies[operation] = (
            current_avg * (count - 1) + latency
        ) / count

        if not success:
            self.error_counts[operation] += 1


@dataclass
class CircuitBreakerState:
    """Circuit breaker state for fault tolerance."""

    failure_count: int = 0
    last_failure_time: float = 0
    state: str = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    failure_threshold: int = 5
    recovery_timeout: int = 60  # seconds
    half_open_max_calls: int = 3
    half_open_calls: int = 0


@dataclass
class CacheEntry:
    """Cache entry with TTL support."""

    data: Any
    created_at: float = field(default_factory=time.time)
    ttl: int = 300  # 5 minutes default

    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        return time.time() - self.created_at > self.ttl


@dataclass
class JWTToken:
    """JWT token container with metadata."""

    token: str
    header: Dict[str, Any]
    payload: Dict[str, Any]
    signature: str
    issued_at: float
    expires_at: Optional[float] = None

    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at

    @property
    def time_to_expiry(self) -> Optional[float]:
        """Get time to expiry in seconds."""
        if self.expires_at is None:
            return None
        return max(0, self.expires_at - time.time())


@dataclass
class EncryptedData:
    """Container for encrypted data with metadata."""

    ciphertext: bytes
    algorithm: str
    iv: Optional[bytes] = None
    tag: Optional[bytes] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ReactiveSecretUtil:
    """
    Reactive security utilities with async/reactive patterns for JWT operations,
    encryption, hashing, and cryptographic functions.
    """

    def __init__(
        self,
        default_jwt_algorithm: str = "HS256",
        default_jwt_expiry: int = 3600,  # 1 hour
        max_concurrent_operations: int = 50,
        enable_caching: bool = True,
        cache_ttl: int = 300,
        circuit_breaker_failure_threshold: int = 5,
        circuit_breaker_recovery_timeout: int = 60,
        thread_pool_size: int = 10,
    ):
        """
        Initialize reactive security utilities.

        Args:
            default_jwt_algorithm: Default JWT signing algorithm
            default_jwt_expiry: Default JWT expiry time in seconds
            max_concurrent_operations: Maximum concurrent operations
            enable_caching: Whether to enable caching
            cache_ttl: Cache TTL in seconds
            circuit_breaker_failure_threshold: Circuit breaker failure threshold
            circuit_breaker_recovery_timeout: Circuit breaker recovery timeout
            thread_pool_size: Thread pool size for blocking operations
        """
        # JWT configuration
        self._default_jwt_algorithm = default_jwt_algorithm
        self._default_jwt_expiry = default_jwt_expiry

        # Async concurrency control
        self._semaphore = asyncio.Semaphore(max_concurrent_operations)

        # Circuit breaker for fault tolerance
        self._circuit_breaker = CircuitBreakerState(
            failure_threshold=circuit_breaker_failure_threshold,
            recovery_timeout=circuit_breaker_recovery_timeout,
        )

        # Caching
        self._enable_caching = enable_caching
        self._cache_ttl = cache_ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._cache_lock = asyncio.Lock()

        # Thread pool for blocking operations
        self._thread_pool = ThreadPoolExecutor(max_workers=thread_pool_size)

        # Metrics
        self._metrics = CryptoMetrics()

        # Key storage (in production, use secure key management)
        self._secret_keys: Dict[str, str] = {}
        self._public_keys: Dict[str, Any] = {}
        self._private_keys: Dict[str, Any] = {}

        # Cleanup task for cache
        self._cleanup_task: Optional[asyncio.Task] = None
        self._start_cleanup_task()

    def _start_cleanup_task(self):
        """Start background cache cleanup task."""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_cache_periodically())

    async def _cleanup_cache_periodically(self):
        """Periodically cleanup expired cache entries."""
        while True:
            try:
                await asyncio.sleep(60)  # Cleanup every minute
                await self._cleanup_expired_cache()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"Cache cleanup error: {e}")

    async def _cleanup_expired_cache(self):
        """Remove expired cache entries."""
        async with self._cache_lock:
            expired_keys = [
                key for key, entry in self._cache.items() if entry.is_expired()
            ]
            for key in expired_keys:
                del self._cache[key]

    def _get_cache_key(self, operation: str, **kwargs) -> str:
        """Generate cache key for operation."""
        key_parts = [operation] + [f"{k}={v}" for k, v in sorted(kwargs.items())]
        return ":".join(str(part) for part in key_parts)

    async def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Get data from cache."""
        if not self._enable_caching:
            return None

        async with self._cache_lock:
            entry = self._cache.get(cache_key)
            if entry and not entry.is_expired():
                self._metrics.cache_hits += 1
                return entry.data
            elif entry:
                # Remove expired entry
                del self._cache[cache_key]

            self._metrics.cache_misses += 1
            return None

    async def _put_in_cache(self, cache_key: str, data: Any, ttl: Optional[int] = None):
        """Put data in cache."""
        if not self._enable_caching:
            return

        async with self._cache_lock:
            self._cache[cache_key] = CacheEntry(data=data, ttl=ttl or self._cache_ttl)

    async def _check_circuit_breaker(self, operation: str):
        """Check circuit breaker state."""
        current_time = time.time()

        if self._circuit_breaker.state == "OPEN":
            if (
                current_time - self._circuit_breaker.last_failure_time
                > self._circuit_breaker.recovery_timeout
            ):
                self._circuit_breaker.state = "HALF_OPEN"
                self._circuit_breaker.half_open_calls = 0
                logger.info(f"Circuit breaker half-open for operation: {operation}")
            else:
                raise RuntimeError(f"Circuit breaker open for operation: {operation}")

        elif self._circuit_breaker.state == "HALF_OPEN":
            if (
                self._circuit_breaker.half_open_calls
                >= self._circuit_breaker.half_open_max_calls
            ):
                raise RuntimeError(
                    f"Circuit breaker half-open limit exceeded: {operation}"
                )

    async def _record_success(self, operation: str, latency: float):
        """Record successful operation."""
        self._metrics.record_operation(operation, latency, success=True)

        if self._circuit_breaker.state == "HALF_OPEN":
            self._circuit_breaker.half_open_calls += 1
            if (
                self._circuit_breaker.half_open_calls
                >= self._circuit_breaker.half_open_max_calls
            ):
                self._circuit_breaker.state = "CLOSED"
                self._circuit_breaker.failure_count = 0
                logger.info(f"Circuit breaker closed for operation: {operation}")

    async def _record_failure(self, operation: str, latency: float, error: Exception):
        """Record failed operation."""
        self._metrics.record_operation(operation, latency, success=False)
        self._circuit_breaker.failure_count += 1
        self._circuit_breaker.last_failure_time = time.time()

        if (
            self._circuit_breaker.failure_count
            >= self._circuit_breaker.failure_threshold
        ):
            self._circuit_breaker.state = "OPEN"
            logger.warning(
                f"Circuit breaker opened for operation: {operation} due to: {error}"
            )

    @asynccontextmanager
    async def _with_circuit_breaker(self, operation: str):
        """Context manager for circuit breaker pattern."""
        start_time = time.time()

        try:
            await self._check_circuit_breaker(operation)
            async with self._semaphore:
                yield

            latency = time.time() - start_time
            await self._record_success(operation, latency)

        except Exception as e:
            latency = time.time() - start_time
            await self._record_failure(operation, latency, e)
            raise

    # JWT Operations

    async def generate_jwt_async(
        self,
        payload: Dict[str, Any],
        secret_key: str,
        algorithm: Optional[str] = None,
        expiry_seconds: Optional[int] = None,
        additional_headers: Optional[Dict[str, Any]] = None,
    ) -> JWTToken:
        """
        Generate a JWT token asynchronously.

        Args:
            payload: JWT payload
            secret_key: Secret key for signing
            algorithm: JWT algorithm (defaults to configured algorithm)
            expiry_seconds: Token expiry in seconds
            additional_headers: Additional headers to include

        Returns:
            JWTToken object with metadata
        """
        async with self._with_circuit_breaker("generate_jwt"):
            if not _HAS_CRYPTO_LIBS:
                raise RuntimeError("JWT library not available. Please install PyJWT.")

            algorithm = algorithm or self._default_jwt_algorithm
            expiry_seconds = expiry_seconds or self._default_jwt_expiry

            # Add standard claims
            current_time = time.time()
            payload = payload.copy()
            payload["iat"] = int(current_time)
            payload["exp"] = int(current_time + expiry_seconds)

            # Generate token in thread pool
            loop = asyncio.get_event_loop()
            token = await loop.run_in_executor(
                self._thread_pool,
                self._generate_jwt_sync,
                payload,
                secret_key,
                algorithm,
                additional_headers,
            )

            # Parse token for metadata
            header = jwt.get_unverified_header(token)
            unverified_payload = jwt.decode(token, options={"verify_signature": False})

            return JWTToken(
                token=token,
                header=header,
                payload=unverified_payload,
                signature=token.split(".")[-1],
                issued_at=current_time,
                expires_at=current_time + expiry_seconds,
            )

    def _generate_jwt_sync(
        self,
        payload: Dict[str, Any],
        secret_key: str,
        algorithm: str,
        additional_headers: Optional[Dict[str, Any]],
    ) -> str:
        """Synchronous JWT generation."""
        headers = additional_headers or {}
        return jwt.encode(payload, secret_key, algorithm=algorithm, headers=headers)

    async def verify_jwt_async(
        self,
        token: str,
        secret_key: str,
        algorithms: Optional[List[str]] = None,
        verify_expiry: bool = True,
    ) -> Dict[str, Any]:
        """
        Verify a JWT token asynchronously.

        Args:
            token: JWT token to verify
            secret_key: Secret key for verification
            algorithms: Allowed algorithms
            verify_expiry: Whether to verify expiry

        Returns:
            Decoded payload if valid

        Raises:
            jwt.InvalidTokenError: If token is invalid
        """
        cache_key = self._get_cache_key(
            "verify_jwt", token=token[:20]
        )  # Cache with token prefix

        # Try cache first (for non-expired verifications)
        if not verify_expiry:
            cached_result = await self._get_from_cache(cache_key)
            if cached_result is not None:
                return cached_result

        async with self._with_circuit_breaker("verify_jwt"):
            if not _HAS_CRYPTO_LIBS:
                raise RuntimeError("JWT library not available. Please install PyJWT.")

            algorithms = algorithms or [self._default_jwt_algorithm]

            # Verify token in thread pool
            loop = asyncio.get_event_loop()
            payload = await loop.run_in_executor(
                self._thread_pool,
                self._verify_jwt_sync,
                token,
                secret_key,
                algorithms,
                verify_expiry,
            )

            # Cache result if not verifying expiry
            if not verify_expiry:
                await self._put_in_cache(cache_key, payload, ttl=300)

            return payload

    def _verify_jwt_sync(
        self, token: str, secret_key: str, algorithms: List[str], verify_expiry: bool
    ) -> Dict[str, Any]:
        """Synchronous JWT verification."""
        options = {"verify_exp": verify_expiry}
        return jwt.decode(token, secret_key, algorithms=algorithms, options=options)

    async def decode_jwt_without_verification_async(
        self, token: str
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Decode JWT without verification asynchronously.

        Args:
            token: JWT token to decode

        Returns:
            Tuple of (header, payload)
        """
        cache_key = self._get_cache_key("decode_jwt", token=token[:20])

        # Try cache first
        cached_result = await self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result

        async with self._with_circuit_breaker("decode_jwt"):
            if not _HAS_CRYPTO_LIBS:
                raise RuntimeError("JWT library not available. Please install PyJWT.")

            # Decode in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self._thread_pool, self._decode_jwt_sync, token
            )

            # Cache result
            await self._put_in_cache(cache_key, result, ttl=600)

            return result

    def _decode_jwt_sync(self, token: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Synchronous JWT decoding."""
        header = jwt.get_unverified_header(token)
        payload = jwt.decode(token, options={"verify_signature": False})
        return header, payload

    async def refresh_jwt_async(
        self, token: str, secret_key: str, new_expiry_seconds: Optional[int] = None
    ) -> JWTToken:
        """
        Refresh a JWT token asynchronously.

        Args:
            token: Existing JWT token
            secret_key: Secret key
            new_expiry_seconds: New expiry time

        Returns:
            New JWTToken
        """
        async with self._with_circuit_breaker("refresh_jwt"):
            # Verify current token (ignore expiry)
            payload = await self.verify_jwt_async(
                token, secret_key, verify_expiry=False
            )

            # Remove old timestamps
            payload.pop("iat", None)
            payload.pop("exp", None)

            # Generate new token
            return await self.generate_jwt_async(
                payload=payload,
                secret_key=secret_key,
                expiry_seconds=new_expiry_seconds,
            )

    # Hashing Operations

    async def hash_async(
        self,
        data: Union[str, bytes],
        algorithm: str = "sha256",
        salt: Optional[Union[str, bytes]] = None,
    ) -> str:
        """
        Hash data asynchronously.

        Args:
            data: Data to hash
            algorithm: Hash algorithm
            salt: Optional salt

        Returns:
            Hexadecimal hash string
        """
        cache_key = self._get_cache_key(
            "hash",
            data_hash=hashlib.md5(str(data).encode()).hexdigest()[:10],
            algorithm=algorithm,
        )

        # Try cache first
        cached_result = await self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result

        async with self._with_circuit_breaker("hash"):
            # Hash in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self._thread_pool, self._hash_sync, data, algorithm, salt
            )

            # Cache result
            await self._put_in_cache(cache_key, result, ttl=3600)  # Long TTL for hashes

            return result

    def _hash_sync(
        self, data: Union[str, bytes], algorithm: str, salt: Optional[Union[str, bytes]]
    ) -> str:
        """Synchronous hashing."""
        if isinstance(data, str):
            data = data.encode("utf-8")

        if salt:
            if isinstance(salt, str):
                salt = salt.encode("utf-8")
            data = salt + data

        hash_obj = hashlib.new(algorithm)
        hash_obj.update(data)
        return hash_obj.hexdigest()

    async def hmac_async(
        self, data: Union[str, bytes], key: Union[str, bytes], algorithm: str = "sha256"
    ) -> str:
        """
        Generate HMAC asynchronously.

        Args:
            data: Data to authenticate
            key: Secret key
            algorithm: HMAC algorithm

        Returns:
            HMAC hexadecimal string
        """
        async with self._with_circuit_breaker("hmac"):
            # HMAC in thread pool
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                self._thread_pool, self._hmac_sync, data, key, algorithm
            )

    def _hmac_sync(
        self, data: Union[str, bytes], key: Union[str, bytes], algorithm: str
    ) -> str:
        """Synchronous HMAC generation."""
        if isinstance(data, str):
            data = data.encode("utf-8")
        if isinstance(key, str):
            key = key.encode("utf-8")

        return hmac.new(key, data, getattr(hashlib, algorithm)).hexdigest()

    # Encryption Operations (if cryptography is available)

    async def encrypt_symmetric_async(
        self, data: Union[str, bytes], key: Union[str, bytes], algorithm: str = "AES"
    ) -> EncryptedData:
        """
        Encrypt data with symmetric encryption asynchronously.

        Args:
            data: Data to encrypt
            key: Encryption key
            algorithm: Encryption algorithm

        Returns:
            EncryptedData object
        """
        async with self._with_circuit_breaker("encrypt_symmetric"):
            if not _HAS_CRYPTO_LIBS:
                # Fallback to simple base64 encoding with warning
                logger.warning(
                    "Cryptography library not available. Using insecure base64 encoding."
                )
                if isinstance(data, str):
                    data = data.encode("utf-8")
                encoded = base64.b64encode(data)
                return EncryptedData(
                    ciphertext=encoded,
                    algorithm="base64_fallback",
                    metadata={"warning": "insecure_fallback"},
                )

            # Encrypt in thread pool
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                self._thread_pool, self._encrypt_symmetric_sync, data, key, algorithm
            )

    def _encrypt_symmetric_sync(
        self, data: Union[str, bytes], key: Union[str, bytes], algorithm: str
    ) -> EncryptedData:
        """Synchronous symmetric encryption."""
        if isinstance(data, str):
            data = data.encode("utf-8")
        if isinstance(key, str):
            key = key.encode("utf-8")

        # Generate random IV
        iv = secrets.token_bytes(16)

        # Use AES-GCM for authenticated encryption
        cipher = Cipher(
            algorithms.AES(key[:32]),  # Use first 32 bytes as key
            modes.GCM(iv),
            backend=default_backend(),
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()

        return EncryptedData(
            ciphertext=ciphertext, algorithm="AES-GCM", iv=iv, tag=encryptor.tag
        )

    async def decrypt_symmetric_async(
        self, encrypted_data: EncryptedData, key: Union[str, bytes]
    ) -> bytes:
        """
        Decrypt symmetric encrypted data asynchronously.

        Args:
            encrypted_data: EncryptedData object
            key: Decryption key

        Returns:
            Decrypted data
        """
        async with self._with_circuit_breaker("decrypt_symmetric"):
            if encrypted_data.algorithm == "base64_fallback":
                # Handle fallback case
                return base64.b64decode(encrypted_data.ciphertext)

            if not _HAS_CRYPTO_LIBS:
                raise RuntimeError("Cryptography library not available for decryption.")

            # Decrypt in thread pool
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                self._thread_pool, self._decrypt_symmetric_sync, encrypted_data, key
            )

    def _decrypt_symmetric_sync(
        self, encrypted_data: EncryptedData, key: Union[str, bytes]
    ) -> bytes:
        """Synchronous symmetric decryption."""
        if isinstance(key, str):
            key = key.encode("utf-8")

        cipher = Cipher(
            algorithms.AES(key[:32]),
            modes.GCM(encrypted_data.iv, encrypted_data.tag),
            backend=default_backend(),
        )
        decryptor = cipher.decryptor()
        return decryptor.update(encrypted_data.ciphertext) + decryptor.finalize()

    # Utility Methods

    async def generate_secret_key_async(self, length: int = 32) -> str:
        """Generate a random secret key asynchronously."""
        async with self._with_circuit_breaker("generate_secret_key"):
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                self._thread_pool, lambda: secrets.token_urlsafe(length)
            )

    async def constant_time_compare_async(
        self, a: Union[str, bytes], b: Union[str, bytes]
    ) -> bool:
        """Perform constant-time comparison asynchronously."""
        async with self._with_circuit_breaker("constant_time_compare"):
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                self._thread_pool, hmac.compare_digest, a, b
            )

    # Streaming Operations

    async def jwt_validation_stream(
        self, token_stream: AsyncGenerator[str, None], secret_key: str
    ) -> AsyncGenerator[Tuple[str, bool, Optional[str]], None]:
        """
        Validate a stream of JWT tokens asynchronously.

        Args:
            token_stream: Stream of JWT tokens
            secret_key: Secret key for validation

        Yields:
            Tuple of (token, is_valid, error_message)
        """
        async for token in token_stream:
            try:
                await self.verify_jwt_async(token, secret_key)
                yield (token, True, None)
            except Exception as e:
                yield (token, False, str(e))

    async def hash_stream(
        self,
        data_stream: AsyncGenerator[Union[str, bytes], None],
        algorithm: str = "sha256",
    ) -> AsyncGenerator[str, None]:
        """
        Hash a stream of data asynchronously.

        Args:
            data_stream: Stream of data to hash
            algorithm: Hash algorithm

        Yields:
            Hash strings
        """
        async for data in data_stream:
            hash_result = await self.hash_async(data, algorithm)
            yield hash_result

    # Health and Monitoring

    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status."""
        cache_size = len(self._cache)

        return {
            "status": (
                "healthy" if self._circuit_breaker.state != "OPEN" else "degraded"
            ),
            "crypto_libraries_available": _HAS_CRYPTO_LIBS,
            "circuit_breaker": {
                "state": self._circuit_breaker.state,
                "failure_count": self._circuit_breaker.failure_count,
                "last_failure_time": self._circuit_breaker.last_failure_time,
            },
            "cache": {
                "enabled": self._enable_caching,
                "size": cache_size,
                "hits": self._metrics.cache_hits,
                "misses": self._metrics.cache_misses,
                "hit_ratio": self._metrics.cache_hits
                / max(1, self._metrics.cache_hits + self._metrics.cache_misses),
            },
            "metrics": {
                "operation_counts": dict(self._metrics.operation_counts),
                "average_latencies": self._metrics.average_latencies,
                "error_counts": dict(self._metrics.error_counts),
            },
            "thread_pool": {
                "active_threads": getattr(self._thread_pool, "_threads", 0)
            },
        }

    async def clear_cache(self):
        """Clear all cached data."""
        async with self._cache_lock:
            self._cache.clear()

    async def reset_circuit_breaker(self):
        """Reset circuit breaker to closed state."""
        self._circuit_breaker.state = "CLOSED"
        self._circuit_breaker.failure_count = 0
        self._circuit_breaker.half_open_calls = 0

    async def shutdown(self):
        """Shutdown the utility and cleanup resources."""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        self._thread_pool.shutdown(wait=True)

    # Backward compatibility: sync wrapper methods

    def generate_jwt(
        self,
        payload: Dict[str, Any],
        secret_key: str,
        algorithm: Optional[str] = None,
        expiry_seconds: Optional[int] = None,
    ) -> str:
        """Sync wrapper for generate_jwt_async."""
        jwt_token = asyncio.run(
            self.generate_jwt_async(payload, secret_key, algorithm, expiry_seconds)
        )
        return jwt_token.token

    def verify_jwt(
        self, token: str, secret_key: str, algorithms: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Sync wrapper for verify_jwt_async."""
        return asyncio.run(self.verify_jwt_async(token, secret_key, algorithms))

    def hash_data(self, data: Union[str, bytes], algorithm: str = "sha256") -> str:
        """Sync wrapper for hash_async."""
        return asyncio.run(self.hash_async(data, algorithm))

    def generate_hmac(
        self, data: Union[str, bytes], key: Union[str, bytes], algorithm: str = "sha256"
    ) -> str:
        """Sync wrapper for hmac_async."""
        return asyncio.run(self.hmac_async(data, key, algorithm))


# Example usage demonstrating reactive patterns
class ExampleUsage:
    """Example usage of ReactiveSecretUtil."""

    def __init__(self):
        self.secret_util = ReactiveSecretUtil(
            enable_caching=True, max_concurrent_operations=50
        )

    async def example_jwt_operations(self):
        """Example of JWT operations."""
        # Generate secret key
        secret_key = await self.secret_util.generate_secret_key_async()

        # Generate JWT
        jwt_token = await self.secret_util.generate_jwt_async(
            payload={"user_id": "123", "role": "admin"}, secret_key=secret_key
        )

        print(f"Generated JWT: {jwt_token.token}")
        print(f"Expires in: {jwt_token.time_to_expiry} seconds")

        # Verify JWT
        payload = await self.secret_util.verify_jwt_async(jwt_token.token, secret_key)
        print(f"Verified payload: {payload}")

    async def example_streaming_validation(self):
        """Example of streaming JWT validation."""
        secret_key = await self.secret_util.generate_secret_key_async()

        # Create token stream
        async def token_stream():
            for i in range(5):
                jwt_token = await self.secret_util.generate_jwt_async(
                    payload={"user_id": str(i)}, secret_key=secret_key
                )
                yield jwt_token.token

                # Also yield an invalid token
                yield "invalid.token.here"

        # Validate stream
        async for token, is_valid, error in self.secret_util.jwt_validation_stream(
            token_stream(), secret_key
        ):
            print(f"Token valid: {is_valid}, Error: {error}")

    async def example_encryption(self):
        """Example of encryption operations."""
        # Generate key
        key = await self.secret_util.generate_secret_key_async()

        # Encrypt data
        encrypted = await self.secret_util.encrypt_symmetric_async(
            "sensitive data", key
        )
        print(f"Encrypted: {encrypted}")

        # Decrypt data
        decrypted = await self.secret_util.decrypt_symmetric_async(encrypted, key)
        print(f"Decrypted: {decrypted.decode()}")

    async def monitor_health(self):
        """Example of monitoring health."""
        health_status = await self.secret_util.get_health_status()
        print(f"Health status: {health_status}")


if __name__ == "__main__":
    # Example usage
    example = ExampleUsage()
    asyncio.run(example.example_jwt_operations())
