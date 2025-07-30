"""
Modern reactive HTTP client with asyncio and async generators.

Features:
- Reactive HTTP operations with async/await and async generators
- Connection pooling and resource management
- Request/response interceptors
- Circuit breaker pattern
- Retry logic with exponential backoff
- Rate limiting and concurrency control
- Streaming support for large payloads
- Comprehensive metrics and monitoring
- Request/response caching
"""

import asyncio
import aiohttp
import json
import time
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import (
    Any,
    Dict,
    List,
    Optional,
    TypeVar,
    Generic,
    AsyncGenerator,
    Callable,
    Set,
    Type,
    Tuple,
)
from collections import deque
from contextlib import asynccontextmanager
import weakref

logger = logging.getLogger(__name__)

# Type variables
T = TypeVar("T")
R = TypeVar("R")


class HttpMethod(Enum):
    """HTTP method enumeration."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


@dataclass
class RetryConfig:
    """Configuration for retry logic."""

    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 30.0
    backoff_multiplier: float = 2.0
    retryable_status_codes: Set[int] = field(
        default_factory=lambda: {408, 429, 500, 502, 503, 504}
    )
    retryable_exceptions: Set[Type[Exception]] = field(
        default_factory=lambda: {aiohttp.ClientError, asyncio.TimeoutError}
    )


@dataclass
class CacheConfig:
    """Configuration for response caching."""

    enabled: bool = True
    ttl: float = 300.0  # 5 minutes
    cache_key: Optional[str] = None
    cache_methods: Set[HttpMethod] = field(default_factory=lambda: {HttpMethod.GET})
    cache_headers: Set[str] = field(default_factory=set)


@dataclass
class HttpRequestConfig:
    """HTTP request configuration."""

    method: HttpMethod
    url: str
    headers: Dict[str, str] = field(default_factory=dict)
    body: Any = None
    timeout: float = 30.0
    retry_config: RetryConfig = field(default_factory=RetryConfig)
    cache_config: Optional[CacheConfig] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResponseMetadata:
    """HTTP response metadata."""

    request_time: datetime
    response_time: datetime
    duration: timedelta
    from_cache: bool = False
    attempt: int = 1
    url: str = ""
    method: HttpMethod = HttpMethod.GET

    @property
    def latency(self) -> timedelta:
        """Get response latency."""
        return self.duration


@dataclass
class HttpResponseWrapper(Generic[T]):
    """HTTP response wrapper."""

    status: int
    headers: Dict[str, str]
    body: T
    metadata: ResponseMetadata


@dataclass
class HttpClientConfig:
    """HTTP client configuration."""

    connect_timeout: float = 10.0
    request_timeout: float = 30.0
    max_concurrent_requests: int = 100
    max_requests_per_second: int = 1000
    enable_circuit_breaker: bool = True
    enable_retries: bool = True
    enable_caching: bool = True
    enable_metrics: bool = True
    user_agent: str = "ReactiveHttpClient/1.0"
    follow_redirects: bool = True
    connector_limit: int = 100
    connector_limit_per_host: int = 30


@dataclass
class HttpClientMetrics:
    """HTTP client metrics."""

    requests_total: int = 0
    requests_successful: int = 0
    requests_failed: int = 0
    average_latency: timedelta = field(default_factory=lambda: timedelta(0))
    p95_latency: timedelta = field(default_factory=lambda: timedelta(0))
    p99_latency: timedelta = field(default_factory=lambda: timedelta(0))
    cache_hits: int = 0
    cache_misses: int = 0
    circuit_breaker_open_count: int = 0
    rate_limited_requests: int = 0


class RequestInterceptor(ABC):
    """Abstract base class for request interceptors."""

    @abstractmethod
    async def intercept(self, request: HttpRequestConfig) -> HttpRequestConfig:
        """Intercept and potentially modify a request."""
        pass

    @property
    def name(self) -> str:
        """Get interceptor name."""
        return self.__class__.__name__


class ResponseInterceptor(ABC):
    """Abstract base class for response interceptors."""

    @abstractmethod
    async def intercept(
        self, response: HttpResponseWrapper[Any]
    ) -> HttpResponseWrapper[Any]:
        """Intercept and potentially modify a response."""
        pass

    @property
    def name(self) -> str:
        """Get interceptor name."""
        return self.__class__.__name__


class CircuitBreakerState(Enum):
    """Circuit breaker states."""

    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


# Exception classes
class HttpException(Exception):
    """HTTP error exception."""

    def __init__(self, status_code: int, message: str):
        super().__init__(message)
        self.status_code = status_code


class RateLimitedException(Exception):
    """Rate limit exceeded exception."""

    pass


class CircuitBreakerOpenException(Exception):
    """Circuit breaker open exception."""

    pass


class HttpCircuitBreaker:
    """Circuit breaker for HTTP operations."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        slow_call_threshold: float = 10.0,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.slow_call_threshold = slow_call_threshold

        self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._last_failure_time: Optional[float] = None
        self._next_attempt_time: Optional[float] = None
        self._lock = asyncio.Lock()

    async def execute(self, operation: Callable):
        """Execute operation with circuit breaker protection."""
        async with self._lock:
            current_time = time.time()

            if self._state == CircuitBreakerState.OPEN:
                if self._next_attempt_time and current_time >= self._next_attempt_time:
                    self._state = CircuitBreakerState.HALF_OPEN
                else:
                    raise CircuitBreakerOpenException("Circuit breaker is OPEN")

            start_time = time.time()
            try:
                result = await operation()
                end_time = time.time()
                duration = end_time - start_time

                if duration > self.slow_call_threshold:
                    self._record_failure()
                else:
                    self._record_success()

                return result

            except Exception as e:
                self._record_failure()
                raise e

    def _record_success(self):
        """Record successful operation."""
        self._failure_count = 0
        self._state = CircuitBreakerState.CLOSED

    def _record_failure(self):
        """Record failed operation."""
        self._failure_count += 1
        self._last_failure_time = time.time()

        if self._failure_count >= self.failure_threshold:
            self._state = CircuitBreakerState.OPEN
            self._next_attempt_time = time.time() + self.recovery_timeout


