"""
Reactive Validation Engine Implementation

A modern validation framework with reactive processing, caching, and comprehensive metrics.
Features:
- Type-safe validation rules with async support
- Validation result caching for performance
- Batch validation with concurrency control
- Field-level and object-level validation
- Comprehensive metrics and monitoring
- Fluent DSL for validation rule composition
"""

import asyncio
import re
import time
import uuid
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import (
    Any,
    AsyncIterator,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Protocol,
    Type,
    TypeVar,
    Union,
    runtime_checkable,
)
import logging
from concurrent.futures import ThreadPoolExecutor
from weakref import WeakValueDictionary

# Type variables
T = TypeVar("T")
P = TypeVar("P")


# Validation result types
class ValidationResult:
    """Base class for validation results"""

    pass


@dataclass(frozen=True)
class Valid(ValidationResult):
    """Validation passed"""

    pass


@dataclass(frozen=True)
class Invalid(ValidationResult):
    """Validation failed with errors"""

    errors: List["ValidationError"]


@dataclass(frozen=True)
class PartialValid(ValidationResult):
    """Validation partially passed with errors and warnings"""

    errors: List["ValidationError"]
    warnings: List["ValidationWarning"]


@dataclass(frozen=True)
class ValidationError:
    """Validation error details"""

    field: str
    message: str
    code: str
    value: Any


@dataclass(frozen=True)
class ValidationWarning:
    """Validation warning details"""

    field: str
    message: str
    value: Any


@dataclass
class ValidationContext:
    """Context for validation operations"""

    entity_id: str = ""
    entity_type: str = ""
    source: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)
    strict: bool = False
    locale: str = "en-US"


# Validation rule interface
class ValidationRule(ABC, Generic[T]):
    """Abstract base class for validation rules"""

    @abstractmethod
    async def validate(self, value: T, context: ValidationContext) -> ValidationResult:
        """Validate a value and return the result"""
        pass


# Composed validation rule
class ComposedValidationRule(ValidationRule[T]):
    """Validation rule that combines multiple rules"""

    def __init__(
        self, rules: List[ValidationRule[T]], stop_on_first_error: bool = False
    ):
        self.rules = rules
        self.stop_on_first_error = stop_on_first_error

    async def validate(self, value: T, context: ValidationContext) -> ValidationResult:
        errors = []
        warnings = []

        for rule in self.rules:
            result = await rule.validate(value, context)

            if isinstance(result, Valid):
                continue
            elif isinstance(result, Invalid):
                errors.extend(result.errors)
                if self.stop_on_first_error:
                    break
            elif isinstance(result, PartialValid):
                errors.extend(result.errors)
                warnings.extend(result.warnings)
                if self.stop_on_first_error and result.errors:
                    break

        if not errors and not warnings:
            return Valid()
        elif not errors:
            return PartialValid([], warnings)
        elif not warnings:
            return Invalid(errors)
        else:
            return PartialValid(errors, warnings)


# Object validation rule with field-level validation
class ObjectValidationRule(ValidationRule[T]):
    """Validation rule for objects with field-level rules"""

    def __init__(
        self, target_type: Type[T], field_rules: Dict[str, List[ValidationRule]]
    ):
        self.target_type = target_type
        self.field_rules = field_rules

    async def validate(self, value: T, context: ValidationContext) -> ValidationResult:
        if not isinstance(value, self.target_type):
            return Invalid(
                [
                    ValidationError(
                        field="type",
                        message=f"Expected {self.target_type.__name__}, got {type(value).__name__}",
                        code="TYPE_MISMATCH",
                        value=value,
                    )
                ]
            )

        # Validate all fields concurrently
        validation_tasks = []

        for field_name, rules in self.field_rules.items():
            if hasattr(value, field_name):
                field_value = getattr(value, field_name)
                field_context = ValidationContext(
                    entity_id=context.entity_id,
                    entity_type=context.entity_type,
                    source=context.source,
                    metadata={**context.metadata, "field": field_name},
                    strict=context.strict,
                    locale=context.locale,
                )

                task = asyncio.create_task(
                    ComposedValidationRule(rules).validate(field_value, field_context)
                )
                validation_tasks.append(task)

        if not validation_tasks:
            return Valid()

        results = await asyncio.gather(*validation_tasks)

        all_errors = []
        all_warnings = []

        for result in results:
            if isinstance(result, Invalid):
                all_errors.extend(result.errors)
            elif isinstance(result, PartialValid):
                all_errors.extend(result.errors)
                all_warnings.extend(result.warnings)

        if not all_errors and not all_warnings:
            return Valid()
        elif not all_errors:
            return PartialValid([], all_warnings)
        elif not all_warnings:
            return Invalid(all_errors)
        else:
            return PartialValid(all_errors, all_warnings)


