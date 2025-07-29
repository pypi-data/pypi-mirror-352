"""Base element interface."""

from datetime import datetime
from typing import Protocol


class IBaseElement(Protocol):
    """Base element interface."""

    id: str
    label: str
    type: str
    created_at: datetime
    updated_at: datetime
