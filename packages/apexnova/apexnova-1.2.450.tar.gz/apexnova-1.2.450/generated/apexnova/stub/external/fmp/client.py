"""
Financial Modeling Prep API client implementation.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Union, Any, Callable
from datetime import datetime, date, timedelta
from decimal import Decimal
from urllib.parse import urljoin, urlencode

import aiohttp
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .exceptions import (
    FMPError,
    FMPAuthenticationError,
    FMPRateLimitError,
    FMPNotFoundError,
    FMPValidationError,
    FMPServerError,
    FMPTimeoutError,
)
from .models import (
    CompanyProfile,
    StockQuote,
    IncomeStatement,
    BalanceSheet,
    CashFlowStatement,
    FinancialRatios,
    KeyMetrics,
    StockPrice,
    SearchResult,
    MarketNews,
    EarningsCalendar,
    Dividend,
    StockSplit,
    ReportingPeriod,
)

logger = logging.getLogger(__name__)


class FinancialModelingPrepClient:
    """
    Financial Modeling Prep API client with comprehensive functionality.

    Features:
    - Rate limiting and retry logic
    - Async and sync support
    - Caching with TTL
    - Comprehensive error handling
    - Data validation
    - Type-safe responses
    """

    BASE_URL = "https://financialmodelingprep.com/api"
    DEFAULT_VERSION = "v3"

    def __init__(
        self,
        api_key: str,
        version: str = DEFAULT_VERSION,
        timeout: int = 30,
        max_retries: int = 3,
        rate_limit_requests: int = 300,
        rate_limit_period: int = 60,
        enable_caching: bool = True,
        cache_ttl: int = 300,
        max_cache_size: int = 1000,
        enable_async: bool = True,
    ):
        """
        Initialize the Financial Modeling Prep client.

        Args:
            api_key: Your FMP API key
            version: API version (default: v3)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            rate_limit_requests: Maximum requests per period
            rate_limit_period: Rate limit period in seconds
            enable_caching: Enable response caching
            cache_ttl: Cache time-to-live in seconds
            max_cache_size: Maximum cache entries
            enable_async: Enable async HTTP session
        """
        self.api_key = api_key
        self.version = version
        self.base_url = f"{self.BASE_URL}/{version}"
        self.timeout = timeout
        self.max_retries = max_retries
        self.rate_limit_requests = rate_limit_requests
        self.rate_limit_period = rate_limit_period
        self.enable_caching = enable_caching
        self.cache_ttl = cache_ttl
        self.max_cache_size = max_cache_size
        self.enable_async = enable_async

        # Rate limiting
        self._request_times: List[float] = []
        self._rate_limit_lock = asyncio.Lock() if enable_async else None

        # Caching
        self._cache: Dict[str, Dict[str, Any]] = {}

        # HTTP sessions
        self._session: Optional[requests.Session] = None
        self._async_session: Optional[aiohttp.ClientSession] = None

        self._setup_sync_session()

    def _setup_sync_session(self) -> None:
        """Set up synchronous HTTP session with retry strategy."""
        self._session = requests.Session()

        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

    async def _setup_async_session(self) -> None:
        """Set up asynchronous HTTP session."""
        if not self._async_session:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._async_session = aiohttp.ClientSession(timeout=timeout)

    def _build_url(self, endpoint: str, **params: Any) -> str:
        """Build full URL with parameters."""
        url = urljoin(self.base_url, endpoint)

        # Add API key
        params["apikey"] = self.api_key

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        if params:
            url += "?" + urlencode(params)

        return url

    def _get_cache_key(self, url: str) -> str:
        """Generate cache key for URL."""
        return url

    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is still valid."""
        return time.time() - cache_entry["timestamp"] < self.cache_ttl

    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Get data from cache if valid."""
        if not self.enable_caching:
            return None

        cache_entry = self._cache.get(cache_key)
        if cache_entry and self._is_cache_valid(cache_entry):
            logger.debug(f"Cache hit for {cache_key}")
            return cache_entry["data"]

        # Remove expired entry
        if cache_entry:
            del self._cache[cache_key]

        return None

    def _set_cache(self, cache_key: str, data: Any) -> None:
        """Set data in cache."""
        if not self.enable_caching:
            return

        # Remove oldest entries if cache is full
        if len(self._cache) >= self.max_cache_size:
            oldest_key = min(
                self._cache.keys(), key=lambda k: self._cache[k]["timestamp"]
            )
            del self._cache[oldest_key]

        self._cache[cache_key] = {
            "data": data,
            "timestamp": time.time(),
        }
        logger.debug(f"Cached data for {cache_key}")

    async def _check_rate_limit(self) -> None:
        """Check and enforce rate limiting."""
        if not self.enable_async or not self._rate_limit_lock:
            return

        async with self._rate_limit_lock:
            now = time.time()

            # Remove old request times
            self._request_times = [
                req_time
                for req_time in self._request_times
                if now - req_time < self.rate_limit_period
            ]

            # Check if we've exceeded the rate limit
            if len(self._request_times) >= self.rate_limit_requests:
                oldest_request = min(self._request_times)
                sleep_time = self.rate_limit_period - (now - oldest_request)
                if sleep_time > 0:
                    logger.warning(
                        f"Rate limit reached, sleeping for {sleep_time:.2f} seconds"
                    )
                    await asyncio.sleep(sleep_time)

            # Record this request
            self._request_times.append(now)

    def _handle_response(self, response: requests.Response, url: str) -> Any:
        """Handle HTTP response and extract data."""
        if response.status_code == 401:
            raise FMPAuthenticationError("Invalid API key")
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise FMPRateLimitError(
                "Rate limit exceeded",
                retry_after=int(retry_after) if retry_after else None,
            )
        elif response.status_code == 404:
            raise FMPNotFoundError("Resource not found")
        elif response.status_code >= 500:
            raise FMPServerError(f"Server error: {response.status_code}")
        elif response.status_code != 200:
            raise FMPError(
                f"HTTP {response.status_code}: {response.text}", response.status_code
            )

        try:
            data = response.json()
        except ValueError as e:
            raise FMPError(f"Invalid JSON response: {e}")

        # Handle API errors in response body
        if isinstance(data, dict) and "Error Message" in data:
            raise FMPError(data["Error Message"])

        return data

    async def _handle_async_response(
        self, response: aiohttp.ClientResponse, url: str
    ) -> Any:
        """Handle async HTTP response and extract data."""
        if response.status == 401:
            raise FMPAuthenticationError("Invalid API key")
        elif response.status == 429:
            retry_after = response.headers.get("Retry-After")
            raise FMPRateLimitError(
                "Rate limit exceeded",
                retry_after=int(retry_after) if retry_after else None,
            )
        elif response.status == 404:
            raise FMPNotFoundError("Resource not found")
        elif response.status >= 500:
            raise FMPServerError(f"Server error: {response.status}")
        elif response.status != 200:
            text = await response.text()
            raise FMPError(f"HTTP {response.status}: {text}", response.status)

        try:
            data = await response.json()
        except ValueError as e:
            raise FMPError(f"Invalid JSON response: {e}")

        # Handle API errors in response body
        if isinstance(data, dict) and "Error Message" in data:
            raise FMPError(data["Error Message"])

        return data

    def _request(self, endpoint: str, **params: Any) -> Any:
        """Make synchronous HTTP request."""
        url = self._build_url(endpoint, **params)
        cache_key = self._get_cache_key(url)

        # Check cache first
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            return cached_data

        try:
            logger.debug(f"Making request to {url}")
            response = self._session.get(url, timeout=self.timeout)
            data = self._handle_response(response, url)

            # Cache the response
            self._set_cache(cache_key, data)

            return data

        except requests.exceptions.Timeout:
            raise FMPTimeoutError("Request timed out")
        except requests.exceptions.RequestException as e:
            raise FMPError(f"Request failed: {e}")

    async def _async_request(self, endpoint: str, **params: Any) -> Any:
        """Make asynchronous HTTP request."""
        await self._setup_async_session()
        await self._check_rate_limit()

        url = self._build_url(endpoint, **params)
        cache_key = self._get_cache_key(url)

        # Check cache first
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            return cached_data

        try:
            logger.debug(f"Making async request to {url}")
            async with self._async_session.get(url) as response:
                data = await self._handle_async_response(response, url)

                # Cache the response
                self._set_cache(cache_key, data)

                return data

        except asyncio.TimeoutError:
            raise FMPTimeoutError("Request timed out")
        except aiohttp.ClientError as e:
            raise FMPError(f"Request failed: {e}")

    # Company Information
    def get_company_profile(self, symbol: str) -> CompanyProfile:
        """Get company profile information."""
        data = self._request(f"profile/{symbol}")
        if not data:
            raise FMPNotFoundError(f"Company profile not found for symbol: {symbol}")
        return CompanyProfile.from_dict(data[0])

    async def get_company_profile_async(self, symbol: str) -> CompanyProfile:
        """Get company profile information (async)."""
        data = await self._async_request(f"profile/{symbol}")
        if not data:
            raise FMPNotFoundError(f"Company profile not found for symbol: {symbol}")
        return CompanyProfile.from_dict(data[0])

    def get_company_executives(self, symbol: str) -> List[Dict[str, Any]]:
        """Get company executives information."""
        return self._request(f"key-executives/{symbol}")

    async def get_company_executives_async(self, symbol: str) -> List[Dict[str, Any]]:
        """Get company executives information (async)."""
        return await self._async_request(f"key-executives/{symbol}")

    # Financial Statements
    def get_income_statement(
        self,
        symbol: str,
        period: ReportingPeriod = ReportingPeriod.ANNUAL,
        limit: int = 10,
    ) -> List[IncomeStatement]:
        """Get income statement data."""
        data = self._request(
            f"income-statement/{symbol}", period=period.value, limit=limit
        )
        return [IncomeStatement.from_dict(item) for item in data]

    async def get_income_statement_async(
        self,
        symbol: str,
        period: ReportingPeriod = ReportingPeriod.ANNUAL,
        limit: int = 10,
    ) -> List[IncomeStatement]:
        """Get income statement data (async)."""
        data = await self._async_request(
            f"income-statement/{symbol}", period=period.value, limit=limit
        )
        return [IncomeStatement.from_dict(item) for item in data]

    def get_balance_sheet(
        self,
        symbol: str,
        period: ReportingPeriod = ReportingPeriod.ANNUAL,
        limit: int = 10,
    ) -> List[BalanceSheet]:
        """Get balance sheet data."""
        data = self._request(
            f"balance-sheet-statement/{symbol}", period=period.value, limit=limit
        )
        return [BalanceSheet.from_dict(item) for item in data]

    async def get_balance_sheet_async(
        self,
        symbol: str,
        period: ReportingPeriod = ReportingPeriod.ANNUAL,
        limit: int = 10,
    ) -> List[BalanceSheet]:
        """Get balance sheet data (async)."""
        data = await self._async_request(
            f"balance-sheet-statement/{symbol}", period=period.value, limit=limit
        )
        return [BalanceSheet.from_dict(item) for item in data]

    def get_cash_flow_statement(
        self,
        symbol: str,
        period: ReportingPeriod = ReportingPeriod.ANNUAL,
        limit: int = 10,
    ) -> List[CashFlowStatement]:
        """Get cash flow statement data."""
        data = self._request(
            f"cash-flow-statement/{symbol}", period=period.value, limit=limit
        )
        return [CashFlowStatement.from_dict(item) for item in data]

    async def get_cash_flow_statement_async(
        self,
        symbol: str,
        period: ReportingPeriod = ReportingPeriod.ANNUAL,
        limit: int = 10,
    ) -> List[CashFlowStatement]:
        """Get cash flow statement data (async)."""
        data = await self._async_request(
            f"cash-flow-statement/{symbol}", period=period.value, limit=limit
        )
        return [CashFlowStatement.from_dict(item) for item in data]

    def get_financial_ratios(
        self,
        symbol: str,
        period: ReportingPeriod = ReportingPeriod.ANNUAL,
        limit: int = 10,
    ) -> List[FinancialRatios]:
        """Get financial ratios data."""
        data = self._request(f"ratios/{symbol}", period=period.value, limit=limit)
        return [FinancialRatios.from_dict(item) for item in data]

    async def get_financial_ratios_async(
        self,
        symbol: str,
        period: ReportingPeriod = ReportingPeriod.ANNUAL,
        limit: int = 10,
    ) -> List[FinancialRatios]:
        """Get financial ratios data (async)."""
        data = await self._async_request(
            f"ratios/{symbol}", period=period.value, limit=limit
        )
        return [FinancialRatios.from_dict(item) for item in data]

    def get_key_metrics(
        self,
        symbol: str,
        period: ReportingPeriod = ReportingPeriod.ANNUAL,
        limit: int = 10,
    ) -> List[KeyMetrics]:
        """Get key metrics data."""
        data = self._request(f"key-metrics/{symbol}", period=period.value, limit=limit)
        return [KeyMetrics.from_dict(item) for item in data]

    async def get_key_metrics_async(
        self,
        symbol: str,
        period: ReportingPeriod = ReportingPeriod.ANNUAL,
        limit: int = 10,
    ) -> List[KeyMetrics]:
        """Get key metrics data (async)."""
        data = await self._async_request(
            f"key-metrics/{symbol}", period=period.value, limit=limit
        )
        return [KeyMetrics.from_dict(item) for item in data]

    # Market Data
    def get_quote(self, symbol: str) -> StockQuote:
        """Get real-time stock quote."""
        data = self._request(f"quote/{symbol}")
        if not data:
            raise FMPNotFoundError(f"Quote not found for symbol: {symbol}")
        return StockQuote.from_dict(data[0])

    async def get_quote_async(self, symbol: str) -> StockQuote:
        """Get real-time stock quote (async)."""
        data = await self._async_request(f"quote/{symbol}")
        if not data:
            raise FMPNotFoundError(f"Quote not found for symbol: {symbol}")
        return StockQuote.from_dict(data[0])

    def get_quotes(self, symbols: List[str]) -> List[StockQuote]:
        """Get real-time quotes for multiple symbols."""
        symbol_list = ",".join(symbols)
        data = self._request(f"quote/{symbol_list}")
        return [StockQuote.from_dict(item) for item in data]

    async def get_quotes_async(self, symbols: List[str]) -> List[StockQuote]:
        """Get real-time quotes for multiple symbols (async)."""
        symbol_list = ",".join(symbols)
        data = await self._async_request(f"quote/{symbol_list}")
        return [StockQuote.from_dict(item) for item in data]

    def get_historical_prices(
        self,
        symbol: str,
        from_date: Optional[Union[str, date]] = None,
        to_date: Optional[Union[str, date]] = None,
        timeseries: int = 100,
    ) -> List[StockPrice]:
        """Get historical stock prices."""
        params = {"timeseries": timeseries}

        if from_date:
            if isinstance(from_date, date):
                from_date = from_date.strftime("%Y-%m-%d")
            params["from"] = from_date

        if to_date:
            if isinstance(to_date, date):
                to_date = to_date.strftime("%Y-%m-%d")
            params["to"] = to_date

        data = self._request(f"historical-price-full/{symbol}", **params)

        if isinstance(data, dict) and "historical" in data:
            return [
                StockPrice.from_dict({**item, "symbol": symbol})
                for item in data["historical"]
            ]
        return []

    async def get_historical_prices_async(
        self,
        symbol: str,
        from_date: Optional[Union[str, date]] = None,
        to_date: Optional[Union[str, date]] = None,
        timeseries: int = 100,
    ) -> List[StockPrice]:
        """Get historical stock prices (async)."""
        params = {"timeseries": timeseries}

        if from_date:
            if isinstance(from_date, date):
                from_date = from_date.strftime("%Y-%m-%d")
            params["from"] = from_date

        if to_date:
            if isinstance(to_date, date):
                to_date = to_date.strftime("%Y-%m-%d")
            params["to"] = to_date

        data = await self._async_request(f"historical-price-full/{symbol}", **params)

        if isinstance(data, dict) and "historical" in data:
            return [
                StockPrice.from_dict({**item, "symbol": symbol})
                for item in data["historical"]
            ]
        return []

    # Search and Screening
    def search_symbols(self, query: str, limit: int = 10) -> List[SearchResult]:
        """Search for symbols by company name or ticker."""
        data = self._request("search", query=query, limit=limit)
        return [SearchResult.from_dict(item) for item in data]

    async def search_symbols_async(
        self, query: str, limit: int = 10
    ) -> List[SearchResult]:
        """Search for symbols by company name or ticker (async)."""
        data = await self._async_request("search", query=query, limit=limit)
        return [SearchResult.from_dict(item) for item in data]

    def get_symbol_list(self) -> List[Dict[str, Any]]:
        """Get complete list of available symbols."""
        return self._request("stock/list")

    async def get_symbol_list_async(self) -> List[Dict[str, Any]]:
        """Get complete list of available symbols (async)."""
        return await self._async_request("stock/list")

    def get_tradable_symbols(self) -> List[Dict[str, Any]]:
        """Get list of tradable symbols."""
        return self._request("available-traded/list")

    async def get_tradable_symbols_async(self) -> List[Dict[str, Any]]:
        """Get list of tradable symbols (async)."""
        return await self._async_request("available-traded/list")

    # News and Events
    def get_market_news(self, limit: int = 50, page: int = 0) -> List[MarketNews]:
        """Get market news."""
        data = self._request("fmp/articles", limit=limit, page=page)
        return [MarketNews.from_dict(item) for item in data]

    async def get_market_news_async(
        self, limit: int = 50, page: int = 0
    ) -> List[MarketNews]:
        """Get market news (async)."""
        data = await self._async_request("fmp/articles", limit=limit, page=page)
        return [MarketNews.from_dict(item) for item in data]

    def get_stock_news(
        self, symbol: str, limit: int = 50, page: int = 0
    ) -> List[MarketNews]:
        """Get news for specific stock."""
        data = self._request(f"stock_news", tickers=symbol, limit=limit, page=page)
        return [MarketNews.from_dict(item) for item in data]

    async def get_stock_news_async(
        self, symbol: str, limit: int = 50, page: int = 0
    ) -> List[MarketNews]:
        """Get news for specific stock (async)."""
        data = await self._async_request(
            f"stock_news", tickers=symbol, limit=limit, page=page
        )
        return [MarketNews.from_dict(item) for item in data]

    def get_earnings_calendar(
        self,
        from_date: Optional[Union[str, date]] = None,
        to_date: Optional[Union[str, date]] = None,
    ) -> List[EarningsCalendar]:
        """Get earnings calendar."""
        params = {}

        if from_date:
            if isinstance(from_date, date):
                from_date = from_date.strftime("%Y-%m-%d")
            params["from"] = from_date

        if to_date:
            if isinstance(to_date, date):
                to_date = to_date.strftime("%Y-%m-%d")
            params["to"] = to_date

        data = self._request("earning_calendar", **params)
        return [EarningsCalendar.from_dict(item) for item in data]

    async def get_earnings_calendar_async(
        self,
        from_date: Optional[Union[str, date]] = None,
        to_date: Optional[Union[str, date]] = None,
    ) -> List[EarningsCalendar]:
        """Get earnings calendar (async)."""
        params = {}

        if from_date:
            if isinstance(from_date, date):
                from_date = from_date.strftime("%Y-%m-%d")
            params["from"] = from_date

        if to_date:
            if isinstance(to_date, date):
                to_date = to_date.strftime("%Y-%m-%d")
            params["to"] = to_date

        data = await self._async_request("earning_calendar", **params)
        return [EarningsCalendar.from_dict(item) for item in data]

    # Dividends and Splits
    def get_dividend_history(self, symbol: str) -> List[Dividend]:
        """Get dividend history for a symbol."""
        data = self._request(f"historical-price-full/stock_dividend/{symbol}")

        if isinstance(data, dict) and "historical" in data:
            return [
                Dividend.from_dict({**item, "symbol": symbol})
                for item in data["historical"]
            ]
        return []

    async def get_dividend_history_async(self, symbol: str) -> List[Dividend]:
        """Get dividend history for a symbol (async)."""
        data = await self._async_request(
            f"historical-price-full/stock_dividend/{symbol}"
        )

        if isinstance(data, dict) and "historical" in data:
            return [
                Dividend.from_dict({**item, "symbol": symbol})
                for item in data["historical"]
            ]
        return []

    def get_stock_splits(self, symbol: str) -> List[StockSplit]:
        """Get stock split history for a symbol."""
        data = self._request(f"historical-price-full/stock_split/{symbol}")

        if isinstance(data, dict) and "historical" in data:
            return [
                StockSplit.from_dict({**item, "symbol": symbol})
                for item in data["historical"]
            ]
        return []

    async def get_stock_splits_async(self, symbol: str) -> List[StockSplit]:
        """Get stock split history for a symbol (async)."""
        data = await self._async_request(f"historical-price-full/stock_split/{symbol}")

        if isinstance(data, dict) and "historical" in data:
            return [
                StockSplit.from_dict({**item, "symbol": symbol})
                for item in data["historical"]
            ]
        return []

    # Utility Methods
    def validate_symbol(self, symbol: str) -> bool:
        """Validate if a symbol exists."""
        try:
            self.get_quote(symbol)
            return True
        except FMPNotFoundError:
            return False

    async def validate_symbol_async(self, symbol: str) -> bool:
        """Validate if a symbol exists (async)."""
        try:
            await self.get_quote_async(symbol)
            return True
        except FMPNotFoundError:
            return False

    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
        logger.info("Cache cleared")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "total_entries": len(self._cache),
            "max_size": self.max_cache_size,
            "ttl_seconds": self.cache_ttl,
            "enabled": self.enable_caching,
        }

    async def close(self) -> None:
        """Close async session if it exists."""
        if self._async_session:
            await self._async_session.close()
            self._async_session = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._session:
            self._session.close()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
