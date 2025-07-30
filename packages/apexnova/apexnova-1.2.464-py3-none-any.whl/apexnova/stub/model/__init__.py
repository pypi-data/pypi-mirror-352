"""Model interfaces."""

from .base_model import IBaseModel
from .base_element import IBaseElement
from .base_vertex import BaseVertex
from .base_edge import BaseEdge

__all__ = [
    "IBaseModel",
    "IBaseElement",
    "BaseVertex",
    "BaseEdge",
]
