from apexnova.identity.user import user_pb2 as _user_pb2
from apexnova.stub import response_pb2 as _response_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ReadUserRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class ReadUserResponse(_message.Message):
    __slots__ = ("user", "standard_response")
    USER_FIELD_NUMBER: _ClassVar[int]
    STANDARD_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    user: _user_pb2.User
    standard_response: _response_pb2.StandardResponse
    def __init__(self, user: _Optional[_Union[_user_pb2.User, _Mapping]] = ..., standard_response: _Optional[_Union[_response_pb2.StandardResponse, _Mapping]] = ...) -> None: ...

class CreateUserRequest(_message.Message):
    __slots__ = ("name", "email")
    NAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    name: str
    email: str
    def __init__(self, name: _Optional[str] = ..., email: _Optional[str] = ...) -> None: ...

class CreateUserResponse(_message.Message):
    __slots__ = ("user", "standard_response")
    USER_FIELD_NUMBER: _ClassVar[int]
    STANDARD_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    user: _user_pb2.User
    standard_response: _response_pb2.StandardResponse
    def __init__(self, user: _Optional[_Union[_user_pb2.User, _Mapping]] = ..., standard_response: _Optional[_Union[_response_pb2.StandardResponse, _Mapping]] = ...) -> None: ...

class UpdateUserRequest(_message.Message):
    __slots__ = ("user",)
    USER_FIELD_NUMBER: _ClassVar[int]
    user: _user_pb2.User
    def __init__(self, user: _Optional[_Union[_user_pb2.User, _Mapping]] = ...) -> None: ...

class UpdateUserResponse(_message.Message):
    __slots__ = ("user", "standard_response")
    USER_FIELD_NUMBER: _ClassVar[int]
    STANDARD_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    user: _user_pb2.User
    standard_response: _response_pb2.StandardResponse
    def __init__(self, user: _Optional[_Union[_user_pb2.User, _Mapping]] = ..., standard_response: _Optional[_Union[_response_pb2.StandardResponse, _Mapping]] = ...) -> None: ...

class DeleteUserRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteUserResponse(_message.Message):
    __slots__ = ("id", "standard_response")
    ID_FIELD_NUMBER: _ClassVar[int]
    STANDARD_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    id: str
    standard_response: _response_pb2.StandardResponse
    def __init__(self, id: _Optional[str] = ..., standard_response: _Optional[_Union[_response_pb2.StandardResponse, _Mapping]] = ...) -> None: ...

class ReadUsersStreamRequest(_message.Message):
    __slots__ = ("ids",)
    IDS_FIELD_NUMBER: _ClassVar[int]
    ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, ids: _Optional[_Iterable[str]] = ...) -> None: ...
