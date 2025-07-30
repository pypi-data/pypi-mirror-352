from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import (
    ClassVar as _ClassVar,
    Mapping as _Mapping,
    Optional as _Optional,
    Union as _Union,
)

DESCRIPTOR: _descriptor.FileDescriptor

class WriteMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    WRITE_MODE_UNSPECIFIED: _ClassVar[WriteMode]
    WRITE_MODE_ERROR: _ClassVar[WriteMode]
    WRITE_MODE_APPEND: _ClassVar[WriteMode]
    WRITE_MODE_OVERWRITE: _ClassVar[WriteMode]
    WRITE_MODE_IGNORE: _ClassVar[WriteMode]

WRITE_MODE_UNSPECIFIED: WriteMode
WRITE_MODE_ERROR: WriteMode
WRITE_MODE_APPEND: WriteMode
WRITE_MODE_OVERWRITE: WriteMode
WRITE_MODE_IGNORE: WriteMode

class TableIdentifier(_message.Message):
    __slots__ = ("catalog", "schema", "table")
    CATALOG_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    TABLE_FIELD_NUMBER: _ClassVar[int]
    catalog: str
    schema: str
    table: str
    def __init__(
        self,
        catalog: _Optional[str] = ...,
        schema: _Optional[str] = ...,
        table: _Optional[str] = ...,
    ) -> None: ...

class CollectExecutionRequest(_message.Message):
    __slots__ = ("serialized_plan",)
    SERIALIZED_PLAN_FIELD_NUMBER: _ClassVar[int]
    serialized_plan: bytes
    def __init__(self, serialized_plan: _Optional[bytes] = ...) -> None: ...

class CountExecutionRequest(_message.Message):
    __slots__ = ("serialized_plan",)
    SERIALIZED_PLAN_FIELD_NUMBER: _ClassVar[int]
    serialized_plan: bytes
    def __init__(self, serialized_plan: _Optional[bytes] = ...) -> None: ...

class ShowExecutionRequest(_message.Message):
    __slots__ = ("serialized_plan", "row_limit")
    SERIALIZED_PLAN_FIELD_NUMBER: _ClassVar[int]
    ROW_LIMIT_FIELD_NUMBER: _ClassVar[int]
    serialized_plan: bytes
    row_limit: int
    def __init__(
        self, serialized_plan: _Optional[bytes] = ..., row_limit: _Optional[int] = ...
    ) -> None: ...

class SaveAsTableExecutionRequest(_message.Message):
    __slots__ = ("serialized_plan", "table_identifier", "mode")
    SERIALIZED_PLAN_FIELD_NUMBER: _ClassVar[int]
    TABLE_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    serialized_plan: bytes
    table_identifier: TableIdentifier
    mode: str
    def __init__(
        self,
        serialized_plan: _Optional[bytes] = ...,
        table_identifier: _Optional[_Union[TableIdentifier, _Mapping]] = ...,
        mode: _Optional[str] = ...,
    ) -> None: ...

class SaveToFileExecutionRequest(_message.Message):
    __slots__ = ("serialized_plan", "file_path", "mode")
    SERIALIZED_PLAN_FIELD_NUMBER: _ClassVar[int]
    FILE_PATH_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    serialized_plan: bytes
    file_path: str
    mode: str
    def __init__(
        self,
        serialized_plan: _Optional[bytes] = ...,
        file_path: _Optional[str] = ...,
        mode: _Optional[str] = ...,
    ) -> None: ...

class ConfigSessionRequest(_message.Message):
    __slots__ = ("session_config",)
    SESSION_CONFIG_FIELD_NUMBER: _ClassVar[int]
    session_config: bytes
    def __init__(self, session_config: _Optional[bytes] = ...) -> None: ...

