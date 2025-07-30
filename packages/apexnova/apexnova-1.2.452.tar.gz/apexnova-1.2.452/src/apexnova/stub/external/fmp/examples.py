"""
Usage examples for the Financial Modeling Prep API client.
"""

import asyncio
from datetime import date, timedelta
from typing import List, Dict, Any

from .client import FinancialModelingPrepClient
from .utils import (
    create_fmp_client,
    StockAnalyzer,
    PortfolioTracker,
    batch_symbol_lookup,
    batch_symbol_lookup_async,
)
from .models import ReportingPeriod


def basic_usage_example():
    """Basic usage example."""
    print("=== Basic FMP API Usage ===")

    # Create client with your API key
    client = create_fmp_client()

    # Get company profile
    profile = client.get_company_profile("AAPL")
    print(f"Company: {profile.company_name}")
    print(f"Industry: {profile.industry}")
    print(f"Market Cap: ${profile.market_cap:,.2f}" if profile.market_cap else "N/A")

    # Get current quote
    quote = client.get_quote("AAPL")
    print(f"Current Price: ${quote.price}")
    print(f"Daily Change: {quote.change} ({quote.changes_percentage}%)")

    # Search for symbols
    search_results = client.search_symbols("Apple")
    print(f"Found {len(search_results)} results for 'Apple'")
    for result in search_results[:3]:
        print(f"  {result.symbol}: {result.name}")


def financial_statements_example():
    """Financial statements example."""
    print("\n=== Financial Statements Example ===")

    client = create_fmp_client()
    symbol = "AAPL"

    # Get income statements (last 3 years)
    income_statements = client.get_income_statement(symbol, ReportingPeriod.ANNUAL, 3)
    print(f"Income Statements for {symbol}:")
    for stmt in income_statements:
        revenue_b = float(stmt.revenue) / 1e9 if stmt.revenue else 0
        net_income_b = float(stmt.net_income) / 1e9 if stmt.net_income else 0
        print(
            f"  {stmt.date}: Revenue=${revenue_b:.1f}B, Net Income=${net_income_b:.1f}B"
        )

    # Get balance sheet
    balance_sheets = client.get_balance_sheet(symbol, ReportingPeriod.ANNUAL, 2)
    print(f"\nBalance Sheet for {symbol}:")
    for stmt in balance_sheets:
        total_assets_b = float(stmt.total_assets) / 1e9 if stmt.total_assets else 0
        total_debt_b = float(stmt.total_debt) / 1e9 if stmt.total_debt else 0
        print(
            f"  {stmt.date}: Assets=${total_assets_b:.1f}B, Debt=${total_debt_b:.1f}B"
        )

    # Get financial ratios
    ratios = client.get_financial_ratios(symbol, ReportingPeriod.ANNUAL, 2)
    print(f"\nFinancial Ratios for {symbol}:")
    for ratio in ratios:
        pe = float(ratio.price_earnings_ratio) if ratio.price_earnings_ratio else None
        roe = float(ratio.return_on_equity) if ratio.return_on_equity else None
        print(
            f"  {ratio.date}: P/E={pe:.2f}"
            if pe
            else "N/A" + f", ROE={roe:.2%}" if roe else "N/A"
        )


def historical_data_example():
    """Historical data example."""
    print("\n=== Historical Data Example ===")

    client = create_fmp_client()
    symbol = "AAPL"

    # Get last 30 days of price data
    to_date = date.today()
    from_date = to_date - timedelta(days=30)

    prices = client.get_historical_prices(symbol, from_date=from_date, to_date=to_date)
    print(f"Historical prices for {symbol} (last 30 days):")
    for price in prices[:5]:  # Show first 5
        print(
            f"  {price.date}: Open=${price.open}, Close=${price.close}, Volume={price.volume:,}"
        )

    # Calculate some basic statistics
    if prices:
        close_prices = [float(p.close) for p in prices]
        avg_price = sum(close_prices) / len(close_prices)
        max_price = max(close_prices)
        min_price = min(close_prices)

        print(f"\nPrice Statistics:")
        print(f"  Average: ${avg_price:.2f}")
        print(f"  High: ${max_price:.2f}")
        print(f"  Low: ${min_price:.2f}")
        print(f"  Volatility: {(max_price - min_price) / avg_price:.2%}")


def portfolio_tracking_example():
    """Portfolio tracking example."""
    print("\n=== Portfolio Tracking Example ===")

    client = create_fmp_client()
    tracker = PortfolioTracker(client)

    # Example portfolio holdings
    holdings = [
        {"symbol": "AAPL", "shares": 100, "cost_basis": 150.00},
        {"symbol": "GOOGL", "shares": 50, "cost_basis": 2500.00},
        {"symbol": "MSFT", "shares": 75, "cost_basis": 300.00},
        {"symbol": "TSLA", "shares": 25, "cost_basis": 800.00},
    ]

    portfolio_summary = tracker.get_portfolio_summary(holdings)

    print("Portfolio Summary:")
    summary = portfolio_summary["summary"]
    print(f"  Total Value: ${summary['total_value']:,.2f}")
    print(f"  Total Cost: ${summary['total_cost']:,.2f}")
    print(f"  Total Gain/Loss: ${summary['total_gain_loss']:,.2f}")
    print(f"  Total Return: {summary['total_return_percent']:.2f}%")

    print("\nHoldings:")
    for holding in portfolio_summary["holdings"]:
        print(
            f"  {holding['symbol']}: {holding['shares']} shares @ ${holding['current_price']:.2f}"
        )
        print(
            f"    Value: ${holding['current_value']:,.2f} ({holding['weight']:.1f}% of portfolio)"
        )
        print(
            f"    Gain/Loss: ${holding['gain_loss']:,.2f} ({holding['gain_loss_percent']:+.2f}%)"
        )


