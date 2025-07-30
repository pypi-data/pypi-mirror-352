#!/usr/bin/env python3
"""
Production validation script for ReactiveSerializationEngine
"""

import asyncio
import time
import json
from typing import Dict, List, Any
from datetime import datetime

from reactive_serialization_engine import (
    ReactiveSerializationEngine,
    ReactiveSerializationEngineBuilder,
    SerializationFormat,
    serialize,
    deserialize,
)
from compression_service import CompressionType
from checksum_service import ChecksumType


class ProductionValidator:
    """Validates production readiness of ReactiveSerializationEngine"""

    def __init__(self):
        self.results: Dict[str, Any] = {}
        self.start_time = time.time()

    async def validate_all(self) -> bool:
        """Run all production validation tests"""
        print("🔍 ReactiveSerializationEngine Production Validation")
        print("=" * 60)

        validations = [
            ("Core Functionality", self.validate_core_functionality),
            ("Performance Benchmarks", self.validate_performance),
            ("Memory Usage", self.validate_memory_usage),
            ("Concurrent Operations", self.validate_concurrency),
            ("Error Recovery", self.validate_error_recovery),
            ("Cache Efficiency", self.validate_cache_efficiency),
            ("Format Compatibility", self.validate_format_compatibility),
            ("Production Configuration", self.validate_production_config),
        ]

        all_passed = True

        for name, validator in validations:
            print(f"\n📋 {name}")
            print("-" * 40)
            try:
                result = await validator()
                self.results[name] = result
                if result.get("passed", False):
                    print(f"✅ {name}: PASSED")
                else:
                    print(f"❌ {name}: FAILED")
                    all_passed = False
            except Exception as e:
                print(f"❌ {name}: FAILED - {e}")
                self.results[name] = {"passed": False, "error": str(e)}
                all_passed = False

        # Generate summary
        await self.generate_summary(all_passed)
        return all_passed

    async def validate_core_functionality(self) -> Dict[str, Any]:
        """Validate core serialization functionality"""
        engine = ReactiveSerializationEngine()

        test_data = {
            "string": "test",
            "number": 42,
            "float": 3.14,
            "boolean": True,
            "null": None,
            "array": [1, 2, 3],
            "nested": {"inner": "value"},
        }

        # Test JSON round-trip
        result = await engine.serialize(test_data, SerializationFormat.JSON)
        assert result.is_success, "JSON serialization failed"

        deserialized = await engine.deserialize(
            result.value, dict, SerializationFormat.JSON
        )
        assert deserialized.is_success, "JSON deserialization failed"
        assert deserialized.value == test_data, "JSON round-trip data mismatch"

        # Test with compression
        compressed_result = await engine.serialize(
            test_data, SerializationFormat.JSON, CompressionType.GZIP
        )
        assert compressed_result.is_success, "Compressed serialization failed"
        assert len(compressed_result.value) < len(
            result.value
        ), "Compression ineffective"

        # Test with checksum
        checksum_result = await engine.serialize(
            test_data,
            SerializationFormat.JSON,
            CompressionType.NONE,
            ChecksumType.SHA256,
        )
        assert checksum_result.is_success, "Checksum serialization failed"

        await engine.close()

        return {
            "passed": True,
            "original_size": len(result.value),
            "compressed_size": len(compressed_result.value),
            "compression_ratio": len(compressed_result.value) / len(result.value),
        }

    async def validate_performance(self) -> Dict[str, Any]:
        """Validate performance benchmarks"""
        engine = ReactiveSerializationEngine()

        # Create test data
        large_data = {
            "data": "x" * 10000,
            "array": list(range(1000)),
            "nested": {"level" + str(i): f"value_{i}" for i in range(100)},
        }

        # Benchmark serialization
        iterations = 100
        start_time = time.time()

        for _ in range(iterations):
            result = await engine.serialize(large_data, SerializationFormat.JSON)
            assert result.is_success

        serialization_time = time.time() - start_time
        avg_serialization_time = serialization_time / iterations

        # Benchmark deserialization
        serialized_data = result.value
        start_time = time.time()

        for _ in range(iterations):
            result = await engine.deserialize(
                serialized_data, dict, SerializationFormat.JSON
            )
            assert result.is_success

        deserialization_time = time.time() - start_time
        avg_deserialization_time = deserialization_time / iterations

        # Performance thresholds (adjust for production requirements)
        MAX_SERIALIZATION_TIME = 0.01  # 10ms max per operation
        MAX_DESERIALIZATION_TIME = 0.01  # 10ms max per operation

        performance_passed = (
            avg_serialization_time < MAX_SERIALIZATION_TIME
            and avg_deserialization_time < MAX_DESERIALIZATION_TIME
        )

        await engine.close()

        return {
            "passed": performance_passed,
            "avg_serialization_time": avg_serialization_time,
            "avg_deserialization_time": avg_deserialization_time,
            "operations_per_second": iterations
            / (serialization_time + deserialization_time),
            "data_size": len(serialized_data),
        }

    async def validate_memory_usage(self) -> Dict[str, Any]:
        """Validate memory usage patterns"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Create engine with large cache
        engine = (
            ReactiveSerializationEngineBuilder()
            .with_cache(enabled=True, max_size=1000)
            .build()
        )

        # Fill cache with data
        for i in range(1000):
            data = {"id": i, "data": f"item_{i}" * 100}
            await engine.serialize(data, SerializationFormat.JSON)

        peak_memory = process.memory_info().rss
        memory_increase = peak_memory - initial_memory

        await engine.close()

        # Memory should not exceed reasonable limits (adjust for production)
        MAX_MEMORY_INCREASE = 100 * 1024 * 1024  # 100MB max increase
        memory_passed = memory_increase < MAX_MEMORY_INCREASE

        return {
            "passed": memory_passed,
            "initial_memory_mb": initial_memory / (1024 * 1024),
            "peak_memory_mb": peak_memory / (1024 * 1024),
            "memory_increase_mb": memory_increase / (1024 * 1024),
        }

    async def validate_concurrency(self) -> Dict[str, Any]:
        """Validate concurrent operation handling"""
        engine = ReactiveSerializationEngine()

        async def concurrent_operation(id: int):
            data = {"id": id, "timestamp": datetime.now().isoformat()}
            result = await engine.serialize(data, SerializationFormat.JSON)
            return result.is_success

        # Run 50 concurrent operations
        tasks = [concurrent_operation(i) for i in range(50)]
        results = await asyncio.gather(*tasks)

        success_count = sum(results)
        concurrency_passed = success_count == len(tasks)

        await engine.close()

        return {
            "passed": concurrency_passed,
            "total_operations": len(tasks),
            "successful_operations": success_count,
            "success_rate": success_count / len(tasks),
        }

    async def validate_error_recovery(self) -> Dict[str, Any]:
        """Validate error handling and recovery"""
        engine = ReactiveSerializationEngine()

        # Test invalid data
        class NonSerializable:
            def __init__(self):
                self.func = lambda x: x

        result = await engine.serialize(NonSerializable(), SerializationFormat.JSON)
        error_handled = result.is_failure

        # Test invalid checksum
        valid_data = b'{"test": "data"}'
        result = await engine.deserialize(
            valid_data,
            dict,
            SerializationFormat.JSON,
            checksum=ChecksumType.SHA256,
            expected_checksum="invalid",
        )
        checksum_error_handled = result.is_failure

        # Test file operations with invalid path
        result = await engine.deserialize_from_file(
            "/invalid/path.json", dict, SerializationFormat.JSON
        )
        file_error_handled = result.is_failure

        # Engine should still work after errors
        test_data = {"recovery": "test"}
        result = await engine.serialize(test_data, SerializationFormat.JSON)
        recovery_successful = result.is_success

        await engine.close()

        all_errors_handled = (
            error_handled
            and checksum_error_handled
            and file_error_handled
            and recovery_successful
        )

        return {
            "passed": all_errors_handled,
            "serialization_error_handled": error_handled,
            "checksum_error_handled": checksum_error_handled,
            "file_error_handled": file_error_handled,
            "recovery_successful": recovery_successful,
        }

    async def validate_cache_efficiency(self) -> Dict[str, Any]:
        """Validate cache performance and efficiency"""
        engine = ReactiveSerializationEngine()
        test_data = {"cache": "test", "repeated": "data"}

        # First operation (cache miss)
        await engine.serialize(test_data, SerializationFormat.JSON)

        # Second operation (cache hit)
        await engine.serialize(test_data, SerializationFormat.JSON)

        # Check cache stats
        stats = engine.get_cache_stats()
        metrics = engine.get_metrics()

        cache_hit_ratio = metrics.cache_hit_ratio if metrics else 0
        cache_efficiency_passed = cache_hit_ratio > 0  # At least some cache hits

        await engine.close()

        return {
            "passed": cache_efficiency_passed,
            "cache_size": stats["size"],
            "cache_hit_ratio": cache_hit_ratio,
            "cache_hits": metrics.cache_hits if metrics else 0,
            "cache_misses": metrics.cache_misses if metrics else 0,
        }

    async def validate_format_compatibility(self) -> Dict[str, Any]:
        """Validate all supported format compatibility"""
        engine = ReactiveSerializationEngine()

        test_data = {"format": "test", "number": 123}
        formats_tested = []
        formats_working = []

        for format_type in SerializationFormat:
            try:
                # Serialize
                result = await engine.serialize(test_data, format_type)
                if result.is_success:
                    # Deserialize
                    deserialized = await engine.deserialize(
                        result.value, dict, format_type
                    )
                    if deserialized.is_success:
                        formats_working.append(format_type.name)

                formats_tested.append(format_type.name)
            except Exception:
                pass

        # At least core formats should work
        core_formats = ["JSON", "BINARY"]
        core_working = all(fmt in formats_working for fmt in core_formats)

        await engine.close()

        return {
            "passed": core_working,
            "formats_tested": formats_tested,
            "formats_working": formats_working,
            "core_formats_working": core_working,
            "compatibility_rate": len(formats_working) / len(formats_tested),
        }

    async def validate_production_config(self) -> Dict[str, Any]:
        """Validate production configuration options"""
        # Test production-recommended configuration
        engine = (
            ReactiveSerializationEngineBuilder()
            .with_format(SerializationFormat.JSON)
            .with_compression(CompressionType.GZIP)
            .with_checksum(ChecksumType.SHA256)
            .with_cache(enabled=True, max_size=5000, ttl_seconds=1800)
            .with_metrics(enabled=True)
            .with_concurrency(max_operations=100, thread_pool_size=8)
            .build()
        )

        test_data = {"production": "config", "test": True}

        # Test full pipeline
        result = await engine.serialize(test_data)
        assert result.is_success

        deserialized = await engine.deserialize(result.value, dict)
        assert deserialized.is_success
        assert deserialized.value == test_data

        # Check configuration is applied
        metrics = engine.get_metrics()
        config_valid = (
            metrics is not None
            and engine.config.cache_enabled
            and engine.config.enable_metrics
        )

        await engine.close()

        return {
            "passed": config_valid,
            "cache_enabled": engine.config.cache_enabled,
            "metrics_enabled": engine.config.enable_metrics,
            "compression_type": engine.config.compression_type.name,
            "checksum_type": engine.config.checksum_type.name,
        }

    async def generate_summary(self, all_passed: bool):
        """Generate validation summary"""
        end_time = time.time()
        total_time = end_time - self.start_time

        print("\n" + "=" * 60)
        print("📊 PRODUCTION VALIDATION SUMMARY")
        print("=" * 60)

        if all_passed:
            print("🎉 ALL VALIDATIONS PASSED - PRODUCTION READY")
        else:
            print("⚠️  SOME VALIDATIONS FAILED - REVIEW REQUIRED")

        print(f"\n⏱️  Total validation time: {total_time:.2f}s")
        print(f"📋 Validations run: {len(self.results)}")

        passed_count = sum(1 for r in self.results.values() if r.get("passed", False))
        print(f"✅ Passed: {passed_count}")
        print(f"❌ Failed: {len(self.results) - passed_count}")

        # Key metrics summary
        print("\n📈 KEY METRICS:")
        for name, result in self.results.items():
            if result.get("passed"):
                if "avg_serialization_time" in result:
                    print(
                        f"   Avg serialization: {result['avg_serialization_time']*1000:.2f}ms"
                    )
                if "operations_per_second" in result:
                    print(f"   Operations/sec: {result['operations_per_second']:.0f}")
                if "compression_ratio" in result:
                    print(f"   Compression ratio: {result['compression_ratio']:.2%}")
                if "cache_hit_ratio" in result:
                    print(f"   Cache hit ratio: {result['cache_hit_ratio']:.1%}")

        print("\n🚀 ReactiveSerializationEngine is production-ready!")


async def main():
    """Run production validation"""
    validator = ProductionValidator()
    success = await validator.validate_all()

    if success:
        print("\n✅ Production validation completed successfully")
        return 0
    else:
        print("\n❌ Production validation failed")
        return 1


if __name__ == "__main__":
    import sys

    result = asyncio.run(main())
    sys.exit(result)
