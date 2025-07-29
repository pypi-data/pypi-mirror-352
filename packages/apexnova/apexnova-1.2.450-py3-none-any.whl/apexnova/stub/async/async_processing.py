"""
Modern async processing utilities with asyncio, channels, and structured concurrency.
"""

import asyncio
import logging
import time
import uuid
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Callable,
    AsyncIterator,
    TypeVar,
    Generic,
    Union,
)
from collections import deque
import threading
from concurrent.futures import ThreadPoolExecutor

from ..core.result import Result

logger = logging.getLogger(__name__)

T = TypeVar("T")
R = TypeVar("R")


@dataclass
class ExecutionMetric:
    """Metrics for task execution."""

    task_name: str
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    total_duration: float = 0.0  # milliseconds
    last_execution: datetime = field(default_factory=datetime.now)

    def average_duration(self) -> float:
        """Get average execution duration."""
        return (
            self.total_duration / self.total_executions
            if self.total_executions > 0
            else 0.0
        )

    def success_rate(self) -> float:
        """Get success rate."""
        return (
            self.successful_executions / self.total_executions
            if self.total_executions > 0
            else 0.0
        )


class AsyncProcessing:
    """Modern async processing utilities with Flow, channels, and structured concurrency."""

    _execution_metrics: Dict[str, ExecutionMetric] = {}
    _lock = threading.Lock()

    @classmethod
    async def process_with_backpressure(
        cls,
        items: List[T],
        processor: Callable[[T], asyncio.Future[R]],
        concurrency: int = 10,
        buffer_size: int = 100,
        task_name: str = "processWithBackpressure",
    ) -> AsyncIterator[Result[R]]:
        """
        Execute tasks with bounded parallelism and backpressure.

        Args:
            items: Items to process
            processor: Async processor function
            concurrency: Maximum concurrent tasks
            buffer_size: Buffer size for backpressure
            task_name: Name for metrics tracking

        Yields:
            Results as they complete
        """
        semaphore = asyncio.Semaphore(concurrency)

        async def process_item(item: T) -> Result[R]:
            start_time = time.time()
            async with semaphore:
                try:
                    result = await processor(item)
                    duration = (time.time() - start_time) * 1000
                    cls._record_success(task_name, duration)
                    return Result.success(result)
                except Exception as e:
                    duration = (time.time() - start_time) * 1000
                    cls._record_failure(task_name, duration)
                    return Result.failure(e)

        # Create tasks in batches to control memory usage
        for i in range(0, len(items), buffer_size):
            batch = items[i : i + buffer_size]
            tasks = [asyncio.create_task(process_item(item)) for item in batch]

            # Yield results as they complete
            for coro in asyncio.as_completed(tasks):
                yield await coro

    @classmethod
    async def retry_with_backoff(
        cls,
        operation: Callable[[], asyncio.Future[T]],
        max_retries: int = 3,
        initial_delay: float = 0.1,  # seconds
        max_delay: float = 10.0,  # seconds
        backoff_factor: float = 2.0,
        jitter: bool = True,
        task_name: str = "retryWithBackoff",
    ) -> Result[T]:
        """
        Retry with exponential backoff and jitter.

        Args:
            operation: Async operation to retry
            max_retries: Maximum number of retries
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            backoff_factor: Backoff multiplication factor
            jitter: Whether to add jitter to delays
            task_name: Name for metrics tracking

        Returns:
            Result of the operation
        """
        current_delay = initial_delay
        last_exception: Optional[Exception] = None

        for attempt in range(max_retries + 1):
            try:
                start_time = time.time()
                result = await operation()
                duration = (time.time() - start_time) * 1000
                cls._record_success(task_name, duration)
                return Result.success(result)
            except Exception as e:
                last_exception = e
                logger.warning(
                    f"Attempt {attempt + 1} failed for task '{task_name}': {e}"
                )

                if attempt < max_retries:
                    delay = current_delay
                    if jitter:
                        delay = delay * (0.5 + random.random() * 0.5)

                    await asyncio.sleep(delay)
                    current_delay = min(current_delay * backoff_factor, max_delay)

        cls._record_failure(task_name, 0)
        return Result.failure(last_exception or RuntimeError("Max retries exceeded"))

    @classmethod
    def _record_success(cls, task_name: str, duration: float) -> None:
        """Record successful execution."""
        with cls._lock:
            metric = cls._execution_metrics.setdefault(
                task_name, ExecutionMetric(task_name)
            )
            metric.total_executions += 1
            metric.successful_executions += 1
            metric.total_duration += duration
            metric.last_execution = datetime.now()

    @classmethod
    def _record_failure(cls, task_name: str, duration: float) -> None:
        """Record failed execution."""
        with cls._lock:
            metric = cls._execution_metrics.setdefault(
                task_name, ExecutionMetric(task_name)
            )
            metric.total_executions += 1
            metric.failed_executions += 1
            metric.total_duration += duration
            metric.last_execution = datetime.now()

    @classmethod
    def get_metrics(cls) -> Dict[str, ExecutionMetric]:
        """Get execution metrics."""
        with cls._lock:
            return cls._execution_metrics.copy()


