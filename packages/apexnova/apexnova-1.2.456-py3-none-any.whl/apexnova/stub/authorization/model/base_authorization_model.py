"""Base authorization model."""

from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic, TYPE_CHECKING

if TYPE_CHECKING:
    from apexnova.stub.authorization_context_pb2 import AuthorizationContext

from apexnova.stub.authorization.authorization_rule import AuthorizationRule
from apexnova.stub.authorization.authorization_status import AuthorizationStatus

T = TypeVar("T")


class BaseAuthorizationModel(ABC, Generic[T]):
    """Base class for authorization models."""

    @abstractmethod
    def get_read_rules(self) -> List[AuthorizationRule[T]]:
        """Get rules for read operations."""
        pass

    @abstractmethod
    def get_create_rules(self) -> List[AuthorizationRule[T]]:
        """Get rules for create operations."""
        pass

    @abstractmethod
    def get_update_rules(self) -> List[AuthorizationRule[T]]:
        """Get rules for update operations."""
        pass

    @abstractmethod
    def get_delete_rules(self) -> List[AuthorizationRule[T]]:
        """Get rules for delete operations."""
        pass

    def _evaluate_rules(
        self,
        rules: List[AuthorizationRule[T]],
        context: "AuthorizationContext",
        entity: T,
    ) -> AuthorizationStatus:
        """Evaluate a list of authorization rules."""
        for rule in rules:
            result = rule.evaluate(context, entity)
            if result != AuthorizationStatus.NEXT:
                return result
        return AuthorizationStatus.FAIL

    def can_read(self, context: "AuthorizationContext", entity: T) -> bool:
        """Check if READ operation is allowed."""
        return (
            self._evaluate_rules(self.get_read_rules(), context, entity)
            == AuthorizationStatus.PASS
        )

    def can_create(self, context: "AuthorizationContext", entity: T) -> bool:
        """Check if CREATE operation is allowed."""
        return (
            self._evaluate_rules(self.get_create_rules(), context, entity)
            == AuthorizationStatus.PASS
        )

    def can_update(self, context: "AuthorizationContext", entity: T) -> bool:
        """Check if UPDATE operation is allowed."""
        return (
            self._evaluate_rules(self.get_update_rules(), context, entity)
            == AuthorizationStatus.PASS
        )

    def can_delete(self, context: "AuthorizationContext", entity: T) -> bool:
        """Check if DELETE operation is allowed."""
        return (
            self._evaluate_rules(self.get_delete_rules(), context, entity)
            == AuthorizationStatus.PASS
        )
