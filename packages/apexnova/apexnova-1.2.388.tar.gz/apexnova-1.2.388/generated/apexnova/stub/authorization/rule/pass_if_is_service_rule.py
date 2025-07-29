"""Pass if service authorization rule."""

from typing import TypeVar

from apexnova.stub.authorization_context_pb2 import AuthorizationContext, Actor
from ..authorization_rule import AuthorizationRule
from ..authorization_status import AuthorizationStatus

T = TypeVar("T")


class PassIfIsServiceRule(AuthorizationRule[T]):
    """Authorization rule that passes if actor is a service."""

    def evaluate(self, context: AuthorizationContext, entity: T) -> AuthorizationStatus:
        """Returns PASS if actor is service, NEXT otherwise."""
        if context.actor.name == Actor.ACTOR_SERVICE.name:
            return AuthorizationStatus.PASS
        else:
            return AuthorizationStatus.NEXT
