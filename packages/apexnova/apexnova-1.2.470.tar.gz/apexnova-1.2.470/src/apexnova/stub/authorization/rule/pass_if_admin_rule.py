"""Pass if admin authorization rule."""

from __future__ import annotations
from typing import TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from apexnova.stub.authorization_context_pb2 import AuthorizationContext, Role

from apexnova.stub.authorization.authorization_rule import AuthorizationRule
from apexnova.stub.authorization.authorization_status import AuthorizationStatus

T = TypeVar("T")


class PassIfAdminRule(AuthorizationRule[T]):
    """Authorization rule that passes if user has admin role."""

    def evaluate(self, context: AuthorizationContext, entity: T) -> AuthorizationStatus:
        """Returns PASS if user has admin role, NEXT otherwise."""
        if Role.ROLE_ADMIN in context.roles:
            return AuthorizationStatus.PASS
        else:
            return AuthorizationStatus.NEXT