class StartExecutionRequest(_message.Message):
    __slots__ = ("collect", "count", "show", "save_as_table", "save_to_file")
    COLLECT_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    SHOW_FIELD_NUMBER: _ClassVar[int]
    SAVE_AS_TABLE_FIELD_NUMBER: _ClassVar[int]
    SAVE_TO_FILE_FIELD_NUMBER: _ClassVar[int]
    collect: CollectExecutionRequest
    count: CountExecutionRequest
    show: ShowExecutionRequest
    save_as_table: SaveAsTableExecutionRequest
    save_to_file: SaveToFileExecutionRequest
    def __init__(
        self,
        collect: _Optional[_Union[CollectExecutionRequest, _Mapping]] = ...,
        count: _Optional[_Union[CountExecutionRequest, _Mapping]] = ...,
        show: _Optional[_Union[ShowExecutionRequest, _Mapping]] = ...,
        save_as_table: _Optional[_Union[SaveAsTableExecutionRequest, _Mapping]] = ...,
        save_to_file: _Optional[_Union[SaveToFileExecutionRequest, _Mapping]] = ...,
    ) -> None: ...

class InferSchemaFromCSVRequest(_message.Message):
    __slots__ = ("file_list", "merge_schemas", "schema")
    FILE_LIST_FIELD_NUMBER: _ClassVar[int]
    MERGE_SCHEMAS_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    file_list: str
    merge_schemas: bool
    schema: str
    def __init__(
        self,
        file_list: _Optional[str] = ...,
        merge_schemas: bool = ...,
        schema: _Optional[str] = ...,
    ) -> None: ...

class InferSchemaFromParquetRequest(_message.Message):
    __slots__ = ("file_list", "merge_schemas")
    FILE_LIST_FIELD_NUMBER: _ClassVar[int]
    MERGE_SCHEMAS_FIELD_NUMBER: _ClassVar[int]
    file_list: str
    merge_schemas: bool
    def __init__(
        self, file_list: _Optional[str] = ..., merge_schemas: bool = ...
    ) -> None: ...

class InferSchemaRequest(_message.Message):
    __slots__ = ("infer_schema_from_csv", "infer_schema_from_parquet")
    INFER_SCHEMA_FROM_CSV_FIELD_NUMBER: _ClassVar[int]
    INFER_SCHEMA_FROM_PARQUET_FIELD_NUMBER: _ClassVar[int]
    infer_schema_from_csv: InferSchemaFromCSVRequest
    infer_schema_from_parquet: InferSchemaFromParquetRequest
    def __init__(
        self,
        infer_schema_from_csv: _Optional[
            _Union[InferSchemaFromCSVRequest, _Mapping]
        ] = ...,
        infer_schema_from_parquet: _Optional[
            _Union[InferSchemaFromParquetRequest, _Mapping]
        ] = ...,
    ) -> None: ...

class InferSchemaResponse(_message.Message):
    __slots__ = ("schema",)
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    schema: str
    def __init__(self, schema: _Optional[str] = ...) -> None: ...

class CancelExecutionRequest(_message.Message):
    __slots__ = ("execution_uuid",)
    EXECUTION_UUID_FIELD_NUMBER: _ClassVar[int]
    execution_uuid: str
    def __init__(self, execution_uuid: _Optional[str] = ...) -> None: ...

class GetExecutionResultRequest(_message.Message):
    __slots__ = ("execution_uuid",)
    EXECUTION_UUID_FIELD_NUMBER: _ClassVar[int]
    execution_uuid: str
    def __init__(self, execution_uuid: _Optional[str] = ...) -> None: ...

class ConfigSessionResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StartExecutionResponse(_message.Message):
    __slots__ = ("execution_id",)
    EXECUTION_ID_FIELD_NUMBER: _ClassVar[int]
    execution_id: str
    def __init__(self, execution_id: _Optional[str] = ...) -> None: ...

class GetExecutionResultResponse(_message.Message):
    __slots__ = ("show_result", "count_result")
    SHOW_RESULT_FIELD_NUMBER: _ClassVar[int]
    COUNT_RESULT_FIELD_NUMBER: _ClassVar[int]
    show_result: str
    count_result: int
    def __init__(
        self, show_result: _Optional[str] = ..., count_result: _Optional[int] = ...
    ) -> None: ...

class CancelExecutionResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
