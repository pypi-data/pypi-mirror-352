from apexnova.notification import notification_pb2 as _notification_pb2
from apexnova.stub import authorization_context_pb2 as _authorization_context_pb2
from apexnova.stub import response_pb2 as _response_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SendEmailRequest(_message.Message):
    __slots__ = ("authorization_context", "email_notification")
    AUTHORIZATION_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    EMAIL_NOTIFICATION_FIELD_NUMBER: _ClassVar[int]
    authorization_context: _authorization_context_pb2.AuthorizationContext
    email_notification: _notification_pb2.EmailNotification
    def __init__(self, authorization_context: _Optional[_Union[_authorization_context_pb2.AuthorizationContext, _Mapping]] = ..., email_notification: _Optional[_Union[_notification_pb2.EmailNotification, _Mapping]] = ...) -> None: ...

class SendSMSRequest(_message.Message):
    __slots__ = ("authorization_context", "sms_notification")
    AUTHORIZATION_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    SMS_NOTIFICATION_FIELD_NUMBER: _ClassVar[int]
    authorization_context: _authorization_context_pb2.AuthorizationContext
    sms_notification: _notification_pb2.SMSNotification
    def __init__(self, authorization_context: _Optional[_Union[_authorization_context_pb2.AuthorizationContext, _Mapping]] = ..., sms_notification: _Optional[_Union[_notification_pb2.SMSNotification, _Mapping]] = ...) -> None: ...

class SendNotificationResponse(_message.Message):
    __slots__ = ("standard_response",)
    STANDARD_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    standard_response: _response_pb2.StandardResponse
    def __init__(self, standard_response: _Optional[_Union[_response_pb2.StandardResponse, _Mapping]] = ...) -> None: ...
