"""External API integrations module."""

from .fmp import (
    FinancialModelingPrepClient,
    FMPError,
    FMPRateLimitError,
    FMPAuthenticationError,
    FMPNotFoundError,
    CompanyProfile,
    FinancialStatement,
    StockQuote,
    MarketData,
    SearchResult,
)

__all__ = [
    # Client
    "FinancialModelingPrepClient",
    # Exceptions
    "FMPError",
    "FMPRateLimitError",
    "FMPAuthenticationError",
    "FMPNotFoundError",
    # Data models
    "CompanyProfile",
    "FinancialStatement",
    "StockQuote",
    "MarketData",
    "SearchResult",
]
