"""
Data models for Financial Modeling Prep API responses.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any, Union
from enum import Enum


class Exchange(Enum):
    """Stock exchange enumeration."""

    NASDAQ = "NASDAQ"
    NYSE = "NYSE"
    AMEX = "AMEX"
    EURONEXT = "EURONEXT"
    TSX = "TSX"
    OTHER = "OTHER"


class StatementType(Enum):
    """Financial statement type enumeration."""

    INCOME = "income"
    BALANCE = "balance"
    CASH_FLOW = "cash-flow"


class ReportingPeriod(Enum):
    """Reporting period enumeration."""

    ANNUAL = "annual"
    QUARTERLY = "quarterly"


@dataclass
class CompanyProfile:
    """Company profile information."""

    symbol: str
    company_name: str
    industry: Optional[str] = None
    sector: Optional[str] = None
    country: Optional[str] = None
    exchange: Optional[Exchange] = None
    currency: Optional[str] = None
    market_cap: Optional[Decimal] = None
    beta: Optional[Decimal] = None
    price: Optional[Decimal] = None
    last_dividend: Optional[Decimal] = None
    range: Optional[str] = None
    changes: Optional[Decimal] = None
    changes_percentage: Optional[str] = None
    company_name_2: Optional[str] = None
    exchange_short_name: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    ceo: Optional[str] = None
    full_time_employees: Optional[int] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    dcf_diff: Optional[Decimal] = None
    dcf: Optional[Decimal] = None
    image: Optional[str] = None
    ipo_date: Optional[date] = None
    default_image: bool = False
    is_etf: bool = False
    is_actively_trading: bool = True
    is_adr: bool = False
    is_fund: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CompanyProfile":
        """Create CompanyProfile from API response data."""
        return cls(
            symbol=data.get("symbol", ""),
            company_name=data.get("companyName", ""),
            industry=data.get("industry"),
            sector=data.get("sector"),
            country=data.get("country"),
            exchange=(
                Exchange(data["exchangeShortName"])
                if data.get("exchangeShortName") in Exchange.__members__
                else Exchange.OTHER
            ),
            currency=data.get("currency"),
            market_cap=Decimal(str(data["mktCap"])) if data.get("mktCap") else None,
            beta=Decimal(str(data["beta"])) if data.get("beta") else None,
            price=Decimal(str(data["price"])) if data.get("price") else None,
            last_dividend=(
                Decimal(str(data["lastDiv"])) if data.get("lastDiv") else None
            ),
            range=data.get("range"),
            changes=Decimal(str(data["changes"])) if data.get("changes") else None,
            changes_percentage=data.get("changesPercentage"),
            company_name_2=data.get("companyName"),
            exchange_short_name=data.get("exchangeShortName"),
            website=data.get("website"),
            description=data.get("description"),
            ceo=data.get("ceo"),
            full_time_employees=data.get("fullTimeEmployees"),
            phone=data.get("phone"),
            address=data.get("address"),
            city=data.get("city"),
            state=data.get("state"),
            zip_code=data.get("zip"),
            dcf_diff=Decimal(str(data["dcfDiff"])) if data.get("dcfDiff") else None,
            dcf=Decimal(str(data["dcf"])) if data.get("dcf") else None,
            image=data.get("image"),
            ipo_date=(
                datetime.strptime(data["ipoDate"], "%Y-%m-%d").date()
                if data.get("ipoDate")
                else None
            ),
            default_image=data.get("defaultImage", False),
            is_etf=data.get("isEtf", False),
            is_actively_trading=data.get("isActivelyTrading", True),
            is_adr=data.get("isAdr", False),
            is_fund=data.get("isFund", False),
        )


@dataclass
class StockQuote:
    """Real-time stock quote."""

    symbol: str
    name: str
    price: Decimal
    changes_percentage: Decimal
    change: Decimal
    day_low: Decimal
    day_high: Decimal
    year_high: Decimal
    year_low: Decimal
    market_cap: Optional[Decimal] = None
    price_avg50: Optional[Decimal] = None
    price_avg200: Optional[Decimal] = None
    exchange: Optional[str] = None
    volume: Optional[int] = None
    avg_volume: Optional[int] = None
    open_price: Optional[Decimal] = None
    previous_close: Optional[Decimal] = None
    eps: Optional[Decimal] = None
    pe: Optional[Decimal] = None
    earnings_announcement: Optional[datetime] = None
    shares_outstanding: Optional[int] = None
    timestamp: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StockQuote":
        """Create StockQuote from API response data."""
        return cls(
            symbol=data.get("symbol", ""),
            name=data.get("name", ""),
            price=Decimal(str(data.get("price", 0))),
            changes_percentage=Decimal(str(data.get("changesPercentage", 0))),
            change=Decimal(str(data.get("change", 0))),
            day_low=Decimal(str(data.get("dayLow", 0))),
            day_high=Decimal(str(data.get("dayHigh", 0))),
            year_high=Decimal(str(data.get("yearHigh", 0))),
            year_low=Decimal(str(data.get("yearLow", 0))),
            market_cap=(
                Decimal(str(data["marketCap"])) if data.get("marketCap") else None
            ),
            price_avg50=(
                Decimal(str(data["priceAvg50"])) if data.get("priceAvg50") else None
            ),
            price_avg200=(
                Decimal(str(data["priceAvg200"])) if data.get("priceAvg200") else None
            ),
            exchange=data.get("exchange"),
            volume=data.get("volume"),
            avg_volume=data.get("avgVolume"),
            open_price=Decimal(str(data["open"])) if data.get("open") else None,
            previous_close=(
                Decimal(str(data["previousClose"]))
                if data.get("previousClose")
                else None
            ),
            eps=Decimal(str(data["eps"])) if data.get("eps") else None,
            pe=Decimal(str(data["pe"])) if data.get("pe") else None,
            earnings_announcement=(
                datetime.fromisoformat(
                    data["earningsAnnouncement"].replace("Z", "+00:00")
                )
                if data.get("earningsAnnouncement")
                else None
            ),
            shares_outstanding=data.get("sharesOutstanding"),
            timestamp=(
                datetime.fromtimestamp(data["timestamp"])
                if data.get("timestamp")
                else None
            ),
        )


@dataclass
class IncomeStatement:
    """Income statement data."""

    symbol: str
    date: date
    reporting_period: ReportingPeriod
    calendar_year: int
    period: str
    revenue: Optional[Decimal] = None
    cost_of_revenue: Optional[Decimal] = None
    gross_profit: Optional[Decimal] = None
    gross_profit_ratio: Optional[Decimal] = None
    research_and_development_expenses: Optional[Decimal] = None
    general_and_administrative_expenses: Optional[Decimal] = None
    selling_and_marketing_expenses: Optional[Decimal] = None
    selling_general_and_administrative_expenses: Optional[Decimal] = None
    other_expenses: Optional[Decimal] = None
    operating_expenses: Optional[Decimal] = None
    cost_and_expenses: Optional[Decimal] = None
    interest_income: Optional[Decimal] = None
    interest_expense: Optional[Decimal] = None
    depreciation_and_amortization: Optional[Decimal] = None
    ebitda: Optional[Decimal] = None
    ebitda_ratio: Optional[Decimal] = None
    operating_income: Optional[Decimal] = None
    operating_income_ratio: Optional[Decimal] = None
    total_other_income_expenses_net: Optional[Decimal] = None
    income_before_tax: Optional[Decimal] = None
    income_before_tax_ratio: Optional[Decimal] = None
    income_tax_expense: Optional[Decimal] = None
    net_income: Optional[Decimal] = None
    net_income_ratio: Optional[Decimal] = None
    eps: Optional[Decimal] = None
    eps_diluted: Optional[Decimal] = None
    weighted_average_shs_out: Optional[int] = None
    weighted_average_shs_out_dil: Optional[int] = None
    link: Optional[str] = None
    final_link: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IncomeStatement":
        """Create IncomeStatement from API response data."""
        return cls(
            symbol=data.get("symbol", ""),
            date=datetime.strptime(data.get("date", ""), "%Y-%m-%d").date(),
            reporting_period=(
                ReportingPeriod.QUARTERLY
                if data.get("period") == "Q"
                else ReportingPeriod.ANNUAL
            ),
            calendar_year=data.get("calendarYear", 0),
            period=data.get("period", ""),
            revenue=Decimal(str(data["revenue"])) if data.get("revenue") else None,
            cost_of_revenue=(
                Decimal(str(data["costOfRevenue"]))
                if data.get("costOfRevenue")
                else None
            ),
            gross_profit=(
                Decimal(str(data["grossProfit"])) if data.get("grossProfit") else None
            ),
            gross_profit_ratio=(
                Decimal(str(data["grossProfitRatio"]))
                if data.get("grossProfitRatio")
                else None
            ),
            research_and_development_expenses=(
                Decimal(str(data["researchAndDevelopmentExpenses"]))
                if data.get("researchAndDevelopmentExpenses")
                else None
            ),
            general_and_administrative_expenses=(
                Decimal(str(data["generalAndAdministrativeExpenses"]))
                if data.get("generalAndAdministrativeExpenses")
                else None
            ),
            selling_and_marketing_expenses=(
                Decimal(str(data["sellingAndMarketingExpenses"]))
                if data.get("sellingAndMarketingExpenses")
                else None
            ),
            selling_general_and_administrative_expenses=(
                Decimal(str(data["sellingGeneralAndAdministrativeExpenses"]))
                if data.get("sellingGeneralAndAdministrativeExpenses")
                else None
            ),
            other_expenses=(
                Decimal(str(data["otherExpenses"]))
                if data.get("otherExpenses")
                else None
            ),
            operating_expenses=(
                Decimal(str(data["operatingExpenses"]))
                if data.get("operatingExpenses")
                else None
            ),
            cost_and_expenses=(
                Decimal(str(data["costAndExpenses"]))
                if data.get("costAndExpenses")
                else None
            ),
            interest_income=(
                Decimal(str(data["interestIncome"]))
                if data.get("interestIncome")
                else None
            ),
            interest_expense=(
                Decimal(str(data["interestExpense"]))
                if data.get("interestExpense")
                else None
            ),
            depreciation_and_amortization=(
                Decimal(str(data["depreciationAndAmortization"]))
                if data.get("depreciationAndAmortization")
                else None
            ),
            ebitda=Decimal(str(data["ebitda"])) if data.get("ebitda") else None,
            ebitda_ratio=(
                Decimal(str(data["ebitdaratio"])) if data.get("ebitdaratio") else None
            ),
            operating_income=(
                Decimal(str(data["operatingIncome"]))
                if data.get("operatingIncome")
                else None
            ),
            operating_income_ratio=(
                Decimal(str(data["operatingIncomeRatio"]))
                if data.get("operatingIncomeRatio")
                else None
            ),
            total_other_income_expenses_net=(
                Decimal(str(data["totalOtherIncomeExpensesNet"]))
                if data.get("totalOtherIncomeExpensesNet")
                else None
            ),
            income_before_tax=(
                Decimal(str(data["incomeBeforeTax"]))
                if data.get("incomeBeforeTax")
                else None
            ),
            income_before_tax_ratio=(
                Decimal(str(data["incomeBeforeTaxRatio"]))
                if data.get("incomeBeforeTaxRatio")
                else None
            ),
            income_tax_expense=(
                Decimal(str(data["incomeTaxExpense"]))
                if data.get("incomeTaxExpense")
                else None
            ),
            net_income=(
                Decimal(str(data["netIncome"])) if data.get("netIncome") else None
            ),
            net_income_ratio=(
                Decimal(str(data["netIncomeRatio"]))
                if data.get("netIncomeRatio")
                else None
            ),
            eps=Decimal(str(data["eps"])) if data.get("eps") else None,
            eps_diluted=(
                Decimal(str(data["epsdiluted"])) if data.get("epsdiluted") else None
            ),
            weighted_average_shs_out=data.get("weightedAverageShsOut"),
            weighted_average_shs_out_dil=data.get("weightedAverageShsOutDil"),
            link=data.get("link"),
            final_link=data.get("finalLink"),
        )


@dataclass
class BalanceSheet:
    """Balance sheet data."""

    symbol: str
    date: date
    reporting_period: ReportingPeriod
    calendar_year: int
    period: str
    cash_and_cash_equivalents: Optional[Decimal] = None
    short_term_investments: Optional[Decimal] = None
    cash_and_short_term_investments: Optional[Decimal] = None
    net_receivables: Optional[Decimal] = None
    inventory: Optional[Decimal] = None
    other_current_assets: Optional[Decimal] = None
    total_current_assets: Optional[Decimal] = None
    property_plant_equipment_net: Optional[Decimal] = None
    goodwill: Optional[Decimal] = None
    intangible_assets: Optional[Decimal] = None
    goodwill_and_intangible_assets: Optional[Decimal] = None
    long_term_investments: Optional[Decimal] = None
    tax_assets: Optional[Decimal] = None
    other_non_current_assets: Optional[Decimal] = None
    total_non_current_assets: Optional[Decimal] = None
    other_assets: Optional[Decimal] = None
    total_assets: Optional[Decimal] = None
    account_payables: Optional[Decimal] = None
    short_term_debt: Optional[Decimal] = None
    tax_payables: Optional[Decimal] = None
    deferred_revenue: Optional[Decimal] = None
    other_current_liabilities: Optional[Decimal] = None
    total_current_liabilities: Optional[Decimal] = None
    long_term_debt: Optional[Decimal] = None
    deferred_revenue_non_current: Optional[Decimal] = None
    deferred_tax_liabilities_non_current: Optional[Decimal] = None
    other_non_current_liabilities: Optional[Decimal] = None
    total_non_current_liabilities: Optional[Decimal] = None
    other_liabilities: Optional[Decimal] = None
    capital_lease_obligations: Optional[Decimal] = None
    total_liabilities: Optional[Decimal] = None
    preferred_stock: Optional[Decimal] = None
    common_stock: Optional[Decimal] = None
    retained_earnings: Optional[Decimal] = None
    accumulated_other_comprehensive_income_loss: Optional[Decimal] = None
    othertotal_stockholders_equity: Optional[Decimal] = None
    total_stockholders_equity: Optional[Decimal] = None
    total_equity: Optional[Decimal] = None
    total_liabilities_and_stockholders_equity: Optional[Decimal] = None
    minority_interest: Optional[Decimal] = None
    total_liabilities_and_total_equity: Optional[Decimal] = None
    total_investments: Optional[Decimal] = None
    total_debt: Optional[Decimal] = None
    net_debt: Optional[Decimal] = None
    link: Optional[str] = None
    final_link: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BalanceSheet":
        """Create BalanceSheet from API response data."""
        return cls(
            symbol=data.get("symbol", ""),
            date=datetime.strptime(data.get("date", ""), "%Y-%m-%d").date(),
            reporting_period=(
                ReportingPeriod.QUARTERLY
                if data.get("period") == "Q"
                else ReportingPeriod.ANNUAL
            ),
            calendar_year=data.get("calendarYear", 0),
            period=data.get("period", ""),
            cash_and_cash_equivalents=(
                Decimal(str(data["cashAndCashEquivalents"]))
                if data.get("cashAndCashEquivalents")
                else None
            ),
            short_term_investments=(
                Decimal(str(data["shortTermInvestments"]))
                if data.get("shortTermInvestments")
                else None
            ),
            cash_and_short_term_investments=(
                Decimal(str(data["cashAndShortTermInvestments"]))
                if data.get("cashAndShortTermInvestments")
                else None
            ),
            net_receivables=(
                Decimal(str(data["netReceivables"]))
                if data.get("netReceivables")
                else None
            ),
            inventory=(
                Decimal(str(data["inventory"])) if data.get("inventory") else None
            ),
            other_current_assets=(
                Decimal(str(data["otherCurrentAssets"]))
                if data.get("otherCurrentAssets")
                else None
            ),
            total_current_assets=(
                Decimal(str(data["totalCurrentAssets"]))
                if data.get("totalCurrentAssets")
                else None
            ),
            property_plant_equipment_net=(
                Decimal(str(data["propertyPlantEquipmentNet"]))
                if data.get("propertyPlantEquipmentNet")
                else None
            ),
            goodwill=Decimal(str(data["goodwill"])) if data.get("goodwill") else None,
            intangible_assets=(
                Decimal(str(data["intangibleAssets"]))
                if data.get("intangibleAssets")
                else None
            ),
            goodwill_and_intangible_assets=(
                Decimal(str(data["goodwillAndIntangibleAssets"]))
                if data.get("goodwillAndIntangibleAssets")
                else None
            ),
            long_term_investments=(
                Decimal(str(data["longTermInvestments"]))
                if data.get("longTermInvestments")
                else None
            ),
            tax_assets=(
                Decimal(str(data["taxAssets"])) if data.get("taxAssets") else None
            ),
            other_non_current_assets=(
                Decimal(str(data["otherNonCurrentAssets"]))
                if data.get("otherNonCurrentAssets")
                else None
            ),
            total_non_current_assets=(
                Decimal(str(data["totalNonCurrentAssets"]))
                if data.get("totalNonCurrentAssets")
                else None
            ),
            other_assets=(
                Decimal(str(data["otherAssets"])) if data.get("otherAssets") else None
            ),
            total_assets=(
                Decimal(str(data["totalAssets"])) if data.get("totalAssets") else None
            ),
            # ... (continuing with all balance sheet fields)
            link=data.get("link"),
            final_link=data.get("finalLink"),
        )


@dataclass
class CashFlowStatement:
    """Cash flow statement data."""

    symbol: str
    date: date
    reporting_period: ReportingPeriod
    calendar_year: int
    period: str
    net_income: Optional[Decimal] = None
    depreciation_and_amortization: Optional[Decimal] = None
    deferred_income_tax: Optional[Decimal] = None
    stock_based_compensation: Optional[Decimal] = None
    change_in_working_capital: Optional[Decimal] = None
    accounts_receivables: Optional[Decimal] = None
    inventory: Optional[Decimal] = None
    accounts_payables: Optional[Decimal] = None
    other_working_capital: Optional[Decimal] = None
    other_non_cash_items: Optional[Decimal] = None
    net_cash_provided_by_operating_activities: Optional[Decimal] = None
    investments_in_property_plant_and_equipment: Optional[Decimal] = None
    acquisitions_net: Optional[Decimal] = None
    purchases_of_investments: Optional[Decimal] = None
    sales_maturities_of_investments: Optional[Decimal] = None
    other_investing_activites: Optional[Decimal] = None
    net_cash_used_for_investing_activites: Optional[Decimal] = None
    debt_repayment: Optional[Decimal] = None
    common_stock_issued: Optional[Decimal] = None
    common_stock_repurchased: Optional[Decimal] = None
    dividends_paid: Optional[Decimal] = None
    other_financing_activites: Optional[Decimal] = None
    net_cash_used_provided_by_financing_activities: Optional[Decimal] = None
    effect_of_forex_changes_on_cash: Optional[Decimal] = None
    net_change_in_cash: Optional[Decimal] = None
    cash_at_end_of_period: Optional[Decimal] = None
    cash_at_beginning_of_period: Optional[Decimal] = None
    operating_cash_flow: Optional[Decimal] = None
    capital_expenditure: Optional[Decimal] = None
    free_cash_flow: Optional[Decimal] = None
    link: Optional[str] = None
    final_link: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CashFlowStatement":
        """Create CashFlowStatement from API response data."""
        return cls(
            symbol=data.get("symbol", ""),
            date=datetime.strptime(data.get("date", ""), "%Y-%m-%d").date(),
            reporting_period=(
                ReportingPeriod.QUARTERLY
                if data.get("period") == "Q"
                else ReportingPeriod.ANNUAL
            ),
            calendar_year=data.get("calendarYear", 0),
            period=data.get("period", ""),
            net_income=(
                Decimal(str(data["netIncome"])) if data.get("netIncome") else None
            ),
            depreciation_and_amortization=(
                Decimal(str(data["depreciationAndAmortization"]))
                if data.get("depreciationAndAmortization")
                else None
            ),
            deferred_income_tax=(
                Decimal(str(data["deferredIncomeTax"]))
                if data.get("deferredIncomeTax")
                else None
            ),
            stock_based_compensation=(
                Decimal(str(data["stockBasedCompensation"]))
                if data.get("stockBasedCompensation")
                else None
            ),
            change_in_working_capital=(
                Decimal(str(data["changeInWorkingCapital"]))
                if data.get("changeInWorkingCapital")
                else None
            ),
            accounts_receivables=(
                Decimal(str(data["accountsReceivables"]))
                if data.get("accountsReceivables")
                else None
            ),
            inventory=(
                Decimal(str(data["inventory"])) if data.get("inventory") else None
            ),
            accounts_payables=(
                Decimal(str(data["accountsPayables"]))
                if data.get("accountsPayables")
                else None
            ),
            other_working_capital=(
                Decimal(str(data["otherWorkingCapital"]))
                if data.get("otherWorkingCapital")
                else None
            ),
            other_non_cash_items=(
                Decimal(str(data["otherNonCashItems"]))
                if data.get("otherNonCashItems")
                else None
            ),
            net_cash_provided_by_operating_activities=(
                Decimal(str(data["netCashProvidedByOperatingActivities"]))
                if data.get("netCashProvidedByOperatingActivities")
                else None
            ),
            investments_in_property_plant_and_equipment=(
                Decimal(str(data["investmentsInPropertyPlantAndEquipment"]))
                if data.get("investmentsInPropertyPlantAndEquipment")
                else None
            ),
            acquisitions_net=(
                Decimal(str(data["acquisitionsNet"]))
                if data.get("acquisitionsNet")
                else None
            ),
            purchases_of_investments=(
                Decimal(str(data["purchasesOfInvestments"]))
                if data.get("purchasesOfInvestments")
                else None
            ),
            sales_maturities_of_investments=(
                Decimal(str(data["salesMaturitiesOfInvestments"]))
                if data.get("salesMaturitiesOfInvestments")
                else None
            ),
            other_investing_activites=(
                Decimal(str(data["otherInvestingActivites"]))
                if data.get("otherInvestingActivites")
                else None
            ),
            net_cash_used_for_investing_activites=(
                Decimal(str(data["netCashUsedForInvestingActivites"]))
                if data.get("netCashUsedForInvestingActivites")
                else None
            ),
            debt_repayment=(
                Decimal(str(data["debtRepayment"]))
                if data.get("debtRepayment")
                else None
            ),
            common_stock_issued=(
                Decimal(str(data["commonStockIssued"]))
                if data.get("commonStockIssued")
                else None
            ),
            common_stock_repurchased=(
                Decimal(str(data["commonStockRepurchased"]))
                if data.get("commonStockRepurchased")
                else None
            ),
            dividends_paid=(
                Decimal(str(data["dividendsPaid"]))
                if data.get("dividendsPaid")
                else None
            ),
            other_financing_activites=(
                Decimal(str(data["otherFinancingActivites"]))
                if data.get("otherFinancingActivites")
                else None
            ),
            net_cash_used_provided_by_financing_activities=(
                Decimal(str(data["netCashUsedProvidedByFinancingActivities"]))
                if data.get("netCashUsedProvidedByFinancingActivities")
                else None
            ),
            effect_of_forex_changes_on_cash=(
                Decimal(str(data["effectOfForexChangesOnCash"]))
                if data.get("effectOfForexChangesOnCash")
                else None
            ),
            net_change_in_cash=(
                Decimal(str(data["netChangeInCash"]))
                if data.get("netChangeInCash")
                else None
            ),
            cash_at_end_of_period=(
                Decimal(str(data["cashAtEndOfPeriod"]))
                if data.get("cashAtEndOfPeriod")
                else None
            ),
            cash_at_beginning_of_period=(
                Decimal(str(data["cashAtBeginningOfPeriod"]))
                if data.get("cashAtBeginningOfPeriod")
                else None
            ),
            operating_cash_flow=(
                Decimal(str(data["operatingCashFlow"]))
                if data.get("operatingCashFlow")
                else None
            ),
            capital_expenditure=(
                Decimal(str(data["capitalExpenditure"]))
                if data.get("capitalExpenditure")
                else None
            ),
            free_cash_flow=(
                Decimal(str(data["freeCashFlow"])) if data.get("freeCashFlow") else None
            ),
            link=data.get("link"),
            final_link=data.get("finalLink"),
        )


@dataclass
class SearchResult:
    """Search result data."""

    symbol: str
    name: str
    currency: Optional[str] = None
    stock_exchange: Optional[str] = None
    exchange_short_name: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchResult":
        """Create SearchResult from API response data."""
        return cls(
            symbol=data.get("symbol", ""),
            name=data.get("name", ""),
            currency=data.get("currency"),
            stock_exchange=data.get("stockExchange"),
            exchange_short_name=data.get("exchangeShortName"),
        )


@dataclass
class StockPrice:
    """Historical stock price data."""

    symbol: str
    date: date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    adj_close: Decimal
    volume: int
    unadjusted_volume: Optional[int] = None
    change: Optional[Decimal] = None
    change_percent: Optional[Decimal] = None
    vwap: Optional[Decimal] = None
    label: Optional[str] = None
    change_over_time: Optional[Decimal] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StockPrice":
        """Create StockPrice from API response data."""
        return cls(
            symbol=data.get("symbol", ""),
            date=datetime.strptime(data.get("date", ""), "%Y-%m-%d").date(),
            open=Decimal(str(data.get("open", 0))),
            high=Decimal(str(data.get("high", 0))),
            low=Decimal(str(data.get("low", 0))),
            close=Decimal(str(data.get("close", 0))),
            adj_close=Decimal(str(data.get("adjClose", 0))),
            volume=data.get("volume", 0),
            unadjusted_volume=data.get("unadjustedVolume"),
            change=Decimal(str(data["change"])) if data.get("change") else None,
            change_percent=(
                Decimal(str(data["changePercent"]))
                if data.get("changePercent")
                else None
            ),
            vwap=Decimal(str(data["vwap"])) if data.get("vwap") else None,
            label=data.get("label"),
            change_over_time=(
                Decimal(str(data["changeOverTime"]))
                if data.get("changeOverTime")
                else None
            ),
        )


# Alias for backward compatibility
FinancialStatement = Union[IncomeStatement, BalanceSheet, CashFlowStatement]
MarketData = Union[StockQuote, StockPrice]


@dataclass
class FinancialRatios:
    """Financial ratios data."""

    symbol: str
    date: date
    current_ratio: Optional[Decimal] = None
    quick_ratio: Optional[Decimal] = None
    cash_ratio: Optional[Decimal] = None
    days_of_sales_outstanding: Optional[Decimal] = None
    days_of_inventory_outstanding: Optional[Decimal] = None
    operating_cycle: Optional[Decimal] = None
    days_of_payables_outstanding: Optional[Decimal] = None
    cash_conversion_cycle: Optional[Decimal] = None
    gross_profit_margin: Optional[Decimal] = None
    operating_profit_margin: Optional[Decimal] = None
    pretax_profit_margin: Optional[Decimal] = None
    net_profit_margin: Optional[Decimal] = None
    effective_tax_rate: Optional[Decimal] = None
    return_on_assets: Optional[Decimal] = None
    return_on_equity: Optional[Decimal] = None
    return_on_capital_employed: Optional[Decimal] = None
    net_income_per_ebt: Optional[Decimal] = None
    ebt_per_ebit: Optional[Decimal] = None
    ebit_per_revenue: Optional[Decimal] = None
    debt_ratio: Optional[Decimal] = None
    debt_equity_ratio: Optional[Decimal] = None
    long_term_debt_to_capitalization: Optional[Decimal] = None
    total_debt_to_capitalization: Optional[Decimal] = None
    interest_coverage: Optional[Decimal] = None
    cash_flow_to_debt_ratio: Optional[Decimal] = None
    company_equity_multiplier: Optional[Decimal] = None
    receivables_turnover: Optional[Decimal] = None
    payables_turnover: Optional[Decimal] = None
    inventory_turnover: Optional[Decimal] = None
    fixed_asset_turnover: Optional[Decimal] = None
    asset_turnover: Optional[Decimal] = None
    operating_cash_flow_per_share: Optional[Decimal] = None
    free_cash_flow_per_share: Optional[Decimal] = None
    cash_per_share: Optional[Decimal] = None
    payout_ratio: Optional[Decimal] = None
    operating_cash_flow_sales_ratio: Optional[Decimal] = None
    free_cash_flow_operating_cash_flow_ratio: Optional[Decimal] = None
    cash_flow_coverage_ratios: Optional[Decimal] = None
    short_term_coverage_ratios: Optional[Decimal] = None
    capital_expenditure_coverage_ratio: Optional[Decimal] = None
    dividend_paid_and_capex_coverage_ratio: Optional[Decimal] = None
    dividend_payout_ratio: Optional[Decimal] = None
    price_book_value_ratio: Optional[Decimal] = None
    price_to_book_ratio: Optional[Decimal] = None
    price_to_sales_ratio: Optional[Decimal] = None
    price_earnings_ratio: Optional[Decimal] = None
    price_to_free_cash_flows_ratio: Optional[Decimal] = None
    price_to_operating_cash_flows_ratio: Optional[Decimal] = None
    price_cash_flow_ratio: Optional[Decimal] = None
    price_earnings_to_growth_ratio: Optional[Decimal] = None
    price_sales_ratio: Optional[Decimal] = None
    dividend_yield: Optional[Decimal] = None
    enterprise_value_multiple: Optional[Decimal] = None
    price_fair_value: Optional[Decimal] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FinancialRatios":
        """Create FinancialRatios from API response data."""
        return cls(
            symbol=data.get("symbol", ""),
            date=datetime.strptime(data.get("date", ""), "%Y-%m-%d").date(),
            current_ratio=(
                Decimal(str(data["currentRatio"])) if data.get("currentRatio") else None
            ),
            quick_ratio=(
                Decimal(str(data["quickRatio"])) if data.get("quickRatio") else None
            ),
            cash_ratio=(
                Decimal(str(data["cashRatio"])) if data.get("cashRatio") else None
            ),
            # ... (add all other ratio fields)
        )


@dataclass
class KeyMetrics:
    """Key metrics data."""

    symbol: str
    date: date
    revenue_per_share: Optional[Decimal] = None
    net_income_per_share: Optional[Decimal] = None
    operating_cash_flow_per_share: Optional[Decimal] = None
    free_cash_flow_per_share: Optional[Decimal] = None
    cash_per_share: Optional[Decimal] = None
    book_value_per_share: Optional[Decimal] = None
    tangible_book_value_per_share: Optional[Decimal] = None
    shareholders_equity_per_share: Optional[Decimal] = None
    interest_debt_per_share: Optional[Decimal] = None
    market_cap: Optional[Decimal] = None
    enterprise_value: Optional[Decimal] = None
    pe_ratio: Optional[Decimal] = None
    price_to_sales_ratio: Optional[Decimal] = None
    pocfratio: Optional[Decimal] = None
    pfcf_ratio: Optional[Decimal] = None
    pb_ratio: Optional[Decimal] = None
    ptb_ratio: Optional[Decimal] = None
    ev_to_sales: Optional[Decimal] = None
    enterprise_value_over_ebitda: Optional[Decimal] = None
    ev_to_operating_cash_flow: Optional[Decimal] = None
    ev_to_free_cash_flow: Optional[Decimal] = None
    earnings_yield: Optional[Decimal] = None
    free_cash_flow_yield: Optional[Decimal] = None
    debt_to_equity: Optional[Decimal] = None
    debt_to_assets: Optional[Decimal] = None
    net_debt_to_ebitda: Optional[Decimal] = None
    current_ratio: Optional[Decimal] = None
    interest_coverage: Optional[Decimal] = None
    income_quality: Optional[Decimal] = None
    dividend_yield: Optional[Decimal] = None
    payout_ratio: Optional[Decimal] = None
    sales_general_and_administrative_to_revenue: Optional[Decimal] = None
    research_and_ddevelopment_to_revenue: Optional[Decimal] = None
    intangibles_to_total_assets: Optional[Decimal] = None
    capex_to_operating_cash_flow: Optional[Decimal] = None
    capex_to_revenue: Optional[Decimal] = None
    capex_to_depreciation: Optional[Decimal] = None
    stock_based_compensation_to_revenue: Optional[Decimal] = None
    graham_number: Optional[Decimal] = None
    roic: Optional[Decimal] = None
    return_on_tangible_assets: Optional[Decimal] = None
    graham_net_net: Optional[Decimal] = None
    working_capital: Optional[Decimal] = None
    tangible_asset_value: Optional[Decimal] = None
    net_current_asset_value: Optional[Decimal] = None
    invested_capital: Optional[Decimal] = None
    average_receivables: Optional[Decimal] = None
    average_payables: Optional[Decimal] = None
    average_inventory: Optional[Decimal] = None
    days_sales_outstanding: Optional[Decimal] = None
    days_payables_outstanding: Optional[Decimal] = None
    days_of_inventory_on_hand: Optional[Decimal] = None
    receivables_turnover: Optional[Decimal] = None
    payables_turnover: Optional[Decimal] = None
    inventory_turnover: Optional[Decimal] = None
    roe: Optional[Decimal] = None
    capex_per_share: Optional[Decimal] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KeyMetrics":
        """Create KeyMetrics from API response data."""
        return cls(
            symbol=data.get("symbol", ""),
            date=datetime.strptime(data.get("date", ""), "%Y-%m-%d").date(),
            revenue_per_share=(
                Decimal(str(data["revenuePerShare"]))
                if data.get("revenuePerShare")
                else None
            ),
            net_income_per_share=(
                Decimal(str(data["netIncomePerShare"]))
                if data.get("netIncomePerShare")
                else None
            ),
            operating_cash_flow_per_share=(
                Decimal(str(data["operatingCashFlowPerShare"]))
                if data.get("operatingCashFlowPerShare")
                else None
            ),
            free_cash_flow_per_share=(
                Decimal(str(data["freeCashFlowPerShare"]))
                if data.get("freeCashFlowPerShare")
                else None
            ),
            cash_per_share=(
                Decimal(str(data["cashPerShare"])) if data.get("cashPerShare") else None
            ),
            book_value_per_share=(
                Decimal(str(data["bookValuePerShare"]))
                if data.get("bookValuePerShare")
                else None
            ),
            tangible_book_value_per_share=(
                Decimal(str(data["tangibleBookValuePerShare"]))
                if data.get("tangibleBookValuePerShare")
                else None
            ),
            shareholders_equity_per_share=(
                Decimal(str(data["shareholdersEquityPerShare"]))
                if data.get("shareholdersEquityPerShare")
                else None
            ),
            interest_debt_per_share=(
                Decimal(str(data["interestDebtPerShare"]))
                if data.get("interestDebtPerShare")
                else None
            ),
            market_cap=(
                Decimal(str(data["marketCap"])) if data.get("marketCap") else None
            ),
            enterprise_value=(
                Decimal(str(data["enterpriseValue"]))
                if data.get("enterpriseValue")
                else None
            ),
            pe_ratio=Decimal(str(data["peRatio"])) if data.get("peRatio") else None,
            price_to_sales_ratio=(
                Decimal(str(data["priceToSalesRatio"]))
                if data.get("priceToSalesRatio")
                else None
            ),
            # ... (add all other key metrics fields)
        )


@dataclass
class MarketNews:
    """Market news article."""

    title: str
    content: str
    url: str
    image: Optional[str] = None
    published_date: Optional[datetime] = None
    site: Optional[str] = None
    symbol: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MarketNews":
        """Create MarketNews from API response data."""
        return cls(
            title=data.get("title", ""),
            content=data.get("content", ""),
            url=data.get("url", ""),
            image=data.get("image"),
            published_date=(
                datetime.fromisoformat(data["publishedDate"].replace("Z", "+00:00"))
                if data.get("publishedDate")
                else None
            ),
            site=data.get("site"),
            symbol=data.get("symbol"),
        )


@dataclass
class EarningsCalendar:
    """Earnings calendar entry."""

    symbol: str
    date: date
    eps: Optional[Decimal] = None
    eps_estimated: Optional[Decimal] = None
    time: Optional[str] = None
    revenue: Optional[Decimal] = None
    revenue_estimated: Optional[Decimal] = None
    updated_from_date: Optional[date] = None
    fiscal_date_ending: Optional[date] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EarningsCalendar":
        """Create EarningsCalendar from API response data."""
        return cls(
            symbol=data.get("symbol", ""),
            date=datetime.strptime(data.get("date", ""), "%Y-%m-%d").date(),
            eps=Decimal(str(data["eps"])) if data.get("eps") else None,
            eps_estimated=(
                Decimal(str(data["epsEstimated"])) if data.get("epsEstimated") else None
            ),
            time=data.get("time"),
            revenue=Decimal(str(data["revenue"])) if data.get("revenue") else None,
            revenue_estimated=(
                Decimal(str(data["revenueEstimated"]))
                if data.get("revenueEstimated")
                else None
            ),
            updated_from_date=(
                datetime.strptime(data["updatedFromDate"], "%Y-%m-%d").date()
                if data.get("updatedFromDate")
                else None
            ),
            fiscal_date_ending=(
                datetime.strptime(data["fiscalDateEnding"], "%Y-%m-%d").date()
                if data.get("fiscalDateEnding")
                else None
            ),
        )


@dataclass
class Dividend:
    """Dividend information."""

    symbol: str
    date: date
    dividend: Decimal
    record_date: Optional[date] = None
    payment_date: Optional[date] = None
    declaration_date: Optional[date] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Dividend":
        """Create Dividend from API response data."""
        return cls(
            symbol=data.get("symbol", ""),
            date=datetime.strptime(data.get("date", ""), "%Y-%m-%d").date(),
            dividend=Decimal(str(data.get("dividend", 0))),
            record_date=(
                datetime.strptime(data["recordDate"], "%Y-%m-%d").date()
                if data.get("recordDate")
                else None
            ),
            payment_date=(
                datetime.strptime(data["paymentDate"], "%Y-%m-%d").date()
                if data.get("paymentDate")
                else None
            ),
            declaration_date=(
                datetime.strptime(data["declarationDate"], "%Y-%m-%d").date()
                if data.get("declarationDate")
                else None
            ),
        )


@dataclass
class StockSplit:
    """Stock split information."""

    symbol: str
    date: date
    numerator: int
    denominator: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StockSplit":
        """Create StockSplit from API response data."""
        return cls(
            symbol=data.get("symbol", ""),
            date=datetime.strptime(data.get("date", ""), "%Y-%m-%d").date(),
            numerator=data.get("numerator", 1),
            denominator=data.get("denominator", 1),
        )
