from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EntityStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ENTITY_STATUS_UNSPECIFIED: _ClassVar[EntityStatus]
    ENTITY_STATUS_CREATED: _ClassVar[EntityStatus]
    ENTITY_STATUS_UPLOADED: _ClassVar[EntityStatus]
    ENTITY_STATUS_VERIFIED: _ClassVar[EntityStatus]
ENTITY_STATUS_UNSPECIFIED: EntityStatus
ENTITY_STATUS_CREATED: EntityStatus
ENTITY_STATUS_UPLOADED: EntityStatus
ENTITY_STATUS_VERIFIED: EntityStatus

class Entity(_message.Message):
    __slots__ = ("id", "name", "description", "tags", "blob_storage_url", "last_modified", "access_tier", "status")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    BLOB_STORAGE_URL_FIELD_NUMBER: _ClassVar[int]
    LAST_MODIFIED_FIELD_NUMBER: _ClassVar[int]
    ACCESS_TIER_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    tags: _containers.RepeatedScalarFieldContainer[str]
    blob_storage_url: str
    last_modified: str
    access_tier: str
    status: EntityStatus
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., tags: _Optional[_Iterable[str]] = ..., blob_storage_url: _Optional[str] = ..., last_modified: _Optional[str] = ..., access_tier: _Optional[str] = ..., status: _Optional[_Union[EntityStatus, str]] = ...) -> None: ...
