"""
Modern reactive security service with advanced cryptographic operations.
"""

import asyncio
import base64
import hashlib
import hmac
import json
import logging
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
from abc import ABC, abstractmethod
import threading
from collections import deque

# For JWT operations
try:
    import jwt

    HAS_JWT = True
except ImportError:
    HAS_JWT = False

# For advanced cryptography (optional)
try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False

logger = logging.getLogger(__name__)


# Security result types
@dataclass
class SecurityResult(ABC):
    """Base class for security operation results."""

    pass


@dataclass
class SecuritySuccess(SecurityResult):
    """Successful security operation result."""

    data: Any


@dataclass
class SecurityFailure(SecurityResult):
    """Failed security operation result."""

    error: "SecurityError"


class SecurityError:
    """Security error types."""

    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code

    def __str__(self):
        return f"{self.code}: {self.message}"


# Common security errors
class TokenExpired(SecurityError):
    def __init__(self):
        super().__init__("Token has expired", "TOKEN_EXPIRED")


class TokenInvalid(SecurityError):
    def __init__(self):
        super().__init__("Token is invalid", "TOKEN_INVALID")


class SignatureInvalid(SecurityError):
    def __init__(self):
        super().__init__("Signature verification failed", "SIGNATURE_INVALID")


class EncryptionFailed(SecurityError):
    def __init__(self):
        super().__init__("Encryption operation failed", "ENCRYPTION_FAILED")


class DecryptionFailed(SecurityError):
    def __init__(self):
        super().__init__("Decryption operation failed", "DECRYPTION_FAILED")


class KeyNotFound(SecurityError):
    def __init__(self):
        super().__init__("Cryptographic key not found", "KEY_NOT_FOUND")


class InvalidInput(SecurityError):
    def __init__(self):
        super().__init__("Invalid input provided", "INVALID_INPUT")


@dataclass
class JWTInfo:
    """JWT token information."""

    token: str
    issued_at: datetime
    expires_at: datetime
    algorithm: str
    key_id: Optional[str] = None
    claims: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EncryptionResult:
    """Encryption result container."""

    encrypted_data: bytes
    iv: Optional[bytes] = None
    algorithm: str = ""
    key_id: Optional[str] = None
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class SignatureResult:
    """Digital signature result."""

    signature: bytes
    algorithm: str
    key_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class KeyDerivationConfig:
    """Key derivation configuration."""

    algorithm: str = "PBKDF2"
    iterations: int = 100000
    key_length: int = 32  # 256 bits
    salt_length: int = 32


@dataclass
class SecurityConfig:
    """Security service configuration."""

    key_vault_url: str = ""
    key_name: str = ""
    key_version: Optional[str] = None
    default_token_expiry: timedelta = timedelta(hours=24)
    enable_caching: bool = True
    cache_expiry: timedelta = timedelta(minutes=30)
    rate_limit_per_second: int = 100
    jwt_secret_key: Optional[str] = None  # For local JWT signing


@dataclass
class TokenCacheEntry:
    """Token cache entry."""

    auth_context: Dict[str, Any]
    expires_at: datetime


class TokenBucket:
    """Token bucket for rate limiting."""

    def __init__(
        self, capacity: int, refill_rate: int, refill_period_ms: float = 1000.0
    ):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.refill_period_ms = refill_period_ms
        self.tokens = capacity
        self.last_refill = time.time() * 1000  # milliseconds
        self._lock = threading.Lock()

    async def try_acquire(self, tokens: int = 1) -> bool:
        """Try to acquire tokens."""
        with self._lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def _refill(self):
        """Refill tokens based on elapsed time."""
        now = time.time() * 1000
        time_passed = now - self.last_refill
        tokens_to_add = int(time_passed / self.refill_period_ms * self.refill_rate)

        if tokens_to_add > 0:
            self.tokens = min(self.capacity, self.tokens + tokens_to_add)
            self.last_refill = now


