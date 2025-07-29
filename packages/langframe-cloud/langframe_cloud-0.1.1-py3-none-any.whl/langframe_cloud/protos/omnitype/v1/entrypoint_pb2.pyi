from langframe_cloud.protos.omnitype.v1 import common_pb2 as _common_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import (
    ClassVar as _ClassVar,
    Mapping as _Mapping,
    Optional as _Optional,
    Union as _Union,
)

DESCRIPTOR: _descriptor.FileDescriptor

class RegisterAppRequest(_message.Message):
    __slots__ = ("name", "canonical_name")
    NAME_FIELD_NUMBER: _ClassVar[int]
    CANONICAL_NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    canonical_name: str
    def __init__(
        self, name: _Optional[str] = ..., canonical_name: _Optional[str] = ...
    ) -> None: ...

class RegisterAppResponse(_message.Message):
    __slots__ = ("uuid",)
    UUID_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    def __init__(self, uuid: _Optional[str] = ...) -> None: ...

class GetOrCreateSessionRequest(_message.Message):
    __slots__ = ("app_uuid", "environment_name", "engine_metadata")
    APP_UUID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    ENGINE_METADATA_FIELD_NUMBER: _ClassVar[int]
    app_uuid: str
    environment_name: str
    engine_metadata: _common_pb2.EngineInstanceMetadata
    def __init__(
        self,
        app_uuid: _Optional[str] = ...,
        environment_name: _Optional[str] = ...,
        engine_metadata: _Optional[
            _Union[_common_pb2.EngineInstanceMetadata, _Mapping]
        ] = ...,
    ) -> None: ...

class GetOrCreateSessionResponse(_message.Message):
    __slots__ = (
        "uuid",
        "name",
        "canonical_name",
        "uris",
        "existing",
        "ephemeral_catalog_id",
    )
    UUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CANONICAL_NAME_FIELD_NUMBER: _ClassVar[int]
    URIS_FIELD_NUMBER: _ClassVar[int]
    EXISTING_FIELD_NUMBER: _ClassVar[int]
    EPHEMERAL_CATALOG_ID_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    name: str
    canonical_name: str
    uris: _common_pb2.EngineRequestUris
    existing: bool
    ephemeral_catalog_id: str
    def __init__(
        self,
        uuid: _Optional[str] = ...,
        name: _Optional[str] = ...,
        canonical_name: _Optional[str] = ...,
        uris: _Optional[_Union[_common_pb2.EngineRequestUris, _Mapping]] = ...,
        existing: bool = ...,
        ephemeral_catalog_id: _Optional[str] = ...,
    ) -> None: ...

class TerminateSessionRequest(_message.Message):
    __slots__ = ("uuid",)
    UUID_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    def __init__(self, uuid: _Optional[str] = ...) -> None: ...

class TerminateSessionResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
