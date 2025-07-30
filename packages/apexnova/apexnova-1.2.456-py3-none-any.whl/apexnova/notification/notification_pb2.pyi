from apexnova.stub import authorization_context_pb2 as _authorization_context_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class NotificationCategory(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NOTIFICATION_CATEGORY_UNSPECIFIED: _ClassVar[NotificationCategory]
    NOTIFICATION_CATEGORY_MARKETING: _ClassVar[NotificationCategory]
    NOTIFICATION_CATEGORY_TRANSACTIONAL: _ClassVar[NotificationCategory]
    NOTIFICATION_CATEGORY_PROMOTIONAL: _ClassVar[NotificationCategory]
NOTIFICATION_CATEGORY_UNSPECIFIED: NotificationCategory
NOTIFICATION_CATEGORY_MARKETING: NotificationCategory
NOTIFICATION_CATEGORY_TRANSACTIONAL: NotificationCategory
NOTIFICATION_CATEGORY_PROMOTIONAL: NotificationCategory

class EmailNotification(_message.Message):
    __slots__ = ("authorization_context", "recipients", "cc_recipients", "bcc_recipients", "subject", "template_data", "attachments", "reply_tos", "category")
    class TemplateDataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    AUTHORIZATION_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    RECIPIENTS_FIELD_NUMBER: _ClassVar[int]
    CC_RECIPIENTS_FIELD_NUMBER: _ClassVar[int]
    BCC_RECIPIENTS_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_DATA_FIELD_NUMBER: _ClassVar[int]
    ATTACHMENTS_FIELD_NUMBER: _ClassVar[int]
    REPLY_TOS_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    authorization_context: _authorization_context_pb2.AuthorizationContext
    recipients: _containers.RepeatedScalarFieldContainer[str]
    cc_recipients: _containers.RepeatedScalarFieldContainer[str]
    bcc_recipients: _containers.RepeatedScalarFieldContainer[str]
    subject: str
    template_data: _containers.ScalarMap[str, str]
    attachments: _containers.RepeatedScalarFieldContainer[str]
    reply_tos: _containers.RepeatedScalarFieldContainer[str]
    category: NotificationCategory
    def __init__(self, authorization_context: _Optional[_Union[_authorization_context_pb2.AuthorizationContext, _Mapping]] = ..., recipients: _Optional[_Iterable[str]] = ..., cc_recipients: _Optional[_Iterable[str]] = ..., bcc_recipients: _Optional[_Iterable[str]] = ..., subject: _Optional[str] = ..., template_data: _Optional[_Mapping[str, str]] = ..., attachments: _Optional[_Iterable[str]] = ..., reply_tos: _Optional[_Iterable[str]] = ..., category: _Optional[_Union[NotificationCategory, str]] = ...) -> None: ...

class SMSNotification(_message.Message):
    __slots__ = ("authorization_context", "recipient", "content", "category")
    AUTHORIZATION_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    RECIPIENT_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    authorization_context: _authorization_context_pb2.AuthorizationContext
    recipient: str
    content: str
    category: NotificationCategory
    def __init__(self, authorization_context: _Optional[_Union[_authorization_context_pb2.AuthorizationContext, _Mapping]] = ..., recipient: _Optional[str] = ..., content: _Optional[str] = ..., category: _Optional[_Union[NotificationCategory, str]] = ...) -> None: ...
