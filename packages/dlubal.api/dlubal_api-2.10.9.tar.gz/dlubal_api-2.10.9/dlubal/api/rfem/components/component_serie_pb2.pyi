from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ComponentSerie(_message.Message):
    __slots__ = ("category_function", "category_manufacturer", "category_material", "category_object_assignment", "category_standard_edition", "comment", "design_code_filename", "image_filename", "name", "no", "parameter_data_filename", "parameter_structure_filename", "user_defined", "user_defined_name_enabled", "visualization_filename", "id_for_export_import", "metadata_for_export_import")
    class CategoryObjectAssignment(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        CATEGORY_OBJECT_ASSIGNMENT_MEMBER_START_END: _ClassVar[ComponentSerie.CategoryObjectAssignment]
        CATEGORY_OBJECT_ASSIGNMENT_INVALID: _ClassVar[ComponentSerie.CategoryObjectAssignment]
        CATEGORY_OBJECT_ASSIGNMENT_MEMBER: _ClassVar[ComponentSerie.CategoryObjectAssignment]
        CATEGORY_OBJECT_ASSIGNMENT_MEMBER_X_LOCATION: _ClassVar[ComponentSerie.CategoryObjectAssignment]
    CATEGORY_OBJECT_ASSIGNMENT_MEMBER_START_END: ComponentSerie.CategoryObjectAssignment
    CATEGORY_OBJECT_ASSIGNMENT_INVALID: ComponentSerie.CategoryObjectAssignment
    CATEGORY_OBJECT_ASSIGNMENT_MEMBER: ComponentSerie.CategoryObjectAssignment
    CATEGORY_OBJECT_ASSIGNMENT_MEMBER_X_LOCATION: ComponentSerie.CategoryObjectAssignment
    CATEGORY_FUNCTION_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_MANUFACTURER_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_MATERIAL_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_OBJECT_ASSIGNMENT_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_STANDARD_EDITION_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    DESIGN_CODE_FILENAME_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FILENAME_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    PARAMETER_DATA_FILENAME_FIELD_NUMBER: _ClassVar[int]
    PARAMETER_STRUCTURE_FILENAME_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    VISUALIZATION_FILENAME_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    category_function: str
    category_manufacturer: str
    category_material: str
    category_object_assignment: ComponentSerie.CategoryObjectAssignment
    category_standard_edition: str
    comment: str
    design_code_filename: str
    image_filename: str
    name: str
    no: int
    parameter_data_filename: str
    parameter_structure_filename: str
    user_defined: bool
    user_defined_name_enabled: bool
    visualization_filename: str
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, category_function: _Optional[str] = ..., category_manufacturer: _Optional[str] = ..., category_material: _Optional[str] = ..., category_object_assignment: _Optional[_Union[ComponentSerie.CategoryObjectAssignment, str]] = ..., category_standard_edition: _Optional[str] = ..., comment: _Optional[str] = ..., design_code_filename: _Optional[str] = ..., image_filename: _Optional[str] = ..., name: _Optional[str] = ..., no: _Optional[int] = ..., parameter_data_filename: _Optional[str] = ..., parameter_structure_filename: _Optional[str] = ..., user_defined: bool = ..., user_defined_name_enabled: bool = ..., visualization_filename: _Optional[str] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...
