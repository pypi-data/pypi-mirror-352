"""ApexNova stub utilities for Python.

This package provides utility classes and services for working with ApexNova
protobuf definitions, including authorization, telemetry, and repository patterns.
It also includes external API integrations like Financial Modeling Prep.
"""

# Authorization components
from apexnova.stub.authorization.authorization_status import AuthorizationStatus
from apexnova.stub.authorization.authorization_rule import AuthorizationRule
from apexnova.stub.authorization.model.base_authorization_model import (
    BaseAuthorizationModel,
)

# Services
from apexnova.stub.service.application_insights_service import (
    ApplicationInsightsService,
)
from apexnova.stub.service.request_handler_service import RequestHandlerService

# Models
from apexnova.stub.model.base_model import IBaseModel
from apexnova.stub.model.base_element import IBaseElement

# Feature management
from apexnova.stub.feature.context.feature_targeting_context import (
    FeatureTargetingContext,
)

# External API integrations
from apexnova.stub.external.fmp import (
    FinancialModelingPrepClient,
    FMPError,
    FMPRateLimitError,
    FMPAuthenticationError,
    FMPNotFoundError,
    CompanyProfile,
    StockQuote,
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

__version__ = "1.0.0"

__all__ = [
    # Authorization
    "AuthorizationStatus",
    "AuthorizationRule",
    "BaseAuthorizationModel",
    # Services
    "ApplicationInsightsService",
    "RequestHandlerService",
    # Models
    "IBaseModel",
    "IBaseElement",
    # Feature management
    "FeatureTargetingContext",
    # External APIs - FMP
    "FinancialModelingPrepClient",
    "FMPError",
    "FMPRateLimitError",
    "FMPAuthenticationError",
    "FMPNotFoundError",
    "CompanyProfile",
    "StockQuote",
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
