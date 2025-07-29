"""Pass if vertex owner authorization rule."""

from typing import TypeVar

from apexnova.stub.authorization_context_pb2 import AuthorizationContext
from ..authorization_rule import AuthorizationRule
from ..authorization_status import AuthorizationStatus
from ...model.base_element import IBaseElement

T = TypeVar("T")


class PassIfIsVertexOwnerRule(AuthorizationRule[T]):
    """Authorization rule that passes if user is the vertex owner."""

    def evaluate(self, context: AuthorizationContext, entity: T) -> AuthorizationStatus:
        """Returns PASS if entity is IBaseElement and user is owner, NEXT otherwise."""
        if (
            hasattr(entity, "id")
            and hasattr(entity, "label")
            and entity.id == context.id
        ):
            return AuthorizationStatus.PASS
        else:
            return AuthorizationStatus.NEXT
