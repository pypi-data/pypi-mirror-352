"""
Comprehensive resilience patterns for production-ready fault tolerance.
"""

import asyncio
import logging
import time
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Optional, TypeVar, Union, Dict, List
from collections import deque
import threading

from .resilience_components import CircuitBreakerState

logger = logging.getLogger(__name__)

T = TypeVar("T")


# Result types for resilience operations
@dataclass
class ResilienceResult(ABC):
    """Base class for resilience operation results."""

    pass


@dataclass
class Success(ResilienceResult):
    """Successful operation result."""

    value: Any
    execution_time: timedelta = timedelta()


@dataclass
class Failure(ResilienceResult):
    """Failed operation result."""

    error: Exception
    execution_time: timedelta = timedelta()


@dataclass
class Fallback(ResilienceResult):
    """Fallback result when operation fails."""

    value: Any
    original_error: Exception
    execution_time: timedelta = timedelta()


class BackoffStrategy(Enum):
    """Retry backoff strategies."""

    FIXED = "FIXED"
    LINEAR = "LINEAR"
    EXPONENTIAL = "EXPONENTIAL"


@dataclass
class CircuitBreakerMetrics:
    """Circuit breaker metrics."""

    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    slow_calls: int = 0
    open_count: int = 0
    half_open_count: int = 0
    average_response_time: float = 0.0
    last_state_change: Optional[datetime] = None


