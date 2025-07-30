"""Base Gremlin authorization repository."""

from abc import ABC
from typing import List, TypeVar, Generic, Dict, Any, Optional, TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from apexnova.stub.authorization_context_pb2 import AuthorizationContext

from apexnova.stub.model.base_element import IBaseElement

# Type variables
T = TypeVar("T", bound=IBaseElement)
ID = TypeVar("ID")


class AuthorizationModel(Protocol):
    """Protocol for authorization models."""

    def can_create(self, context: "AuthorizationContext", entity: Any) -> bool:
        """Check if entity can be created."""
        ...

    def can_read(self, context: "AuthorizationContext", entity: Any) -> bool:
        """Check if entity can be read."""
        ...

    def can_update(self, context: "AuthorizationContext", entity: Any) -> bool:
        """Check if entity can be updated."""
        ...

    def can_delete(self, context: "AuthorizationContext", entity: Any) -> bool:
        """Check if entity can be deleted."""
        ...


AM = TypeVar("AM", bound=AuthorizationModel)


class BaseGremlinAuthorizationRepository(ABC, Generic[AM, T, ID]):
    """Base repository with authorization for Gremlin graph operations."""

    def __init__(
        self,
        authorization_model: AM,
        gremlin_endpoint: Optional[str] = None,
        element_type: Optional[type] = None,
    ):
        """
        Initialize the Gremlin repository.

        Args:
            authorization_model: Authorization model for permission checks
            gremlin_endpoint: Gremlin server endpoint
            element_type: Class type for the elements
        """
        self.authorization_model = authorization_model
        self.element_type = element_type
        self.enabled = False
        self.connection: Optional[Any] = None
        self.g: Optional[Any] = None

        # Try to initialize Gremlin connection
        if gremlin_endpoint:
            self._initialize_gremlin_connection(gremlin_endpoint)

    def _initialize_gremlin_connection(self, endpoint: str) -> None:
        """Initialize Gremlin connection if available."""
        try:
            # Import gremlinpython at runtime to make it optional
            from gremlinpython.driver.driver_remote_connection import DriverRemoteConnection  # type: ignore
            from gremlinpython.process.anonymous_traversal import traversal  # type: ignore

            self.connection = DriverRemoteConnection(endpoint, "g")
            self.g = traversal().withRemote(self.connection)  # type: ignore
            self.enabled = True
        except ImportError:
            # Gremlin not available
            self.enabled = False
        except Exception:
            # Connection failed
            self.enabled = False

    def create(self, authorization_context: "AuthorizationContext", element: T) -> T:
        """Create a new element in the graph."""
        if not self.authorization_model.can_create(authorization_context, element):
            raise PermissionError(
                "Permission Denied: You do not have permission to create this entity."
            )

        if not self.enabled or self.g is None:
            raise RuntimeError("Gremlin connection not available")

        try:
            # Create vertex with properties
            query = self.g.addV(getattr(element, "type", "vertex"))
            query = query.property("id", element.id)
            query = query.property("label", getattr(element, "label", ""))

            query.next()
            return element
        except Exception as e:
            raise RuntimeError(f"Failed to create entity: {e}")

    def read_by_id(self, authorization_context: "AuthorizationContext", id: ID) -> T:
        """Read an element by ID."""
        if not self.enabled or self.g is None:
            raise RuntimeError("Gremlin connection not available")

        try:
            # Find vertex by ID
            vertex = self.g.V().hasId(str(id)).next()
            element = self._vertex_to_element(vertex)

            if not self.authorization_model.can_read(authorization_context, element):
                raise PermissionError(
                    "Permission Denied: You do not have permission to read this entity."
                )

            return element
        except StopIteration:
            raise ValueError("No Such Item Exists")
        except Exception as e:
            raise RuntimeError(f"Failed to read entity: {e}")

    def update(self, authorization_context: "AuthorizationContext", element: T) -> T:
        """Update an existing element."""
        if not self.authorization_model.can_update(authorization_context, element):
            raise PermissionError(
                "Permission Denied: You do not have permission to update this entity."
            )

        if not self.enabled or self.g is None:
            raise RuntimeError("Gremlin connection not available")

        try:
            # Update vertex properties
            query = self.g.V().hasId(element.id)
            query = query.property("label", getattr(element, "label", ""))
            query.next()
            return element
        except Exception as e:
            raise RuntimeError(f"Failed to update entity: {e}")

    def delete(self, authorization_context: "AuthorizationContext", element: T) -> None:
        """Delete an element."""
        if not self.authorization_model.can_delete(authorization_context, element):
            raise PermissionError(
                "Permission Denied: You do not have permission to delete this entity."
            )

        if not self.enabled or self.g is None:
            raise RuntimeError("Gremlin connection not available")

        try:
            self.g.V().hasId(element.id).drop().iterate()
        except Exception as e:
            raise RuntimeError(f"Failed to delete entity: {e}")

    def filter(
        self, authorization_context: "AuthorizationContext", properties: Dict[str, Any]
    ) -> List[T]:
        """Filter elements by properties with authorization."""
        if not self.enabled or self.g is None:
            raise RuntimeError("Gremlin connection not available")

        try:
            query = self.g.V()

            # Add property filters
            for key, value in properties.items():
                query = query.has(key, value)

            vertices = query.toList()
            elements = [self._vertex_to_element(v) for v in vertices]

            # Filter by read permissions
            authorized_elements: List[T] = []
            for element in elements:
                if self.authorization_model.can_read(authorization_context, element):
                    authorized_elements.append(element)

            return authorized_elements
        except Exception as e:
            raise RuntimeError(f"Failed to filter entities: {e}")

    def _vertex_to_element(self, vertex: Any) -> T:
        """Convert a Gremlin vertex to an element object."""
        if not self.element_type:
            raise RuntimeError("Element type not specified")

        # Extract vertex properties
        vertex_id = (
            getattr(vertex, "id", str(vertex)) if hasattr(vertex, "id") else str(vertex)
        )
        label = getattr(vertex, "label", "") if hasattr(vertex, "label") else ""
        vertex_type = getattr(vertex, "type", "") if hasattr(vertex, "type") else ""

        element_data = {
            "id": vertex_id,
            "label": label,
            "type": vertex_type,
        }

        # This would need proper implementation based on your element structure
        return self.element_type(**element_data)  # type: ignore

    def close(self) -> None:
        """Close the Gremlin connection."""
        if self.connection is not None:
            try:
                self.connection.close()
            except Exception:
                pass
