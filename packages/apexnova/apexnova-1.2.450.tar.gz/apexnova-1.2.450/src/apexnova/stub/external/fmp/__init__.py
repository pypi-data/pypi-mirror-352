"""Financial Modeling Prep API client."""

from .client import FinancialModelingPrepClient
from .exceptions import (
    FMPError,
    FMPRateLimitError,
    FMPAuthenticationError,
    FMPNotFoundError,
)
from .models import (
    CompanyProfile,
    FinancialStatement,
    StockQuote,
    MarketData,
    SearchResult,
    IncomeStatement,
    BalanceSheet,
    CashFlowStatement,
    FinancialRatios,
    KeyMetrics,
    StockPrice,
    MarketNews,
    EarningsCalendar,
    Dividend,
    StockSplit,
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
    "IncomeStatement",
    "BalanceSheet",
    "CashFlowStatement",
    "FinancialRatios",
    "KeyMetrics",
    "StockPrice",
    "MarketNews",
    "EarningsCalendar",
    "Dividend",
    "StockSplit",
]
