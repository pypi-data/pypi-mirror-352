"""Base Gremlin authorization repository."""

from abc import ABC
from typing import List, TypeVar, Generic, Dict, Any, Optional, TYPE_CHECKING

try:
    from gremlinpython.driver import client
    from gremlinpython.driver.driver_remote_connection import DriverRemoteConnection
    from gremlinpython.process.anonymous_traversal import traversal
    from gremlinpython.process.graph_traversal import __

    GREMLIN_AVAILABLE = True
except ImportError:
    GREMLIN_AVAILABLE = False

    # Mock classes for when Gremlin is not available
    class MockClient:
        def submit(self, query):
            return []


if TYPE_CHECKING:
    from apexnova.stub.authorization_context_pb2 import AuthorizationContext
from ..authorization.model.base_authorization_model import BaseAuthorizationModel
from ..model.base_element import IBaseElement

T = TypeVar("T", bound=IBaseElement)
AM = TypeVar("AM", bound=BaseAuthorizationModel)
ID = TypeVar("ID")


class BaseGremlinAuthorizationRepository(ABC, Generic[AM, T, ID]):
    """Base repository with authorization for Gremlin graph operations."""

    def __init__(
        self,
        authorization_model: AM,
        gremlin_endpoint: Optional[str] = None,
        element_type: type = None,
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

        if GREMLIN_AVAILABLE and gremlin_endpoint:
            try:
                self.connection = DriverRemoteConnection(gremlin_endpoint, "g")
                self.g = traversal().withRemote(self.connection)
                self.enabled = True
            except Exception:
                self.g = None
                self.enabled = False
        else:
            self.g = None
            self.enabled = False

    def create(self, authorization_context: "AuthorizationContext", element: T) -> T:
        """Create a new element in the graph."""
        if not self.authorization_model.can_create(authorization_context, element):
            raise PermissionError(
                "Permission Denied: You do not have permission to create this entity."
            )

        if not self.enabled:
            raise RuntimeError("Gremlin connection not available")

        # Create vertex with properties
        query = self.g.addV(element.type)
        query = query.property("id", element.id)
        query = query.property("label", element.label)

        try:
            result = query.next()
            return element  # Return the original element for now
        except Exception as e:
            raise RuntimeError(f"Failed to create entity: {e}")

    def read_by_id(self, authorization_context: "AuthorizationContext", id: ID) -> T:
        """Read an element by ID."""
        if not self.enabled:
            raise RuntimeError("Gremlin connection not available")

        try:
            # Find vertex by ID
            vertex = self.g.V().hasId(str(id)).next()

            # Convert vertex to element (simplified)
            element = self._vertex_to_element(vertex)

            if not self.authorization_model.can_read(authorization_context, element):
                raise PermissionError(
                    "Permission Denied: You do not have permission to read this entity."
                )

            return element
        except StopIteration:
            raise ValueError("No Such Item Exists")

    def update(self, authorization_context: "AuthorizationContext", element: T) -> T:
        """Update an existing element."""
        if not self.authorization_model.can_update(authorization_context, element):
            raise PermissionError(
                "Permission Denied: You do not have permission to update this entity."
            )

        if not self.enabled:
            raise RuntimeError("Gremlin connection not available")

        try:
            # Update vertex properties
            query = self.g.V().hasId(element.id)
            query = query.property("label", element.label)

            result = query.next()
            return element
        except Exception as e:
            raise RuntimeError(f"Failed to update entity: {e}")

    def delete(self, authorization_context: "AuthorizationContext", element: T) -> None:
        """Delete an element."""
        if not self.authorization_model.can_delete(authorization_context, element):
            raise PermissionError(
                "Permission Denied: You do not have permission to delete this entity."
            )

        if not self.enabled:
            raise RuntimeError("Gremlin connection not available")

        try:
            self.g.V().hasId(element.id).drop().iterate()
        except Exception as e:
            raise RuntimeError(f"Failed to delete entity: {e}")

    def filter(
        self, authorization_context: AuthorizationContext, properties: Dict[str, Any]
    ) -> List[T]:
        """Filter elements by properties with authorization."""
        if not self.enabled:
            raise RuntimeError("Gremlin connection not available")

        try:
            query = self.g.V()

            # Add property filters
            for key, value in properties.items():
                query = query.has(key, value)

            vertices = query.toList()
            elements = [self._vertex_to_element(v) for v in vertices]

            # Filter by read permissions
            authorized_elements = []
            for element in elements:
                if self.authorization_model.can_read(authorization_context, element):
                    authorized_elements.append(element)

            return authorized_elements
        except Exception as e:
            raise RuntimeError(f"Failed to filter entities: {e}")

    def _vertex_to_element(self, vertex) -> T:
        """Convert a Gremlin vertex to an element object."""
        # This is a simplified conversion - in real implementation,
        # you would properly map vertex properties to your element type
        if not self.element_type:
            raise RuntimeError("Element type not specified")

        # Mock conversion for demonstration
        # In real implementation, you'd extract properties and create proper object
        element_data = {
            "id": vertex.id if hasattr(vertex, "id") else str(vertex),
            "label": getattr(vertex, "label", ""),
            "type": getattr(vertex, "type", ""),
        }

        # This would need proper implementation based on your element structure
        return self.element_type(**element_data)

    def close(self):
        """Close the Gremlin connection."""
        if hasattr(self, "connection") and self.connection:
            self.connection.close()
