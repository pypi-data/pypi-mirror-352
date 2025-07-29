"""Feature targeting context for Azure feature management."""

from typing import List, Optional

from apexnova.authorization_context_pb2 import AuthorizationContext
from apexnova.stub.role_pb2 import Role
from apexnova.stub.actor_pb2 import Actor
from apexnova.stub.device_pb2 import Device
from apexnova.stub.user_agent_pb2 import UserAgent
from apexnova.stub.location_pb2 import Location
from apexnova.stub.tier_pb2 import Tier


class FeatureTargetingContext:
    """Context for feature targeting based on authorization context."""

    def __init__(self, authorization_context: AuthorizationContext):
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
        return [role.name for role in self._roles]

    @groups.setter
    def groups(self, value: List[str]) -> None:
        """Set the user groups."""
        # Convert string names back to Role enum values
        self._roles = [Role.Value(name) for name in value if hasattr(Role, name)]

    @property
    def device(self) -> Device:
        """Get the device."""
        return self._device

    @property
    def user_agent(self) -> UserAgent:
        """Get the user agent."""
        return self._user_agent

    @property
    def ip_address(self) -> str:
        """Get the IP address."""
        return self._ip_address

    @property
    def actor(self) -> Actor:
        """Get the actor."""
        return self._actor

    @property
    def request_time(self) -> int:
        """Get the request time."""
        return self._request_time

    @property
    def location(self) -> Location:
        """Get the location."""
        return self._location

    @property
    def tier(self) -> Tier:
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

    def to_dict(self) -> dict:
        """Convert context to dictionary for feature evaluation."""
        return {
            "userId": self.user_id,
            "groups": self.groups,
            "device": self.device.name,
            "userAgent": self.user_agent.name,
            "ipAddress": self.ip_address,
            "actor": self.actor.name,
            "requestTime": self.request_time,
            "location": self.location.name,
            "tier": self.tier.name,
            "clientRequestId": self.client_request_id,
            "accountId": self.account_id,
        }
