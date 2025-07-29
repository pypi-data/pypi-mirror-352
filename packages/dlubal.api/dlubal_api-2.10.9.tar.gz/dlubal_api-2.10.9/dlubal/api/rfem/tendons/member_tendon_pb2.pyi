from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MemberTendon(_message.Message):
    __slots__ = ("area", "comment", "generating_object_info", "is_generated", "length", "material", "member_sets", "members", "name", "no", "section", "tendon_anchor_end", "tendon_anchor_start", "tendon_type", "type", "user_defined_name_enabled", "id_for_export_import", "metadata_for_export_import")
    class TendonType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TENDON_TYPE_REINFORCEMENT: _ClassVar[MemberTendon.TendonType]
        TENDON_TYPE_POSTTENSIONED_BONDED: _ClassVar[MemberTendon.TendonType]
        TENDON_TYPE_POSTTENSIONED_UNBONDED: _ClassVar[MemberTendon.TendonType]
        TENDON_TYPE_PRETENSIONED: _ClassVar[MemberTendon.TendonType]
    TENDON_TYPE_REINFORCEMENT: MemberTendon.TendonType
    TENDON_TYPE_POSTTENSIONED_BONDED: MemberTendon.TendonType
    TENDON_TYPE_POSTTENSIONED_UNBONDED: MemberTendon.TendonType
    TENDON_TYPE_PRETENSIONED: MemberTendon.TendonType
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_UNKNOWN: _ClassVar[MemberTendon.Type]
        TYPE_STANDARD: _ClassVar[MemberTendon.Type]
    TYPE_UNKNOWN: MemberTendon.Type
    TYPE_STANDARD: MemberTendon.Type
    AREA_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    MATERIAL_FIELD_NUMBER: _ClassVar[int]
    MEMBER_SETS_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    SECTION_FIELD_NUMBER: _ClassVar[int]
    TENDON_ANCHOR_END_FIELD_NUMBER: _ClassVar[int]
    TENDON_ANCHOR_START_FIELD_NUMBER: _ClassVar[int]
    TENDON_TYPE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    area: float
    comment: str
    generating_object_info: str
    is_generated: bool
    length: float
    material: int
    member_sets: _containers.RepeatedScalarFieldContainer[int]
    members: _containers.RepeatedScalarFieldContainer[int]
    name: str
    no: int
    section: int
    tendon_anchor_end: int
    tendon_anchor_start: int
    tendon_type: MemberTendon.TendonType
    type: MemberTendon.Type
    user_defined_name_enabled: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, area: _Optional[float] = ..., comment: _Optional[str] = ..., generating_object_info: _Optional[str] = ..., is_generated: bool = ..., length: _Optional[float] = ..., material: _Optional[int] = ..., member_sets: _Optional[_Iterable[int]] = ..., members: _Optional[_Iterable[int]] = ..., name: _Optional[str] = ..., no: _Optional[int] = ..., section: _Optional[int] = ..., tendon_anchor_end: _Optional[int] = ..., tendon_anchor_start: _Optional[int] = ..., tendon_type: _Optional[_Union[MemberTendon.TendonType, str]] = ..., type: _Optional[_Union[MemberTendon.Type, str]] = ..., user_defined_name_enabled: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
