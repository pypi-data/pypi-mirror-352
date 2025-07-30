from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AccountType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ACCOUNT_TYPE_UNSPECIFIED: _ClassVar[AccountType]
    ACCOUNT_TYPE_PERSONAL: _ClassVar[AccountType]
    ACCOUNT_TYPE_BUSINESS: _ClassVar[AccountType]

class AccountStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ACCOUNT_STATUS_UNSPECIFIED: _ClassVar[AccountStatus]
    ACCOUNT_STATUS_ACTIVE: _ClassVar[AccountStatus]
    ACCOUNT_STATUS_INACTIVE: _ClassVar[AccountStatus]
    ACCOUNT_STATUS_SUSPENDED: _ClassVar[AccountStatus]
ACCOUNT_TYPE_UNSPECIFIED: AccountType
ACCOUNT_TYPE_PERSONAL: AccountType
ACCOUNT_TYPE_BUSINESS: AccountType
ACCOUNT_STATUS_UNSPECIFIED: AccountStatus
ACCOUNT_STATUS_ACTIVE: AccountStatus
ACCOUNT_STATUS_INACTIVE: AccountStatus
ACCOUNT_STATUS_SUSPENDED: AccountStatus

class ThirdPartyInfo(_message.Message):
    __slots__ = ("provider_id", "email", "profile_url")
    PROVIDER_ID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PROFILE_URL_FIELD_NUMBER: _ClassVar[int]
    provider_id: str
    email: str
    profile_url: str
    def __init__(self, provider_id: _Optional[str] = ..., email: _Optional[str] = ..., profile_url: _Optional[str] = ...) -> None: ...

class Account(_message.Message):
    __slots__ = ("id", "type", "status", "email", "phone", "google", "apple", "microsoft", "owner_name", "preferred_username", "picture_url")
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    GOOGLE_FIELD_NUMBER: _ClassVar[int]
    APPLE_FIELD_NUMBER: _ClassVar[int]
    MICROSOFT_FIELD_NUMBER: _ClassVar[int]
    OWNER_NAME_FIELD_NUMBER: _ClassVar[int]
    PREFERRED_USERNAME_FIELD_NUMBER: _ClassVar[int]
    PICTURE_URL_FIELD_NUMBER: _ClassVar[int]
    id: str
    type: AccountType
    status: AccountStatus
    email: str
    phone: str
    google: ThirdPartyInfo
    apple: ThirdPartyInfo
    microsoft: ThirdPartyInfo
    owner_name: str
    preferred_username: str
    picture_url: str
    def __init__(self, id: _Optional[str] = ..., type: _Optional[_Union[AccountType, str]] = ..., status: _Optional[_Union[AccountStatus, str]] = ..., email: _Optional[str] = ..., phone: _Optional[str] = ..., google: _Optional[_Union[ThirdPartyInfo, _Mapping]] = ..., apple: _Optional[_Union[ThirdPartyInfo, _Mapping]] = ..., microsoft: _Optional[_Union[ThirdPartyInfo, _Mapping]] = ..., owner_name: _Optional[str] = ..., preferred_username: _Optional[str] = ..., picture_url: _Optional[str] = ...) -> None: ...
