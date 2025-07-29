from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class DiagonalBrace(_message.Message):
    __slots__ = ("comment", "deep_beams", "generating_object_info", "is_generated", "member_sets", "members", "name", "no", "shear_walls", "user_defined_name_enabled", "id_for_export_import", "metadata_for_export_import")
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    DEEP_BEAMS_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    MEMBER_SETS_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    SHEAR_WALLS_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    comment: str
    deep_beams: _containers.RepeatedScalarFieldContainer[int]
    generating_object_info: str
    is_generated: bool
    member_sets: _containers.RepeatedScalarFieldContainer[int]
    members: _containers.RepeatedScalarFieldContainer[int]
    name: str
    no: int
    shear_walls: _containers.RepeatedScalarFieldContainer[int]
    user_defined_name_enabled: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, comment: _Optional[str] = ..., deep_beams: _Optional[_Iterable[int]] = ..., generating_object_info: _Optional[str] = ..., is_generated: bool = ..., member_sets: _Optional[_Iterable[int]] = ..., members: _Optional[_Iterable[int]] = ..., name: _Optional[str] = ..., no: _Optional[int] = ..., shear_walls: _Optional[_Iterable[int]] = ..., user_defined_name_enabled: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
