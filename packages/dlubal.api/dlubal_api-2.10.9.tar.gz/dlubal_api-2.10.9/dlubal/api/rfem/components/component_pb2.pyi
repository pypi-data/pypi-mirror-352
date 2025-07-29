from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Component(_message.Message):
    __slots__ = ("comment", "component_on_member_end_longitudinal_alignment", "component_on_member_end_longitudinal_offset", "component_on_member_end_rotation_angle_0", "component_on_member_end_rotation_angle_1", "component_on_member_end_rotation_angle_2", "component_on_member_end_rotation_sequence", "component_on_member_end_section_point", "component_on_member_end_section_point_y_offset", "component_on_member_end_section_point_z_offset", "component_series", "component_snap_point_number", "component_snap_point_offset_y", "component_snap_point_offset_z", "name", "no", "type", "user_defined", "user_defined_name_enabled", "id_for_export_import", "metadata_for_export_import")
    class ComponentOnMemberEndLongitudinalAlignment(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        COMPONENT_ON_MEMBER_END_LONGITUDINAL_ALIGNMENT_LEFT: _ClassVar[Component.ComponentOnMemberEndLongitudinalAlignment]
        COMPONENT_ON_MEMBER_END_LONGITUDINAL_ALIGNMENT_CENTER: _ClassVar[Component.ComponentOnMemberEndLongitudinalAlignment]
        COMPONENT_ON_MEMBER_END_LONGITUDINAL_ALIGNMENT_RIGHT: _ClassVar[Component.ComponentOnMemberEndLongitudinalAlignment]
    COMPONENT_ON_MEMBER_END_LONGITUDINAL_ALIGNMENT_LEFT: Component.ComponentOnMemberEndLongitudinalAlignment
    COMPONENT_ON_MEMBER_END_LONGITUDINAL_ALIGNMENT_CENTER: Component.ComponentOnMemberEndLongitudinalAlignment
    COMPONENT_ON_MEMBER_END_LONGITUDINAL_ALIGNMENT_RIGHT: Component.ComponentOnMemberEndLongitudinalAlignment
    class ComponentOnMemberEndRotationSequence(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        COMPONENT_ON_MEMBER_END_ROTATION_SEQUENCE_XYZ: _ClassVar[Component.ComponentOnMemberEndRotationSequence]
        COMPONENT_ON_MEMBER_END_ROTATION_SEQUENCE_XZY: _ClassVar[Component.ComponentOnMemberEndRotationSequence]
        COMPONENT_ON_MEMBER_END_ROTATION_SEQUENCE_YXZ: _ClassVar[Component.ComponentOnMemberEndRotationSequence]
        COMPONENT_ON_MEMBER_END_ROTATION_SEQUENCE_YZX: _ClassVar[Component.ComponentOnMemberEndRotationSequence]
        COMPONENT_ON_MEMBER_END_ROTATION_SEQUENCE_ZXY: _ClassVar[Component.ComponentOnMemberEndRotationSequence]
        COMPONENT_ON_MEMBER_END_ROTATION_SEQUENCE_ZYX: _ClassVar[Component.ComponentOnMemberEndRotationSequence]
    COMPONENT_ON_MEMBER_END_ROTATION_SEQUENCE_XYZ: Component.ComponentOnMemberEndRotationSequence
    COMPONENT_ON_MEMBER_END_ROTATION_SEQUENCE_XZY: Component.ComponentOnMemberEndRotationSequence
    COMPONENT_ON_MEMBER_END_ROTATION_SEQUENCE_YXZ: Component.ComponentOnMemberEndRotationSequence
    COMPONENT_ON_MEMBER_END_ROTATION_SEQUENCE_YZX: Component.ComponentOnMemberEndRotationSequence
    COMPONENT_ON_MEMBER_END_ROTATION_SEQUENCE_ZXY: Component.ComponentOnMemberEndRotationSequence
    COMPONENT_ON_MEMBER_END_ROTATION_SEQUENCE_ZYX: Component.ComponentOnMemberEndRotationSequence
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TYPE_PHANTOM: _ClassVar[Component.Type]
        TYPE_STANDARD: _ClassVar[Component.Type]
    TYPE_PHANTOM: Component.Type
    TYPE_STANDARD: Component.Type
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    COMPONENT_ON_MEMBER_END_LONGITUDINAL_ALIGNMENT_FIELD_NUMBER: _ClassVar[int]
    COMPONENT_ON_MEMBER_END_LONGITUDINAL_OFFSET_FIELD_NUMBER: _ClassVar[int]
    COMPONENT_ON_MEMBER_END_ROTATION_ANGLE_0_FIELD_NUMBER: _ClassVar[int]
    COMPONENT_ON_MEMBER_END_ROTATION_ANGLE_1_FIELD_NUMBER: _ClassVar[int]
    COMPONENT_ON_MEMBER_END_ROTATION_ANGLE_2_FIELD_NUMBER: _ClassVar[int]
    COMPONENT_ON_MEMBER_END_ROTATION_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    COMPONENT_ON_MEMBER_END_SECTION_POINT_FIELD_NUMBER: _ClassVar[int]
    COMPONENT_ON_MEMBER_END_SECTION_POINT_Y_OFFSET_FIELD_NUMBER: _ClassVar[int]
    COMPONENT_ON_MEMBER_END_SECTION_POINT_Z_OFFSET_FIELD_NUMBER: _ClassVar[int]
    COMPONENT_SERIES_FIELD_NUMBER: _ClassVar[int]
    COMPONENT_SNAP_POINT_NUMBER_FIELD_NUMBER: _ClassVar[int]
    COMPONENT_SNAP_POINT_OFFSET_Y_FIELD_NUMBER: _ClassVar[int]
    COMPONENT_SNAP_POINT_OFFSET_Z_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    comment: str
    component_on_member_end_longitudinal_alignment: Component.ComponentOnMemberEndLongitudinalAlignment
    component_on_member_end_longitudinal_offset: float
    component_on_member_end_rotation_angle_0: float
    component_on_member_end_rotation_angle_1: float
    component_on_member_end_rotation_angle_2: float
    component_on_member_end_rotation_sequence: Component.ComponentOnMemberEndRotationSequence
    component_on_member_end_section_point: int
    component_on_member_end_section_point_y_offset: float
    component_on_member_end_section_point_z_offset: float
    component_series: int
    component_snap_point_number: int
    component_snap_point_offset_y: float
    component_snap_point_offset_z: float
    name: str
    no: int
    type: Component.Type
    user_defined: bool
    user_defined_name_enabled: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, comment: _Optional[str] = ..., component_on_member_end_longitudinal_alignment: _Optional[_Union[Component.ComponentOnMemberEndLongitudinalAlignment, str]] = ..., component_on_member_end_longitudinal_offset: _Optional[float] = ..., component_on_member_end_rotation_angle_0: _Optional[float] = ..., component_on_member_end_rotation_angle_1: _Optional[float] = ..., component_on_member_end_rotation_angle_2: _Optional[float] = ..., component_on_member_end_rotation_sequence: _Optional[_Union[Component.ComponentOnMemberEndRotationSequence, str]] = ..., component_on_member_end_section_point: _Optional[int] = ..., component_on_member_end_section_point_y_offset: _Optional[float] = ..., component_on_member_end_section_point_z_offset: _Optional[float] = ..., component_series: _Optional[int] = ..., component_snap_point_number: _Optional[int] = ..., component_snap_point_offset_y: _Optional[float] = ..., component_snap_point_offset_z: _Optional[float] = ..., name: _Optional[str] = ..., no: _Optional[int] = ..., type: _Optional[_Union[Component.Type, str]] = ..., user_defined: bool = ..., user_defined_name_enabled: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
