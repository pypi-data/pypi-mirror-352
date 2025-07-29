from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class InstanceSize(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INSTANCE_SIZE_UNSPECIFIED: _ClassVar[InstanceSize]
    INSTANCE_SIZE_S: _ClassVar[InstanceSize]
    INSTANCE_SIZE_M: _ClassVar[InstanceSize]
    INSTANCE_SIZE_L: _ClassVar[InstanceSize]
    INSTANCE_SIZE_XL: _ClassVar[InstanceSize]

INSTANCE_SIZE_UNSPECIFIED: InstanceSize
INSTANCE_SIZE_S: InstanceSize
INSTANCE_SIZE_M: InstanceSize
INSTANCE_SIZE_L: InstanceSize
INSTANCE_SIZE_XL: InstanceSize

class EngineInstanceMetadata(_message.Message):
    __slots__ = ("instance_size",)
    INSTANCE_SIZE_FIELD_NUMBER: _ClassVar[int]
    instance_size: InstanceSize
    def __init__(
        self, instance_size: _Optional[_Union[InstanceSize, str]] = ...
    ) -> None: ...

class EngineRequestUris(_message.Message):
    __slots__ = ("remote_actions_uri", "remote_results_uri_prefix")
    REMOTE_ACTIONS_URI_FIELD_NUMBER: _ClassVar[int]
    REMOTE_RESULTS_URI_PREFIX_FIELD_NUMBER: _ClassVar[int]
    remote_actions_uri: str
    remote_results_uri_prefix: str
    def __init__(
        self,
        remote_actions_uri: _Optional[str] = ...,
        remote_results_uri_prefix: _Optional[str] = ...,
    ) -> None: ...
