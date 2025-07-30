from apexnova.identity.account import account_pb2 as _account_pb2
from apexnova.stub import authorization_context_pb2 as _authorization_context_pb2
from apexnova.stub import response_pb2 as _response_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ReadAccountRequest(_message.Message):
    __slots__ = ("authorization_context", "id")
    AUTHORIZATION_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    authorization_context: _authorization_context_pb2.AuthorizationContext
    id: str
    def __init__(self, authorization_context: _Optional[_Union[_authorization_context_pb2.AuthorizationContext, _Mapping]] = ..., id: _Optional[str] = ...) -> None: ...

class ReadAccountResponse(_message.Message):
    __slots__ = ("account", "standard_response")
    ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    STANDARD_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    account: _account_pb2.Account
    standard_response: _response_pb2.StandardResponse
    def __init__(self, account: _Optional[_Union[_account_pb2.Account, _Mapping]] = ..., standard_response: _Optional[_Union[_response_pb2.StandardResponse, _Mapping]] = ...) -> None: ...

class CreateAccountRequest(_message.Message):
    __slots__ = ("authorization_context", "owner_name", "preferred_username", "password", "phone", "picture_url", "account_type", "account_status", "email")
    AUTHORIZATION_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    OWNER_NAME_FIELD_NUMBER: _ClassVar[int]
    PREFERRED_USERNAME_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    PICTURE_URL_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_TYPE_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_STATUS_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    authorization_context: _authorization_context_pb2.AuthorizationContext
    owner_name: str
    preferred_username: str
    password: str
    phone: str
    picture_url: str
    account_type: _account_pb2.AccountType
    account_status: _account_pb2.AccountStatus
    email: str
    def __init__(self, authorization_context: _Optional[_Union[_authorization_context_pb2.AuthorizationContext, _Mapping]] = ..., owner_name: _Optional[str] = ..., preferred_username: _Optional[str] = ..., password: _Optional[str] = ..., phone: _Optional[str] = ..., picture_url: _Optional[str] = ..., account_type: _Optional[_Union[_account_pb2.AccountType, str]] = ..., account_status: _Optional[_Union[_account_pb2.AccountStatus, str]] = ..., email: _Optional[str] = ...) -> None: ...

class CreateAccountResponse(_message.Message):
    __slots__ = ("account", "refresh_token", "standard_response")
    ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    REFRESH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    STANDARD_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    account: _account_pb2.Account
    refresh_token: str
    standard_response: _response_pb2.StandardResponse
    def __init__(self, account: _Optional[_Union[_account_pb2.Account, _Mapping]] = ..., refresh_token: _Optional[str] = ..., standard_response: _Optional[_Union[_response_pb2.StandardResponse, _Mapping]] = ...) -> None: ...

class UpdateAccountRequest(_message.Message):
    __slots__ = ("authorization_context", "id", "owner_name", "phone", "picture_url", "account_type", "account_status", "email")
    AUTHORIZATION_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    OWNER_NAME_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    PICTURE_URL_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_TYPE_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_STATUS_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    authorization_context: _authorization_context_pb2.AuthorizationContext
    id: str
    owner_name: str
    phone: str
    picture_url: str
    account_type: _account_pb2.AccountType
    account_status: _account_pb2.AccountStatus
    email: str
    def __init__(self, authorization_context: _Optional[_Union[_authorization_context_pb2.AuthorizationContext, _Mapping]] = ..., id: _Optional[str] = ..., owner_name: _Optional[str] = ..., phone: _Optional[str] = ..., picture_url: _Optional[str] = ..., account_type: _Optional[_Union[_account_pb2.AccountType, str]] = ..., account_status: _Optional[_Union[_account_pb2.AccountStatus, str]] = ..., email: _Optional[str] = ...) -> None: ...

class UpdateAccountResponse(_message.Message):
    __slots__ = ("account", "standard_response")
    ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    STANDARD_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    account: _account_pb2.Account
    standard_response: _response_pb2.StandardResponse
    def __init__(self, account: _Optional[_Union[_account_pb2.Account, _Mapping]] = ..., standard_response: _Optional[_Union[_response_pb2.StandardResponse, _Mapping]] = ...) -> None: ...

class DeleteAccountRequest(_message.Message):
    __slots__ = ("authorization_context", "id")
    AUTHORIZATION_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    authorization_context: _authorization_context_pb2.AuthorizationContext
    id: str
    def __init__(self, authorization_context: _Optional[_Union[_authorization_context_pb2.AuthorizationContext, _Mapping]] = ..., id: _Optional[str] = ...) -> None: ...