class AdvancedCircuitBreaker:
    """
    Advanced circuit breaker with sliding window and slow call detection.
    """

    def __init__(
        self,
        failure_threshold: float = 0.5,  # 50% failure rate
        slow_call_threshold: float = 0.5,  # 50% slow call rate
        slow_call_duration: timedelta = timedelta(seconds=1),
        sliding_window_size: int = 100,
        minimum_calls: int = 10,
        wait_duration_in_open_state: timedelta = timedelta(seconds=60),
        permitted_calls_in_half_open: int = 10,
        name: str = "circuit_breaker",
    ):
        """Initialize advanced circuit breaker."""
        self.failure_threshold = failure_threshold
        self.slow_call_threshold = slow_call_threshold
        self.slow_call_duration = slow_call_duration
        self.sliding_window_size = sliding_window_size
        self.minimum_calls = minimum_calls
        self.wait_duration_in_open_state = wait_duration_in_open_state
        self.permitted_calls_in_half_open = permitted_calls_in_half_open
        self.name = name

        self.state = CircuitBreakerState.CLOSED
        self.call_results: deque = deque(maxlen=sliding_window_size)
        self.half_open_calls = 0
        self.last_open_time: Optional[datetime] = None
        self.metrics = CircuitBreakerMetrics()
        self._lock = threading.Lock()

    async def execute(self, operation: Callable[[], T]) -> T:
        """Execute operation with circuit breaker protection."""
        if not self._can_execute():
            self.metrics.failed_calls += 1
            raise Exception(f"Circuit breaker '{self.name}' is OPEN")

        start_time = time.time()
        try:
            result = await self._execute_operation(operation)
            execution_time = time.time() - start_time
            self._record_success(execution_time)
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            self._record_failure(execution_time)
            raise

    def _can_execute(self) -> bool:
        """Check if operation can be executed."""
        with self._lock:
            if self.state == CircuitBreakerState.CLOSED:
                return True

            if self.state == CircuitBreakerState.OPEN:
                if self._should_transition_to_half_open():
                    self._transition_to_half_open()
                    return True
                return False

            # HALF_OPEN state
            if self.half_open_calls < self.permitted_calls_in_half_open:
                self.half_open_calls += 1
                return True
            return False

    def _should_transition_to_half_open(self) -> bool:
        """Check if circuit should transition from OPEN to HALF_OPEN."""
        if self.last_open_time:
            return (
                datetime.now() > self.last_open_time + self.wait_duration_in_open_state
            )
        return False

    def _transition_to_half_open(self) -> None:
        """Transition to HALF_OPEN state."""
        self.state = CircuitBreakerState.HALF_OPEN
        self.half_open_calls = 0
        self.metrics.half_open_count += 1
        self.metrics.last_state_change = datetime.now()
        logger.info(f"Circuit breaker '{self.name}' transitioning to HALF_OPEN")

    def _record_success(self, execution_time: float) -> None:
        """Record successful call."""
        with self._lock:
            self.metrics.total_calls += 1
            self.metrics.successful_calls += 1

            is_slow = execution_time > self.slow_call_duration.total_seconds()
            if is_slow:
                self.metrics.slow_calls += 1

            self.call_results.append((True, is_slow, execution_time))
            self._update_metrics()

            if self.state == CircuitBreakerState.HALF_OPEN:
                if self._should_close():
                    self._transition_to_closed()

    def _record_failure(self, execution_time: float) -> None:
        """Record failed call."""
        with self._lock:
            self.metrics.total_calls += 1
            self.metrics.failed_calls += 1

            is_slow = execution_time > self.slow_call_duration.total_seconds()
            if is_slow:
                self.metrics.slow_calls += 1

            self.call_results.append((False, is_slow, execution_time))
            self._update_metrics()

            if self.state in (
                CircuitBreakerState.CLOSED,
                CircuitBreakerState.HALF_OPEN,
            ):
                if self._should_open():
                    self._transition_to_open()

    def _should_open(self) -> bool:
        """Check if circuit should open."""
        if len(self.call_results) < self.minimum_calls:
            return False

        failure_rate = self._calculate_failure_rate()
        slow_call_rate = self._calculate_slow_call_rate()

        return (
            failure_rate >= self.failure_threshold
            or slow_call_rate >= self.slow_call_threshold
        )

    def _should_close(self) -> bool:
        """Check if circuit should close (from HALF_OPEN)."""
        # Count recent calls in HALF_OPEN state
        recent_results = list(self.call_results)[-self.half_open_calls :]
        if not recent_results:
            return False

        failures = sum(1 for success, _, _ in recent_results if not success)
        failure_rate = failures / len(recent_results)

        return failure_rate < self.failure_threshold

    def _calculate_failure_rate(self) -> float:
        """Calculate current failure rate."""
        if not self.call_results:
            return 0.0
        failures = sum(1 for success, _, _ in self.call_results if not success)
        return failures / len(self.call_results)

    def _calculate_slow_call_rate(self) -> float:
        """Calculate current slow call rate."""
        if not self.call_results:
            return 0.0
        slow_calls = sum(1 for _, is_slow, _ in self.call_results if is_slow)
        return slow_calls / len(self.call_results)

    def _transition_to_open(self) -> None:
        """Transition to OPEN state."""
        self.state = CircuitBreakerState.OPEN
        self.last_open_time = datetime.now()
        self.metrics.open_count += 1
        self.metrics.last_state_change = datetime.now()
        logger.warning(f"Circuit breaker '{self.name}' is now OPEN")

    def _transition_to_closed(self) -> None:
        """Transition to CLOSED state."""
        self.state = CircuitBreakerState.CLOSED
        self.half_open_calls = 0
        self.metrics.last_state_change = datetime.now()
        logger.info(f"Circuit breaker '{self.name}' is now CLOSED")

    def _update_metrics(self) -> None:
        """Update circuit breaker metrics."""
        if self.call_results:
            total_time = sum(time for _, _, time in self.call_results)
            self.metrics.average_response_time = total_time / len(self.call_results)

    async def _execute_operation(self, operation: Callable[[], T]) -> T:
        """Execute the operation."""
        if asyncio.iscoroutinefunction(operation):
            return await operation()
        else:
            return operation()

    def get_metrics(self) -> CircuitBreakerMetrics:
        """Get circuit breaker metrics."""
        return self.metrics


