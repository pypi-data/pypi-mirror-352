from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TendonAnchor(_message.Message):
    __slots__ = ("anchorage_set", "comment", "generating_object_info", "is_generated", "name", "no", "type", "user_defined_name_enabled", "id_for_export_import", "metadata_for_export_import")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNKNOWN: _ClassVar[TendonAnchor.Type]
        TYPE_ACTIVE: _ClassVar[TendonAnchor.Type]
        TYPE_DEAD_END: _ClassVar[TendonAnchor.Type]
    TYPE_UNKNOWN: TendonAnchor.Type
    TYPE_ACTIVE: TendonAnchor.Type
    TYPE_DEAD_END: TendonAnchor.Type
    ANCHORAGE_SET_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    anchorage_set: float
    comment: str
    generating_object_info: str
    is_generated: bool
    name: str
    no: int
    type: TendonAnchor.Type
    user_defined_name_enabled: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, anchorage_set: _Optional[float] = ..., comment: _Optional[str] = ..., generating_object_info: _Optional[str] = ..., is_generated: bool = ..., name: _Optional[str] = ..., no: _Optional[int] = ..., type: _Optional[_Union[TendonAnchor.Type, str]] = ..., user_defined_name_enabled: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
