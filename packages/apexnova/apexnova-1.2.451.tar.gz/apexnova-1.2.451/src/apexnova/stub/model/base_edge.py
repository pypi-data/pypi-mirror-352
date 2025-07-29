"""
Base edge model for graph databases.
"""

from abc import abstractmethod
from datetime import datetime

from .base_element import IBaseElement


class BaseEdge(IBaseElement):
    """
    Abstract base class for edge models in graph databases.

    Edges represent relationships between vertices in a graph database.
    """

    @property
    def type(self) -> str:
        """Get element type (always 'edge' for edges)."""
        return "edge"

    @property
    @abstractmethod
    def id(self) -> str:
        """Get edge ID."""
        pass

    @property
    @abstractmethod
    def label(self) -> str:
        """Get edge label."""
        pass

    @property
    @abstractmethod
    def created_at(self) -> datetime:
        """Get creation timestamp."""
        pass

    @property
    @abstractmethod
    def updated_at(self) -> datetime:
        """Get last update timestamp."""
        pass

    @property
    @abstractmethod
    def in_v_label(self) -> str:
        """Get incoming vertex label."""
        pass

    @property
    @abstractmethod
    def out_v_label(self) -> str:
        """Get outgoing vertex label."""
        pass

    @property
    @abstractmethod
    def in_v(self) -> str:
        """Get incoming vertex ID."""
        pass

    @property
    @abstractmethod
    def out_v(self) -> str:
        """Get outgoing vertex ID."""
        pass
