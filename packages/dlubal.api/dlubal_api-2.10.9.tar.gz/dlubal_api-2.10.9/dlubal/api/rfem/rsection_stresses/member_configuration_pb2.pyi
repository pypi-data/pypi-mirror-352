from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MemberConfiguration(_message.Message):
    __slots__ = ("assigned_to_deep_beams", "assigned_to_member_sets", "assigned_to_members", "assigned_to_shear_walls", "comment", "name", "no", "special_settings", "user_defined_name_enabled", "id_for_export_import", "metadata_for_export_import")
    class SpecialSettingsTable(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    ASSIGNED_TO_DEEP_BEAMS_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_MEMBER_SETS_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_MEMBERS_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_TO_SHEAR_WALLS_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    SPECIAL_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    assigned_to_deep_beams: _containers.RepeatedScalarFieldContainer[int]
    assigned_to_member_sets: _containers.RepeatedScalarFieldContainer[int]
    assigned_to_members: _containers.RepeatedScalarFieldContainer[int]
    assigned_to_shear_walls: _containers.RepeatedScalarFieldContainer[int]
    comment: str
    name: str
    no: int
    special_settings: MemberConfiguration.SpecialSettingsTable
    user_defined_name_enabled: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, assigned_to_deep_beams: _Optional[_Iterable[int]] = ..., assigned_to_member_sets: _Optional[_Iterable[int]] = ..., assigned_to_members: _Optional[_Iterable[int]] = ..., assigned_to_shear_walls: _Optional[_Iterable[int]] = ..., comment: _Optional[str] = ..., name: _Optional[str] = ..., no: _Optional[int] = ..., special_settings: _Optional[_Union[MemberConfiguration.SpecialSettingsTable, _Mapping]] = ..., user_defined_name_enabled: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
