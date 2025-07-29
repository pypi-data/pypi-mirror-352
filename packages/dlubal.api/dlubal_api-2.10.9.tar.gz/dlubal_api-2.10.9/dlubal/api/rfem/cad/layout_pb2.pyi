from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Layout(_message.Message):
    __slots__ = ("comment", "generating_object_info", "is_generated", "length", "name", "no", "size_type", "type", "user_defined_name_enabled", "width", "id_for_export_import", "metadata_for_export_import")
    class SizeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SIZE_TYPE_A0: _ClassVar[Layout.SizeType]
        SIZE_TYPE_A1: _ClassVar[Layout.SizeType]
        SIZE_TYPE_A2: _ClassVar[Layout.SizeType]
        SIZE_TYPE_A3_LANDSCAPE: _ClassVar[Layout.SizeType]
        SIZE_TYPE_A3_PORTRAIT: _ClassVar[Layout.SizeType]
        SIZE_TYPE_A4_LANDSCAPE: _ClassVar[Layout.SizeType]
        SIZE_TYPE_A4_PORTRAIT: _ClassVar[Layout.SizeType]
        SIZE_TYPE_CUSTOM: _ClassVar[Layout.SizeType]
    SIZE_TYPE_A0: Layout.SizeType
    SIZE_TYPE_A1: Layout.SizeType
    SIZE_TYPE_A2: Layout.SizeType
    SIZE_TYPE_A3_LANDSCAPE: Layout.SizeType
    SIZE_TYPE_A3_PORTRAIT: Layout.SizeType
    SIZE_TYPE_A4_LANDSCAPE: Layout.SizeType
    SIZE_TYPE_A4_PORTRAIT: Layout.SizeType
    SIZE_TYPE_CUSTOM: Layout.SizeType
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNKNOWN: _ClassVar[Layout.Type]
        TYPE_STANDARD: _ClassVar[Layout.Type]
    TYPE_UNKNOWN: Layout.Type
    TYPE_STANDARD: Layout.Type
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    SIZE_TYPE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    comment: str
    generating_object_info: str
    is_generated: bool
    length: int
    name: str
    no: int
    size_type: Layout.SizeType
    type: Layout.Type
    user_defined_name_enabled: bool
    width: int
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, comment: _Optional[str] = ..., generating_object_info: _Optional[str] = ..., is_generated: bool = ..., length: _Optional[int] = ..., name: _Optional[str] = ..., no: _Optional[int] = ..., size_type: _Optional[_Union[Layout.SizeType, str]] = ..., type: _Optional[_Union[Layout.Type, str]] = ..., user_defined_name_enabled: bool = ..., width: _Optional[int] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
