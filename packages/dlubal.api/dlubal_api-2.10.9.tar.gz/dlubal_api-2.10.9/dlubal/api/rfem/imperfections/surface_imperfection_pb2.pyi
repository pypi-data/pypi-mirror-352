from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SurfaceImperfection(_message.Message):
    __slots__ = ("no", "definition_type", "imperfection_case", "imperfection_direction", "initial_bow", "initial_bow_relative", "parameters", "reference_length", "surfaces", "comment", "is_generated", "generating_object_info", "id_for_export_import", "metadata_for_export_import")
    class DefinitionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DEFINITION_TYPE_RELATIVE: _ClassVar[SurfaceImperfection.DefinitionType]
        DEFINITION_TYPE_ABSOLUTE: _ClassVar[SurfaceImperfection.DefinitionType]
    DEFINITION_TYPE_RELATIVE: SurfaceImperfection.DefinitionType
    DEFINITION_TYPE_ABSOLUTE: SurfaceImperfection.DefinitionType
    class ImperfectionDirection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        IMPERFECTION_DIRECTION_UNKNOWN: _ClassVar[SurfaceImperfection.ImperfectionDirection]
        IMPERFECTION_DIRECTION_LOCAL_Z: _ClassVar[SurfaceImperfection.ImperfectionDirection]
        IMPERFECTION_DIRECTION_LOCAL_Z_NEGATIVE: _ClassVar[SurfaceImperfection.ImperfectionDirection]
    IMPERFECTION_DIRECTION_UNKNOWN: SurfaceImperfection.ImperfectionDirection
    IMPERFECTION_DIRECTION_LOCAL_Z: SurfaceImperfection.ImperfectionDirection
    IMPERFECTION_DIRECTION_LOCAL_Z_NEGATIVE: SurfaceImperfection.ImperfectionDirection
    NO_FIELD_NUMBER: _ClassVar[int]
    DEFINITION_TYPE_FIELD_NUMBER: _ClassVar[int]
    IMPERFECTION_CASE_FIELD_NUMBER: _ClassVar[int]
    IMPERFECTION_DIRECTION_FIELD_NUMBER: _ClassVar[int]
    INITIAL_BOW_FIELD_NUMBER: _ClassVar[int]
    INITIAL_BOW_RELATIVE_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_LENGTH_FIELD_NUMBER: _ClassVar[int]
    SURFACES_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATED_FIELD_NUMBER: _ClassVar[int]
    GENERATING_OBJECT_INFO_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    no: int
    definition_type: SurfaceImperfection.DefinitionType
    imperfection_case: int
    imperfection_direction: SurfaceImperfection.ImperfectionDirection
    initial_bow: float
    initial_bow_relative: float
    parameters: _containers.RepeatedScalarFieldContainer[int]
    reference_length: float
    surfaces: _containers.RepeatedScalarFieldContainer[int]
    comment: str
    is_generated: bool
    generating_object_info: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, no: _Optional[int] = ..., definition_type: _Optional[_Union[SurfaceImperfection.DefinitionType, str]] = ..., imperfection_case: _Optional[int] = ..., imperfection_direction: _Optional[_Union[SurfaceImperfection.ImperfectionDirection, str]] = ..., initial_bow: _Optional[float] = ..., initial_bow_relative: _Optional[float] = ..., parameters: _Optional[_Iterable[int]] = ..., reference_length: _Optional[float] = ..., surfaces: _Optional[_Iterable[int]] = ..., comment: _Optional[str] = ..., is_generated: bool = ..., generating_object_info: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