class RateLimiter:
    """Token bucket rate limiter."""

    def __init__(self, tokens_per_second: int, bucket_capacity: Optional[int] = None):
        self.tokens_per_second = tokens_per_second
        self.bucket_capacity = bucket_capacity or tokens_per_second
        self._tokens = self.bucket_capacity
        self._last_refill = time.time()
        self._lock = asyncio.Lock()

    async def acquire(self) -> bool:
        """Acquire a token if available."""
        async with self._lock:
            self._refill_tokens()
            if self._tokens > 0:
                self._tokens -= 1
                return True
            return False

    def _refill_tokens(self):
        """Refill tokens based on elapsed time."""
        now = time.time()
        time_passed = now - self._last_refill
        tokens_to_add = int(time_passed * self.tokens_per_second)

        if tokens_to_add > 0:
            self._tokens = min(self.bucket_capacity, self._tokens + tokens_to_add)
            self._last_refill = now


class CacheEntry:
    """Cache entry with expiration."""

    def __init__(self, response: HttpResponseWrapper[Any], expiry_time: float):
        self.response = response
        self.expiry_time = expiry_time

    @property
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        return time.time() > self.expiry_time


class ReactiveHttpClient:
    """Modern reactive HTTP client implementation."""

    def __init__(self, config: Optional[HttpClientConfig] = None):
        self.config = config or HttpClientConfig()
        self._session: Optional[aiohttp.ClientSession] = None
        self._closed = False

        # Interceptors
        self._request_interceptors: List[RequestInterceptor] = []
        self._response_interceptors: List[ResponseInterceptor] = []

        # Resilience patterns
        self._circuit_breaker: Optional[HttpCircuitBreaker] = None
        if self.config.enable_circuit_breaker:
            self._circuit_breaker = HttpCircuitBreaker()

        self._rate_limiter = RateLimiter(self.config.max_requests_per_second)
        self._concurrency_semaphore = asyncio.Semaphore(
            self.config.max_concurrent_requests
        )

        # Caching
        self._response_cache: Dict[str, CacheEntry] = {}

        # Metrics
        self._requests_total = 0
        self._requests_successful = 0
        self._requests_failed = 0
        self._cache_hits = 0
        self._cache_misses = 0
        self._circuit_breaker_open_count = 0
        self._rate_limited_requests = 0
        self._latencies: deque[float] = deque(maxlen=1000)

        # Weak reference cleanup
        self._finalizer = weakref.finalize(self, self._cleanup_resources)

    @property
    def session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(
                total=self.config.request_timeout, connect=self.config.connect_timeout
            )

            connector = aiohttp.TCPConnector(
                limit=self.config.connector_limit,
                limit_per_host=self.config.connector_limit_per_host,
            )

            headers = {"User-Agent": self.config.user_agent}

            self._session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers=headers,
                auto_decompress=True,
            )

        return self._session

    def add_request_interceptor(
        self, interceptor: RequestInterceptor
    ) -> "ReactiveHttpClient":
        """Add request interceptor."""
        self._request_interceptors.append(interceptor)
        return self

    def add_response_interceptor(
        self, interceptor: ResponseInterceptor
    ) -> "ReactiveHttpClient":
        """Add response interceptor."""
        self._response_interceptors.append(interceptor)
        return self

    async def execute(
        self, request_config: HttpRequestConfig, response_type: Type[T] = str
    ) -> HttpResponseWrapper[T]:
        """Execute HTTP request."""
        if self._closed:
            raise RuntimeError("HTTP client is closed")

        self._requests_total += 1

        # Rate limiting
        if not await self._rate_limiter.acquire():
            self._rate_limited_requests += 1
            raise RateLimitedException("Rate limit exceeded")

        # Concurrency limiting
        async with self._concurrency_semaphore:
            try:
                # Check cache first
                if (
                    self.config.enable_caching
                    and request_config.cache_config
                    and request_config.cache_config.enabled
                ):

                    cached_response = self._get_cached_response(request_config)
                    if cached_response:
                        self._cache_hits += 1
                        return cached_response
                    self._cache_misses += 1

                # Execute with circuit breaker
                if self._circuit_breaker:
                    try:
                        response = await self._circuit_breaker.execute(
                            lambda: self._execute_internal(
                                request_config, response_type
                            )
                        )
                    except CircuitBreakerOpenException:
                        self._circuit_breaker_open_count += 1
                        raise
                else:
                    response = await self._execute_internal(
                        request_config, response_type
                    )

                # Cache response if applicable
                if (
                    self.config.enable_caching
                    and request_config.cache_config
                    and request_config.cache_config.enabled
                ):
                    self._cache_response(request_config, response)

                self._requests_successful += 1
                return response

            except Exception:
                self._requests_failed += 1
                raise

    async def execute_streaming(
        self, request_config: HttpRequestConfig, chunk_size: int = 8192
    ) -> AsyncGenerator[bytes, None]:
        """Execute request with streaming response."""
        if self._closed:
            raise RuntimeError("HTTP client is closed")

        # Apply request interceptors
        current_config = request_config
        for interceptor in self._request_interceptors:
            current_config = await interceptor.intercept(current_config)

        async with self.session.request(
            method=current_config.method.value,
            url=current_config.url,
            headers=current_config.headers,
            data=self._prepare_body(current_config.body),
            timeout=aiohttp.ClientTimeout(total=current_config.timeout),
        ) as response:

            if response.status >= 400:
                raise HttpException(response.status, f"HTTP error: {response.status}")

            async for chunk in response.content.iter_chunked(chunk_size):
                yield chunk

    async def execute_batch(
        self,
        requests: List[HttpRequestConfig],
        response_type: Type[T] = str,
        concurrency: int = 10,
    ) -> AsyncGenerator[Tuple[HttpRequestConfig, HttpResponseWrapper[T]], None]:
        """Execute multiple requests concurrently."""
        semaphore = asyncio.Semaphore(concurrency)

        async def execute_single(request: HttpRequestConfig):
            async with semaphore:
                try:
                    response = await self.execute(request, response_type)
                    return request, response
                except Exception:
                    # Return error response
                    error_response = HttpResponseWrapper(
                        status=0,
                        headers={},
                        body=None,
                        metadata=ResponseMetadata(
                            request_time=datetime.now(),
                            response_time=datetime.now(),
                            duration=timedelta(0),
                            url=request.url,
                            method=request.method,
                        ),
                    )
                    return request, error_response

        # Create tasks for all requests
        tasks = [asyncio.create_task(execute_single(request)) for request in requests]

        # Yield results as they complete
        for task in asyncio.as_completed(tasks):
            request, response = await task
            yield request, response

    # Convenience methods
    async def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        cache_config: Optional[CacheConfig] = None,
        response_type: Type[T] = str,
    ) -> HttpResponseWrapper[T]:
        """Execute GET request."""
        config = HttpRequestConfig(
            method=HttpMethod.GET,
            url=url,
            headers=headers or {},
            cache_config=cache_config,
        )
        return await self.execute(config, response_type)

    async def post(
        self,
        url: str,
        body: Any = None,
        headers: Optional[Dict[str, str]] = None,
        response_type: Type[T] = str,
    ) -> HttpResponseWrapper[T]:
        """Execute POST request."""
        config = HttpRequestConfig(
            method=HttpMethod.POST, url=url, headers=headers or {}, body=body
        )
        return await self.execute(config, response_type)

    async def put(
        self,
        url: str,
        body: Any = None,
        headers: Optional[Dict[str, str]] = None,
        response_type: Type[T] = str,
    ) -> HttpResponseWrapper[T]:
        """Execute PUT request."""
        config = HttpRequestConfig(
            method=HttpMethod.PUT, url=url, headers=headers or {}, body=body
        )
        return await self.execute(config, response_type)

    async def delete(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        response_type: Type[T] = str,
    ) -> HttpResponseWrapper[T]:
        """Execute DELETE request."""
        config = HttpRequestConfig(
            method=HttpMethod.DELETE, url=url, headers=headers or {}
        )
        return await self.execute(config, response_type)

    async def get_metrics(self) -> HttpClientMetrics:
        """Get client metrics."""
        latencies_list = list(self._latencies)

        if latencies_list:
            avg_latency = timedelta(seconds=sum(latencies_list) / len(latencies_list))
            sorted_latencies = sorted(latencies_list)
            p95_latency = timedelta(
                seconds=sorted_latencies[int(len(sorted_latencies) * 0.95)]
            )
            p99_latency = timedelta(
                seconds=sorted_latencies[int(len(sorted_latencies) * 0.99)]
            )
        else:
            avg_latency = p95_latency = p99_latency = timedelta(0)

        return HttpClientMetrics(
            requests_total=self._requests_total,
            requests_successful=self._requests_successful,
            requests_failed=self._requests_failed,
            average_latency=avg_latency,
            p95_latency=p95_latency,
            p99_latency=p99_latency,
            cache_hits=self._cache_hits,
            cache_misses=self._cache_misses,
            circuit_breaker_open_count=self._circuit_breaker_open_count,
            rate_limited_requests=self._rate_limited_requests,
        )

    def clear_cache(self):
        """Clear response cache."""
        self._response_cache.clear()

    async def close(self):
        """Close the HTTP client."""
        if not self._closed:
            self._closed = True
            if self._session and not self._session.closed:
                await self._session.close()
            self.clear_cache()
            logger.info("HTTP client closed")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any):
        """Async context manager exit."""
        await self.close()

    # Private methods
    async def _execute_internal(
        self, request_config: HttpRequestConfig, response_type: Type[T]
    ) -> HttpResponseWrapper[T]:
        """Internal request execution with retries."""
        current_config = request_config

        # Apply request interceptors
        for interceptor in self._request_interceptors:
            current_config = await interceptor.intercept(current_config)

        start_time = datetime.now()

        return await self._retry_with_backoff(
            current_config.retry_config,
            lambda: self._make_request(current_config, response_type, start_time),
        )

    async def _make_request(
        self, config: HttpRequestConfig, response_type: Type[T], start_time: datetime
    ) -> HttpResponseWrapper[T]:
        """Make actual HTTP request."""
        async with self.session.request(
            method=config.method.value,
            url=config.url,
            headers=config.headers,
            data=self._prepare_body(config.body),
            timeout=aiohttp.ClientTimeout(total=config.timeout),
        ) as aio_response:

            end_time = datetime.now()
            duration = end_time - start_time

            # Record latency
            self._latencies.append(duration.total_seconds())

            # Parse response body
            body = await self._parse_response_body(aio_response, response_type)

            # Create response wrapper
            response = HttpResponseWrapper(
                status=aio_response.status,
                headers=dict(aio_response.headers),
                body=body,
                metadata=ResponseMetadata(
                    request_time=start_time,
                    response_time=end_time,
                    duration=duration,
                    url=config.url,
                    method=config.method,
                ),
            )

            # Apply response interceptors
            for interceptor in self._response_interceptors:
                response = await interceptor.intercept(response)

            # Check for HTTP errors
            if aio_response.status >= 400:
                raise HttpException(
                    aio_response.status, f"HTTP error: {aio_response.status}"
                )

            return response

    def _prepare_body(self, body: Any) -> Any:
        """Prepare request body."""
        if body is None:
            return None
        elif isinstance(body, (str, bytes)):
            return body
        else:
            return json.dumps(body)

    async def _parse_response_body(
        self, response: aiohttp.ClientResponse, response_type: Type[T]
    ) -> Any:
        """Parse response body based on type."""
        if response_type == bytes:
            return await response.read()
        elif response_type == str:
            return await response.text()
        else:
            text = await response.text()
            if text:
                return json.loads(text)
            return None

    async def _retry_with_backoff(
        self, retry_config: RetryConfig, operation: Callable
    ) -> Any:
        """Retry operation with exponential backoff."""
        attempt = 0
        delay = retry_config.initial_delay

        while attempt < retry_config.max_attempts:
            try:
                return await operation()
            except Exception as e:
                attempt += 1

                should_retry = False
                if isinstance(e, HttpException):
                    should_retry = e.status_code in retry_config.retryable_status_codes
                else:
                    should_retry = any(
                        isinstance(e, exc_type)
                        for exc_type in retry_config.retryable_exceptions
                    )

                if attempt >= retry_config.max_attempts or not should_retry:
                    raise e

                await asyncio.sleep(delay)
                delay = min(
                    delay * retry_config.backoff_multiplier, retry_config.max_delay
                )

        raise RuntimeError("This should never be reached")

    def _get_cached_response(
        self, config: HttpRequestConfig
    ) -> Optional[HttpResponseWrapper[Any]]:
        """Get cached response if available."""
        if not config.cache_config or not config.cache_config.cache_key:
            cache_key = self._generate_cache_key(config)
        else:
            cache_key = config.cache_config.cache_key

        cache_entry = self._response_cache.get(cache_key)
        if cache_entry and not cache_entry.is_expired:
            # Update metadata to indicate cache hit
            cached_response = cache_entry.response
            cached_response.metadata.from_cache = True
            return cached_response
        elif cache_entry:
            # Remove expired entry
            del self._response_cache[cache_key]

        return None

    def _cache_response(
        self, config: HttpRequestConfig, response: HttpResponseWrapper[Any]
    ):
        """Cache response if applicable."""
        cache_config = config.cache_config
        if (
            not cache_config
            or not cache_config.cache_methods
            or config.method not in cache_config.cache_methods
        ):
            return

        cache_key = cache_config.cache_key or self._generate_cache_key(config)
        expiry_time = time.time() + cache_config.ttl

        self._response_cache[cache_key] = CacheEntry(response, expiry_time)

    def _generate_cache_key(self, config: HttpRequestConfig) -> str:
        """Generate cache key for request."""
        return f"{config.method.value}:{config.url}:{hash(frozenset(config.headers.items()))}"

    @staticmethod
    def _cleanup_resources():
        """Cleanup resources (called by finalizer)."""
        logger.debug("HTTP client resources cleaned up")


