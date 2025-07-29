"""Fail if not logged in authorization rule."""

from typing import TypeVar

from apexnova.authorization_context_pb2 import AuthorizationContext
from ..authorization_rule import AuthorizationRule
from ..authorization_status import AuthorizationStatus

T = TypeVar("T")


class FailIfNotLoggedInRule(AuthorizationRule[T]):
    """Authorization rule that fails if user is not logged in."""

    def evaluate(self, context: AuthorizationContext, entity: T) -> AuthorizationStatus:
        """Returns PASS if account_id is present, FAIL otherwise."""
        if context.account_id:
            return AuthorizationStatus.PASS
        else:
            return AuthorizationStatus.FAIL
