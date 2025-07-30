"""
Utility functions and convenience classes for FMP API.
"""

import os
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date, timedelta
from decimal import Decimal
import logging

from .client import FinancialModelingPrepClient
from .models import (
    CompanyProfile,
    StockQuote,
    IncomeStatement,
    BalanceSheet,
    CashFlowStatement,
    StockPrice,
    SearchResult,
    ReportingPeriod,
)
from .exceptions import FMPError

logger = logging.getLogger(__name__)


class FMPClientFactory:
    """Factory for creating FMP clients with common configurations."""

    @staticmethod
    def create_client(
        api_key: Optional[str] = None, config_name: str = "default"
    ) -> FinancialModelingPrepClient:
        """
        Create an FMP client with predefined configurations.

        Args:
            api_key: API key (if None, tries to get from environment)
            config_name: Configuration preset name

        Returns:
            Configured FMP client
        """
        if api_key is None:
            api_key = os.getenv("FMP_API_KEY")
            if not api_key:
                raise ValueError(
                    "API key must be provided or set in FMP_API_KEY environment variable"
                )

        configs = {
            "default": {
                "timeout": 30,
                "max_retries": 3,
                "enable_caching": True,
                "cache_ttl": 300,
            },
            "fast": {
                "timeout": 10,
                "max_retries": 1,
                "enable_caching": True,
                "cache_ttl": 60,
            },
            "reliable": {
                "timeout": 60,
                "max_retries": 5,
                "enable_caching": True,
                "cache_ttl": 600,
                "rate_limit_requests": 150,  # More conservative
            },
            "no_cache": {
                "timeout": 30,
                "max_retries": 3,
                "enable_caching": False,
            },
        }

        config = configs.get(config_name, configs["default"])
        return FinancialModelingPrepClient(api_key=api_key, **config)