class DeleteAccountResponse(_message.Message):
    __slots__ = ("standard_response",)
    STANDARD_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    standard_response: _response_pb2.StandardResponse
    def __init__(self, standard_response: _Optional[_Union[_response_pb2.StandardResponse, _Mapping]] = ...) -> None: ...

class LoginRequest(_message.Message):
    __slots__ = ("authorization_context", "preferred_username", "password")
    AUTHORIZATION_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    PREFERRED_USERNAME_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    authorization_context: _authorization_context_pb2.AuthorizationContext
    preferred_username: str
    password: str
    def __init__(self, authorization_context: _Optional[_Union[_authorization_context_pb2.AuthorizationContext, _Mapping]] = ..., preferred_username: _Optional[str] = ..., password: _Optional[str] = ...) -> None: ...

class LoginResponse(_message.Message):
    __slots__ = ("authorization_context", "refresh_token", "standard_response", "account")
    AUTHORIZATION_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    REFRESH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    STANDARD_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    authorization_context: _authorization_context_pb2.AuthorizationContext
    refresh_token: str
    standard_response: _response_pb2.StandardResponse
    account: _account_pb2.Account
    def __init__(self, authorization_context: _Optional[_Union[_authorization_context_pb2.AuthorizationContext, _Mapping]] = ..., refresh_token: _Optional[str] = ..., standard_response: _Optional[_Union[_response_pb2.StandardResponse, _Mapping]] = ..., account: _Optional[_Union[_account_pb2.Account, _Mapping]] = ...) -> None: ...

class LogoutRequest(_message.Message):
    __slots__ = ("authorization_context", "id")
    AUTHORIZATION_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    authorization_context: _authorization_context_pb2.AuthorizationContext
    id: str
    def __init__(self, authorization_context: _Optional[_Union[_authorization_context_pb2.AuthorizationContext, _Mapping]] = ..., id: _Optional[str] = ...) -> None: ...

class LogoutResponse(_message.Message):
    __slots__ = ("standard_response", "account")
    STANDARD_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    standard_response: _response_pb2.StandardResponse
    account: _account_pb2.Account
    def __init__(self, standard_response: _Optional[_Union[_response_pb2.StandardResponse, _Mapping]] = ..., account: _Optional[_Union[_account_pb2.Account, _Mapping]] = ...) -> None: ...

class RefreshTokenRequest(_message.Message):
    __slots__ = ("authorization_context", "id", "refresh_token")
    AUTHORIZATION_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    REFRESH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    authorization_context: _authorization_context_pb2.AuthorizationContext
    id: str
    refresh_token: str
    def __init__(self, authorization_context: _Optional[_Union[_authorization_context_pb2.AuthorizationContext, _Mapping]] = ..., id: _Optional[str] = ..., refresh_token: _Optional[str] = ...) -> None: ...

class RefreshTokenResponse(_message.Message):
    __slots__ = ("refresh_token", "standard_response")
    REFRESH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    STANDARD_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    refresh_token: str
    standard_response: _response_pb2.StandardResponse
    def __init__(self, refresh_token: _Optional[str] = ..., standard_response: _Optional[_Union[_response_pb2.StandardResponse, _Mapping]] = ...) -> None: ...

class ChangePasswordRequest(_message.Message):
    __slots__ = ("authorization_context", "id", "old_password", "new_password")
    AUTHORIZATION_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    OLD_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    NEW_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    authorization_context: _authorization_context_pb2.AuthorizationContext
    id: str
    old_password: str
    new_password: str
    def __init__(self, authorization_context: _Optional[_Union[_authorization_context_pb2.AuthorizationContext, _Mapping]] = ..., id: _Optional[str] = ..., old_password: _Optional[str] = ..., new_password: _Optional[str] = ...) -> None: ...

class ChangePasswordResponse(_message.Message):
    __slots__ = ("standard_response", "refresh_token", "account")
    STANDARD_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    REFRESH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    standard_response: _response_pb2.StandardResponse
    refresh_token: str
    account: _account_pb2.Account
    def __init__(self, standard_response: _Optional[_Union[_response_pb2.StandardResponse, _Mapping]] = ..., refresh_token: _Optional[str] = ..., account: _Optional[_Union[_account_pb2.Account, _Mapping]] = ...) -> None: ...
