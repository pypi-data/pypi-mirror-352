from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LoadModel(_message.Message):
    __slots__ = ("comment", "load_components", "name", "no", "type", "user_defined_name_enabled", "id_for_export_import", "metadata_for_export_import")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNKNOWN: _ClassVar[LoadModel.Type]
        TYPE_ON_MEMBERS: _ClassVar[LoadModel.Type]
        TYPE_ON_SURFACES: _ClassVar[LoadModel.Type]
    TYPE_UNKNOWN: LoadModel.Type
    TYPE_ON_MEMBERS: LoadModel.Type
    TYPE_ON_SURFACES: LoadModel.Type
    class LoadComponentsTable(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    LOAD_COMPONENTS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    comment: str
    load_components: LoadModel.LoadComponentsTable
    name: str
    no: int
    type: LoadModel.Type
    user_defined_name_enabled: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, comment: _Optional[str] = ..., load_components: _Optional[_Union[LoadModel.LoadComponentsTable, _Mapping]] = ..., name: _Optional[str] = ..., no: _Optional[int] = ..., type: _Optional[_Union[LoadModel.Type, str]] = ..., user_defined_name_enabled: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
