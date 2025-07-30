"""
Financial Modeling Prep API exceptions.
"""

from typing import Optional, Dict, Any


class FMPError(Exception):
    """Base exception for Financial Modeling Prep API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        endpoint: Optional[str] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        self.endpoint = endpoint

    def __str__(self) -> str:
        parts = [self.message]
        if self.status_code:
            parts.append(f"Status: {self.status_code}")
        if self.endpoint:
            parts.append(f"Endpoint: {self.endpoint}")
        return " | ".join(parts)


class FMPAuthenticationError(FMPError):
    """Raised when API key is invalid or missing."""

    def __init__(self, message: str = "Invalid or missing API key"):
        super().__init__(message, status_code=401)


class FMPRateLimitError(FMPError):
    """Raised when API rate limit is exceeded."""

    def __init__(
        self,
        message: str = "API rate limit exceeded",
        retry_after: Optional[int] = None,
    ):
        super().__init__(message, status_code=429)
        self.retry_after = retry_after


class FMPNotFoundError(FMPError):
    """Raised when requested resource is not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class FMPValidationError(FMPError):
    """Raised when request parameters are invalid."""

    def __init__(self, message: str = "Invalid request parameters"):
        super().__init__(message, status_code=400)


class FMPServerError(FMPError):
    """Raised when server returns 5xx error."""

    def __init__(self, message: str = "Internal server error", status_code: int = 500):
        super().__init__(message, status_code=status_code)


class FMPTimeoutError(FMPError):
    """Raised when request times out."""

    def __init__(self, message: str = "Request timeout"):
        super().__init__(message)