# Built-in interceptors
class LoggingRequestInterceptor(RequestInterceptor):
    """Logging request interceptor."""

    def __init__(self, logger_name: str = __name__):
        self.logger = logging.getLogger(logger_name)

    async def intercept(self, request: HttpRequestConfig) -> HttpRequestConfig:
        self.logger.debug(f"HTTP Request: {request.method.value} {request.url}")
        return request


class LoggingResponseInterceptor(ResponseInterceptor):
    """Logging response interceptor."""

    def __init__(self, logger_name: str = __name__):
        self.logger = logging.getLogger(logger_name)

    async def intercept(
        self, response: HttpResponseWrapper[Any]
    ) -> HttpResponseWrapper[Any]:
        self.logger.debug(
            f"HTTP Response: {response.status} ({response.metadata.duration})"
        )
        return response


class AuthenticationInterceptor(RequestInterceptor):
    """Authentication interceptor."""

    def __init__(self, token: str, auth_type: str = "Bearer"):
        self.token = token
        self.auth_type = auth_type

    async def intercept(self, request: HttpRequestConfig) -> HttpRequestConfig:
        headers = request.headers.copy()
        headers["Authorization"] = f"{self.auth_type} {self.token}"
        return HttpRequestConfig(
            method=request.method,
            url=request.url,
            headers=headers,
            body=request.body,
            timeout=request.timeout,
            retry_config=request.retry_config,
            cache_config=request.cache_config,
            metadata=request.metadata,
        )


