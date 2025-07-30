"""
Enhanced security utilities with encryption, hashing, and authentication features.
"""

import base64
import hashlib
import hmac
import logging
import os
import secrets
import string
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

from ..core.result import Result

# Try to import cryptography for advanced features
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


class EncryptionAlgorithm(Enum):
    """Supported encryption algorithms."""

    AES_GCM = ("AES/GCM/NoPadding", 256)
    AES_CBC = ("AES/CBC/PKCS7Padding", 256)
    RSA_OAEP = ("RSA/ECB/OAEPWithSHA-256AndMGF1Padding", 2048)
    RSA_PKCS1 = ("RSA/ECB/PKCS1Padding", 2048)

    def __init__(self, algorithm: str, key_size: int):
        self.algorithm = algorithm
        self.key_size = key_size


class HashAlgorithm(Enum):
    """Supported hash algorithms."""

    SHA256 = "sha256"
    SHA512 = "sha512"
    SHA3_256 = "sha3_256"
    SHA3_512 = "sha3_512"
    BLAKE2B = "blake2b"


class MACAlgorithm(Enum):
    """Supported MAC algorithms."""

    HMAC_SHA256 = "hmac_sha256"
    HMAC_SHA512 = "hmac_sha512"
    HMAC_SHA3_256 = "hmac_sha3_256"
    HMAC_SHA3_512 = "hmac_sha3_512"


