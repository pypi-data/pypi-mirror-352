from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ResponseStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RESPONSE_STATUS_UNSPECIFIED: _ClassVar[ResponseStatus]
    RESPONSE_STATUS_SUCCESS: _ClassVar[ResponseStatus]
    RESPONSE_STATUS_NOT_FOUND: _ClassVar[ResponseStatus]
    RESPONSE_STATUS_INVALID_ARGUMENT: _ClassVar[ResponseStatus]
    RESPONSE_STATUS_PERMISSION_DENIED: _ClassVar[ResponseStatus]
    RESPONSE_STATUS_INTERNAL_ERROR: _ClassVar[ResponseStatus]
    RESPONSE_STATUS_UNAUTHENTICATED: _ClassVar[ResponseStatus]
    RESPONSE_STATUS_BAD_REQUEST: _ClassVar[ResponseStatus]
    RESPONSE_STATUS_FAILED_PRECONDITION: _ClassVar[ResponseStatus]
    RESPONSE_STATUS_UNAVAILABLE: _ClassVar[ResponseStatus]
    RESPONSE_STATUS_UNKNOWN: _ClassVar[ResponseStatus]
RESPONSE_STATUS_UNSPECIFIED: ResponseStatus
RESPONSE_STATUS_SUCCESS: ResponseStatus
RESPONSE_STATUS_NOT_FOUND: ResponseStatus
RESPONSE_STATUS_INVALID_ARGUMENT: ResponseStatus
RESPONSE_STATUS_PERMISSION_DENIED: ResponseStatus
RESPONSE_STATUS_INTERNAL_ERROR: ResponseStatus
RESPONSE_STATUS_UNAUTHENTICATED: ResponseStatus
RESPONSE_STATUS_BAD_REQUEST: ResponseStatus
RESPONSE_STATUS_FAILED_PRECONDITION: ResponseStatus
RESPONSE_STATUS_UNAVAILABLE: ResponseStatus
RESPONSE_STATUS_UNKNOWN: ResponseStatus

class StandardResponse(_message.Message):
    __slots__ = ("status_code", "error_message")
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    status_code: ResponseStatus
    error_message: str
    def __init__(self, status_code: _Optional[_Union[ResponseStatus, str]] = ..., error_message: _Optional[str] = ...) -> None: ...