class ContentTypeInterceptor(RequestInterceptor):
    """Content-Type interceptor."""

    def __init__(self, content_type: str = "application/json"):
        self.content_type = content_type

    async def intercept(self, request: HttpRequestConfig) -> HttpRequestConfig:
        if (
            request.method in {HttpMethod.POST, HttpMethod.PUT, HttpMethod.PATCH}
            and request.body is not None
        ):
            headers = request.headers.copy()
            headers["Content-Type"] = self.content_type
            return HttpRequestConfig(
                method=request.method,
                url=request.url,
                headers=headers,
                body=request.body,
                timeout=request.timeout,
                retry_config=request.retry_config,
                cache_config=request.cache_config,
                metadata=request.metadata,
            )
        return request


# Builder and DSL
class HttpClientBuilder:
    """Builder for HTTP client."""

    def __init__(self):
        self._config = HttpClientConfig()
        self._request_interceptors: List[RequestInterceptor] = []
        self._response_interceptors: List[ResponseInterceptor] = []

    def config(self, **kwargs: Any) -> "HttpClientBuilder":
        """Set configuration options."""
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
        return self

    def request_interceptor(
        self, interceptor: RequestInterceptor
    ) -> "HttpClientBuilder":
        """Add request interceptor."""
        self._request_interceptors.append(interceptor)
        return self

    def response_interceptor(
        self, interceptor: ResponseInterceptor
    ) -> "HttpClientBuilder":
        """Add response interceptor."""
        self._response_interceptors.append(interceptor)
        return self

    def build(self) -> ReactiveHttpClient:
        """Build HTTP client."""
        client = ReactiveHttpClient(self._config)

        for interceptor in self._request_interceptors:
            client.add_request_interceptor(interceptor)

        for interceptor in self._response_interceptors:
            client.add_response_interceptor(interceptor)

        return client


