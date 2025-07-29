"""Example usage of ApexNova Python stub utilities."""

from typing import List

# Import the protobuf generated classes
from apexnova.authorization_context_pb2 import AuthorizationContext
from apexnova.stub.role_pb2 import Role
from apexnova.stub.actor_pb2 import Actor

# Import the utility classes
from apexnova.stub.authorization.authorization_rule import AuthorizationRule
from apexnova.stub.authorization.authorization_status import AuthorizationStatus
from apexnova.stub.authorization.model.base_authorization_model import (
    BaseAuthorizationModel,
)
from apexnova.stub.authorization.rule import (
    AlwaysPassRule,
    FailIfNotLoggedInRule,
    PassIfAdminRule,
)
from apexnova.stub.service.application_insights_service import (
    ApplicationInsightsService,
)
from apexnova.stub.service.request_handler_service import RequestHandlerService
from apexnova.stub.model.base_model import IBaseModel


class User:
    """Example user model implementing IBaseModel protocol."""

    def __init__(self, id: str, name: str, email: str):
        self.id = id
        self.name = name
        self.email = email
        self.address = ""
        self.label = name
        self.phone = ""
        from datetime import datetime

        self.created_at = datetime.now()
        self.updated_at = datetime.now()


class UserAuthorizationModel(BaseAuthorizationModel[User]):
    """Example authorization model for user operations."""

    def get_read_rules(self) -> List[AuthorizationRule[User]]:
        """Users can read if they are logged in."""
        return [FailIfNotLoggedInRule[User](), AlwaysPassRule[User]()]

    def get_create_rules(self) -> List[AuthorizationRule[User]]:
        """Only admins can create users."""
        return [FailIfNotLoggedInRule[User](), PassIfAdminRule[User]()]

    def get_update_rules(self) -> List[AuthorizationRule[User]]:
        """Only admins can update users."""
        return [FailIfNotLoggedInRule[User](), PassIfAdminRule[User]()]

    def get_delete_rules(self) -> List[AuthorizationRule[User]]:
        """Only admins can delete users."""
        return [FailIfNotLoggedInRule[User](), PassIfAdminRule[User]()]


def main():
    """Example usage of the ApexNova utilities."""

    # Create an authorization context
    context = AuthorizationContext()
    context.id = "user123"
    context.account_id = "account456"
    context.roles.extend([Role.ROLE_USER])
    context.actor.name = Actor.ACTOR_USER.name

    # Create a user
    user = User("user123", "John Doe", "john@example.com")

    # Create authorization model
    auth_model = UserAuthorizationModel()

    # Test authorization
    can_read = auth_model.can_read(context, user)
    can_create = auth_model.can_create(context, user)
    can_update = auth_model.can_update(context, user)
    can_delete = auth_model.can_delete(context, user)

    print(f"User can read: {can_read}")  # True (logged in)
    print(f"User can create: {can_create}")  # False (not admin)
    print(f"User can update: {can_update}")  # False (not admin)
    print(f"User can delete: {can_delete}")  # False (not admin)

    # Test with admin role
    admin_context = AuthorizationContext()
    admin_context.id = "admin123"
    admin_context.account_id = "account789"
    admin_context.roles.extend([Role.ROLE_ADMIN])
    admin_context.actor.name = Actor.ACTOR_USER.name

    admin_can_create = auth_model.can_create(admin_context, user)
    print(f"Admin can create: {admin_can_create}")  # True

    # Example telemetry usage
    insights_service = ApplicationInsightsService()
    insights_service.set_service("user-service")

    # Track events
    insights_service.track_event("user_created", context, {"userId": user.id})
    insights_service.track_trace("User operation completed", "INFO", context)

    # Example request handler usage
    request_handler = RequestHandlerService(insights_service)

    print("ApexNova Python utilities example completed successfully!")


if __name__ == "__main__":
    main()
