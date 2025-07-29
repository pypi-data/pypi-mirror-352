from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PileResistanceType(_message.Message):
    __slots__ = ("axial_stiffness", "axial_strength", "comment", "generating_object_info", "interface_strength_reduction", "is_generated", "members", "name", "no", "shear_stiffness_end", "shear_stiffness_start", "shear_strength_end", "shear_strength_start", "skin_resistance_type", "user_defined_name_enabled", "id_for_export_import", "metadata_for_export_import")
    class SkinResistanceType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SKIN_RESISTANCE_TYPE_TRAPEZOIDAL: _ClassVar[PileResistanceType.SkinResistanceType]
        SKIN_RESISTANCE_TYPE_VARYING: _ClassVar[PileResistanceType.SkinResistanceType]
    SKIN_RESISTANCE_TYPE_TRAPEZOIDAL: PileResistanceType.SkinResistanceType
    SKIN_RESISTANCE_TYPE_VARYING: PileResistanceType.SkinResistanceType
    AXIAL_STIFFNESS_FIELD_NUMBER: _ClassVar[int]
    AXIAL_STRENGTH_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    INTERFACE_STRENGTH_REDUCTION_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    SHEAR_STIFFNESS_END_FIELD_NUMBER: _ClassVar[int]
    SHEAR_STIFFNESS_START_FIELD_NUMBER: _ClassVar[int]
    SHEAR_STRENGTH_END_FIELD_NUMBER: _ClassVar[int]
    SHEAR_STRENGTH_START_FIELD_NUMBER: _ClassVar[int]
    SKIN_RESISTANCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    axial_stiffness: float
    axial_strength: float
    comment: str
    generating_object_info: str
    interface_strength_reduction: float
    is_generated: bool
    members: _containers.RepeatedScalarFieldContainer[int]
    name: str
    no: int
    shear_stiffness_end: float
    shear_stiffness_start: float
    shear_strength_end: float
    shear_strength_start: float
    skin_resistance_type: PileResistanceType.SkinResistanceType
    user_defined_name_enabled: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, axial_stiffness: _Optional[float] = ..., axial_strength: _Optional[float] = ..., comment: _Optional[str] = ..., generating_object_info: _Optional[str] = ..., interface_strength_reduction: _Optional[float] = ..., is_generated: bool = ..., members: _Optional[_Iterable[int]] = ..., name: _Optional[str] = ..., no: _Optional[int] = ..., shear_stiffness_end: _Optional[float] = ..., shear_stiffness_start: _Optional[float] = ..., shear_strength_end: _Optional[float] = ..., shear_strength_start: _Optional[float] = ..., skin_resistance_type: _Optional[_Union[PileResistanceType.SkinResistanceType, str]] = ..., user_defined_name_enabled: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