# Field validation builder
class FieldValidationBuilder(Generic[T]):
    """Builder for field-level validation rules"""

    def __init__(self, target_type: Type[T]):
        self.target_type = target_type
        self.field_rules: Dict[str, List[ValidationRule]] = defaultdict(list)

    def field(
        self, field_name: str, *rules: ValidationRule
    ) -> "FieldValidationBuilder[T]":
        """Add validation rules for a field"""
        self.field_rules[field_name].extend(rules)
        return self

    def build(self) -> ObjectValidationRule[T]:
        """Build the object validation rule"""
        return ObjectValidationRule(self.target_type, dict(self.field_rules))


# Common validation rules
class CommonValidationRules:
    """Collection of common validation rules"""

    @staticmethod
    def required() -> ValidationRule[Optional[Any]]:
        """Validate that a value is not None or empty"""

        class RequiredRule(ValidationRule[Optional[Any]]):
            async def validate(
                self, value: Optional[Any], context: ValidationContext
            ) -> ValidationResult:
                field = context.metadata.get("field", "unknown")

                if value is None:
                    return Invalid(
                        [ValidationError(field, "Value is required", "REQUIRED", value)]
                    )

                if isinstance(value, str) and not value.strip():
                    return Invalid(
                        [
                            ValidationError(
                                field, "Value cannot be empty", "REQUIRED", value
                            )
                        ]
                    )

                if isinstance(value, (list, dict, tuple, set)) and len(value) == 0:
                    return Invalid(
                        [
                            ValidationError(
                                field, "Value cannot be empty", "REQUIRED", value
                            )
                        ]
                    )

                return Valid()

        return RequiredRule()

    @staticmethod
    def string_length(
        min_length: Optional[int] = None, max_length: Optional[int] = None
    ) -> ValidationRule[Optional[str]]:
        """Validate string length"""

        class StringLengthRule(ValidationRule[Optional[str]]):
            async def validate(
                self, value: Optional[str], context: ValidationContext
            ) -> ValidationResult:
                if value is None:
                    return Valid()

                field = context.metadata.get("field", "unknown")
                errors = []

                if min_length is not None and len(value) < min_length:
                    errors.append(
                        ValidationError(
                            field,
                            f"Minimum length is {min_length}",
                            "MIN_LENGTH",
                            value,
                        )
                    )

                if max_length is not None and len(value) > max_length:
                    errors.append(
                        ValidationError(
                            field,
                            f"Maximum length is {max_length}",
                            "MAX_LENGTH",
                            value,
                        )
                    )

                return Invalid(errors) if errors else Valid()

        return StringLengthRule()

    @staticmethod
    def number_range(
        min_value: Optional[float] = None, max_value: Optional[float] = None
    ) -> ValidationRule[Optional[Union[int, float]]]:
        """Validate number range"""

        class NumberRangeRule(ValidationRule[Optional[Union[int, float]]]):
            async def validate(
                self, value: Optional[Union[int, float]], context: ValidationContext
            ) -> ValidationResult:
                if value is None:
                    return Valid()

                field = context.metadata.get("field", "unknown")
                errors = []

                if min_value is not None and value < min_value:
                    errors.append(
                        ValidationError(
                            field, f"Minimum value is {min_value}", "MIN_VALUE", value
                        )
                    )

                if max_value is not None and value > max_value:
                    errors.append(
                        ValidationError(
                            field, f"Maximum value is {max_value}", "MAX_VALUE", value
                        )
                    )

                return Invalid(errors) if errors else Valid()

        return NumberRangeRule()

    @staticmethod
    def pattern(
        regex_pattern: str, message: str = "Invalid format"
    ) -> ValidationRule[Optional[str]]:
        """Validate string pattern"""

        class PatternRule(ValidationRule[Optional[str]]):
            def __init__(self):
                self.pattern = re.compile(regex_pattern)

            async def validate(
                self, value: Optional[str], context: ValidationContext
            ) -> ValidationResult:
                if value is None:
                    return Valid()

                field = context.metadata.get("field", "unknown")

                if not self.pattern.match(value):
                    return Invalid(
                        [ValidationError(field, message, "PATTERN_MISMATCH", value)]
                    )

                return Valid()

        return PatternRule()

    @staticmethod
    def email() -> ValidationRule[Optional[str]]:
        """Validate email format"""
        email_pattern = r"^[A-Za-z0-9+_.-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})$"
        return CommonValidationRules.pattern(email_pattern, "Invalid email format")

    @staticmethod
    def uuid() -> ValidationRule[Optional[str]]:
        """Validate UUID format"""
        uuid_pattern = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
        return CommonValidationRules.pattern(uuid_pattern, "Invalid UUID format")

    @staticmethod
    def custom(
        predicate: Callable[[Any], bool], message: str, code: str = "CUSTOM"
    ) -> ValidationRule[Any]:
        """Create custom validation rule"""

        class CustomRule(ValidationRule[Any]):
            async def validate(
                self, value: Any, context: ValidationContext
            ) -> ValidationResult:
                field = context.metadata.get("field", "unknown")

                try:
                    if (
                        await predicate(value)
                        if asyncio.iscoroutinefunction(predicate)
                        else predicate(value)
                    ):
                        return Valid()
                    else:
                        return Invalid([ValidationError(field, message, code, value)])
                except Exception as e:
                    return Invalid(
                        [
                            ValidationError(
                                field,
                                f"Validation error: {e}",
                                "VALIDATION_ERROR",
                                value,
                            )
                        ]
                    )

        return CustomRule()