def stock_analysis_example():
    """Stock analysis example."""
    print("\n=== Stock Analysis Example ===")

    client = create_fmp_client()
    analyzer = StockAnalyzer(client)

    symbol = "AAPL"

    # Get complete stock data
    stock_data = analyzer.get_complete_stock_data(
        symbol, include_historical=True, historical_days=90
    )

    print(f"Complete Analysis for {symbol}:")
    print(f"  Company: {stock_data['profile'].company_name}")
    print(f"  Sector: {stock_data['profile'].sector}")
    print(f"  Current Price: ${stock_data['quote'].price}")
    print(
        f"  Market Cap: ${float(stock_data['profile'].market_cap) / 1e9:.1f}B"
        if stock_data["profile"].market_cap
        else "N/A"
    )

    # Calculate financial health score
    health_score = analyzer.calculate_financial_health_score(stock_data)
    if health_score.get("score"):
        print(
            f"\nFinancial Health Score: {health_score['score']}/100 ({health_score['rating']})"
        )
        print("  Components:")
        for component, data in health_score["components"].items():
            if data["score"] is not None:
                print(
                    f"    {component.title()}: {data['score']:.1f}/100 (weight: {data['weight']:.0%})"
                )

    # Show recent price performance
    if stock_data.get("historical_prices"):
        prices = stock_data["historical_prices"]
        if len(prices) >= 2:
            recent_price = float(prices[0].close)
            old_price = float(prices[-1].close)
            performance = (recent_price - old_price) / old_price * 100
            print(f"\n90-Day Performance: {performance:+.2f}%")


def batch_operations_example():
    """Batch operations example."""
    print("\n=== Batch Operations Example ===")

    client = create_fmp_client()

    # Batch symbol lookup
    symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "INVALID_SYMBOL"]
    results = batch_symbol_lookup(symbols, client)

    print("Batch Symbol Lookup Results:")
    for symbol, result in results.items():
        if hasattr(result, "price"):  # It's a StockQuote
            print(f"  {symbol}: ${result.price} ({result.changes_percentage}%)")
        else:  # It's an error message
            print(f"  {symbol}: {result}")


async def async_operations_example():
    """Async operations example."""
    print("\n=== Async Operations Example ===")

    client = create_fmp_client()

    try:
        # Multiple async calls
        symbols = ["AAPL", "GOOGL", "MSFT"]

        print("Making concurrent async requests...")
        tasks = [client.get_company_profile_async(symbol) for symbol in symbols]

        profiles = await asyncio.gather(*tasks)

        print("Results:")
        for profile in profiles:
            print(f"  {profile.symbol}: {profile.company_name} - {profile.sector}")

        # Async batch lookup
        print("\nAsync batch lookup:")
        batch_results = await batch_symbol_lookup_async(symbols, client)
        for symbol, result in batch_results.items():
            if hasattr(result, "price"):
                print(f"  {symbol}: ${result.price}")
            else:
                print(f"  {symbol}: {result}")

    finally:
        await client.close()


def market_news_example():
    """Market news example."""
    print("\n=== Market News Example ===")

    client = create_fmp_client()

    # Get general market news
    market_news = client.get_market_news(limit=5)
    print("Recent Market News:")
    for article in market_news:
        print(f"  - {article.title}")
        print(f"    Published: {article.published_date}")
        print(f"    URL: {article.url}")
        print()

    # Get stock-specific news
    stock_news = client.get_stock_news("AAPL", limit=3)
    print("AAPL Recent News:")
    for article in stock_news:
        print(f"  - {article.title}")
        print(f"    Published: {article.published_date}")
        print()


def earnings_calendar_example():
    """Earnings calendar example."""
    print("\n=== Earnings Calendar Example ===")

    client = create_fmp_client()

    # Get this week's earnings
    today = date.today()
    week_end = today + timedelta(days=7)

    earnings = client.get_earnings_calendar(from_date=today, to_date=week_end)
    print(f"Earnings Calendar ({today} to {week_end}):")

    for earning in earnings[:10]:  # Show first 10
        eps_text = f"EPS: ${earning.eps}" if earning.eps else "EPS: N/A"
        eps_est_text = (
            f" (Est: ${earning.eps_estimated})" if earning.eps_estimated else ""
        )
        print(f"  {earning.date}: {earning.symbol} - {eps_text}{eps_est_text}")


def main():
    """Run all examples."""
    print("Financial Modeling Prep API Client Examples")
    print("=" * 50)

    try:
        basic_usage_example()
        financial_statements_example()
        historical_data_example()
        portfolio_tracking_example()
        stock_analysis_example()
        batch_operations_example()
        market_news_example()
        earnings_calendar_example()

        # Run async example
        print("\nRunning async example...")
        asyncio.run(async_operations_example())

        print("\n" + "=" * 50)
        print("All examples completed successfully!")

    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
