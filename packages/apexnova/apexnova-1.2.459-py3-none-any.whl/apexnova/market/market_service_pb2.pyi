from apexnova.market import market_pb2 as _market_pb2
from apexnova.stub import authorization_context_pb2 as _authorization_context_pb2
from apexnova.stub import response_pb2 as _response_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ReadStockRequest(_message.Message):
    __slots__ = ("symbol", "authorization_context")
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    AUTHORIZATION_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    authorization_context: _authorization_context_pb2.AuthorizationContext
    def __init__(self, symbol: _Optional[str] = ..., authorization_context: _Optional[_Union[_authorization_context_pb2.AuthorizationContext, _Mapping]] = ...) -> None: ...

class ReadStockResponse(_message.Message):
    __slots__ = ("stock", "standard_response")
    STOCK_FIELD_NUMBER: _ClassVar[int]
    STANDARD_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    stock: _market_pb2.Stock
    standard_response: _response_pb2.StandardResponse
    def __init__(self, stock: _Optional[_Union[_market_pb2.Stock, _Mapping]] = ..., standard_response: _Optional[_Union[_response_pb2.StandardResponse, _Mapping]] = ...) -> None: ...

class ReadQuoteRequest(_message.Message):
    __slots__ = ("symbol", "date", "authorization_context")
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    AUTHORIZATION_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    date: str
    authorization_context: _authorization_context_pb2.AuthorizationContext
    def __init__(self, symbol: _Optional[str] = ..., date: _Optional[str] = ..., authorization_context: _Optional[_Union[_authorization_context_pb2.AuthorizationContext, _Mapping]] = ...) -> None: ...

class ReadQuoteResponse(_message.Message):
    __slots__ = ("quote", "standard_response")
    QUOTE_FIELD_NUMBER: _ClassVar[int]
    STANDARD_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    quote: _market_pb2.QuoteInfo
    standard_response: _response_pb2.StandardResponse
    def __init__(self, quote: _Optional[_Union[_market_pb2.QuoteInfo, _Mapping]] = ..., standard_response: _Optional[_Union[_response_pb2.StandardResponse, _Mapping]] = ...) -> None: ...

class StreamStatementsRequest(_message.Message):
    __slots__ = ("symbol", "fiscal_year", "period", "cursor", "limit", "authorization_context")
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    FISCAL_YEAR_FIELD_NUMBER: _ClassVar[int]
    PERIOD_FIELD_NUMBER: _ClassVar[int]
    CURSOR_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    AUTHORIZATION_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    fiscal_year: int
    period: str
    cursor: str
    limit: int
    authorization_context: _authorization_context_pb2.AuthorizationContext
    def __init__(self, symbol: _Optional[str] = ..., fiscal_year: _Optional[int] = ..., period: _Optional[str] = ..., cursor: _Optional[str] = ..., limit: _Optional[int] = ..., authorization_context: _Optional[_Union[_authorization_context_pb2.AuthorizationContext, _Mapping]] = ...) -> None: ...

class BalanceSheetStatementResponse(_message.Message):
    __slots__ = ("statement", "standard_response")
    STATEMENT_FIELD_NUMBER: _ClassVar[int]
    STANDARD_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    statement: _market_pb2.BalanceSheetStatement
    standard_response: _response_pb2.StandardResponse
    def __init__(self, statement: _Optional[_Union[_market_pb2.BalanceSheetStatement, _Mapping]] = ..., standard_response: _Optional[_Union[_response_pb2.StandardResponse, _Mapping]] = ...) -> None: ...

class CashflowStatementResponse(_message.Message):
    __slots__ = ("statement", "standard_response")
    STATEMENT_FIELD_NUMBER: _ClassVar[int]
    STANDARD_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    statement: _market_pb2.CashflowStatement
    standard_response: _response_pb2.StandardResponse
    def __init__(self, statement: _Optional[_Union[_market_pb2.CashflowStatement, _Mapping]] = ..., standard_response: _Optional[_Union[_response_pb2.StandardResponse, _Mapping]] = ...) -> None: ...

class IncomeStatementResponse(_message.Message):
    __slots__ = ("statement", "standard_response")
    STATEMENT_FIELD_NUMBER: _ClassVar[int]
    STANDARD_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    statement: _market_pb2.IncomeStatement
    standard_response: _response_pb2.StandardResponse
    def __init__(self, statement: _Optional[_Union[_market_pb2.IncomeStatement, _Mapping]] = ..., standard_response: _Optional[_Union[_response_pb2.StandardResponse, _Mapping]] = ...) -> None: ...

class FreeCashFlowGrowthScreenerResponse(_message.Message):
    __slots__ = ("stock", "standard_response")
    STOCK_FIELD_NUMBER: _ClassVar[int]
    STANDARD_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    stock: _market_pb2.Stock
    standard_response: _response_pb2.StandardResponse
    def __init__(self, stock: _Optional[_Union[_market_pb2.Stock, _Mapping]] = ..., standard_response: _Optional[_Union[_response_pb2.StandardResponse, _Mapping]] = ...) -> None: ...

class FreeCashFlowGrowthScreenerRequest(_message.Message):
    __slots__ = ("market_cap_more_than", "market_cap_lower_than", "exchange", "country", "authorization_context")
    MARKET_CAP_MORE_THAN_FIELD_NUMBER: _ClassVar[int]
    MARKET_CAP_LOWER_THAN_FIELD_NUMBER: _ClassVar[int]
    EXCHANGE_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    AUTHORIZATION_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    market_cap_more_than: float
    market_cap_lower_than: float
    exchange: _market_pb2.StockExchange
    country: _market_pb2.Country
    authorization_context: _authorization_context_pb2.AuthorizationContext
    def __init__(self, market_cap_more_than: _Optional[float] = ..., market_cap_lower_than: _Optional[float] = ..., exchange: _Optional[_Union[_market_pb2.StockExchange, str]] = ..., country: _Optional[_Union[_market_pb2.Country, str]] = ..., authorization_context: _Optional[_Union[_authorization_context_pb2.AuthorizationContext, _Mapping]] = ...) -> None: ...