# Validation cache for performance optimization
class ValidationCache:
    """LRU cache for validation results"""

    @dataclass
    class CachedValidationResult:
        result: ValidationResult
        timestamp: datetime
        hit_count: int = 0

    def __init__(self, max_size: int = 10000, ttl: timedelta = timedelta(minutes=5)):
        self.max_size = max_size
        self.ttl = ttl
        self._cache: Dict[str, ValidationCache.CachedValidationResult] = {}
        self._access_order: Dict[str, float] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[ValidationResult]:
        """Get cached validation result"""
        async with self._lock:
            cached = self._cache.get(key)

            if cached and datetime.now() - cached.timestamp < self.ttl:
                cached.hit_count += 1
                self._access_order[key] = time.time()
                return cached.result
            elif cached:
                # Expired entry
                del self._cache[key]
                self._access_order.pop(key, None)

        return None

    async def put(self, key: str, result: ValidationResult):
        """Cache validation result"""
        async with self._lock:
            if len(self._cache) >= self.max_size:
                await self._evict_oldest()

            self._cache[key] = ValidationCache.CachedValidationResult(
                result=result, timestamp=datetime.now(), hit_count=0
            )
            self._access_order[key] = time.time()

    async def _evict_oldest(self):
        """Evict the oldest entry from cache"""
        if not self._access_order:
            return

        oldest_key = min(self._access_order.keys(), key=lambda k: self._access_order[k])
        self._cache.pop(oldest_key, None)
        self._access_order.pop(oldest_key, None)

    async def clear(self):
        """Clear the cache"""
        async with self._lock:
            self._cache.clear()
            self._access_order.clear()

    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        async with self._lock:
            now = datetime.now()
            valid_entries = sum(
                1
                for cached in self._cache.values()
                if now - cached.timestamp < self.ttl
            )
            total_hits = sum(cached.hit_count for cached in self._cache.values())

            return {
                "size": len(self._cache),
                "valid_entries": valid_entries,
                "total_hits": total_hits,
                "hit_rate": total_hits / len(self._cache) if self._cache else 0.0,
            }


