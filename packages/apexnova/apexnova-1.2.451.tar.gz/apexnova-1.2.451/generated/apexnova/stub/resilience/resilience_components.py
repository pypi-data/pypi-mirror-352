"""
Core resilience components for fault tolerance.
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Optional, Type, List, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitBreakerState(Enum):
    """Circuit breaker states."""

    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""

    failure_threshold: int = 5
    recovery_timeout: timedelta = timedelta(seconds=60)
    success_threshold: int = 3
    name: str = "circuit_breaker"


class CircuitBreaker:
    """
    Circuit breaker implementation for fault tolerance.

    Prevents cascading failures by failing fast when a threshold is reached.
    """

    def __init__(self, config: CircuitBreakerConfig):
        """
        Initialize circuit breaker.

        Args:
            config: Circuit breaker configuration
        """
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.total_calls = 0
        self.total_failures = 0
        self.total_successes = 0
        self._lock = asyncio.Lock()

    async def execute(self, operation: Callable[[], T]) -> T:
        """
        Execute operation with circuit breaker protection.

        Args:
            operation: Operation to execute

        Returns:
            Operation result

        Raises:
            Exception: If circuit is open or operation fails
        """
        async with self._lock:
            if not self._can_execute():
                raise Exception(f"Circuit breaker '{self.config.name}' is OPEN")

            self.total_calls += 1

        try:
            result = await self._execute_operation(operation)
            await self._on_success()
            return result
        except Exception as e:
            await self._on_failure()
            raise

    def _can_execute(self) -> bool:
        """Check if operation can be executed."""
        if self.state == CircuitBreakerState.CLOSED:
            return True

        if self.state == CircuitBreakerState.OPEN:
            if (
                self.last_failure_time
                and datetime.now()
                > self.last_failure_time + self.config.recovery_timeout
            ):
                self.state = CircuitBreakerState.HALF_OPEN
                self.success_count = 0
                logger.info(
                    f"Circuit breaker '{self.config.name}' transitioning to HALF_OPEN"
                )
                return True
            return False

        # HALF_OPEN state
        return True

    async def _execute_operation(self, operation: Callable[[], T]) -> T:
        """Execute the operation."""
        if asyncio.iscoroutinefunction(operation):
            return await operation()
        else:
            return operation()

    async def _on_success(self) -> None:
        """Handle successful operation."""
        async with self._lock:
            self.total_successes += 1

            if self.state == CircuitBreakerState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self.state = CircuitBreakerState.CLOSED
                    self.failure_count = 0
                    logger.info(f"Circuit breaker '{self.config.name}' is now CLOSED")
            elif self.state == CircuitBreakerState.CLOSED:
                self.failure_count = 0

    async def _on_failure(self) -> None:
        """Handle failed operation."""
        async with self._lock:
            self.total_failures += 1
            self.failure_count += 1
            self.last_failure_time = datetime.now()

            if self.state in (
                CircuitBreakerState.CLOSED,
                CircuitBreakerState.HALF_OPEN,
            ):
                if self.failure_count >= self.config.failure_threshold:
                    self.state = CircuitBreakerState.OPEN
                    logger.warning(f"Circuit breaker '{self.config.name}' is now OPEN")

    def get_metrics(self) -> dict:
        """Get circuit breaker metrics."""
        return {
            "name": self.config.name,
            "state": self.state.value,
            "total_calls": self.total_calls,
            "total_successes": self.total_successes,
            "total_failures": self.total_failures,
            "failure_rate": (
                self.total_failures / self.total_calls if self.total_calls > 0 else 0
            ),
            "current_failure_count": self.failure_count,
            "current_success_count": self.success_count,
        }


@dataclass
class RetryConfig:
    """Retry policy configuration."""

    max_attempts: int = 3
    base_delay: timedelta = timedelta(milliseconds=100)
    max_delay: timedelta = timedelta(seconds=10)
    backoff_multiplier: float = 2.0
    retryable_exceptions: List[Type[Exception]] = None

    def __post_init__(self):
        if self.retryable_exceptions is None:
            self.retryable_exceptions = [Exception]


class RetryPolicy:
    """
    Retry policy with exponential backoff.
    """

    def __init__(self, config: RetryConfig):
        """
        Initialize retry policy.

        Args:
            config: Retry configuration
        """
        self.config = config

    async def execute(self, operation: Callable[[], T]) -> T:
        """
        Execute operation with retry logic.

        Args:
            operation: Operation to execute

        Returns:
            Operation result

        Raises:
            Exception: If all retry attempts fail
        """
        last_exception: Optional[Exception] = None

        for attempt in range(1, self.config.max_attempts + 1):
            try:
                if asyncio.iscoroutinefunction(operation):
                    return await operation()
                else:
                    return operation()
            except Exception as e:
                last_exception = e

                if not self._is_retryable(e) or attempt == self.config.max_attempts:
                    logger.error(f"Operation failed after {attempt} attempts: {e}")
                    raise

                delay = self._calculate_delay(attempt)
                logger.warning(
                    f"Attempt {attempt} failed, retrying in {delay.total_seconds()}s: {e}"
                )
                await asyncio.sleep(delay.total_seconds())

        raise last_exception or Exception("Retry failed")

    def _is_retryable(self, exception: Exception) -> bool:
        """Check if exception is retryable."""
        return any(
            isinstance(exception, exc_type)
            for exc_type in self.config.retryable_exceptions
        )

    def _calculate_delay(self, attempt: int) -> timedelta:
        """Calculate delay for retry attempt."""
        delay_ms = (
            self.config.base_delay.total_seconds()
            * 1000
            * (self.config.backoff_multiplier ** (attempt - 1))
        )
        delay_ms = min(delay_ms, self.config.max_delay.total_seconds() * 1000)
        return timedelta(milliseconds=delay_ms)


class ResilienceDecorator:
    """
    Decorator that combines circuit breaker and retry patterns.
    """

    def __init__(self, circuit_breaker: CircuitBreaker, retry_policy: RetryPolicy):
        """
        Initialize resilience decorator.

        Args:
            circuit_breaker: Circuit breaker instance
            retry_policy: Retry policy instance
        """
        self.circuit_breaker = circuit_breaker
        self.retry_policy = retry_policy

    async def execute(self, operation: Callable[[], T]) -> T:
        """
        Execute operation with resilience patterns.

        Circuit breaker is checked first, then retry policy is applied.

        Args:
            operation: Operation to execute

        Returns:
            Operation result
        """

        async def wrapped_operation():
            return await self.circuit_breaker.execute(operation)

        return await self.retry_policy.execute(wrapped_operation)


class ResilienceFactory:
    """
    Factory for creating resilience components.
    """

    @staticmethod
    def create_circuit_breaker(
        failure_threshold: int = 5,
        recovery_timeout: timedelta = timedelta(seconds=60),
        success_threshold: int = 3,
        name: str = "circuit_breaker",
    ) -> CircuitBreaker:
        """Create a circuit breaker instance."""
        config = CircuitBreakerConfig(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            success_threshold=success_threshold,
            name=name,
        )
        return CircuitBreaker(config)

    @staticmethod
    def create_retry_policy(
        max_attempts: int = 3,
        base_delay: timedelta = timedelta(milliseconds=100),
        max_delay: timedelta = timedelta(seconds=10),
        backoff_multiplier: float = 2.0,
        retryable_exceptions: Optional[List[Type[Exception]]] = None,
    ) -> RetryPolicy:
        """Create a retry policy instance."""
        config = RetryConfig(
            max_attempts=max_attempts,
            base_delay=base_delay,
            max_delay=max_delay,
            backoff_multiplier=backoff_multiplier,
            retryable_exceptions=retryable_exceptions,
        )
        return RetryPolicy(config)

    @staticmethod
    def create_resilience_decorator(
        circuit_breaker_config: Optional[CircuitBreakerConfig] = None,
        retry_config: Optional[RetryConfig] = None,
    ) -> ResilienceDecorator:
        """Create a resilience decorator with default configurations."""
        circuit_breaker = CircuitBreaker(
            circuit_breaker_config or CircuitBreakerConfig()
        )
        retry_policy = RetryPolicy(retry_config or RetryConfig())
        return ResilienceDecorator(circuit_breaker, retry_policy)
