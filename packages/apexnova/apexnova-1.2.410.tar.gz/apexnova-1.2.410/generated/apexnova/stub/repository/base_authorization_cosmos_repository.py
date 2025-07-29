"""Base authorization Cosmos repository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, TypeVar, Generic, Iterable

from apexnova.stub.model.base_model import IBaseModel

T = TypeVar("T", bound=IBaseModel)
AM = TypeVar("AM")  # Authorization model type variable without bound
ID = TypeVar("ID")


class BaseAuthorizationCosmosRepository(ABC, Generic[AM, T, ID]):
    """Base repository interface with authorization for Cosmos DB operations."""

    @abstractmethod
    def save(self, entity: T) -> T:
        """Save an entity."""
        pass

    @abstractmethod
    def find_by_id(self, id: ID) -> Optional[T]:
        """Find entity by ID."""
        pass

    @abstractmethod
    def find_all(self) -> Iterable[T]:
        """Find all entities."""
        pass

    @abstractmethod
    def delete(self, entity: T) -> None:
        """Delete an entity."""
        pass

    @abstractmethod
    def delete_by_id(self, id: ID) -> None:
        """Delete entity by ID."""
        pass

    @abstractmethod
    def exists_by_id(self, id: ID) -> bool:
        """Check if entity exists by ID."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Count all entities."""
        pass

    @abstractmethod
    def save_all(self, entities: Iterable[T]) -> Iterable[T]:
        """Save multiple entities."""
        pass

    @abstractmethod
    def find_by_id_with_partition_key(self, id: ID, partition_key: str) -> Optional[T]:
        """Find entity by ID with partition key."""
        pass

    @abstractmethod
    def delete_by_id_with_partition_key(self, id: ID, partition_key: str) -> None:
        """Delete entity by ID with partition key."""
        pass

    @abstractmethod
    def find_all_with_partition_key(self, partition_key: str) -> Iterable[T]:
        """Find all entities with partition key."""
        pass

    @abstractmethod
    def filter(self, properties: Dict[str, Any]) -> List[T]:
        """Filter entities by properties."""
        pass
