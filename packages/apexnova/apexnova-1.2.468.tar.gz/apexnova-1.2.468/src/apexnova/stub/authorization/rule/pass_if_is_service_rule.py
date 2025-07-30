"""Pass if service authorization rule."""

from typing import TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from apexnova.stub.authorization_context_pb2 import AuthorizationContext

from apexnova.stub.authorization.authorization_rule import AuthorizationRule
from apexnova.stub.authorization.authorization_status import AuthorizationStatus

T = TypeVar("T")


class PassIfIsServiceRule(AuthorizationRule[T]):
    """Authorization rule that passes if actor is a service."""

    def evaluate(
        self, context: "AuthorizationContext", entity: T
    ) -> AuthorizationStatus:
        """Returns PASS if actor is service, NEXT otherwise."""
        # Import at runtime to avoid circular dependencies
        from apexnova.stub.authorization_context_pb2 import Actor

        # Compare the actor value directly (protobuf enum value)
        if context.actor == Actor.ACTOR_SERVICE:
            return AuthorizationStatus.PASS
        else:
            return AuthorizationStatus.NEXT