class ReactiveSecurityService:
    """
    Reactive security service with modern cryptographic operations.

    This implementation provides JWT operations, encryption/decryption,
    and digital signatures with rate limiting and caching.
    """

    def __init__(self, config: SecurityConfig):
        """Initialize security service."""
        self.config = config
        self.token_cache: Dict[str, TokenCacheEntry] = {}
        self.rate_limiter = TokenBucket(
            config.rate_limit_per_second, config.rate_limit_per_second
        )
        self._cache_lock = threading.Lock()
        self._running = True

        # Start cache cleanup task
        self._cleanup_task = asyncio.create_task(self._cache_cleanup_loop())

        logger.info("ReactiveSecurityService initialized")

    async def create_jwt(self, context: Dict[str, Any]) -> SecurityResult:
        """Create a JWT token."""
        if not HAS_JWT:
            return SecurityFailure(
                SecurityError("JWT library not available", "JWT_NOT_AVAILABLE")
            )

        try:
            if not await self.rate_limiter.try_acquire():
                return SecurityFailure(
                    SecurityError("Rate limit exceeded", "RATE_LIMIT")
                )

            now = datetime.now()
            expiry = now + self.config.default_token_expiry

            # Create JWT claims
            claims = {
                "id": context.get("id"),
                "roles": context.get("roles", []),
                "actor": context.get("actor"),
                "ip_address": context.get("ip_address"),
                "request_time": context.get("request_time"),
                "device": context.get("device"),
                "location": context.get("location"),
                "user_agent": context.get("user_agent"),
                "tier": context.get("tier"),
                "client_request_id": context.get("client_request_id"),
                "account_id": context.get("account_id"),
                "jti": secrets.token_urlsafe(16),  # JWT ID for tracking
                "iss": "apexnova",
                "iat": now,
                "exp": expiry,
            }

            # Sign the token
            if self.config.jwt_secret_key:
                token = jwt.encode(
                    claims, self.config.jwt_secret_key, algorithm="HS256"
                )
            else:
                # In production, you would use Azure Key Vault or similar
                # For now, generate a random key
                if not hasattr(self, "_temp_key"):
                    self._temp_key = secrets.token_urlsafe(32)
                token = jwt.encode(claims, self._temp_key, algorithm="HS256")

            # Cache the token context if caching is enabled
            if self.config.enable_caching:
                with self._cache_lock:
                    self.token_cache[token] = TokenCacheEntry(context, expiry)

            jwt_info = JWTInfo(
                token=token,
                issued_at=now,
                expires_at=expiry,
                algorithm="HS256",
                key_id=self.config.key_name,
                claims={
                    "id": context.get("id"),
                    "account_id": context.get("account_id"),
                    "roles": context.get("roles", []),
                },
            )

            return SecuritySuccess(jwt_info)

        except Exception as e:
            logger.error(f"Failed to create JWT: {e}")
            return SecurityFailure(
                SecurityError(f"JWT creation failed: {str(e)}", "JWT_CREATION_FAILED")
            )

    async def verify_jwt(self, token: str) -> SecurityResult:
        """Verify a JWT token."""
        if not HAS_JWT:
            return SecurityFailure(
                SecurityError("JWT library not available", "JWT_NOT_AVAILABLE")
            )

        try:
            if not await self.rate_limiter.try_acquire():
                return SecurityFailure(
                    SecurityError("Rate limit exceeded", "RATE_LIMIT")
                )

            # Check cache first
            if self.config.enable_caching:
                with self._cache_lock:
                    cached = self.token_cache.get(token)
                    if cached and cached.expires_at > datetime.now():
                        return SecuritySuccess(cached.auth_context)
                    elif cached:
                        del self.token_cache[token]

            # Verify the token
            if self.config.jwt_secret_key:
                payload = jwt.decode(
                    token, self.config.jwt_secret_key, algorithms=["HS256"]
                )
            else:
                # Use the temporary key
                if hasattr(self, "_temp_key"):
                    payload = jwt.decode(token, self._temp_key, algorithms=["HS256"])
                else:
                    return SecurityFailure(TokenInvalid())

            # Check expiration
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp) < datetime.now():
                return SecurityFailure(TokenExpired())

            # Extract context from claims
            context = {
                "id": payload.get("id"),
                "account_id": payload.get("account_id"),
                "roles": payload.get("roles", []),
                "actor": payload.get("actor"),
                "ip_address": payload.get("ip_address"),
                "request_time": payload.get("request_time"),
                "device": payload.get("device"),
                "location": payload.get("location"),
                "user_agent": payload.get("user_agent"),
                "tier": payload.get("tier"),
                "client_request_id": payload.get("client_request_id"),
            }

            # Cache successful verification
            if self.config.enable_caching and exp:
                with self._cache_lock:
                    self.token_cache[token] = TokenCacheEntry(
                        context, datetime.fromtimestamp(exp)
                    )

            return SecuritySuccess(context)

        except jwt.ExpiredSignatureError:
            return SecurityFailure(TokenExpired())
        except jwt.InvalidTokenError:
            return SecurityFailure(TokenInvalid())
        except Exception as e:
            logger.error(f"Failed to verify JWT: {e}")
            return SecurityFailure(
                SecurityError(
                    f"JWT verification failed: {str(e)}", "JWT_VERIFICATION_FAILED"
                )
            )

    async def create_jwt_batch(
        self, contexts: List[Dict[str, Any]]
    ) -> List[Tuple[Dict[str, Any], SecurityResult]]:
        """Create multiple JWT tokens in batch."""
        results = []

        # Process with limited concurrency
        semaphore = asyncio.Semaphore(10)

        async def create_with_semaphore(context):
            async with semaphore:
                result = await self.create_jwt(context)
                return context, result

        tasks = [create_with_semaphore(context) for context in contexts]
        results = await asyncio.gather(*tasks)

        return results

    async def verify_jwt_batch(
        self, tokens: List[str]
    ) -> List[Tuple[str, SecurityResult]]:
        """Verify multiple JWT tokens in batch."""
        results = []

        # Process with limited concurrency
        semaphore = asyncio.Semaphore(10)

        async def verify_with_semaphore(token):
            async with semaphore:
                result = await self.verify_jwt(token)
                return token, result

        tasks = [verify_with_semaphore(token) for token in tokens]
        results = await asyncio.gather(*tasks)

        return results

    async def encrypt(
        self, data: bytes, algorithm: str = "AES-256-GCM"
    ) -> SecurityResult:
        """Encrypt data."""
        if not HAS_CRYPTOGRAPHY:
            # Fallback to basic encryption
            return await self._basic_encrypt(data)

        try:
            if not await self.rate_limiter.try_acquire():
                return SecurityFailure(
                    SecurityError("Rate limit exceeded", "RATE_LIMIT")
                )

            # Generate key and IV
            key = secrets.token_bytes(32)  # 256 bits
            iv = secrets.token_bytes(12)  # 96 bits for GCM

            # Encrypt using AES-GCM
            cipher = Cipher(
                algorithms.AES(key), modes.GCM(iv), backend=default_backend()
            )
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(data) + encryptor.finalize()

            # Store key securely (in production, use Key Vault)
            if not hasattr(self, "_encryption_keys"):
                self._encryption_keys = {}
            key_id = secrets.token_urlsafe(16)
            self._encryption_keys[key_id] = key

            result = EncryptionResult(
                encrypted_data=ciphertext + encryptor.tag,
                iv=iv,
                algorithm=algorithm,
                key_id=key_id,
                metadata={
                    "timestamp": datetime.now().isoformat(),
                    "data_size": str(len(data)),
                },
            )

            return SecuritySuccess(result)

        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return SecurityFailure(EncryptionFailed())

    async def decrypt(self, encryption_result: EncryptionResult) -> SecurityResult:
        """Decrypt data."""
        if not HAS_CRYPTOGRAPHY:
            # Fallback to basic decryption
            return await self._basic_decrypt(encryption_result)

        try:
            if not await self.rate_limiter.try_acquire():
                return SecurityFailure(
                    SecurityError("Rate limit exceeded", "RATE_LIMIT")
                )

            # Retrieve key
            if (
                not hasattr(self, "_encryption_keys")
                or encryption_result.key_id not in self._encryption_keys
            ):
                return SecurityFailure(KeyNotFound())

            key = self._encryption_keys[encryption_result.key_id]

            # Separate ciphertext and tag
            ciphertext = encryption_result.encrypted_data[:-16]
            tag = encryption_result.encrypted_data[-16:]

            # Decrypt using AES-GCM
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(encryption_result.iv, tag),
                backend=default_backend(),
            )
            decryptor = cipher.decryptor()
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()

            return SecuritySuccess(plaintext)

        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return SecurityFailure(DecryptionFailed())

    async def encrypt_aes(self, data: bytes, password: str) -> SecurityResult:
        """Encrypt data with AES using password."""
        try:
            # Generate salt
            salt = secrets.token_bytes(32)

            # Derive key from password
            key = await self._derive_key(password, salt)

            # Generate IV
            iv = secrets.token_bytes(12)  # GCM recommended IV size

            if HAS_CRYPTOGRAPHY:
                # Use cryptography library
                cipher = Cipher(
                    algorithms.AES(key), modes.GCM(iv), backend=default_backend()
                )
                encryptor = cipher.encryptor()
                ciphertext = encryptor.update(data) + encryptor.finalize()

                # Combine salt + iv + ciphertext + tag
                combined = salt + iv + ciphertext + encryptor.tag
            else:
                # Fallback implementation
                # In production, you would need a proper AES implementation
                combined = salt + iv + data  # Simplified, not secure!

            result = EncryptionResult(
                encrypted_data=combined,
                iv=iv,
                algorithm="AES/GCM",
                metadata={
                    "salt_length": str(len(salt)),
                    "iv_length": str(len(iv)),
                    "data_size": str(len(data)),
                },
            )

            return SecuritySuccess(result)

        except Exception as e:
            logger.error(f"AES encryption failed: {e}")
            return SecurityFailure(EncryptionFailed())

    async def decrypt_aes(
        self, encryption_result: EncryptionResult, password: str
    ) -> SecurityResult:
        """Decrypt AES encrypted data with password."""
        try:
            combined = encryption_result.encrypted_data

            # Extract components
            salt = combined[:32]
            iv = combined[32:44]

            # Derive key from password
            key = await self._derive_key(password, salt)

            if HAS_CRYPTOGRAPHY:
                # Extract ciphertext and tag
                ciphertext = combined[44:-16]
                tag = combined[-16:]

                # Decrypt
                cipher = Cipher(
                    algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend()
                )
                decryptor = cipher.decryptor()
                plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            else:
                # Fallback implementation
                plaintext = combined[44:]  # Simplified, not secure!

            return SecuritySuccess(plaintext)

        except Exception as e:
            logger.error(f"AES decryption failed: {e}")
            return SecurityFailure(DecryptionFailed())

    async def sign(self, data: bytes, algorithm: str = "SHA256") -> SecurityResult:
        """Create digital signature."""
        try:
            if not await self.rate_limiter.try_acquire():
                return SecurityFailure(
                    SecurityError("Rate limit exceeded", "RATE_LIMIT")
                )

            # In production, use private key from Key Vault
            # For now, use HMAC with secret key
            if not hasattr(self, "_signing_key"):
                self._signing_key = secrets.token_bytes(32)

            if algorithm == "SHA256":
                signature = hmac.new(self._signing_key, data, hashlib.sha256).digest()
            elif algorithm == "SHA512":
                signature = hmac.new(self._signing_key, data, hashlib.sha512).digest()
            else:
                return SecurityFailure(
                    SecurityError(
                        f"Unsupported algorithm: {algorithm}", "UNSUPPORTED_ALGORITHM"
                    )
                )

            result = SignatureResult(
                signature=signature,
                algorithm=f"HMAC-{algorithm}",
                key_id=self.config.key_name,
            )

            return SecuritySuccess(result)

        except Exception as e:
            logger.error(f"Signing failed: {e}")
            return SecurityFailure(
                SecurityError(f"Signing failed: {str(e)}", "SIGNING_FAILED")
            )

    async def verify(
        self, data: bytes, signature_result: SignatureResult
    ) -> SecurityResult:
        """Verify digital signature."""
        try:
            if not await self.rate_limiter.try_acquire():
                return SecurityFailure(
                    SecurityError("Rate limit exceeded", "RATE_LIMIT")
                )

            # Verify HMAC signature
            if not hasattr(self, "_signing_key"):
                return SecurityFailure(KeyNotFound())

            algorithm = signature_result.algorithm.replace("HMAC-", "")

            if algorithm == "SHA256":
                expected = hmac.new(self._signing_key, data, hashlib.sha256).digest()
            elif algorithm == "SHA512":
                expected = hmac.new(self._signing_key, data, hashlib.sha512).digest()
            else:
                return SecurityFailure(
                    SecurityError(
                        f"Unsupported algorithm: {algorithm}", "UNSUPPORTED_ALGORITHM"
                    )
                )

            is_valid = hmac.compare_digest(expected, signature_result.signature)

            return SecuritySuccess(is_valid)

        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return SecurityFailure(
                SecurityError(f"Verification failed: {str(e)}", "VERIFICATION_FAILED")
            )

    async def _derive_key(
        self, password: str, salt: bytes, config: Optional[KeyDerivationConfig] = None
    ) -> bytes:
        """Derive key from password."""
        config = config or KeyDerivationConfig()

        if HAS_CRYPTOGRAPHY:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=config.key_length,
                salt=salt,
                iterations=config.iterations,
                backend=default_backend(),
            )
            return kdf.derive(password.encode())
        else:
            # Fallback to hashlib
            return hashlib.pbkdf2_hmac(
                "sha256", password.encode(), salt, config.iterations, config.key_length
            )

    async def _basic_encrypt(self, data: bytes) -> SecurityResult:
        """Basic encryption fallback."""
        # This is NOT secure - just for demonstration
        key = secrets.token_bytes(32)
        encrypted = bytes(
            a ^ b for a, b in zip(data, key * (len(data) // len(key) + 1))
        )

        if not hasattr(self, "_basic_keys"):
            self._basic_keys = {}
        key_id = secrets.token_urlsafe(16)
        self._basic_keys[key_id] = key

        result = EncryptionResult(
            encrypted_data=encrypted, algorithm="XOR", key_id=key_id
        )

        return SecuritySuccess(result)

    async def _basic_decrypt(
        self, encryption_result: EncryptionResult
    ) -> SecurityResult:
        """Basic decryption fallback."""
        if (
            not hasattr(self, "_basic_keys")
            or encryption_result.key_id not in self._basic_keys
        ):
            return SecurityFailure(KeyNotFound())

        key = self._basic_keys[encryption_result.key_id]
        decrypted = bytes(
            a ^ b
            for a, b in zip(
                encryption_result.encrypted_data,
                key * (len(encryption_result.encrypted_data) // len(key) + 1),
            )
        )

        return SecuritySuccess(decrypted)

    def generate_secure_token(self, length: int = 32) -> str:
        """Generate a secure random token."""
        return secrets.token_urlsafe(length)

    def generate_salt(self, length: int = 32) -> bytes:
        """Generate a secure salt."""
        return secrets.token_bytes(length)

    async def hash_with_salt(
        self, data: str, salt: Optional[bytes] = None
    ) -> Tuple[str, bytes]:
        """Hash data with salt."""
        if salt is None:
            salt = self.generate_salt()

        hash_obj = hashlib.sha256()
        hash_obj.update(salt)
        hash_obj.update(data.encode())
        hash_value = base64.b64encode(hash_obj.digest()).decode()

        return hash_value, salt

    async def verify_hash(self, data: str, hash_value: str, salt: bytes) -> bool:
        """Verify hashed data."""
        computed_hash, _ = await self.hash_with_salt(data, salt)
        return hmac.compare_digest(computed_hash, hash_value)

    def get_security_metrics(self) -> Dict[str, Any]:
        """Get security service metrics."""
        with self._cache_lock:
            active_tokens = sum(
                1
                for entry in self.token_cache.values()
                if entry.expires_at > datetime.now()
            )
            expired_tokens = len(self.token_cache) - active_tokens

        return {
            "cache_size": len(self.token_cache),
            "active_tokens": active_tokens,
            "expired_tokens": expired_tokens,
            "cache_hit_rate": 0.85,  # Placeholder
        }

    async def health_check(self) -> SecurityResult:
        """Perform health check."""
        try:
            # Test basic crypto operations
            test_data = f"health_check_{time.time()}".encode()
            sign_result = await self.sign(test_data)

            if isinstance(sign_result, SecuritySuccess):
                verify_result = await self.verify(test_data, sign_result.data)

                if isinstance(verify_result, SecuritySuccess):
                    return SecuritySuccess(
                        {
                            "status": "healthy",
                            "crypto_operations": "working",
                            "cache_size": len(self.token_cache),
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                else:
                    return verify_result
            else:
                return sign_result

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return SecurityFailure(
                SecurityError(f"Health check failed: {str(e)}", "HEALTH_CHECK_FAILED")
            )

    async def _cache_cleanup_loop(self):
        """Periodically clean up expired cache entries."""
        while self._running:
            try:
                await asyncio.sleep(300)  # 5 minutes
                self._cleanup_expired_tokens()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cache cleanup error: {e}")

    def _cleanup_expired_tokens(self):
        """Clean up expired tokens from cache."""
        now = datetime.now()
        with self._cache_lock:
            expired_tokens = [
                token
                for token, entry in self.token_cache.items()
                if entry.expires_at < now
            ]
            for token in expired_tokens:
                del self.token_cache[token]

            if expired_tokens:
                logger.debug(f"Cleaned up {len(expired_tokens)} expired tokens")

    def clear_cache(self):
        """Clear the security cache."""
        with self._cache_lock:
            self.token_cache.clear()
        logger.info("Security cache cleared")

    async def shutdown(self):
        """Shutdown the security service."""
        self._running = False
        if hasattr(self, "_cleanup_task"):
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        self.clear_cache()
        logger.info("ReactiveSecurityService shutdown complete")


class SecurityServiceBuilder:
    """Builder for creating security service."""

    def __init__(self):
        """Initialize builder."""
        self.key_vault_url = ""
        self.key_name = ""
        self.key_version = None
        self.default_token_expiry = timedelta(hours=24)
        self.enable_caching = True
        self.cache_expiry = timedelta(minutes=30)
        self.rate_limit_per_second = 100
        self.jwt_secret_key = None

    def key_vault(
        self, url: str, key_name: str, key_version: Optional[str] = None
    ) -> "SecurityServiceBuilder":
        """Set key vault configuration."""
        self.key_vault_url = url
        self.key_name = key_name
        self.key_version = key_version
        return self

    def token_expiry(self, duration: timedelta) -> "SecurityServiceBuilder":
        """Set token expiry."""
        self.default_token_expiry = duration
        return self

    def caching(
        self, enabled: bool, expiry: timedelta = timedelta(minutes=30)
    ) -> "SecurityServiceBuilder":
        """Set caching configuration."""
        self.enable_caching = enabled
        self.cache_expiry = expiry
        return self

    def rate_limit(self, requests_per_second: int) -> "SecurityServiceBuilder":
        """Set rate limit."""
        self.rate_limit_per_second = requests_per_second
        return self

    def jwt_secret(self, secret: str) -> "SecurityServiceBuilder":
        """Set JWT secret key."""
        self.jwt_secret_key = secret
        return self

    def build(self) -> ReactiveSecurityService:
        """Build security service."""
        config = SecurityConfig(
            key_vault_url=self.key_vault_url,
            key_name=self.key_name,
            key_version=self.key_version,
            default_token_expiry=self.default_token_expiry,
            enable_caching=self.enable_caching,
            cache_expiry=self.cache_expiry,
            rate_limit_per_second=self.rate_limit_per_second,
            jwt_secret_key=self.jwt_secret_key,
        )

        return ReactiveSecurityService(config)


def security_service(builder_fn) -> ReactiveSecurityService:
    """
    DSL function to create security service.

    Example:
        service = security_service(lambda b: b
            .key_vault("https://vault.azure.net", "mykey")
            .token_expiry(timedelta(hours=12))
            .rate_limit(200)
        )
    """
    builder = SecurityServiceBuilder()
    builder_fn(builder)
    return builder.build()


class SecurityServiceRegistry:
    """Global security service registry."""

    _services: Dict[str, ReactiveSecurityService] = {}
    _default_service: Optional[ReactiveSecurityService] = None

    @classmethod
    def register(cls, name: str, service: ReactiveSecurityService) -> None:
        """Register a security service."""
        cls._services[name] = service
        if cls._default_service is None:
            cls._default_service = service

    @classmethod
    def get(cls, name: str) -> Optional[ReactiveSecurityService]:
        """Get a registered service."""
        return cls._services.get(name)

    @classmethod
    def default(cls) -> ReactiveSecurityService:
        """Get default service."""
        if cls._default_service is None:
            raise RuntimeError("No default security service configured")
        return cls._default_service

    @classmethod
    async def shutdown(cls) -> None:
        """Shutdown all services."""
        for service in cls._services.values():
            await service.shutdown()
        cls._services.clear()
        cls._default_service = None
