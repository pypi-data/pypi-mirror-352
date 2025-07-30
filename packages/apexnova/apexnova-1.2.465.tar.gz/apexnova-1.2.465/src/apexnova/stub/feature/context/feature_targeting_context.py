"""Feature targeting context for Azure feature management."""

from typing import List, TYPE_CHECKING, Dict, Any

if TYPE_CHECKING:
    from apexnova.stub.authorization_context_pb2 import (
        AuthorizationContext,
        Actor,
        Device,
        UserAgent,
        Location,
        Tier,
    )


class FeatureTargetingContext:
    """Context for feature targeting based on authorization context."""

    def __init__(self, authorization_context: "AuthorizationContext"):
        """
        Initialize feature targeting context from authorization context.

        Args:
            authorization_context: The authorization context
        """
        self._user_id = authorization_context.id
        self._roles = list(authorization_context.roles)
        self._device = authorization_context.device
        self._user_agent = authorization_context.user_agent
        self._ip_address = authorization_context.ip_address
        self._actor = authorization_context.actor
        self._request_time = authorization_context.request_time
        self._location = authorization_context.location
        self._tier = authorization_context.tier
        self._client_request_id = authorization_context.client_request_id
        self._account_id = authorization_context.account_id

    @property
    def user_id(self) -> str:
        """Get the user ID."""
        return self._user_id

    @user_id.setter
    def user_id(self, value: str) -> None:
        """Set the user ID."""
        self._user_id = value

    @property
    def groups(self) -> List[str]:
        """Get the user groups (role names)."""
        return [getattr(role, "name", str(role)) for role in self._roles]

    @groups.setter
    def groups(self, value: List[str]) -> None:
        """Set the user groups."""
        # Convert string names back to Role enum values
        # Note: This would need runtime import handling
        pass  # Simplified for now

    @property
    def device(self) -> "Device":
        """Get the device."""
        return self._device

    @property
    def user_agent(self) -> "UserAgent":
        """Get the user agent."""
        return self._user_agent

    @property
    def ip_address(self) -> str:
        """Get the IP address."""
        return self._ip_address

    @property
    def actor(self) -> "Actor":
        """Get the actor."""
        return self._actor

    @property
    def request_time(self) -> int:
        """Get the request time."""
        return self._request_time

    @property
    def location(self) -> "Location":
        """Get the location."""
        return self._location

    @property
    def tier(self) -> "Tier":
        """Get the tier."""
        return self._tier

    @property
    def client_request_id(self) -> str:
        """Get the client request ID."""
        return self._client_request_id

    @property
    def account_id(self) -> str:
        """Get the account ID."""
        return self._account_id

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for feature evaluation."""
        return {
            "userId": self.user_id,
            "groups": self.groups,
            "ipAddress": self.ip_address,
            "requestTime": self.request_time,
            "clientRequestId": self.client_request_id,
            "accountId": self.account_id,
            # Note: Protobuf enum .name attributes would need runtime import handling
            "device": self.device,
            "userAgent": self.user_agent,
            "actor": self.actor,
            "location": self.location,
            "tier": self.tier,
        }
