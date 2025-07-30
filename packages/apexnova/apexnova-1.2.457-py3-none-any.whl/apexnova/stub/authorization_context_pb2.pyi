from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Role(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ROLE_UNSPECIFIED: _ClassVar[Role]
    ROLE_ADMIN: _ClassVar[Role]
    ROLE_USER: _ClassVar[Role]
    ROLE_GUEST: _ClassVar[Role]

class Actor(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ACTOR_UNSPECIFIED: _ClassVar[Actor]
    ACTOR_END_USER: _ClassVar[Actor]
    ACTOR_SERVICE: _ClassVar[Actor]

class Device(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DEVICE_UNSPECIFIED: _ClassVar[Device]
    DEVICE_DESKTOP_WINDOWS: _ClassVar[Device]
    DEVICE_DESKTOP_MAC: _ClassVar[Device]
    DEVICE_MOBILE_ANDROID: _ClassVar[Device]
    DEVICE_MOBILE_IOS: _ClassVar[Device]
    DEVICE_TABLET_ANDROID: _ClassVar[Device]
    DEVICE_TABLET_IOS: _ClassVar[Device]
    DEVICE_SMART_TV: _ClassVar[Device]
    DEVICE_WEARABLE: _ClassVar[Device]
    DEVICE_SET_TOP_BOX: _ClassVar[Device]
    DEVICE_GAME_CONSOLE: _ClassVar[Device]
    DEVICE_E_READER: _ClassVar[Device]
    DEVICE_OTHER: _ClassVar[Device]

class Location(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LOCATION_UNSPECIFIED: _ClassVar[Location]
    LOCATION_USA: _ClassVar[Location]
    LOCATION_CANADA: _ClassVar[Location]
    LOCATION_UK: _ClassVar[Location]
    LOCATION_GERMANY: _ClassVar[Location]
    LOCATION_FRANCE: _ClassVar[Location]
    LOCATION_INDIA: _ClassVar[Location]
    LOCATION_CHINA: _ClassVar[Location]
    LOCATION_JAPAN: _ClassVar[Location]
    LOCATION_AUSTRALIA: _ClassVar[Location]
    LOCATION_OTHER: _ClassVar[Location]

class UserAgent(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    USER_AGENT_UNSPECIFIED: _ClassVar[UserAgent]
    USER_AGENT_BROWSER_CHROME: _ClassVar[UserAgent]
    USER_AGENT_BROWSER_FIREFOX: _ClassVar[UserAgent]
    USER_AGENT_BROWSER_SAFARI: _ClassVar[UserAgent]
    USER_AGENT_BROWSER_EDGE: _ClassVar[UserAgent]
    USER_AGENT_BROWSER_OPERA: _ClassVar[UserAgent]
    USER_AGENT_MOBILE_APP_ANDROID: _ClassVar[UserAgent]
    USER_AGENT_MOBILE_APP_IOS: _ClassVar[UserAgent]
    USER_AGENT_API_CLIENT: _ClassVar[UserAgent]
    USER_AGENT_SMART_TV_APP: _ClassVar[UserAgent]
    USER_AGENT_WEARABLE_APP: _ClassVar[UserAgent]
    USER_AGENT_SET_TOP_BOX_APP: _ClassVar[UserAgent]
    USER_AGENT_GAME_CONSOLE_APP: _ClassVar[UserAgent]
    USER_AGENT_E_READER_APP: _ClassVar[UserAgent]
    USER_AGENT_BOT_GOOGLE: _ClassVar[UserAgent]
    USER_AGENT_BOT_BING: _ClassVar[UserAgent]
    USER_AGENT_BOT_YAHOO: _ClassVar[UserAgent]
    USER_AGENT_OTHER: _ClassVar[UserAgent]

class Tier(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TIER_UNSPECIFIED: _ClassVar[Tier]
    TIER_PRODUCTION: _ClassVar[Tier]
    TIER_DEVELOPMENT: _ClassVar[Tier]
    TIER_TEST: _ClassVar[Tier]
ROLE_UNSPECIFIED: Role
ROLE_ADMIN: Role
ROLE_USER: Role
ROLE_GUEST: Role
ACTOR_UNSPECIFIED: Actor
ACTOR_END_USER: Actor
ACTOR_SERVICE: Actor
DEVICE_UNSPECIFIED: Device
DEVICE_DESKTOP_WINDOWS: Device
DEVICE_DESKTOP_MAC: Device
DEVICE_MOBILE_ANDROID: Device
DEVICE_MOBILE_IOS: Device
DEVICE_TABLET_ANDROID: Device
DEVICE_TABLET_IOS: Device
DEVICE_SMART_TV: Device
DEVICE_WEARABLE: Device
DEVICE_SET_TOP_BOX: Device
DEVICE_GAME_CONSOLE: Device
DEVICE_E_READER: Device
DEVICE_OTHER: Device
LOCATION_UNSPECIFIED: Location
LOCATION_USA: Location
LOCATION_CANADA: Location
LOCATION_UK: Location
LOCATION_GERMANY: Location
LOCATION_FRANCE: Location
LOCATION_INDIA: Location
LOCATION_CHINA: Location
LOCATION_JAPAN: Location
LOCATION_AUSTRALIA: Location
LOCATION_OTHER: Location
USER_AGENT_UNSPECIFIED: UserAgent
USER_AGENT_BROWSER_CHROME: UserAgent
USER_AGENT_BROWSER_FIREFOX: UserAgent
USER_AGENT_BROWSER_SAFARI: UserAgent
USER_AGENT_BROWSER_EDGE: UserAgent
USER_AGENT_BROWSER_OPERA: UserAgent
USER_AGENT_MOBILE_APP_ANDROID: UserAgent
USER_AGENT_MOBILE_APP_IOS: UserAgent
USER_AGENT_API_CLIENT: UserAgent
USER_AGENT_SMART_TV_APP: UserAgent
USER_AGENT_WEARABLE_APP: UserAgent
USER_AGENT_SET_TOP_BOX_APP: UserAgent
USER_AGENT_GAME_CONSOLE_APP: UserAgent
USER_AGENT_E_READER_APP: UserAgent
USER_AGENT_BOT_GOOGLE: UserAgent
USER_AGENT_BOT_BING: UserAgent
USER_AGENT_BOT_YAHOO: UserAgent
USER_AGENT_OTHER: UserAgent
TIER_UNSPECIFIED: Tier
TIER_PRODUCTION: Tier
TIER_DEVELOPMENT: Tier
TIER_TEST: Tier

class AuthorizationContext(_message.Message):
    __slots__ = ("id", "roles", "actor", "ip_address", "request_time", "device", "location", "user_agent", "tier", "client_request_id", "account_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    ROLES_FIELD_NUMBER: _ClassVar[int]
    ACTOR_FIELD_NUMBER: _ClassVar[int]
    IP_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    REQUEST_TIME_FIELD_NUMBER: _ClassVar[int]
    DEVICE_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    USER_AGENT_FIELD_NUMBER: _ClassVar[int]
    TIER_FIELD_NUMBER: _ClassVar[int]
    CLIENT_REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    roles: _containers.RepeatedScalarFieldContainer[Role]
    actor: Actor
    ip_address: str
    request_time: int
    device: Device
    location: Location
    user_agent: UserAgent
    tier: Tier
    client_request_id: str
    account_id: str
    def __init__(self, id: _Optional[str] = ..., roles: _Optional[_Iterable[_Union[Role, str]]] = ..., actor: _Optional[_Union[Actor, str]] = ..., ip_address: _Optional[str] = ..., request_time: _Optional[int] = ..., device: _Optional[_Union[Device, str]] = ..., location: _Optional[_Union[Location, str]] = ..., user_agent: _Optional[_Union[UserAgent, str]] = ..., tier: _Optional[_Union[Tier, str]] = ..., client_request_id: _Optional[str] = ..., account_id: _Optional[str] = ...) -> None: ...
