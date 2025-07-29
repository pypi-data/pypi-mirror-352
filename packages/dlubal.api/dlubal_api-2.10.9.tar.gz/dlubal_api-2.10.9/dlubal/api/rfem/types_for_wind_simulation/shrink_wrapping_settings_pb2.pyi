from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ShrinkWrappingSettings(_message.Message):
    __slots__ = ("assigned_ifc_objects", "assigned_members", "assigned_solids", "assigned_surfaces", "assigned_visual_objects", "closure_real_size", "closure_relative_to_model_parameter", "comment", "detail_size", "level_of_detail", "name", "no", "orient_normals_for_surface_results", "simplification_defined_by", "small_openings_closure_type", "user_defined_name_enabled", "id_for_export_import", "metadata_for_export_import")
    class SimplificationDefinedBy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SIMPLIFICATION_DEFINED_BY_LEVEL_OF_DETAILS: _ClassVar[ShrinkWrappingSettings.SimplificationDefinedBy]
        SIMPLIFICATION_DEFINED_BY_DETAIL_SIZE: _ClassVar[ShrinkWrappingSettings.SimplificationDefinedBy]
    SIMPLIFICATION_DEFINED_BY_LEVEL_OF_DETAILS: ShrinkWrappingSettings.SimplificationDefinedBy
    SIMPLIFICATION_DEFINED_BY_DETAIL_SIZE: ShrinkWrappingSettings.SimplificationDefinedBy
    class SmallOpeningsClosureType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SMALL_OPENINGS_CLOSURE_TYPE_PERCENT_OF_MODEL_DIAMETER: _ClassVar[ShrinkWrappingSettings.SmallOpeningsClosureType]
        SMALL_OPENINGS_CLOSURE_TYPE_REAL_SIZE: _ClassVar[ShrinkWrappingSettings.SmallOpeningsClosureType]
    SMALL_OPENINGS_CLOSURE_TYPE_PERCENT_OF_MODEL_DIAMETER: ShrinkWrappingSettings.SmallOpeningsClosureType
    SMALL_OPENINGS_CLOSURE_TYPE_REAL_SIZE: ShrinkWrappingSettings.SmallOpeningsClosureType
    ASSIGNED_IFC_OBJECTS_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_MEMBERS_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_SOLIDS_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_SURFACES_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_VISUAL_OBJECTS_FIELD_NUMBER: _ClassVar[int]
    CLOSURE_REAL_SIZE_FIELD_NUMBER: _ClassVar[int]
    CLOSURE_RELATIVE_TO_MODEL_PARAMETER_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    DETAIL_SIZE_FIELD_NUMBER: _ClassVar[int]
    LEVEL_OF_DETAIL_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    ORIENT_NORMALS_FOR_SURFACE_RESULTS_FIELD_NUMBER: _ClassVar[int]
    SIMPLIFICATION_DEFINED_BY_FIELD_NUMBER: _ClassVar[int]
    SMALL_OPENINGS_CLOSURE_TYPE_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    assigned_ifc_objects: _containers.RepeatedScalarFieldContainer[int]
    assigned_members: _containers.RepeatedScalarFieldContainer[int]
    assigned_solids: _containers.RepeatedScalarFieldContainer[int]
    assigned_surfaces: _containers.RepeatedScalarFieldContainer[int]
    assigned_visual_objects: _containers.RepeatedScalarFieldContainer[int]
    closure_real_size: float
    closure_relative_to_model_parameter: float
    comment: str
    detail_size: float
    level_of_detail: int
    name: str
    no: int
    orient_normals_for_surface_results: bool
    simplification_defined_by: ShrinkWrappingSettings.SimplificationDefinedBy
    small_openings_closure_type: ShrinkWrappingSettings.SmallOpeningsClosureType
    user_defined_name_enabled: bool
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, assigned_ifc_objects: _Optional[_Iterable[int]] = ..., assigned_members: _Optional[_Iterable[int]] = ..., assigned_solids: _Optional[_Iterable[int]] = ..., assigned_surfaces: _Optional[_Iterable[int]] = ..., assigned_visual_objects: _Optional[_Iterable[int]] = ..., closure_real_size: _Optional[float] = ..., closure_relative_to_model_parameter: _Optional[float] = ..., comment: _Optional[str] = ..., detail_size: _Optional[float] = ..., level_of_detail: _Optional[int] = ..., name: _Optional[str] = ..., no: _Optional[int] = ..., orient_normals_for_surface_results: bool = ..., simplification_defined_by: _Optional[_Union[ShrinkWrappingSettings.SimplificationDefinedBy, str]] = ..., small_openings_closure_type: _Optional[_Union[ShrinkWrappingSettings.SmallOpeningsClosureType, str]] = ..., user_defined_name_enabled: bool = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
