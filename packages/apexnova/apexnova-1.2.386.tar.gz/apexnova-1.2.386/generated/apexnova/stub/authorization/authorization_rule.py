"""Authorization rule interface."""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from apexnova.authorization_context_pb2 import AuthorizationContext
from .authorization_status import AuthorizationStatus

T = TypeVar("T")


class AuthorizationRule(ABC, Generic[T]):
    """Interface for authorization rules."""

    @abstractmethod
    def evaluate(self, context: AuthorizationContext, entity: T) -> AuthorizationStatus:
        """
        Evaluate the authorization rule for a given context and entity.

        Args:
            context: The authorization context
            entity: The entity to evaluate

        Returns:
            AuthorizationStatus indicating the result
        """
        pass