# Reactive validation engine
class ReactiveValidationEngine:
    """
    Modern reactive validation engine with caching, metrics, and batch processing
    """

    @dataclass
    class ValidationMetrics:
        rule_name: str
        total_validations: int = 0
        successful_validations: int = 0
        failed_validations: int = 0
        average_latency_ms: float = 0.0
        cache_hits: int = 0
        cache_misses: int = 0

    def __init__(
        self, cache: Optional[ValidationCache] = None, concurrency: int = None
    ):
        self.cache = cache or ValidationCache()
        self.concurrency = concurrency or min(32, (os.cpu_count() or 1) + 4)
        self.logger = logging.getLogger(self.__class__.__name__)

        # Metrics
        self._metrics: Dict[str, ReactiveValidationEngine.ValidationMetrics] = {}
        self._semaphore = asyncio.Semaphore(self.concurrency)
        self._metrics_lock = asyncio.Lock()

    async def validate(
        self,
        value: T,
        rule: ValidationRule[T],
        context: ValidationContext,
        cache_key: Optional[str] = None,
        timeout: timedelta = timedelta(seconds=5),
    ) -> ValidationResult:
        """Validate a value with caching and metrics"""
        start_time = datetime.now()
        rule_name = rule.__class__.__name__

        # Initialize metrics if needed
        async with self._metrics_lock:
            if rule_name not in self._metrics:
                self._metrics[rule_name] = ReactiveValidationEngine.ValidationMetrics(
                    rule_name
                )

            metrics = self._metrics[rule_name]

        try:
            await self._semaphore.acquire()

            # Check cache first
            if cache_key:
                cached_result = await self.cache.get(cache_key)
                if cached_result is not None:
                    metrics.cache_hits += 1
                    return cached_result
                else:
                    metrics.cache_misses += 1

            # Perform validation with timeout
            try:
                result = await asyncio.wait_for(
                    rule.validate(value, context), timeout=timeout.total_seconds()
                )
            except asyncio.TimeoutError:
                result = Invalid(
                    [
                        ValidationError(
                            field="validation",
                            message=f"Validation timeout after {timeout.total_seconds()}s",
                            code="TIMEOUT",
                            value=value,
                        )
                    ]
                )

            # Cache the result
            if cache_key:
                await self.cache.put(cache_key, result)

            # Update metrics
            metrics.total_validations += 1
            if isinstance(result, Valid):
                metrics.successful_validations += 1
            else:
                metrics.failed_validations += 1

            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            metrics.average_latency_ms = (
                (metrics.average_latency_ms + latency_ms) / 2
                if metrics.total_validations > 1
                else latency_ms
            )

            return result

        except Exception as e:
            self.logger.error(f"Validation error for rule {rule_name}: {e}")
            metrics.failed_validations += 1

            return Invalid(
                [
                    ValidationError(
                        field="validation",
                        message=f"Validation engine error: {e}",
                        code="VALIDATION_ERROR",
                        value=value,
                    )
                ]
            )
        finally:
            self._semaphore.release()

    async def validate_batch(
        self,
        values: List[T],
        rule: ValidationRule[T],
        context_provider: Callable[[T], ValidationContext],
        cache_key_provider: Optional[Callable[[T], str]] = None,
    ) -> AsyncIterator[tuple[T, ValidationResult]]:
        """Validate multiple values concurrently"""

        async def validate_single(value: T) -> tuple[T, ValidationResult]:
            context = context_provider(value)
            cache_key = cache_key_provider(value) if cache_key_provider else None
            result = await self.validate(value, rule, context, cache_key)
            return value, result

        # Process in batches to avoid overwhelming the system
        batch_size = min(self.concurrency, len(values))

        for i in range(0, len(values), batch_size):
            batch = values[i : i + batch_size]
            tasks = [asyncio.create_task(validate_single(value)) for value in batch]

            for completed_task in asyncio.as_completed(tasks):
                yield await completed_task

    async def get_metrics(self) -> Dict[str, ValidationMetrics]:
        """Get validation metrics"""
        async with self._metrics_lock:
            return dict(self._metrics)

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return await self.cache.get_stats()

    async def clear_cache(self):
        """Clear validation cache"""
        await self.cache.clear()


# DSL builders and utilities
def validator(target_type: Type[T]) -> FieldValidationBuilder[T]:
    """Create a field validation builder"""
    return FieldValidationBuilder(target_type)


def validate_rule(rule: ValidationRule[T]) -> ComposedValidationRule[T]:
    """Create a composed validation rule from a single rule"""
    return ComposedValidationRule([rule])


def validate_rules(*rules: ValidationRule[T]) -> ComposedValidationRule[T]:
    """Create a composed validation rule from multiple rules"""
    return ComposedValidationRule(list(rules))


# Extension functions for validation rules
async def test_validation(
    rule: ValidationRule[T], value: T, context: Optional[ValidationContext] = None
) -> bool:
    """Test if a validation rule passes"""
    ctx = context or ValidationContext()
    result = await rule.validate(value, ctx)
    return isinstance(result, Valid)


async def get_validation_errors(
    rule: ValidationRule[T], value: T, context: Optional[ValidationContext] = None
) -> List[ValidationError]:
    """Get validation errors from a rule"""
    ctx = context or ValidationContext()
    result = await rule.validate(value, ctx)

    if isinstance(result, Invalid):
        return result.errors
    elif isinstance(result, PartialValid):
        return result.errors
    else:
        return []


# Validation result operators
def combine_validation_results(
    result1: ValidationResult, result2: ValidationResult
) -> ValidationResult:
    """Combine two validation results"""
    all_errors = []
    all_warnings = []

    for result in [result1, result2]:
        if isinstance(result, Invalid):
            all_errors.extend(result.errors)
        elif isinstance(result, PartialValid):
            all_errors.extend(result.errors)
            all_warnings.extend(result.warnings)

    if not all_errors and not all_warnings:
        return Valid()
    elif not all_errors:
        return PartialValid([], all_warnings)
    elif not all_warnings:
        return Invalid(all_errors)
    else:
        return PartialValid(all_errors, all_warnings)


# Example usage classes
@dataclass
class User:
    """Example user class for validation"""

    name: str = ""
    email: str = ""
    age: int = 0


class UserValidator:
    """Example validator for User class"""

    @staticmethod
    def create_validator() -> ObjectValidationRule[User]:
        return (
            validator(User)
            .field(
                "name",
                CommonValidationRules.required(),
                CommonValidationRules.string_length(min_length=2, max_length=50),
            )
            .field(
                "email", CommonValidationRules.required(), CommonValidationRules.email()
            )
            .field(
                "age",
                CommonValidationRules.required(),
                CommonValidationRules.number_range(min_value=0, max_value=150),
            )
            .build()
        )


# Import os at the top
import os
