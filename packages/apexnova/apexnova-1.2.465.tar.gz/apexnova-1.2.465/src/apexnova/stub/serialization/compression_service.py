"""
CompressionService - Handles data compression and decompression

Supports multiple compression algorithms:
- GZIP
- DEFLATE
- BROTLI
- LZ4
- SNAPPY
"""

import gzip
import zlib
import logging
from typing import Dict, Callable

# Circular import resolved by defining CompressionType here
from enum import Enum


class CompressionType(Enum):
    """Supported compression algorithms"""

    NONE = "none"
    GZIP = "gzip"
    DEFLATE = "deflate"
    BROTLI = "brotli"
    LZ4 = "lz4"
    SNAPPY = "snappy"


logger = logging.getLogger(__name__)


class CompressionService:
    """Service for handling data compression and decompression"""

    def __init__(self):
        self._compressors: Dict[CompressionType, Callable[[bytes], bytes]] = {
            CompressionType.NONE: self._compress_none,
            CompressionType.GZIP: self._compress_gzip,
            CompressionType.DEFLATE: self._compress_deflate,
            CompressionType.BROTLI: self._compress_brotli,
            CompressionType.LZ4: self._compress_lz4,
            CompressionType.SNAPPY: self._compress_snappy,
        }

        self._decompressors: Dict[CompressionType, Callable[[bytes], bytes]] = {
            CompressionType.NONE: self._decompress_none,
            CompressionType.GZIP: self._decompress_gzip,
            CompressionType.DEFLATE: self._decompress_deflate,
            CompressionType.BROTLI: self._decompress_brotli,
            CompressionType.LZ4: self._decompress_lz4,
            CompressionType.SNAPPY: self._decompress_snappy,
        }

    def compress(self, data: bytes, compression_type: CompressionType) -> bytes:
        """Compress data using specified algorithm"""
        try:
            compressor = self._compressors.get(compression_type)
            if not compressor:
                raise ValueError(f"Unsupported compression type: {compression_type}")
            return compressor(data)
        except Exception as e:
            logger.error(f"Compression failed with {compression_type}: {e}")
            raise

    async def compress_async(
        self, data: bytes, compression_type: CompressionType
    ) -> bytes:
        """Compress data using specified algorithm (async version)"""
        return self.compress(data, compression_type)

    def decompress(self, data: bytes, compression_type: CompressionType) -> bytes:
        """Decompress data using specified algorithm"""
        try:
            decompressor = self._decompressors.get(compression_type)
            if not decompressor:
                raise ValueError(f"Unsupported compression type: {compression_type}")
            return decompressor(data)
        except Exception as e:
            logger.error(f"Decompression failed with {compression_type}: {e}")
            raise

    async def decompress_async(
        self, data: bytes, compression_type: CompressionType
    ) -> bytes:
        """Decompress data using specified algorithm (async version)"""
        return self.decompress(data, compression_type)

    def _compress_none(self, data: bytes) -> bytes:
        """No compression - return data as-is"""
        return data

    def _decompress_none(self, data: bytes) -> bytes:
        """No decompression - return data as-is"""
        return data

    def _compress_gzip(self, data: bytes) -> bytes:
        """Compress data using GZIP"""
        return gzip.compress(data)

    def _decompress_gzip(self, data: bytes) -> bytes:
        """Decompress data using GZIP"""
        return gzip.decompress(data)

    def _compress_deflate(self, data: bytes) -> bytes:
        """Compress data using DEFLATE"""
        return zlib.compress(data)

    def _decompress_deflate(self, data: bytes) -> bytes:
        """Decompress data using DEFLATE"""
        return zlib.decompress(data)

    def _compress_brotli(self, data: bytes) -> bytes:
        """Compress data using Brotli"""
        try:
            import brotli

            return brotli.compress(data)
        except ImportError:
            logger.warning("Brotli not available, falling back to GZIP")
            return self._compress_gzip(data)

    def _decompress_brotli(self, data: bytes) -> bytes:
        """Decompress data using Brotli"""
        try:
            import brotli

            return brotli.decompress(data)
        except ImportError:
            logger.warning("Brotli not available, falling back to GZIP")
            return self._decompress_gzip(data)

    def _compress_lz4(self, data: bytes) -> bytes:
        """Compress data using LZ4"""
        try:
            import lz4.frame

            return lz4.frame.compress(data)
        except ImportError:
            logger.warning("LZ4 not available, falling back to GZIP")
            return self._compress_gzip(data)

    def _decompress_lz4(self, data: bytes) -> bytes:
        """Decompress data using LZ4"""
        try:
            import lz4.frame

            return lz4.frame.decompress(data)
        except ImportError:
            logger.warning("LZ4 not available, falling back to GZIP")
            return self._decompress_gzip(data)

    def _compress_snappy(self, data: bytes) -> bytes:
        """Compress data using Snappy"""
        try:
            import snappy

            return snappy.compress(data)
        except ImportError:
            logger.warning("Snappy not available, falling back to GZIP")
            return self._compress_gzip(data)

    def _decompress_snappy(self, data: bytes) -> bytes:
        """Decompress data using Snappy"""
        try:
            import snappy

            return snappy.decompress(data)
        except ImportError:
            logger.warning("Snappy not available, falling back to GZIP")
            return self._decompress_gzip(data)

    def get_supported_algorithms(self) -> list[CompressionType]:
        """Get list of supported compression algorithms"""
        supported = [
            CompressionType.NONE,
            CompressionType.GZIP,
            CompressionType.DEFLATE,
        ]

        # Check for optional dependencies
        try:
            import brotli

            supported.append(CompressionType.BROTLI)
        except ImportError:
            pass

        try:
            import lz4.frame

            supported.append(CompressionType.LZ4)
        except ImportError:
            pass

        try:
            import snappy

            supported.append(CompressionType.SNAPPY)
        except ImportError:
            pass

        return supported

    def get_compression_ratio(
        self, original_data: bytes, compressed_data: bytes
    ) -> float:
        """Calculate compression ratio"""
        if len(original_data) == 0:
            return 0.0
        return len(compressed_data) / len(original_data)

    def estimate_compression_benefit(
        self, data: bytes, compression_type: CompressionType
    ) -> Dict[str, float]:
        """Estimate compression benefit for given data"""
        if compression_type == CompressionType.NONE:
            return {"ratio": 1.0, "size_reduction": 0.0, "benefit": False}

        try:
            compressed = self._compressors[compression_type](data)
            ratio = self.get_compression_ratio(data, compressed)
            size_reduction = (len(data) - len(compressed)) / len(data) * 100
            benefit = ratio < 0.9  # Consider beneficial if 10%+ reduction

            return {
                "ratio": ratio,
                "size_reduction": size_reduction,
                "benefit": benefit,
                "original_size": len(data),
                "compressed_size": len(compressed),
            }
        except Exception as e:
            logger.error(f"Failed to estimate compression benefit: {e}")
            return {
                "ratio": 1.0,
                "size_reduction": 0.0,
                "benefit": False,
                "error": str(e),
            }
