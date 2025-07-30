"""Authorization rule interface."""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, TYPE_CHECKING

if TYPE_CHECKING:
    from apexnova.stub.authorization_context_pb2 import AuthorizationContext

from apexnova.stub.authorization.authorization_status import AuthorizationStatus

T = TypeVar("T")


class AuthorizationRule(ABC, Generic[T]):
    """I nterface for authorization rules."""

    @abstractmethod
    def evaluate(
        self, context: "AuthorizationContext", entity: T
    ) -> AuthorizationStatus:
        """
        Evaluate the authorization rule for a given context and entity.

        Args:
            context: The authorization context
            entity: The entity to evaluate

        Returns:
            AuthorizationStatus indicating the result
        """
        pass