def create_http_client(**config_kwargs: Any) -> ReactiveHttpClient:
    """Create HTTP client with configuration."""
    builder = HttpClientBuilder()
    if config_kwargs:
        builder.config(**config_kwargs)
    return builder.build()


# Convenience context manager
@asynccontextmanager
async def http_client(**config_kwargs: Any):
    """Create HTTP client as async context manager."""
    client = create_http_client(**config_kwargs)
    try:
        yield client
    finally:
        await client.close()


# Extension methods (implemented as functions)
async def get_json(client: ReactiveHttpClient, url: str, **kwargs: Any) -> Any:
    """Get JSON response."""
    response = await client.get(url, **kwargs)
    return response.body


async def post_json(
    client: ReactiveHttpClient, url: str, body: Any, **kwargs: Any
) -> Any:
    """Post JSON and get JSON response."""
    headers = kwargs.get("headers", {})
    headers["Content-Type"] = "application/json"
    kwargs["headers"] = headers

    response = await client.post(url, body, **kwargs)
    return response.body


async def put_json(
    client: ReactiveHttpClient, url: str, body: Any, **kwargs: Any
) -> Any:
    """Put JSON and get JSON response."""
    headers = kwargs.get("headers", {})
    headers["Content-Type"] = "application/json"
    kwargs["headers"] = headers

    response = await client.put(url, body, **kwargs)
    return response.body
