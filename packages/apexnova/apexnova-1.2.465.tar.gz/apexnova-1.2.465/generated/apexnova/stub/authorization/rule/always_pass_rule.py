"""Always pass authorization rule."""

from typing import TypeVar

from apexnova.stub.authorization_context_pb2 import AuthorizationContext
from apexnova.stub.authorization.authorization_rule import AuthorizationRule
from apexnova.stub.authorization.authorization_status import AuthorizationStatus

T = TypeVar("T")


class AlwaysPassRule(AuthorizationRule[T]):
    """Authorization rule that always passes."""

    def evaluate(self, context: AuthorizationContext, entity: T) -> AuthorizationStatus:
        """Always returns PASS status."""
        return AuthorizationStatus.PASS
