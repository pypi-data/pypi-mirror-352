"""Fail if not owner authorization rule."""

from typing import TypeVar, Callable

from apexnova.stub.authorization_context_pb2 import AuthorizationContext
from ..authorization_rule import AuthorizationRule
from ..authorization_status import AuthorizationStatus

T = TypeVar("T")


class FailIfNotOwnerRule(AuthorizationRule[T]):
    """Authorization rule that fails if user is not the owner."""

    def __init__(self, owner_id_extractor: Callable[[T], str]):
        """
        Initialize with owner ID extractor function.

        Args:
            owner_id_extractor: Function to extract owner ID from entity
        """
        self.owner_id_extractor = owner_id_extractor

    def evaluate(self, context: AuthorizationContext, entity: T) -> AuthorizationStatus:
        """Returns NEXT if user is owner, FAIL otherwise."""
        if self.owner_id_extractor(entity) == context.id:
            return AuthorizationStatus.NEXT
        else:
            return AuthorizationStatus.FAIL