@dataclass
class EncryptedData:
    """Container for encrypted data."""

    data: bytes
    iv: Optional[bytes] = None
    tag: Optional[bytes] = None
    algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_GCM
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class KeyPairContainer:
    """Container for cryptographic key pair."""

    public_key: Any  # PublicKey type
    private_key: Any  # PrivateKey type
    algorithm: str
    key_size: int
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class DigitalSignature:
    """Container for digital signature."""

    signature: bytes
    algorithm: str
    public_key: bytes
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class CryptographyService:
    """Enhanced cryptography service."""

    def __init__(self):
        """Initialize cryptography service."""
        self.key_cache: Dict[str, Any] = {}

    def generate_symmetric_key(self, algorithm: EncryptionAlgorithm) -> Result[bytes]:
        """Generate a symmetric encryption key."""
        try:
            if algorithm in (EncryptionAlgorithm.AES_GCM, EncryptionAlgorithm.AES_CBC):
                key_size_bytes = algorithm.key_size // 8
                key = secrets.token_bytes(key_size_bytes)
                return Result.success(key)
            else:
                return Result.failure(
                    ValueError(f"Unsupported symmetric algorithm: {algorithm}")
                )
        except Exception as e:
            logger.error(f"Failed to generate symmetric key: {e}")
            return Result.failure(e)

    def generate_key_pair(
        self, algorithm: EncryptionAlgorithm
    ) -> Result[KeyPairContainer]:
        """Generate an asymmetric key pair."""
        if not HAS_CRYPTOGRAPHY:
            return Result.failure(ImportError("cryptography library not available"))

        try:
            if algorithm in (
                EncryptionAlgorithm.RSA_OAEP,
                EncryptionAlgorithm.RSA_PKCS1,
            ):
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=algorithm.key_size,
                    backend=default_backend(),
                )
                public_key = private_key.public_key()

                container = KeyPairContainer(
                    public_key=public_key,
                    private_key=private_key,
                    algorithm=algorithm.algorithm,
                    key_size=algorithm.key_size,
                )

                return Result.success(container)
            else:
                return Result.failure(
                    ValueError(f"Unsupported asymmetric algorithm: {algorithm}")
                )
        except Exception as e:
            logger.error(f"Failed to generate key pair: {e}")
            return Result.failure(e)

    def encrypt_symmetric(
        self, data: bytes, key: bytes, algorithm: EncryptionAlgorithm
    ) -> Result[EncryptedData]:
        """Encrypt data with symmetric key."""
        if not HAS_CRYPTOGRAPHY:
            # Fallback to basic XOR encryption (NOT SECURE!)
            return self._basic_encrypt(data, key, algorithm)

        try:
            if algorithm == EncryptionAlgorithm.AES_GCM:
                iv = os.urandom(12)  # 96 bits for GCM
                cipher = Cipher(
                    algorithms.AES(key), modes.GCM(iv), backend=default_backend()
                )
                encryptor = cipher.encryptor()
                ciphertext = encryptor.update(data) + encryptor.finalize()

                return Result.success(
                    EncryptedData(
                        data=ciphertext, iv=iv, tag=encryptor.tag, algorithm=algorithm
                    )
                )

            elif algorithm == EncryptionAlgorithm.AES_CBC:
                iv = os.urandom(16)  # 128 bits for CBC
                cipher = Cipher(
                    algorithms.AES(key), modes.CBC(iv), backend=default_backend()
                )
                encryptor = cipher.encryptor()

                # Pad data for CBC
                pad_length = 16 - (len(data) % 16)
                padded_data = data + bytes([pad_length] * pad_length)

                ciphertext = encryptor.update(padded_data) + encryptor.finalize()

                return Result.success(
                    EncryptedData(data=ciphertext, iv=iv, algorithm=algorithm)
                )

            else:
                return Result.failure(
                    ValueError(f"Unsupported symmetric algorithm: {algorithm}")
                )

        except Exception as e:
            logger.error(f"Failed to encrypt data: {e}")
            return Result.failure(e)

    def decrypt_symmetric(
        self, encrypted_data: EncryptedData, key: bytes
    ) -> Result[bytes]:
        """Decrypt data with symmetric key."""
        if not HAS_CRYPTOGRAPHY:
            # Fallback to basic XOR decryption
            return self._basic_decrypt(encrypted_data, key)

        try:
            if encrypted_data.algorithm == EncryptionAlgorithm.AES_GCM:
                cipher = Cipher(
                    algorithms.AES(key),
                    modes.GCM(encrypted_data.iv, encrypted_data.tag),
                    backend=default_backend(),
                )
                decryptor = cipher.decryptor()
                plaintext = decryptor.update(encrypted_data.data) + decryptor.finalize()

                return Result.success(plaintext)

            elif encrypted_data.algorithm == EncryptionAlgorithm.AES_CBC:
                cipher = Cipher(
                    algorithms.AES(key),
                    modes.CBC(encrypted_data.iv),
                    backend=default_backend(),
                )
                decryptor = cipher.decryptor()
                padded_plaintext = (
                    decryptor.update(encrypted_data.data) + decryptor.finalize()
                )

                # Remove padding
                pad_length = padded_plaintext[-1]
                plaintext = padded_plaintext[:-pad_length]

                return Result.success(plaintext)

            else:
                return Result.failure(
                    ValueError(
                        f"Unsupported symmetric algorithm: {encrypted_data.algorithm}"
                    )
                )

        except Exception as e:
            logger.error(f"Failed to decrypt data: {e}")
            return Result.failure(e)

    def encrypt_asymmetric(
        self, data: bytes, public_key: Any, algorithm: EncryptionAlgorithm
    ) -> Result[EncryptedData]:
        """Encrypt data with public key."""
        if not HAS_CRYPTOGRAPHY:
            return Result.failure(ImportError("cryptography library not available"))

        try:
            if algorithm == EncryptionAlgorithm.RSA_OAEP:
                ciphertext = public_key.encrypt(
                    data,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None,
                    ),
                )
                return Result.success(
                    EncryptedData(data=ciphertext, algorithm=algorithm)
                )

            elif algorithm == EncryptionAlgorithm.RSA_PKCS1:
                ciphertext = public_key.encrypt(data, padding.PKCS1v15())
                return Result.success(
                    EncryptedData(data=ciphertext, algorithm=algorithm)
                )

            else:
                return Result.failure(
                    ValueError(f"Unsupported asymmetric algorithm: {algorithm}")
                )

        except Exception as e:
            logger.error(f"Failed to encrypt data with public key: {e}")
            return Result.failure(e)

    def decrypt_asymmetric(
        self, encrypted_data: EncryptedData, private_key: Any
    ) -> Result[bytes]:
        """Decrypt data with private key."""
        if not HAS_CRYPTOGRAPHY:
            return Result.failure(ImportError("cryptography library not available"))

        try:
            if encrypted_data.algorithm == EncryptionAlgorithm.RSA_OAEP:
                plaintext = private_key.decrypt(
                    encrypted_data.data,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None,
                    ),
                )
                return Result.success(plaintext)

            elif encrypted_data.algorithm == EncryptionAlgorithm.RSA_PKCS1:
                plaintext = private_key.decrypt(encrypted_data.data, padding.PKCS1v15())
                return Result.success(plaintext)

            else:
                return Result.failure(
                    ValueError(
                        f"Unsupported asymmetric algorithm: {encrypted_data.algorithm}"
                    )
                )

        except Exception as e:
            logger.error(f"Failed to decrypt data with private key: {e}")
            return Result.failure(e)

    def sign(
        self, data: bytes, private_key: Any, algorithm: str = "SHA256withRSA"
    ) -> Result[DigitalSignature]:
        """Create digital signature."""
        if not HAS_CRYPTOGRAPHY:
            # Fallback to HMAC
            return self._hmac_sign(data, algorithm)

        try:
            signature = private_key.sign(
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )

            public_key_bytes = private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )

            return Result.success(
                DigitalSignature(
                    signature=signature,
                    algorithm=algorithm,
                    public_key=public_key_bytes,
                )
            )

        except Exception as e:
            logger.error(f"Failed to create digital signature: {e}")
            return Result.failure(e)

    def verify_signature(
        self, data: bytes, digital_signature: DigitalSignature, public_key: Any
    ) -> Result[bool]:
        """Verify digital signature."""
        if not HAS_CRYPTOGRAPHY:
            # Fallback to HMAC verification
            return self._hmac_verify(data, digital_signature)

        try:
            public_key.verify(
                digital_signature.signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
            return Result.success(True)

        except Exception:
            return Result.success(False)

    def generate_random_bytes(self, size: int) -> bytes:
        """Generate secure random bytes."""
        return secrets.token_bytes(size)

    def generate_random_string(
        self, length: int, charset: str = string.ascii_letters + string.digits
    ) -> str:
        """Generate secure random string."""
        return "".join(secrets.choice(charset) for _ in range(length))

    def derive_key_from_password(
        self, password: str, salt: bytes, iterations: int = 100000, key_length: int = 32
    ) -> Result[bytes]:
        """Derive key from password using PBKDF2."""
        try:
            if HAS_CRYPTOGRAPHY:
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=key_length,
                    salt=salt,
                    iterations=iterations,
                    backend=default_backend(),
                )
                key = kdf.derive(password.encode())
            else:
                # Fallback to hashlib
                key = hashlib.pbkdf2_hmac(
                    "sha256", password.encode(), salt, iterations, key_length
                )

            return Result.success(key)

        except Exception as e:
            logger.error(f"Failed to derive key from password: {e}")
            return Result.failure(e)

    def get_cached_key(self, key_id: str, key_supplier) -> Result[Any]:
        """Get key from cache or generate new one."""
        cached_key = self.key_cache.get(key_id)
        if cached_key:
            return Result.success(cached_key)

        result = key_supplier()
        if result.is_success:
            self.key_cache[key_id] = result.value

        return result

    def clear_key_cache(self):
        """Clear key cache."""
        self.key_cache.clear()

    def _basic_encrypt(
        self, data: bytes, key: bytes, algorithm: EncryptionAlgorithm
    ) -> Result[EncryptedData]:
        """Basic XOR encryption (NOT SECURE!)."""
        encrypted = bytes(
            a ^ b for a, b in zip(data, key * (len(data) // len(key) + 1))
        )
        return Result.success(EncryptedData(data=encrypted, algorithm=algorithm))

    def _basic_decrypt(
        self, encrypted_data: EncryptedData, key: bytes
    ) -> Result[bytes]:
        """Basic XOR decryption (NOT SECURE!)."""
        decrypted = bytes(
            a ^ b
            for a, b in zip(
                encrypted_data.data, key * (len(encrypted_data.data) // len(key) + 1)
            )
        )
        return Result.success(decrypted)

    def _hmac_sign(self, data: bytes, algorithm: str) -> Result[DigitalSignature]:
        """Create HMAC signature as fallback."""
        key = self.generate_random_bytes(32)
        signature = hmac.new(key, data, hashlib.sha256).digest()

        return Result.success(
            DigitalSignature(
                signature=signature,
                algorithm=f"HMAC-{algorithm}",
                public_key=key,  # Store key as "public key" for HMAC
            )
        )

    def _hmac_verify(
        self, data: bytes, digital_signature: DigitalSignature
    ) -> Result[bool]:
        """Verify HMAC signature."""
        expected = hmac.new(digital_signature.public_key, data, hashlib.sha256).digest()
        is_valid = hmac.compare_digest(expected, digital_signature.signature)
        return Result.success(is_valid)


class HashService:
    """Hash computation service."""

    def compute_hash(self, data: bytes, algorithm: HashAlgorithm) -> Result[bytes]:
        """Compute hash of data."""
        try:
            if algorithm == HashAlgorithm.BLAKE2B and not hasattr(hashlib, "blake2b"):
                return Result.failure(
                    ValueError(f"Unsupported hash algorithm: {algorithm.value}")
                )

            hash_obj = hashlib.new(algorithm.value)
            hash_obj.update(data)
            return Result.success(hash_obj.digest())

        except Exception as e:
            logger.error(f"Failed to compute hash: {e}")
            return Result.failure(e)

    def compute_hash_hex(self, data: bytes, algorithm: HashAlgorithm) -> Result[str]:
        """Compute hash as hex string."""
        result = self.compute_hash(data, algorithm)
        if result.is_success:
            return Result.success(result.value.hex())
        return result

    def compute_hash_string(self, data: str, algorithm: HashAlgorithm) -> Result[str]:
        """Compute hash of string."""
        return self.compute_hash_hex(data.encode(), algorithm)

    def compute_hmac(
        self, data: bytes, key: bytes, algorithm: MACAlgorithm
    ) -> Result[bytes]:
        """Compute HMAC."""
        try:
            # Map MAC algorithm to hash algorithm
            hash_algo = algorithm.value.replace("hmac_", "")

            if hash_algo == "sha3_256" and not hasattr(hashlib, "sha3_256"):
                return Result.failure(
                    ValueError(f"Unsupported MAC algorithm: {algorithm.value}")
                )

            mac = hmac.new(key, data, getattr(hashlib, hash_algo))
            return Result.success(mac.digest())

        except Exception as e:
            logger.error(f"Failed to compute HMAC: {e}")
            return Result.failure(e)

    def compute_hmac_hex(
        self, data: bytes, key: bytes, algorithm: MACAlgorithm
    ) -> Result[str]:
        """Compute HMAC as hex string."""
        result = self.compute_hmac(data, key, algorithm)
        if result.is_success:
            return Result.success(result.value.hex())
        return result

    def verify_hmac(
        self, data: bytes, expected_hmac: bytes, key: bytes, algorithm: MACAlgorithm
    ) -> Result[bool]:
        """Verify HMAC."""
        result = self.compute_hmac(data, key, algorithm)
        if result.is_success:
            is_valid = hmac.compare_digest(expected_hmac, result.value)
            return Result.success(is_valid)
        return result

    def compute_file_hash(
        self, file_path: str, algorithm: HashAlgorithm
    ) -> Result[str]:
        """Compute hash of file."""
        try:
            hash_obj = hashlib.new(algorithm.value)

            with open(file_path, "rb") as f:
                while chunk := f.read(8192):
                    hash_obj.update(chunk)

            return Result.success(hash_obj.hexdigest())

        except Exception as e:
            logger.error(f"Failed to compute file hash: {e}")
            return Result.failure(e)


class PasswordStrengthLevel(Enum):
    """Password strength levels."""

    VERY_WEAK = 0
    WEAK = 1
    FAIR = 2
    GOOD = 3
    STRONG = 4
    VERY_STRONG = 5


@dataclass
class PasswordStrength:
    """Password strength assessment."""

    level: PasswordStrengthLevel
    score: int
    feedback: List[str]


class PasswordUtils:
    """Password utility functions."""

    @staticmethod
    def generate_secure_password(
        length: int = 16,
        include_uppercase: bool = True,
        include_lowercase: bool = True,
        include_numbers: bool = True,
        include_special_chars: bool = True,
    ) -> str:
        """Generate a secure password."""
        charset = ""

        if include_uppercase:
            charset += string.ascii_uppercase
        if include_lowercase:
            charset += string.ascii_lowercase
        if include_numbers:
            charset += string.digits
        if include_special_chars:
            charset += "!@#$%^&*()_+-=[]{}|;:,.<>?"

        if not charset:
            raise ValueError("At least one character type must be included")

        return "".join(secrets.choice(charset) for _ in range(length))

    @staticmethod
    def check_password_strength(password: str) -> PasswordStrength:
        """Check password strength."""
        score = 0
        feedback = []

        if len(password) >= 8:
            score += 1
        else:
            feedback.append("Password should be at least 8 characters")

        if len(password) >= 12:
            score += 1

        if any(c.isupper() for c in password):
            score += 1
        else:
            feedback.append("Include uppercase letters")

        if any(c.islower() for c in password):
            score += 1
        else:
            feedback.append("Include lowercase letters")

        if any(c.isdigit() for c in password):
            score += 1
        else:
            feedback.append("Include numbers")

        if any(not c.isalnum() for c in password):
            score += 1
        else:
            feedback.append("Include special characters")

        strength_level = PasswordStrengthLevel(min(score, 5))

        return PasswordStrength(strength_level, score, feedback)

    @staticmethod
    def generate_salt(size: int = 32) -> bytes:
        """Generate salt for password hashing."""
        return secrets.token_bytes(size)


class KeyUtils:
    """Key utility functions."""

    @staticmethod
    def export_public_key_to_pem(public_key: Any) -> str:
        """Export public key to PEM format."""
        if HAS_CRYPTOGRAPHY:
            pem_bytes = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            return pem_bytes.decode()
        else:
            # Fallback for demonstration
            encoded = base64.b64encode(str(public_key).encode()).decode()
            return f"-----BEGIN PUBLIC KEY-----\n{encoded}\n-----END PUBLIC KEY-----"

    @staticmethod
    def export_private_key_to_pem(
        private_key: Any, password: Optional[bytes] = None
    ) -> str:
        """Export private key to PEM format."""
        if HAS_CRYPTOGRAPHY:
            encryption = serialization.NoEncryption()
            if password:
                encryption = serialization.BestAvailableEncryption(password)

            pem_bytes = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=encryption,
            )
            return pem_bytes.decode()
        else:
            # Fallback for demonstration
            encoded = base64.b64encode(str(private_key).encode()).decode()
            return f"-----BEGIN PRIVATE KEY-----\n{encoded}\n-----END PRIVATE KEY-----"

    @staticmethod
    def import_public_key_from_pem(pem: str) -> Result[Any]:
        """Import public key from PEM format."""
        if not HAS_CRYPTOGRAPHY:
            return Result.failure(ImportError("cryptography library not available"))

        try:
            public_key = serialization.load_pem_public_key(
                pem.encode(), backend=default_backend()
            )
            return Result.success(public_key)
        except Exception as e:
            return Result.failure(e)

    @staticmethod
    def import_private_key_from_pem(
        pem: str, password: Optional[bytes] = None
    ) -> Result[Any]:
        """Import private key from PEM format."""
        if not HAS_CRYPTOGRAPHY:
            return Result.failure(ImportError("cryptography library not available"))

        try:
            private_key = serialization.load_pem_private_key(
                pem.encode(), password=password, backend=default_backend()
            )
            return Result.success(private_key)
        except Exception as e:
            return Result.failure(e)

    @staticmethod
    def generate_key_fingerprint(public_key: Any) -> str:
        """Generate key fingerprint."""
        if HAS_CRYPTOGRAPHY:
            key_bytes = public_key.public_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        else:
            key_bytes = str(public_key).encode()

        digest = hashlib.sha256(key_bytes).digest()
        return ":".join(f"{b:02x}" for b in digest)
