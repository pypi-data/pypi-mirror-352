"""Pass if admin authorization rule."""

from typing import TypeVar

from apexnova.authorization_context_pb2 import AuthorizationContext
from apexnova.stub.role_pb2 import Role
from ..authorization_rule import AuthorizationRule
from ..authorization_status import AuthorizationStatus

T = TypeVar("T")


class PassIfAdminRule(AuthorizationRule[T]):
    """Authorization rule that passes if user has admin role."""

    def evaluate(self, context: AuthorizationContext, entity: T) -> AuthorizationStatus:
        """Returns PASS if user has admin role, NEXT otherwise."""
        if Role.ROLE_ADMIN in context.roles:
            return AuthorizationStatus.PASS
        else:
            return AuthorizationStatus.NEXT
