"""Pass if vertex owner authorization rule."""

from __future__ import annotations
from typing import TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from apexnova.stub.authorization_context_pb2 import AuthorizationContext

from apexnova.stub.authorization.authorization_rule import AuthorizationRule
from apexnova.stub.authorization.authorization_status import AuthorizationStatus
from apexnova.stub.model.base_element import IBaseElement

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