class CircuitBreakerState(Enum):
    """Circuit breaker states."""

    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreaker:
    """Circuit breaker pattern for async operations."""

    def __init__(
        self,
        failure_threshold: int = 10,
        timeout: timedelta = timedelta(minutes=1),
        success_threshold: int = 3,
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Time to wait before trying half-open
            success_threshold: Successes needed to close circuit from half-open
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.success_threshold = success_threshold
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitBreakerState.CLOSED
        self.success_count = 0
        self._lock = asyncio.Lock()

    async def execute(self, operation: Callable[[], asyncio.Future[T]]) -> Result[T]:
        """
        Execute operation with circuit breaker protection.

        Args:
            operation: Async operation to execute

        Returns:
            Result of the operation
        """
        async with self._lock:
            if self.state == CircuitBreakerState.OPEN:
                if self._should_try_operation():
                    self.state = CircuitBreakerState.HALF_OPEN
                    self.success_count = 0
                else:
                    return Result.failure(RuntimeError("Circuit breaker is OPEN"))

        try:
            result = await operation()
            await self._on_success()
            return Result.success(result)
        except Exception as e:
            await self._on_failure()
            return Result.failure(e)

    def _should_try_operation(self) -> bool:
        """Check if we should try operation when circuit is open."""
        if self.last_failure_time:
            return datetime.now() > self.last_failure_time + self.timeout
        return True

    async def _on_success(self) -> None:
        """Handle successful operation."""
        async with self._lock:
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.success_threshold:
                    self.state = CircuitBreakerState.CLOSED
                    self.failure_count = 0
            elif self.state == CircuitBreakerState.CLOSED:
                self.failure_count = 0

    async def _on_failure(self) -> None:
        """Handle failed operation."""
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()

            if self.failure_count >= self.failure_threshold:
                self.state = CircuitBreakerState.OPEN


class RateLimiter:
    """Rate limiter using token bucket algorithm."""

    def __init__(self, tokens_per_second: float, bucket_capacity: Optional[int] = None):
        """
        Initialize rate limiter.

        Args:
            tokens_per_second: Rate of token generation
            bucket_capacity: Maximum tokens in bucket (default: 2x rate)
        """
        self.tokens_per_second = tokens_per_second
        self.bucket_capacity = bucket_capacity or int(tokens_per_second * 2)
        self.tokens = float(self.bucket_capacity)
        self.last_refill = time.time()
        self._lock = asyncio.Lock()

    async def acquire(self, permits: int = 1) -> bool:
        """
        Try to acquire permits.

        Args:
            permits: Number of permits to acquire

        Returns:
            True if permits acquired, False otherwise
        """
        async with self._lock:
            self._refill_tokens()

            if self.tokens >= permits:
                self.tokens -= permits
                return True
            return False

    async def acquire_blocking(self, permits: int = 1) -> None:
        """
        Acquire permits, blocking until available.

        Args:
            permits: Number of permits to acquire
        """
        while not await self.acquire(permits):
            await asyncio.sleep(0.01)  # Wait 10ms before retrying

    def _refill_tokens(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        tokens_to_add = (now - self.last_refill) * self.tokens_per_second
        self.tokens = min(self.tokens + tokens_to_add, float(self.bucket_capacity))
        self.last_refill = now


# Task execution result types
@dataclass
class TaskResult(ABC):
    """Base class for task results."""

    execution_time: timedelta


@dataclass
class SuccessResult(TaskResult):
    """Successful task result."""

    result: Any


@dataclass
class FailureResult(TaskResult):
    """Failed task result."""

    exception: Exception
    attempt: int


@dataclass
class TimeoutResult(TaskResult):
    """Timeout task result."""

    pass


@dataclass
class CancelledResult(TaskResult):
    """Cancelled task result."""

    reason: str


@dataclass
class TaskContext:
    """Task execution context."""

    task_id: str
    attempt: int
    start_time: datetime
    metadata: Dict[str, str]


class TaskPriority(Enum):
    """Task priority levels."""

    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class RetryPolicy:
    """Retry policy configuration."""

    max_attempts: int = 3
    base_delay: timedelta = field(default_factory=lambda: timedelta(milliseconds=100))
    max_delay: timedelta = field(default_factory=lambda: timedelta(seconds=10))
    backoff_multiplier: float = 1.5
    retryable_exceptions: List[type] = field(default_factory=lambda: [Exception])


@dataclass
class Task:
    """Task definition."""

    name: str
    action: Callable[[], asyncio.Future[Result[Any]]]
    priority: TaskPriority = TaskPriority.NORMAL
    timeout: timedelta = field(default_factory=lambda: timedelta(minutes=5))
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    metadata: Dict[str, str] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class TaskStatistics:
    """Task execution statistics."""

    started: int = 0
    completed: int = 0
    failed: int = 0
    timeout: int = 0
    cancelled: int = 0
    total_execution_time: timedelta = timedelta()
    min_execution_time: timedelta = timedelta(days=1)
    max_execution_time: timedelta = timedelta()
    _lock: threading.Lock = field(
        default_factory=threading.Lock, init=False, repr=False
    )

    def increment_started(self) -> None:
        """Increment started count."""
        with self._lock:
            self.started += 1

    def increment_completed(self) -> None:
        """Increment completed count."""
        with self._lock:
            self.completed += 1

    def increment_failed(self) -> None:
        """Increment failed count."""
        with self._lock:
            self.failed += 1

    def increment_timeout(self) -> None:
        """Increment timeout count."""
        with self._lock:
            self.timeout += 1

    def increment_cancelled(self) -> None:
        """Increment cancelled count."""
        with self._lock:
            self.cancelled += 1

    def add_execution_time(self, duration: timedelta) -> None:
        """Add execution time to statistics."""
        with self._lock:
            self.total_execution_time += duration
            if duration < self.min_execution_time:
                self.min_execution_time = duration
            if duration > self.max_execution_time:
                self.max_execution_time = duration

    def get_average_execution_time(self) -> timedelta:
        """Get average execution time."""
        with self._lock:
            total_tasks = self.completed + self.failed
            if total_tasks > 0:
                return self.total_execution_time / total_tasks
            return timedelta()

    def get_min_execution_time(self) -> timedelta:
        """Get minimum execution time."""
        with self._lock:
            return (
                timedelta()
                if self.min_execution_time == timedelta(days=1)
                else self.min_execution_time
            )

    def get_max_execution_time(self) -> timedelta:
        """Get maximum execution time."""
        with self._lock:
            return self.max_execution_time

    def get_success_rate(self) -> float:
        """Get success rate."""
        with self._lock:
            return self.completed / self.started if self.started > 0 else 0.0


class BackgroundJobScheduler:
    """Background job scheduler with worker pool."""

    def __init__(self, worker_count: Optional[int] = None):
        """
        Initialize scheduler.

        Args:
            worker_count: Number of workers (default: CPU count)
        """
        self.worker_count = worker_count or asyncio.cpu_count() or 4
        self.task_queue: asyncio.Queue[Task] = asyncio.Queue()
        self.active_jobs: Dict[str, asyncio.Task] = {}
        self.completed_tasks: Dict[str, TaskResult] = {}
        self.task_stats: Dict[str, TaskStatistics] = {}
        self.is_running = True
        self.workers: List[asyncio.Task] = []
        self._lock = asyncio.Lock()

        logger.info(
            f"Initializing background job scheduler with {self.worker_count} workers"
        )

    async def start(self) -> None:
        """Start the scheduler and workers."""
        for worker_id in range(self.worker_count):
            worker = asyncio.create_task(self._worker(worker_id))
            self.workers.append(worker)
            logger.info(f"Started worker {worker_id}")

    async def _worker(self, worker_id: int) -> None:
        """Worker coroutine."""
        logger.info(f"Worker {worker_id} started")
        while self.is_running:
            try:
                # Wait for task with timeout to allow periodic checks
                task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                await self._execute_task(task, worker_id)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                if self.is_running:
                    logger.error(f"Worker {worker_id} error: {e}", exc_info=True)
        logger.info(f"Worker {worker_id} stopped")

    async def submit_task(self, task: Task) -> str:
        """
        Submit a task for execution.

        Args:
            task: Task to execute

        Returns:
            Task ID
        """
        if not self.is_running:
            raise RuntimeError("Scheduler is not running")

        await self.task_queue.put(task)
        logger.debug(f"Submitted task: {task.name} ({task.id})")
        return task.id

    async def submit_tasks(self, tasks: List[Task]) -> List[str]:
        """
        Submit multiple tasks.

        Args:
            tasks: Tasks to execute

        Returns:
            List of task IDs
        """
        task_ids = []
        for task in tasks:
            task_id = await self.submit_task(task)
            task_ids.append(task_id)
        return task_ids

    async def _execute_task(self, task: Task, worker_id: int) -> None:
        """Execute a task."""
        logger.debug(f"Worker {worker_id} executing task: {task.name} ({task.id})")

        stats = self.task_stats.setdefault(task.name, TaskStatistics())
        stats.increment_started()

        start_time = datetime.now()
        context = TaskContext(task.id, 1, start_time, task.metadata)

        # Create task with timeout
        exec_task = asyncio.create_task(self._execute_with_retry(task, context))

        async with self._lock:
            self.active_jobs[task.id] = exec_task

        try:
            result = await asyncio.wait_for(
                exec_task, timeout=task.timeout.total_seconds()
            )
            execution_time = datetime.now() - start_time

            if isinstance(result, SuccessResult):
                stats.increment_completed()
                stats.add_execution_time(execution_time)
                logger.debug(
                    f"Task completed successfully: {task.name} ({task.id}) in {execution_time}"
                )
            elif isinstance(result, FailureResult):
                stats.increment_failed()
                stats.add_execution_time(execution_time)
                logger.error(
                    f"Task failed: {task.name} ({task.id}) after {result.attempt} attempts",
                    exc_info=result.exception,
                )

            self.completed_tasks[task.id] = result

        except asyncio.TimeoutError:
            execution_time = datetime.now() - start_time
            stats.increment_timeout()
            result = TimeoutResult(execution_time=execution_time)
            self.completed_tasks[task.id] = result
            logger.warning(
                f"Task timed out: {task.name} ({task.id}) after {execution_time}"
            )
            exec_task.cancel()

        except asyncio.CancelledError:
            execution_time = datetime.now() - start_time
            stats.increment_cancelled()
            result = CancelledResult(
                reason="Task cancelled", execution_time=execution_time
            )
            self.completed_tasks[task.id] = result
            raise

        finally:
            async with self._lock:
                self.active_jobs.pop(task.id, None)

    async def _execute_with_retry(
        self, task: Task, initial_context: TaskContext
    ) -> TaskResult:
        """Execute task with retry logic."""
        attempt = 1
        last_exception: Optional[Exception] = None

        while attempt <= task.retry_policy.max_attempts:
            context = TaskContext(
                initial_context.task_id,
                attempt,
                initial_context.start_time,
                initial_context.metadata,
            )

            start_time = datetime.now()

            try:
                result = await task.action()
                if result.is_success:
                    execution_time = datetime.now() - start_time
                    return SuccessResult(
                        result=result.value, execution_time=execution_time
                    )
                else:
                    last_exception = result.error
                    if (
                        not self._should_retry(result.error, task.retry_policy)
                        or attempt >= task.retry_policy.max_attempts
                    ):
                        execution_time = datetime.now() - start_time
                        return FailureResult(
                            exception=result.error,
                            attempt=attempt,
                            execution_time=execution_time,
                        )

            except asyncio.CancelledError:
                raise
            except Exception as e:
                last_exception = e
                if (
                    not self._should_retry(e, task.retry_policy)
                    or attempt >= task.retry_policy.max_attempts
                ):
                    execution_time = datetime.now() - start_time
                    return FailureResult(
                        exception=e, attempt=attempt, execution_time=execution_time
                    )

            if attempt < task.retry_policy.max_attempts:
                delay = self._calculate_retry_delay(attempt, task.retry_policy)
                logger.debug(
                    f"Retrying task {task.name} ({task.id}) in {delay} (attempt {attempt})"
                )
                await asyncio.sleep(delay.total_seconds())

            attempt += 1

        execution_time = datetime.now() - initial_context.start_time
        return FailureResult(
            exception=last_exception
            or RuntimeError(
                f"Task failed after {task.retry_policy.max_attempts} attempts"
            ),
            attempt=attempt - 1,
            execution_time=execution_time,
        )

    def _should_retry(self, exception: Exception, retry_policy: RetryPolicy) -> bool:
        """Check if exception is retryable."""
        return any(
            isinstance(exception, exc_type)
            for exc_type in retry_policy.retryable_exceptions
        )

    def _calculate_retry_delay(
        self, attempt: int, retry_policy: RetryPolicy
    ) -> timedelta:
        """Calculate retry delay with exponential backoff."""
        delay_ms = (
            retry_policy.base_delay.total_seconds()
            * 1000
            * (retry_policy.backoff_multiplier ** (attempt - 1))
        )
        delay_ms = min(delay_ms, retry_policy.max_delay.total_seconds() * 1000)
        return timedelta(milliseconds=delay_ms)

    def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """Get task result by ID."""
        return self.completed_tasks.get(task_id)

    def get_active_task_count(self) -> int:
        """Get number of active tasks."""
        return len(self.active_jobs)

    def get_queue_size(self) -> int:
        """Get task queue size."""
        return self.task_queue.qsize()

    def get_task_statistics(self) -> Dict[str, TaskStatistics]:
        """Get task statistics."""
        return self.task_stats.copy()

    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a task.

        Args:
            task_id: Task ID to cancel

        Returns:
            True if cancelled, False if not found
        """
        async with self._lock:
            task = self.active_jobs.get(task_id)
            if task and not task.done():
                task.cancel()
                return True
            return False

    async def cancel_all_tasks(self) -> None:
        """Cancel all active tasks."""
        async with self._lock:
            for task in self.active_jobs.values():
                if not task.done():
                    task.cancel()
            self.active_jobs.clear()

    async def shutdown(self) -> None:
        """Shutdown the scheduler."""
        logger.info("Shutting down background job scheduler")
        self.is_running = False
        await self.cancel_all_tasks()

        # Wait for workers to finish
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()


class ScheduledTaskRunner:
    """Scheduled task runner for periodic and delayed tasks."""

    def __init__(self, background_job_scheduler: BackgroundJobScheduler):
        """
        Initialize scheduled task runner.

        Args:
            background_job_scheduler: Background job scheduler to use
        """
        self.background_job_scheduler = background_job_scheduler
        self.scheduled_jobs: Dict[str, asyncio.Task] = {}
        self._lock = asyncio.Lock()

    async def schedule_repeating(
        self,
        name: str,
        interval: timedelta,
        action: Callable[[], asyncio.Future[Result[Any]]],
    ) -> str:
        """
        Schedule a repeating task.

        Args:
            name: Task name
            interval: Execution interval
            action: Task action

        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())

        async def repeating_task():
            logger.info(
                f"Starting scheduled task: {name} with interval {interval.total_seconds()}s"
            )

            while True:
                try:
                    task = Task(name=name, action=action, priority=TaskPriority.LOW)
                    await self.background_job_scheduler.submit_task(task)

                    await asyncio.sleep(interval.total_seconds())
                except asyncio.CancelledError:
                    logger.info(f"Scheduled task cancelled: {name}")
                    break
                except Exception as e:
                    logger.error(f"Error in scheduled task {name}: {e}", exc_info=True)

        job = asyncio.create_task(repeating_task())

        async with self._lock:
            self.scheduled_jobs[job_id] = job

        return job_id

    async def schedule_delayed(
        self,
        name: str,
        delay: timedelta,
        action: Callable[[], asyncio.Future[Result[Any]]],
    ) -> str:
        """
        Schedule a delayed task.

        Args:
            name: Task name
            delay: Execution delay
            action: Task action

        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())

        async def delayed_task():
            await asyncio.sleep(delay.total_seconds())

            task = Task(name=name, action=action, priority=TaskPriority.NORMAL)
            await self.background_job_scheduler.submit_task(task)

            async with self._lock:
                self.scheduled_jobs.pop(job_id, None)

        job = asyncio.create_task(delayed_task())

        async with self._lock:
            self.scheduled_jobs[job_id] = job

        return job_id

    async def cancel_scheduled_task(self, job_id: str) -> bool:
        """
        Cancel a scheduled task.

        Args:
            job_id: Job ID to cancel

        Returns:
            True if cancelled, False if not found
        """
        async with self._lock:
            job = self.scheduled_jobs.pop(job_id, None)
            if job and not job.done():
                job.cancel()
                return True
            return False

    def get_active_scheduled_task_count(self) -> int:
        """Get number of active scheduled tasks."""
        return sum(1 for job in self.scheduled_jobs.values() if not job.done())

    async def shutdown(self) -> None:
        """Shutdown the scheduled task runner."""
        logger.info("Shutting down scheduled task runner")
        async with self._lock:
            for job in self.scheduled_jobs.values():
                if not job.done():
                    job.cancel()
            self.scheduled_jobs.clear()


class AsyncResultAggregator(Generic[T]):
    """Async result aggregator for collecting multiple results."""

    def __init__(self):
        """Initialize aggregator."""
        self.results: List[Result[T]] = []
        self.completed_count = 0
        self.total_count = 0
        self._lock = asyncio.Lock()

    async def collect_results(
        self,
        operations: List[Callable[[], asyncio.Future[Result[T]]]],
        transform: Callable[[List[Result[T]]], R],
    ) -> R:
        """
        Collect results from multiple operations.

        Args:
            operations: List of async operations
            transform: Function to transform results

        Returns:
            Transformed result
        """
        self.total_count = len(operations)
        self.completed_count = 0

        async def execute_op(operation):
            result = await operation()
            async with self._lock:
                self.completed_count += 1
            return result

        tasks = [asyncio.create_task(execute_op(op)) for op in operations]
        all_results = await asyncio.gather(*tasks)

        return transform(all_results)

    def get_progress(self) -> float:
        """Get completion progress."""
        return self.completed_count / self.total_count if self.total_count > 0 else 0.0


class StreamProcessing:
    """Stream processing utilities."""

    @staticmethod
    async def buffer_with_timeout(
        source: AsyncIterator[T], size: int, timeout: timedelta
    ) -> AsyncIterator[List[T]]:
        """
        Buffer items with timeout.

        Args:
            source: Source async iterator
            size: Buffer size
            timeout: Timeout for buffer emission

        Yields:
            Buffered items
        """
        buffer: List[T] = []
        last_emission_time = time.time()

        async def emit_buffer():
            nonlocal buffer, last_emission_time
            if buffer:
                yield buffer.copy()
                buffer.clear()
                last_emission_time = time.time()

        try:
            async for item in source:
                buffer.append(item)
                current_time = time.time()

                if (
                    len(buffer) >= size
                    or (current_time - last_emission_time) >= timeout.total_seconds()
                ):
                    async for batch in emit_buffer():
                        yield batch
        finally:
            # Emit remaining items
            if buffer:
                yield buffer

    @staticmethod
    async def parallel_map(
        source: AsyncIterator[T],
        transform: Callable[[T], asyncio.Future[R]],
        concurrency: int = None,
    ) -> AsyncIterator[R]:
        """
        Parallel map transformation.

        Args:
            source: Source async iterator
            transform: Transform function
            concurrency: Maximum concurrency

        Yields:
            Transformed items
        """
        concurrency = concurrency or asyncio.cpu_count() or 4
        semaphore = asyncio.Semaphore(concurrency)

        async def transform_with_semaphore(item: T) -> R:
            async with semaphore:
                return await transform(item)

        # Create queue for results
        result_queue: asyncio.Queue[R] = asyncio.Queue()
        active_tasks = set()

        async def process_items():
            async for item in source:
                task = asyncio.create_task(transform_with_semaphore(item))
                active_tasks.add(task)

                # Clean up completed tasks
                done_tasks = {t for t in active_tasks if t.done()}
                for task in done_tasks:
                    result = await task
                    await result_queue.put(result)
                    active_tasks.remove(task)

            # Wait for remaining tasks
            for task in active_tasks:
                result = await task
                await result_queue.put(result)

            # Signal completion
            await result_queue.put(None)

        # Start processing
        asyncio.create_task(process_items())

        # Yield results
        while True:
            result = await result_queue.get()
            if result is None:
                break
            yield result

    @staticmethod
    async def throttle(
        source: AsyncIterator[T], duration: timedelta
    ) -> AsyncIterator[T]:
        """
        Throttle stream to emit at most one item per duration.

        Args:
            source: Source async iterator
            duration: Minimum time between emissions

        Yields:
            Throttled items
        """
        last_emission_time = 0.0

        async for item in source:
            current_time = time.time()
            if current_time - last_emission_time >= duration.total_seconds():
                yield item
                last_emission_time = current_time

    @staticmethod
    async def retry_with_exponential_backoff(
        source: AsyncIterator[T],
        max_attempts: int = 3,
        base_delay: timedelta = timedelta(milliseconds=500),
        max_delay: timedelta = timedelta(seconds=30),
    ) -> AsyncIterator[T]:
        """
        Retry stream processing with exponential backoff.

        Args:
            source: Source async iterator
            max_attempts: Maximum retry attempts
            base_delay: Base retry delay
            max_delay: Maximum retry delay

        Yields:
            Items from source with retry logic
        """
        attempt = 1

        while attempt <= max_attempts:
            try:
                async for item in source:
                    yield item
                break
            except Exception as e:
                if attempt >= max_attempts:
                    raise

                delay_ms = min(
                    base_delay.total_seconds() * 1000 * (2 ** (attempt - 1)),
                    max_delay.total_seconds() * 1000,
                )

                await asyncio.sleep(delay_ms / 1000)
                attempt += 1
