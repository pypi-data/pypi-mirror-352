"""Base model interface."""

from datetime import datetime
from typing import Protocol


class IBaseModel(Protocol):
    """Base model interface."""

    id: str
    address: str
    created_at: datetime
    updated_at: datetime
    label: str
    phone: str
