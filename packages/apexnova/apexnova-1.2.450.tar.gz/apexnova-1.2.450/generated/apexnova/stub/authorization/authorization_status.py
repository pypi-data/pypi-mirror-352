"""Authorization status enumeration."""

from enum import Enum


class AuthorizationStatus(Enum):
    """Enumeration for authorization status results."""

    PASS = "PASS"
    FAIL = "FAIL"
    NEXT = "NEXT"