class EnhancedRetry:
    """
    Enhanced retry mechanism with multiple backoff strategies and jitter.
    """

    def __init__(
        self,
        max_attempts: int = 3,
        backoff_strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL,
        base_delay: timedelta = timedelta(milliseconds=100),
        max_delay: timedelta = timedelta(seconds=30),
        backoff_multiplier: float = 2.0,
        jitter: bool = True,
        retry_on: Optional[List[Type[Exception]]] = None,
        name: str = "retry",
    ):
        """Initialize enhanced retry."""
        self.max_attempts = max_attempts
        self.backoff_strategy = backoff_strategy
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_multiplier = backoff_multiplier
        self.jitter = jitter
        self.retry_on = retry_on or [Exception]
        self.name = name

        self.total_attempts = 0
        self.successful_attempts = 0
        self.failed_attempts = 0

    async def execute(self, operation: Callable[[], T]) -> T:
        """Execute operation with retry logic."""
        last_exception: Optional[Exception] = None

        for attempt in range(1, self.max_attempts + 1):
            self.total_attempts += 1

            try:
                result = await self._execute_operation(operation)
                self.successful_attempts += 1
                return result
            except Exception as e:
                last_exception = e

                if not self._should_retry(e) or attempt == self.max_attempts:
                    self.failed_attempts += 1
                    logger.error(
                        f"Operation '{self.name}' failed after {attempt} attempts: {e}"
                    )
                    raise

                delay = self._calculate_delay(attempt)
                logger.warning(
                    f"Attempt {attempt} failed for '{self.name}', retrying in {delay.total_seconds()}s"
                )
                await asyncio.sleep(delay.total_seconds())

        self.failed_attempts += 1
        raise last_exception or Exception("Retry failed")

    def _should_retry(self, exception: Exception) -> bool:
        """Check if exception is retryable."""
        return any(isinstance(exception, exc_type) for exc_type in self.retry_on)

    def _calculate_delay(self, attempt: int) -> timedelta:
        """Calculate delay for retry attempt."""
        if self.backoff_strategy == BackoffStrategy.FIXED:
            base_delay_ms = self.base_delay.total_seconds() * 1000
        elif self.backoff_strategy == BackoffStrategy.LINEAR:
            base_delay_ms = self.base_delay.total_seconds() * 1000 * attempt
        else:  # EXPONENTIAL
            base_delay_ms = (
                self.base_delay.total_seconds()
                * 1000
                * (self.backoff_multiplier ** (attempt - 1))
            )

        # Apply max delay
        delay_ms = min(base_delay_ms, self.max_delay.total_seconds() * 1000)

        # Apply jitter
        if self.jitter:
            delay_ms = delay_ms * (0.5 + random.random() * 0.5)

        return timedelta(milliseconds=delay_ms)

    async def _execute_operation(self, operation: Callable[[], T]) -> T:
        """Execute the operation."""
        if asyncio.iscoroutinefunction(operation):
            return await operation()
        else:
            return operation()

    def get_metrics(self) -> dict:
        """Get retry metrics."""
        return {
            "name": self.name,
            "total_attempts": self.total_attempts,
            "successful_attempts": self.successful_attempts,
            "failed_attempts": self.failed_attempts,
            "success_rate": (
                self.successful_attempts / self.total_attempts
                if self.total_attempts > 0
                else 0
            ),
        }


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter for controlling request rates.
    """

    def __init__(
        self,
        permits_per_second: float,
        burst_capacity: Optional[int] = None,
        name: str = "rate_limiter",
    ):
        """Initialize token bucket rate limiter."""
        self.permits_per_second = permits_per_second
        self.burst_capacity = burst_capacity or int(permits_per_second * 2)
        self.name = name

        self.tokens = float(self.burst_capacity)
        self.last_refill = time.time()
        self.total_requests = 0
        self.accepted_requests = 0
        self.rejected_requests = 0
        self._lock = threading.Lock()

    async def acquire(self, permits: int = 1) -> bool:
        """Try to acquire permits."""
        with self._lock:
            self._refill_tokens()
            self.total_requests += 1

            if self.tokens >= permits:
                self.tokens -= permits
                self.accepted_requests += 1
                return True
            else:
                self.rejected_requests += 1
                return False

    async def acquire_or_wait(
        self, permits: int = 1, timeout: Optional[timedelta] = None
    ) -> bool:
        """Acquire permits, waiting if necessary."""
        start_time = time.time()
        timeout_seconds = timeout.total_seconds() if timeout else float("inf")

        while True:
            if await self.acquire(permits):
                return True

            elapsed = time.time() - start_time
            if elapsed >= timeout_seconds:
                return False

            # Calculate wait time
            with self._lock:
                tokens_needed = permits - self.tokens
                wait_time = tokens_needed / self.permits_per_second

            # Wait for tokens to refill
            wait_time = min(wait_time, timeout_seconds - elapsed)
            await asyncio.sleep(wait_time)

    def _refill_tokens(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.permits_per_second

        self.tokens = min(self.tokens + tokens_to_add, float(self.burst_capacity))
        self.last_refill = now

    def get_metrics(self) -> dict:
        """Get rate limiter metrics."""
        return {
            "name": self.name,
            "total_requests": self.total_requests,
            "accepted_requests": self.accepted_requests,
            "rejected_requests": self.rejected_requests,
            "rejection_rate": (
                self.rejected_requests / self.total_requests
                if self.total_requests > 0
                else 0
            ),
            "current_tokens": self.tokens,
            "burst_capacity": self.burst_capacity,
        }


@dataclass
class BulkheadMetrics:
    """Bulkhead metrics."""

    total_calls: int = 0
    accepted_calls: int = 0
    rejected_calls: int = 0
    active_calls: int = 0
    max_concurrent_calls: int = 0
    average_execution_time: float = 0.0


class Bulkhead:
    """
    Bulkhead pattern to limit concurrent calls.
    """

    def __init__(
        self,
        max_concurrent_calls: int = 10,
        max_wait_duration: Optional[timedelta] = None,
        name: str = "bulkhead",
    ):
        """Initialize bulkhead."""
        self.max_concurrent_calls = max_concurrent_calls
        self.max_wait_duration = max_wait_duration
        self.name = name

        self.semaphore = asyncio.Semaphore(max_concurrent_calls)
        self.metrics = BulkheadMetrics(max_concurrent_calls=max_concurrent_calls)
        self.execution_times: deque = deque(maxlen=1000)
        self._lock = threading.Lock()

    async def execute(self, operation: Callable[[], T]) -> T:
        """Execute operation with bulkhead protection."""
        timeout = (
            self.max_wait_duration.total_seconds() if self.max_wait_duration else None
        )

        with self._lock:
            self.metrics.total_calls += 1

        try:
            async with asyncio.timeout(timeout) if timeout else asyncio.nullcontext():
                await self.semaphore.acquire()
        except asyncio.TimeoutError:
            with self._lock:
                self.metrics.rejected_calls += 1
            raise Exception(f"Bulkhead '{self.name}' timeout waiting for permit")

        with self._lock:
            self.metrics.accepted_calls += 1
            self.metrics.active_calls += 1

        start_time = time.time()
        try:
            result = await self._execute_operation(operation)
            execution_time = time.time() - start_time

            with self._lock:
                self.execution_times.append(execution_time)
                self._update_metrics()

            return result
        finally:
            self.semaphore.release()
            with self._lock:
                self.metrics.active_calls -= 1

    async def _execute_operation(self, operation: Callable[[], T]) -> T:
        """Execute the operation."""
        if asyncio.iscoroutinefunction(operation):
            return await operation()
        else:
            return operation()

    def _update_metrics(self) -> None:
        """Update bulkhead metrics."""
        if self.execution_times:
            self.metrics.average_execution_time = sum(self.execution_times) / len(
                self.execution_times
            )

    def get_metrics(self) -> BulkheadMetrics:
        """Get bulkhead metrics."""
        return self.metrics

    def get_utilization(self) -> float:
        """Get current utilization percentage."""
        return self.metrics.active_calls / self.max_concurrent_calls


class Timeout:
    """
    Timeout pattern for limiting operation duration.
    """

    def __init__(self, duration: timedelta, name: str = "timeout"):
        """Initialize timeout."""
        self.duration = duration
        self.name = name

        self.total_calls = 0
        self.successful_calls = 0
        self.timeout_calls = 0

    async def execute(self, operation: Callable[[], T]) -> T:
        """Execute operation with timeout."""
        self.total_calls += 1

        try:
            async with asyncio.timeout(self.duration.total_seconds()):
                result = await self._execute_operation(operation)
                self.successful_calls += 1
                return result
        except asyncio.TimeoutError:
            self.timeout_calls += 1
            raise Exception(
                f"Operation '{self.name}' timed out after {self.duration.total_seconds()}s"
            )

    async def _execute_operation(self, operation: Callable[[], T]) -> T:
        """Execute the operation."""
        if asyncio.iscoroutinefunction(operation):
            return await operation()
        else:
            return operation()

    def get_metrics(self) -> dict:
        """Get timeout metrics."""
        return {
            "name": self.name,
            "total_calls": self.total_calls,
            "successful_calls": self.successful_calls,
            "timeout_calls": self.timeout_calls,
            "timeout_rate": (
                self.timeout_calls / self.total_calls if self.total_calls > 0 else 0
            ),
        }


class FallbackHandler:
    """
    Fallback pattern for providing alternative results on failure.
    """

    def __init__(
        self,
        fallback_value: Optional[Any] = None,
        fallback_function: Optional[Callable[[], Any]] = None,
        fallback_on: Optional[List[Type[Exception]]] = None,
        name: str = "fallback",
    ):
        """Initialize fallback handler."""
        self.fallback_value = fallback_value
        self.fallback_function = fallback_function
        self.fallback_on = fallback_on or [Exception]
        self.name = name

        self.total_calls = 0
        self.primary_success = 0
        self.fallback_used = 0

    async def execute(self, operation: Callable[[], T]) -> Union[T, Any]:
        """Execute operation with fallback."""
        self.total_calls += 1

        try:
            result = await self._execute_operation(operation)
            self.primary_success += 1
            return result
        except Exception as e:
            if self._should_fallback(e):
                self.fallback_used += 1
                logger.warning(f"Using fallback for '{self.name}' due to: {e}")

                if self.fallback_function:
                    return await self._execute_operation(self.fallback_function)
                else:
                    return self.fallback_value
            else:
                raise

    def _should_fallback(self, exception: Exception) -> bool:
        """Check if fallback should be used."""
        return any(isinstance(exception, exc_type) for exc_type in self.fallback_on)

    async def _execute_operation(self, operation: Callable[[], T]) -> T:
        """Execute the operation."""
        if asyncio.iscoroutinefunction(operation):
            return await operation()
        else:
            return operation()

    def get_metrics(self) -> dict:
        """Get fallback metrics."""
        return {
            "name": self.name,
            "total_calls": self.total_calls,
            "primary_success": self.primary_success,
            "fallback_used": self.fallback_used,
            "fallback_rate": (
                self.fallback_used / self.total_calls if self.total_calls > 0 else 0
            ),
        }


class ResiliencePolicy:
    """
    Combines multiple resilience patterns into a single policy.
    """

    def __init__(
        self,
        circuit_breaker: Optional[AdvancedCircuitBreaker] = None,
        retry: Optional[EnhancedRetry] = None,
        rate_limiter: Optional[TokenBucketRateLimiter] = None,
        bulkhead: Optional[Bulkhead] = None,
        timeout: Optional[Timeout] = None,
        fallback: Optional[FallbackHandler] = None,
        name: str = "resilience_policy",
    ):
        """Initialize resilience policy."""
        self.circuit_breaker = circuit_breaker
        self.retry = retry
        self.rate_limiter = rate_limiter
        self.bulkhead = bulkhead
        self.timeout = timeout
        self.fallback = fallback
        self.name = name

    async def execute(self, operation: Callable[[], T]) -> ResilienceResult:
        """
        Execute operation with all configured resilience patterns.

        Execution order:
        1. Circuit Breaker
        2. Rate Limiter
        3. Bulkhead
        4. Timeout
        5. Retry (wraps the above)
        6. Fallback (if all else fails)
        """
        start_time = time.time()

        async def wrapped_operation():
            # Check circuit breaker
            if self.circuit_breaker:
                await self.circuit_breaker.execute(lambda: None)  # Just check state

            # Check rate limiter
            if self.rate_limiter:
                if not await self.rate_limiter.acquire():
                    raise Exception(f"Rate limit exceeded for '{self.name}'")

            # Execute with bulkhead
            if self.bulkhead:
                return await self.bulkhead.execute(
                    lambda: self._execute_with_timeout(operation)
                )
            else:
                return await self._execute_with_timeout(operation)

        try:
            # Execute with retry
            if self.retry:
                result = await self.retry.execute(wrapped_operation)
            else:
                result = await wrapped_operation()

            execution_time = timedelta(seconds=time.time() - start_time)
            return Success(value=result, execution_time=execution_time)

        except Exception as e:
            execution_time = timedelta(seconds=time.time() - start_time)

            # Try fallback
            if self.fallback:
                try:
                    fallback_result = await self.fallback.execute(lambda: None)
                    return Fallback(
                        value=fallback_result,
                        original_error=e,
                        execution_time=execution_time,
                    )
                except:
                    pass

            return Failure(error=e, execution_time=execution_time)

    async def _execute_with_timeout(self, operation: Callable[[], T]) -> T:
        """Execute operation with timeout if configured."""
        if self.timeout:
            return await self.timeout.execute(operation)
        else:
            if asyncio.iscoroutinefunction(operation):
                return await operation()
            else:
                return operation()

    def get_metrics(self) -> dict:
        """Get combined metrics from all patterns."""
        metrics = {"name": self.name}

        if self.circuit_breaker:
            metrics["circuit_breaker"] = self.circuit_breaker.get_metrics()
        if self.retry:
            metrics["retry"] = self.retry.get_metrics()
        if self.rate_limiter:
            metrics["rate_limiter"] = self.rate_limiter.get_metrics()
        if self.bulkhead:
            metrics["bulkhead"] = self.bulkhead.get_metrics()
        if self.timeout:
            metrics["timeout"] = self.timeout.get_metrics()
        if self.fallback:
            metrics["fallback"] = self.fallback.get_metrics()

        return metrics


class ResiliencePolicyBuilder:
    """Builder for creating resilience policies."""

    def __init__(self, name: str = "resilience_policy"):
        """Initialize builder."""
        self.name = name
        self.circuit_breaker: Optional[AdvancedCircuitBreaker] = None
        self.retry: Optional[EnhancedRetry] = None
        self.rate_limiter: Optional[TokenBucketRateLimiter] = None
        self.bulkhead: Optional[Bulkhead] = None
        self.timeout: Optional[Timeout] = None
        self.fallback: Optional[FallbackHandler] = None

    def with_circuit_breaker(
        self,
        failure_threshold: float = 0.5,
        slow_call_threshold: float = 0.5,
        slow_call_duration: timedelta = timedelta(seconds=1),
        wait_duration: timedelta = timedelta(seconds=60),
    ) -> "ResiliencePolicyBuilder":
        """Add circuit breaker to policy."""
        self.circuit_breaker = AdvancedCircuitBreaker(
            failure_threshold=failure_threshold,
            slow_call_threshold=slow_call_threshold,
            slow_call_duration=slow_call_duration,
            wait_duration_in_open_state=wait_duration,
            name=f"{self.name}_circuit_breaker",
        )
        return self

    def with_retry(
        self,
        max_attempts: int = 3,
        backoff_strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL,
        base_delay: timedelta = timedelta(milliseconds=100),
    ) -> "ResiliencePolicyBuilder":
        """Add retry to policy."""
        self.retry = EnhancedRetry(
            max_attempts=max_attempts,
            backoff_strategy=backoff_strategy,
            base_delay=base_delay,
            name=f"{self.name}_retry",
        )
        return self

    def with_rate_limiter(
        self, permits_per_second: float, burst_capacity: Optional[int] = None
    ) -> "ResiliencePolicyBuilder":
        """Add rate limiter to policy."""
        self.rate_limiter = TokenBucketRateLimiter(
            permits_per_second=permits_per_second,
            burst_capacity=burst_capacity,
            name=f"{self.name}_rate_limiter",
        )
        return self

    def with_bulkhead(
        self,
        max_concurrent_calls: int = 10,
        max_wait_duration: Optional[timedelta] = None,
    ) -> "ResiliencePolicyBuilder":
        """Add bulkhead to policy."""
        self.bulkhead = Bulkhead(
            max_concurrent_calls=max_concurrent_calls,
            max_wait_duration=max_wait_duration,
            name=f"{self.name}_bulkhead",
        )
        return self

    def with_timeout(self, duration: timedelta) -> "ResiliencePolicyBuilder":
        """Add timeout to policy."""
        self.timeout = Timeout(duration=duration, name=f"{self.name}_timeout")
        return self

    def with_fallback(
        self,
        fallback_value: Optional[Any] = None,
        fallback_function: Optional[Callable[[], Any]] = None,
    ) -> "ResiliencePolicyBuilder":
        """Add fallback to policy."""
        self.fallback = FallbackHandler(
            fallback_value=fallback_value,
            fallback_function=fallback_function,
            name=f"{self.name}_fallback",
        )
        return self

    def build(self) -> ResiliencePolicy:
        """Build resilience policy."""
        return ResiliencePolicy(
            circuit_breaker=self.circuit_breaker,
            retry=self.retry,
            rate_limiter=self.rate_limiter,
            bulkhead=self.bulkhead,
            timeout=self.timeout,
            fallback=self.fallback,
            name=self.name,
        )


def resilience_policy(
    name: str, builder_fn: Callable[[ResiliencePolicyBuilder], None]
) -> ResiliencePolicy:
    """
    DSL function to create resilience policy.

    Example:
        policy = resilience_policy("api_call", lambda b: b
            .with_circuit_breaker(failure_threshold=0.5)
            .with_retry(max_attempts=3)
            .with_timeout(duration=timedelta(seconds=5))
            .with_fallback(fallback_value={"error": "Service unavailable"})
        )
    """
    builder = ResiliencePolicyBuilder(name)
    builder_fn(builder)
    return builder.build()


class ResilienceRegistry:
    """
    Central registry for managing resilience components.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize registry."""
        if not self._initialized:
            self.policies: Dict[str, ResiliencePolicy] = {}
            self.circuit_breakers: Dict[str, AdvancedCircuitBreaker] = {}
            self.rate_limiters: Dict[str, TokenBucketRateLimiter] = {}
            self.bulkheads: Dict[str, Bulkhead] = {}
            self._initialized = True

    def register_policy(self, name: str, policy: ResiliencePolicy) -> None:
        """Register a resilience policy."""
        self.policies[name] = policy

        # Also register individual components
        if policy.circuit_breaker:
            self.circuit_breakers[f"{name}_circuit_breaker"] = policy.circuit_breaker
        if policy.rate_limiter:
            self.rate_limiters[f"{name}_rate_limiter"] = policy.rate_limiter
        if policy.bulkhead:
            self.bulkheads[f"{name}_bulkhead"] = policy.bulkhead

    def get_policy(self, name: str) -> Optional[ResiliencePolicy]:
        """Get a registered policy."""
        return self.policies.get(name)

    def get_global_metrics(self) -> dict:
        """Get metrics for all registered components."""
        return {
            "policies": {
                name: policy.get_metrics() for name, policy in self.policies.items()
            },
            "circuit_breakers": {
                name: cb.get_metrics() for name, cb in self.circuit_breakers.items()
            },
            "rate_limiters": {
                name: rl.get_metrics() for name, rl in self.rate_limiters.items()
            },
            "bulkheads": {
                name: bh.get_metrics() for name, bh in self.bulkheads.items()
            },
        }
