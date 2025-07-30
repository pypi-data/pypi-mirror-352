"""
Base vertex model for graph databases.
"""

from abc import abstractmethod
from datetime import datetime

from .base_element import IBaseElement


class BaseVertex(IBaseElement):
    """
    Abstract base class for vertex models in graph databases.

    Vertices represent entities or nodes in a graph database.
    """

    @property
    def type(self) -> str:
        """Get element type (always 'vertex' for vertices)."""
        return "vertex"

    @property
    @abstractmethod
    def id(self) -> str:
        """Get vertex ID."""
        pass

    @property
    @abstractmethod
    def label(self) -> str:
        """Get vertex label."""
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
    def address(self) -> str:
        """Get vertex address/location."""
        pass