class StockAnalyzer:
    """High-level stock analysis utility class."""

    def __init__(self, client: FinancialModelingPrepClient):
        self.client = client

    def get_complete_stock_data(
        self, symbol: str, include_historical: bool = True, historical_days: int = 365
    ) -> Dict[str, Any]:
        """
        Get comprehensive stock data for analysis.

        Args:
            symbol: Stock symbol
            include_historical: Whether to include historical prices
            historical_days: Number of days of historical data

        Returns:
            Dictionary with complete stock information
        """
        try:
            # Basic information
            profile = self.client.get_company_profile(symbol)
            quote = self.client.get_quote(symbol)

            # Financial statements (last 4 years)
            income_annual = self.client.get_income_statement(
                symbol, ReportingPeriod.ANNUAL, 4
            )
            income_quarterly = self.client.get_income_statement(
                symbol, ReportingPeriod.QUARTERLY, 4
            )
            balance_annual = self.client.get_balance_sheet(
                symbol, ReportingPeriod.ANNUAL, 4
            )
            cash_flow_annual = self.client.get_cash_flow_statement(
                symbol, ReportingPeriod.ANNUAL, 4
            )

            # Ratios and metrics
            ratios = self.client.get_financial_ratios(symbol, ReportingPeriod.ANNUAL, 4)
            key_metrics = self.client.get_key_metrics(symbol, ReportingPeriod.ANNUAL, 4)

            result = {
                "symbol": symbol,
                "profile": profile,
                "quote": quote,
                "financials": {
                    "income_annual": income_annual,
                    "income_quarterly": income_quarterly,
                    "balance_sheet": balance_annual,
                    "cash_flow": cash_flow_annual,
                },
                "analysis": {
                    "ratios": ratios,
                    "key_metrics": key_metrics,
                },
                "timestamp": datetime.now(),
            }

            # Add historical prices if requested
            if include_historical:
                to_date = date.today()
                from_date = to_date - timedelta(days=historical_days)
                historical_prices = self.client.get_historical_prices(
                    symbol, from_date=from_date, to_date=to_date
                )
                result["historical_prices"] = historical_prices

            return result

        except Exception as e:
            logger.error(f"Error getting complete stock data for {symbol}: {e}")
            raise

    async def get_complete_stock_data_async(
        self, symbol: str, include_historical: bool = True, historical_days: int = 365
    ) -> Dict[str, Any]:
        """Get comprehensive stock data for analysis (async version)."""
        try:
            # Basic information
            profile = await self.client.get_company_profile_async(symbol)
            quote = await self.client.get_quote_async(symbol)

            # Financial statements (last 4 years)
            income_annual = await self.client.get_income_statement_async(
                symbol, ReportingPeriod.ANNUAL, 4
            )
            income_quarterly = await self.client.get_income_statement_async(
                symbol, ReportingPeriod.QUARTERLY, 4
            )
            balance_annual = await self.client.get_balance_sheet_async(
                symbol, ReportingPeriod.ANNUAL, 4
            )
            cash_flow_annual = await self.client.get_cash_flow_statement_async(
                symbol, ReportingPeriod.ANNUAL, 4
            )

            # Ratios and metrics
            ratios = await self.client.get_financial_ratios_async(
                symbol, ReportingPeriod.ANNUAL, 4
            )
            key_metrics = await self.client.get_key_metrics_async(
                symbol, ReportingPeriod.ANNUAL, 4
            )

            result = {
                "symbol": symbol,
                "profile": profile,
                "quote": quote,
                "financials": {
                    "income_annual": income_annual,
                    "income_quarterly": income_quarterly,
                    "balance_sheet": balance_annual,
                    "cash_flow": cash_flow_annual,
                },
                "analysis": {
                    "ratios": ratios,
                    "key_metrics": key_metrics,
                },
                "timestamp": datetime.now(),
            }

            # Add historical prices if requested
            if include_historical:
                to_date = date.today()
                from_date = to_date - timedelta(days=historical_days)
                historical_prices = await self.client.get_historical_prices_async(
                    symbol, from_date=from_date, to_date=to_date
                )
                result["historical_prices"] = historical_prices

            return result

        except Exception as e:
            logger.error(f"Error getting complete stock data for {symbol}: {e}")
            raise

    def calculate_financial_health_score(
        self, stock_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate a financial health score based on key metrics.

        Args:
            stock_data: Complete stock data from get_complete_stock_data

        Returns:
            Dictionary with health score and analysis
        """
        try:
            ratios = stock_data["analysis"]["ratios"]
            if not ratios:
                return {"score": None, "analysis": "No financial ratios available"}

            latest_ratios = ratios[0]  # Most recent
            score_components = {}

            # Liquidity (30% weight)
            liquidity_score = 0
            if latest_ratios.current_ratio:
                # Current ratio between 1.5-3 is healthy
                cr = float(latest_ratios.current_ratio)
                if 1.5 <= cr <= 3:
                    liquidity_score = 100
                elif cr > 3:
                    liquidity_score = max(0, 100 - (cr - 3) * 10)
                else:
                    liquidity_score = max(0, cr * 66.67)

            score_components["liquidity"] = {
                "score": liquidity_score,
                "weight": 0.3,
                "current_ratio": (
                    float(latest_ratios.current_ratio)
                    if latest_ratios.current_ratio
                    else None
                ),
            }

            # Profitability (40% weight)
            profitability_score = 0
            if latest_ratios.net_profit_margin:
                npm = float(latest_ratios.net_profit_margin)
                # Positive margin is good, >15% is excellent
                if npm > 0.15:
                    profitability_score = 100
                elif npm > 0:
                    profitability_score = min(100, npm * 667)
                else:
                    profitability_score = 0

            score_components["profitability"] = {
                "score": profitability_score,
                "weight": 0.4,
                "net_profit_margin": (
                    float(latest_ratios.net_profit_margin)
                    if latest_ratios.net_profit_margin
                    else None
                ),
            }

            # Leverage (30% weight)
            leverage_score = 0
            if latest_ratios.debt_ratio:
                dr = float(latest_ratios.debt_ratio)
                # Lower debt ratio is better, <0.3 is excellent
                if dr < 0.3:
                    leverage_score = 100
                elif dr < 0.6:
                    leverage_score = 100 - (dr - 0.3) * 233.33
                else:
                    leverage_score = max(0, 30 - (dr - 0.6) * 75)

            score_components["leverage"] = {
                "score": leverage_score,
                "weight": 0.3,
                "debt_ratio": (
                    float(latest_ratios.debt_ratio)
                    if latest_ratios.debt_ratio
                    else None
                ),
            }

            # Calculate weighted average
            total_score = sum(
                comp["score"] * comp["weight"]
                for comp in score_components.values()
                if comp["score"] is not None
            )

            # Determine rating
            if total_score >= 80:
                rating = "Excellent"
            elif total_score >= 65:
                rating = "Good"
            elif total_score >= 50:
                rating = "Fair"
            elif total_score >= 35:
                rating = "Poor"
            else:
                rating = "Very Poor"

            return {
                "score": round(total_score, 2),
                "rating": rating,
                "components": score_components,
                "analysis_date": datetime.now().isoformat(),
                "symbol": stock_data["symbol"],
            }

        except Exception as e:
            logger.error(f"Error calculating financial health score: {e}")
            return {"score": None, "error": str(e)}


class PortfolioTracker:
    """Portfolio tracking and analysis utility."""

    def __init__(self, client: FinancialModelingPrepClient):
        self.client = client
        self.analyzer = StockAnalyzer(client)

    def get_portfolio_summary(self, holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get portfolio summary with current values and performance.

        Args:
            holdings: List of holdings with format:
                [{"symbol": "AAPL", "shares": 100, "cost_basis": 150.00}, ...]

        Returns:
            Portfolio summary with current values and performance
        """
        try:
            symbols = [holding["symbol"] for holding in holdings]
            quotes = self.client.get_quotes(symbols)
            quote_dict = {quote.symbol: quote for quote in quotes}

            portfolio_value = 0
            total_cost = 0
            total_gain_loss = 0
            holdings_summary = []

            for holding in holdings:
                symbol = holding["symbol"]
                shares = holding["shares"]
                cost_basis = Decimal(str(holding["cost_basis"]))

                if symbol in quote_dict:
                    current_price = quote_dict[symbol].price
                    current_value = current_price * shares
                    total_cost_for_holding = cost_basis * shares
                    gain_loss = current_value - total_cost_for_holding
                    gain_loss_percent = (
                        (gain_loss / total_cost_for_holding) * 100
                        if total_cost_for_holding > 0
                        else 0
                    )

                    holdings_summary.append(
                        {
                            "symbol": symbol,
                            "shares": shares,
                            "cost_basis": float(cost_basis),
                            "current_price": float(current_price),
                            "current_value": float(current_value),
                            "total_cost": float(total_cost_for_holding),
                            "gain_loss": float(gain_loss),
                            "gain_loss_percent": float(gain_loss_percent),
                            "weight": 0,  # Will be calculated after total value
                        }
                    )

                    portfolio_value += current_value
                    total_cost += total_cost_for_holding
                    total_gain_loss += gain_loss

            # Calculate weights
            for holding in holdings_summary:
                holding["weight"] = (
                    (holding["current_value"] / portfolio_value) * 100
                    if portfolio_value > 0
                    else 0
                )

            total_return_percent = (
                (total_gain_loss / total_cost) * 100 if total_cost > 0 else 0
            )

            return {
                "summary": {
                    "total_value": float(portfolio_value),
                    "total_cost": float(total_cost),
                    "total_gain_loss": float(total_gain_loss),
                    "total_return_percent": float(total_return_percent),
                    "number_of_holdings": len(holdings_summary),
                },
                "holdings": holdings_summary,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error getting portfolio summary: {e}")
            raise

    async def get_portfolio_summary_async(
        self, holdings: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Get portfolio summary with current values and performance (async)."""
        try:
            symbols = [holding["symbol"] for holding in holdings]
            quotes = await self.client.get_quotes_async(symbols)
            quote_dict = {quote.symbol: quote for quote in quotes}

            portfolio_value = 0
            total_cost = 0
            total_gain_loss = 0
            holdings_summary = []

            for holding in holdings:
                symbol = holding["symbol"]
                shares = holding["shares"]
                cost_basis = Decimal(str(holding["cost_basis"]))

                if symbol in quote_dict:
                    current_price = quote_dict[symbol].price
                    current_value = current_price * shares
                    total_cost_for_holding = cost_basis * shares
                    gain_loss = current_value - total_cost_for_holding
                    gain_loss_percent = (
                        (gain_loss / total_cost_for_holding) * 100
                        if total_cost_for_holding > 0
                        else 0
                    )

                    holdings_summary.append(
                        {
                            "symbol": symbol,
                            "shares": shares,
                            "cost_basis": float(cost_basis),
                            "current_price": float(current_price),
                            "current_value": float(current_value),
                            "total_cost": float(total_cost_for_holding),
                            "gain_loss": float(gain_loss),
                            "gain_loss_percent": float(gain_loss_percent),
                            "weight": 0,  # Will be calculated after total value
                        }
                    )

                    portfolio_value += current_value
                    total_cost += total_cost_for_holding
                    total_gain_loss += gain_loss

            # Calculate weights
            for holding in holdings_summary:
                holding["weight"] = (
                    (holding["current_value"] / portfolio_value) * 100
                    if portfolio_value > 0
                    else 0
                )

            total_return_percent = (
                (total_gain_loss / total_cost) * 100 if total_cost > 0 else 0
            )

            return {
                "summary": {
                    "total_value": float(portfolio_value),
                    "total_cost": float(total_cost),
                    "total_gain_loss": float(total_gain_loss),
                    "total_return_percent": float(total_return_percent),
                    "number_of_holdings": len(holdings_summary),
                },
                "holdings": holdings_summary,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error getting portfolio summary: {e}")
            raise


def create_fmp_client(api_key: Optional[str] = None) -> FinancialModelingPrepClient:
    """
    Convenience function to create FMP client with your API key.

    Args:
        api_key: API key (defaults to your key)

    Returns:
        Configured FMP client
    """
    if api_key is None:
        api_key = "yBFEbklPDJFEinTIlyeMmC2vxo6GZh6o"  # Your provided key

    return FinancialModelingPrepClient(
        api_key=api_key,
        timeout=30,
        max_retries=3,
        enable_caching=True,
        cache_ttl=300,  # 5 minutes
        rate_limit_requests=250,  # Conservative rate limiting
        rate_limit_period=60,
    )


def batch_symbol_lookup(
    symbols: List[str], client: Optional[FinancialModelingPrepClient] = None
) -> Dict[str, Union[StockQuote, str]]:
    """
    Look up multiple symbols and return quotes or error messages.

    Args:
        symbols: List of stock symbols
        client: FMP client (creates one if None)

    Returns:
        Dictionary mapping symbols to quotes or error messages
    """
    if client is None:
        client = create_fmp_client()

    results = {}

    try:
        # Try to get all quotes at once
        quotes = client.get_quotes(symbols)
        for quote in quotes:
            results[quote.symbol] = quote

        # Mark missing symbols
        returned_symbols = {quote.symbol for quote in quotes}
        for symbol in symbols:
            if symbol not in returned_symbols:
                results[symbol] = f"Symbol {symbol} not found"

    except Exception as e:
        # Fall back to individual lookups
        logger.warning(f"Batch lookup failed, falling back to individual: {e}")
        for symbol in symbols:
            try:
                quote = client.get_quote(symbol)
                results[symbol] = quote
            except Exception as individual_error:
                results[symbol] = str(individual_error)

    return results


async def batch_symbol_lookup_async(
    symbols: List[str], client: Optional[FinancialModelingPrepClient] = None
) -> Dict[str, Union[StockQuote, str]]:
    """
    Look up multiple symbols and return quotes or error messages (async).

    Args:
        symbols: List of stock symbols
        client: FMP client (creates one if None)

    Returns:
        Dictionary mapping symbols to quotes or error messages
    """
    if client is None:
        client = create_fmp_client()

    results = {}

    try:
        # Try to get all quotes at once
        quotes = await client.get_quotes_async(symbols)
        for quote in quotes:
            results[quote.symbol] = quote

        # Mark missing symbols
        returned_symbols = {quote.symbol for quote in quotes}
        for symbol in symbols:
            if symbol not in returned_symbols:
                results[symbol] = f"Symbol {symbol} not found"

    except Exception as e:
        # Fall back to individual lookups
        logger.warning(f"Batch lookup failed, falling back to individual: {e}")
        for symbol in symbols:
            try:
                quote = await client.get_quote_async(symbol)
                results[symbol] = quote
            except Exception as individual_error:
                results[symbol] = str(individual_error)

    return results
