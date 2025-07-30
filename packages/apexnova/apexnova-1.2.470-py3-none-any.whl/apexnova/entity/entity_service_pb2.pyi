from apexnova.entity import entity_pb2 as _entity_pb2
from apexnova.stub import authorization_context_pb2 as _authorization_context_pb2
from apexnova.stub import response_pb2 as _response_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateEntityUploadLinkRequest(_message.Message):
    __slots__ = ("authorization_context", "account_id", "name", "description", "tags")
    AUTHORIZATION_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    authorization_context: _authorization_context_pb2.AuthorizationContext
    account_id: str
    name: str
    description: str
    tags: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, authorization_context: _Optional[_Union[_authorization_context_pb2.AuthorizationContext, _Mapping]] = ..., account_id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., tags: _Optional[_Iterable[str]] = ...) -> None: ...

class CreateEntityUploadLinkResponse(_message.Message):
    __slots__ = ("entity", "sas_token", "standard_response")
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    SAS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    STANDARD_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    entity: _entity_pb2.Entity
    sas_token: str
    standard_response: _response_pb2.StandardResponse
    def __init__(self, entity: _Optional[_Union[_entity_pb2.Entity, _Mapping]] = ..., sas_token: _Optional[str] = ..., standard_response: _Optional[_Union[_response_pb2.StandardResponse, _Mapping]] = ...) -> None: ...

class ReadEntityRequest(_message.Message):
    __slots__ = ("authorization_context", "id")
    AUTHORIZATION_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    authorization_context: _authorization_context_pb2.AuthorizationContext
    id: str
    def __init__(self, authorization_context: _Optional[_Union[_authorization_context_pb2.AuthorizationContext, _Mapping]] = ..., id: _Optional[str] = ...) -> None: ...

class ReadEntityResponse(_message.Message):
    __slots__ = ("entity", "sas_token", "standard_response")
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    SAS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    STANDARD_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    entity: _entity_pb2.Entity
    sas_token: str
    standard_response: _response_pb2.StandardResponse
    def __init__(self, entity: _Optional[_Union[_entity_pb2.Entity, _Mapping]] = ..., sas_token: _Optional[str] = ..., standard_response: _Optional[_Union[_response_pb2.StandardResponse, _Mapping]] = ...) -> None: ...

class UpdateEntityRequest(_message.Message):
    __slots__ = ("authorization_context", "id", "name", "description", "tags")
    AUTHORIZATION_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    authorization_context: _authorization_context_pb2.AuthorizationContext
    id: str
    name: str
    description: str
    tags: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, authorization_context: _Optional[_Union[_authorization_context_pb2.AuthorizationContext, _Mapping]] = ..., id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., tags: _Optional[_Iterable[str]] = ...) -> None: ...

class UpdateEntityResponse(_message.Message):
    __slots__ = ("entity", "standard_response")
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    STANDARD_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    entity: _entity_pb2.Entity
    standard_response: _response_pb2.StandardResponse
    def __init__(self, entity: _Optional[_Union[_entity_pb2.Entity, _Mapping]] = ..., standard_response: _Optional[_Union[_response_pb2.StandardResponse, _Mapping]] = ...) -> None: ...

class DeleteEntityRequest(_message.Message):
    __slots__ = ("authorization_context", "id")
    AUTHORIZATION_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    authorization_context: _authorization_context_pb2.AuthorizationContext
    id: str
    def __init__(self, authorization_context: _Optional[_Union[_authorization_context_pb2.AuthorizationContext, _Mapping]] = ..., id: _Optional[str] = ...) -> None: ...

class DeleteEntityResponse(_message.Message):
    __slots__ = ("id", "standard_response")
    ID_FIELD_NUMBER: _ClassVar[int]
    STANDARD_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    id: str
    standard_response: _response_pb2.StandardResponse
    def __init__(self, id: _Optional[str] = ..., standard_response: _Optional[_Union[_response_pb2.StandardResponse, _Mapping]] = ...) -> None: ...

class FilterEntitiesRequest(_message.Message):
    __slots__ = ("authorization_context", "account_id", "previous_cursor", "limit")
    AUTHORIZATION_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_CURSOR_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    authorization_context: _authorization_context_pb2.AuthorizationContext
    account_id: str
    previous_cursor: str
    limit: int
    def __init__(self, authorization_context: _Optional[_Union[_authorization_context_pb2.AuthorizationContext, _Mapping]] = ..., account_id: _Optional[str] = ..., previous_cursor: _Optional[str] = ..., limit: _Optional[int] = ...) -> None: ...

class FilterEntitiesResponse(_message.Message):
    __slots__ = ("entities", "start_cursor", "end_cursor", "has_next_page", "has_previous_page", "standard_response")
    ENTITIES_FIELD_NUMBER: _ClassVar[int]
    START_CURSOR_FIELD_NUMBER: _ClassVar[int]
    END_CURSOR_FIELD_NUMBER: _ClassVar[int]
    HAS_NEXT_PAGE_FIELD_NUMBER: _ClassVar[int]
    HAS_PREVIOUS_PAGE_FIELD_NUMBER: _ClassVar[int]
    STANDARD_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    entities: _containers.RepeatedCompositeFieldContainer[_entity_pb2.Entity]
    start_cursor: str
    end_cursor: str
    has_next_page: bool
    has_previous_page: bool
    standard_response: _response_pb2.StandardResponse
    def __init__(self, entities: _Optional[_Iterable[_Union[_entity_pb2.Entity, _Mapping]]] = ..., start_cursor: _Optional[str] = ..., end_cursor: _Optional[str] = ..., has_next_page: bool = ..., has_previous_page: bool = ..., standard_response: _Optional[_Union[_response_pb2.StandardResponse, _Mapping]] = ...) -> None: ...

class DeleteEntitiesRequest(_message.Message):
    __slots__ = ("authorization_context", "ids")
    AUTHORIZATION_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    IDS_FIELD_NUMBER: _ClassVar[int]
    authorization_context: _authorization_context_pb2.AuthorizationContext
    ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, authorization_context: _Optional[_Union[_authorization_context_pb2.AuthorizationContext, _Mapping]] = ..., ids: _Optional[_Iterable[str]] = ...) -> None: ...

class UpdateEntitiesRequest(_message.Message):
    __slots__ = ("authorization_context", "entities")
    AUTHORIZATION_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    ENTITIES_FIELD_NUMBER: _ClassVar[int]
    authorization_context: _authorization_context_pb2.AuthorizationContext
    entities: _containers.RepeatedCompositeFieldContainer[UpdateEntityRequest]
    def __init__(self, authorization_context: _Optional[_Union[_authorization_context_pb2.AuthorizationContext, _Mapping]] = ..., entities: _Optional[_Iterable[_Union[UpdateEntityRequest, _Mapping]]] = ...) -> None: ...
