"""
ChecksumService - Handles data integrity verification

Supports multiple checksum algorithms:
- CRC32
- MD5
- SHA256
- SHA512
"""

import hashlib
import zlib
import logging
from typing import Dict, Callable, Any

# Circular import resolved by defining ChecksumType here
from enum import Enum


class ChecksumType(Enum):
    """Supported checksum algorithms"""

    NONE = "none"
    CRC32 = "crc32"
    MD5 = "md5"
    SHA256 = "sha256"
    SHA512 = "sha512"


logger = logging.getLogger(__name__)


class ChecksumService:
    """Service for calculating and verifying data checksums"""

    def __init__(self):
        self._calculators: Dict[ChecksumType, Callable[[bytes], str]] = {
            ChecksumType.NONE: self._calculate_none,
            ChecksumType.CRC32: self._calculate_crc32,
            ChecksumType.MD5: self._calculate_md5,
            ChecksumType.SHA256: self._calculate_sha256,
            ChecksumType.SHA512: self._calculate_sha512,
        }

    def calculate_checksum(self, data: bytes, checksum_type: ChecksumType) -> str:
        """Calculate checksum for data using specified algorithm"""
        try:
            calculator = self._calculators.get(checksum_type)
            if not calculator:
                raise ValueError(f"Unsupported checksum type: {checksum_type}")
            return calculator(data)
        except Exception as e:
            logger.error(f"Checksum calculation failed with {checksum_type}: {e}")
            raise

    async def calculate(self, data: bytes, checksum_type: ChecksumType) -> str:
        """Calculate checksum for data using specified algorithm (async version)"""
        return self.calculate_checksum(data, checksum_type)

    def verify_checksum(
        self, data: bytes, checksum_type: ChecksumType, expected_checksum: str
    ) -> bool:
        """Verify data integrity against expected checksum"""
        try:
            calculated_checksum = self.calculate_checksum(data, checksum_type)
            return calculated_checksum.lower() == expected_checksum.lower()
        except Exception as e:
            logger.error(f"Checksum verification failed: {e}")
            return False

    async def verify(
        self, data: bytes, expected_checksum: str, checksum_type: ChecksumType
    ) -> bool:
        """Verify data integrity against expected checksum (async version)"""
        return self.verify_checksum(data, checksum_type, expected_checksum)

    def _calculate_none(self, data: bytes) -> str:
        """No checksum calculation"""
        return ""

    def _calculate_crc32(self, data: bytes) -> str:
        """Calculate CRC32 checksum"""
        crc = zlib.crc32(data) & 0xFFFFFFFF
        return str(crc)

    def _calculate_md5(self, data: bytes) -> str:
        """Calculate MD5 hash"""
        md5_hash = hashlib.md5()
        md5_hash.update(data)
        return md5_hash.hexdigest()

    def _calculate_sha256(self, data: bytes) -> str:
        """Calculate SHA256 hash"""
        sha256_hash = hashlib.sha256()
        sha256_hash.update(data)
        return sha256_hash.hexdigest()

    def _calculate_sha512(self, data: bytes) -> str:
        """Calculate SHA512 hash"""
        sha512_hash = hashlib.sha512()
        sha512_hash.update(data)
        return sha512_hash.hexdigest()

    def get_supported_algorithms(self) -> list[ChecksumType]:
        """Get list of supported checksum algorithms"""
        return list(self._calculators.keys())

    def get_algorithm_strength(self, checksum_type: ChecksumType) -> Dict[str, Any]:
        """Get information about algorithm strength and properties"""
        strength_info = {
            ChecksumType.NONE: {
                "strength": "none",
                "collision_resistance": "none",
                "cryptographic": False,
                "speed": "instant",
                "output_size": 0,
            },
            ChecksumType.CRC32: {
                "strength": "low",
                "collision_resistance": "low",
                "cryptographic": False,
                "speed": "very_fast",
                "output_size": 8,  # hex chars
            },
            ChecksumType.MD5: {
                "strength": "weak",
                "collision_resistance": "broken",
                "cryptographic": True,
                "speed": "fast",
                "output_size": 32,  # hex chars
            },
            ChecksumType.SHA256: {
                "strength": "strong",
                "collision_resistance": "strong",
                "cryptographic": True,
                "speed": "medium",
                "output_size": 64,  # hex chars
            },
            ChecksumType.SHA512: {
                "strength": "very_strong",
                "collision_resistance": "very_strong",
                "cryptographic": True,
                "speed": "medium",
                "output_size": 128,  # hex chars
            },
        }

        return strength_info.get(checksum_type, {})

    def recommend_algorithm(self, use_case: str = "general") -> ChecksumType:
        """Recommend checksum algorithm based on use case"""
        recommendations = {
            "general": ChecksumType.SHA256,
            "performance": ChecksumType.CRC32,
            "security": ChecksumType.SHA512,
            "compatibility": ChecksumType.MD5,
            "fast": ChecksumType.CRC32,
            "cryptographic": ChecksumType.SHA256,
        }

        return recommendations.get(use_case.lower(), ChecksumType.SHA256)

    async def calculate_multiple(
        self, data: bytes, checksum_types: list[ChecksumType]
    ) -> Dict[ChecksumType, str]:
        """Calculate multiple checksums for the same data"""
        results = {}
        for checksum_type in checksum_types:
            try:
                results[checksum_type] = await self.calculate(data, checksum_type)
            except Exception as e:
                logger.error(f"Failed to calculate {checksum_type} checksum: {e}")
                results[checksum_type] = None
        return results

    def compare_checksums(
        self, checksum1: str, checksum2: str, checksum_type: ChecksumType
    ) -> Dict[str, Any]:
        """Compare two checksums and provide detailed analysis"""
        match = checksum1.lower() == checksum2.lower()

        analysis = {
            "match": match,
            "checksum_type": checksum_type,
            "algorithm_info": self.get_algorithm_strength(checksum_type),
            "checksum1": checksum1,
            "checksum2": checksum2,
        }

        if not match:
            analysis["difference_analysis"] = {
                "length_difference": len(checksum1) - len(checksum2),
                "case_sensitive_match": checksum1 == checksum2,
                "potential_issue": "Data corruption or tampering detected",
            }

        return analysis
