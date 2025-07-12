from typing import Any, Union, get_origin, get_args
from types import UnionType
from pydantic import BaseModel
from .types import MediaImageDocument, BasePopulatable


def get_model_fields_and_population(model_class: type[BaseModel]) -> tuple[list[str], dict[str, Any]]:
    """
    Recursively scans class fields and returns fields and populate structure for Strapi API.
    Uses pydantic aliases when available, otherwise field names.

    Returns:
        tuple[list[str], Dict[str, Any]]: (fields_list, populate_dict)

    fields_list: Contains scalar field names for the root model
    populate_dict: Contains nested structure with relations and their fields

    Example result:
    fields = ['title', 'slug']
    populate = {
        'headerImage': {
            'fields': ['name', 'url']
        },
        'category': {
            'fields': ['name'],
            'populate': {
                'icon': {
                    'fields': ['url', 'name']
                }
            }
        }
    }
    """
    processor = _ModelFieldProcessor()
    return processor.process_model(model_class)


class _ModelFieldProcessor:
    """Internal class to handle model field processing with state management."""

    def __init__(self) -> None:
        # Track visited classes to prevent infinite recursion
        # when there are circular references between models
        self._visited_classes: set[type] = set()

    def process_model(self, model_class: type[BaseModel]) -> tuple[list[str], dict[str, Any]]:
        """Process the root model and return fields and populate structure."""
        root_fields: list[str] = []
        populate_dict: dict[str, Any] = {}

        # Get field metadata from pydantic model
        model_fields = getattr(model_class, 'model_fields', {})

        for field_name, field_info in model_fields.items():
            field_type = self._extract_field_type(field_info.annotation)
            actual_field_name = self._get_field_name(field_name, field_info)

            # Scalar fields go to the main fields list
            if self._is_scalar_type(field_type):
                root_fields.append(actual_field_name)
            # Related documents go to the populate structure
            elif self._is_populatable_entry(field_type):
                populate_dict[actual_field_name] = self._get_populate_structure(field_type)

        return root_fields, populate_dict

    def _extract_field_type(self, field_type: Any) -> Any:
        """
        Extract the actual field type, handling Union, Optional and List types.

        Examples:
        - Optional[str] -> str
        - List[Category] -> Category
        - Union[str, None] -> str
        - list[Category] | None -> Category
        """
        # Handle new Union syntax (Python 3.10+): str | None
        if isinstance(field_type, UnionType):
            args = get_args(field_type)
            # For Union types - choose the first non-None type
            if args:
                non_none_types = [arg for arg in args if arg is not type(None)]
                if non_none_types:
                    # После получения не-None типа, проверяем если это контейнер
                    first_non_none = non_none_types[0]
                    origin = get_origin(first_non_none)
                    inner_args = get_args(first_non_none)

                    # Handle containers: List[T], Tuple[T], Set[T] -> T
                    if origin in (list, tuple, set) and inner_args:
                        return inner_args[0]

                    return first_non_none
        else:
            origin = get_origin(field_type)
            args = get_args(field_type)

            # If not a generic type, return as is
            if origin is None:
                return field_type

            # Handle containers: List[T], Tuple[T], Set[T] -> T
            if origin in (list, tuple, set) and args:
                return args[0]

            # For Union types (including Optional) - choose the first non-None type
            if origin is Union and args:
                non_none_types = [arg for arg in args if arg is not type(None)]
                if non_none_types:
                    # После получения не-None типа, проверяем если это контейнер
                    first_non_none = non_none_types[0]
                    inner_origin = get_origin(first_non_none)
                    inner_args = get_args(first_non_none)

                    # Handle containers: List[T], Tuple[T], Set[T] -> T
                    if inner_origin in (list, tuple, set) and inner_args:
                        return inner_args[0]

                    return first_non_none

        return field_type

    def _is_populatable_entry(self, field_type: Any) -> bool:
        """
        Check if the type is a subclass of BasePopulatable.
        This indicates that the field represents a relation to another Strapi entity.
        """
        try:
            return (isinstance(field_type, type) and
                    issubclass(field_type, BasePopulatable) and
                    field_type is not BasePopulatable)
        except (TypeError, AttributeError):
            return False

    def _is_media_image_document(self, field_type: Any) -> bool:
        """
        Check if the type is MediaImageDocument.
        Media files in Strapi have special handling - they only need populate: true.
        """
        try:
            return (isinstance(field_type, type) and
                    issubclass(field_type, MediaImageDocument))
        except (TypeError, AttributeError):
            return False

    def _is_scalar_type(self, field_type: Any) -> bool:
        """
        Check if the type is scalar (string, number, boolean, etc.).
        Scalar fields don't require populate and go directly to the fields list.
        """
        return not self._is_populatable_entry(field_type)

    def _get_field_name(self, field_name: str, field_info: Any) -> str:
        """
        Return field name for Strapi API.
        Priority: pydantic alias -> original field name.
        """
        return getattr(field_info, 'alias', None) or field_name

    def _get_populate_structure(self, field_type: type) -> dict[str, Any] | bool:
        """
        Generate populate structure for a relation field.

        For media files returns True (simple populate).
        For other documents - nested structure with fields and their relations.
        """
        # Media files are handled simply: populate: true
        if self._is_media_image_document(field_type):
            return True

        # For other documents build nested structure
        # Ensure field_type is actually a BaseModel subclass before scanning
        if isinstance(field_type, type) and issubclass(field_type, BaseModel):
            nested_structure = self._scan_nested_model(field_type)
            return nested_structure if nested_structure else True

        # Fallback for unexpected types
        return True

    def _scan_nested_model(self, model_class: type[BaseModel]) -> dict[str, Any]:
        """
        Recursively scan nested model and return its populate structure.

        Uses visited_classes mechanism to prevent infinite recursion
        when there are circular references between models.
        """
        # Prevent infinite recursion with circular references
        if model_class in self._visited_classes:
            return {}

        self._visited_classes.add(model_class)

        try:
            nested_fields: list[str] = []  # Scalar fields of the nested model
            nested_populate: dict[str, Any] = {}  # Relations of the nested model

            model_fields = getattr(model_class, 'model_fields', {})

            for field_name, field_info in model_fields.items():
                field_type = self._extract_field_type(field_info.annotation)
                actual_field_name = self._get_field_name(field_name, field_info)

                if self._is_scalar_type(field_type):
                    nested_fields.append(actual_field_name)
                elif self._is_populatable_entry(field_type):
                    nested_populate[actual_field_name] = self._get_populate_structure(field_type)

            # Build the resulting structure for Strapi
            result: dict[str, Any] = {}
            if nested_fields:
                result['fields'] = nested_fields
            if nested_populate:
                result['populate'] = nested_populate

            return result

        finally:
            # Important: remove class from visited after processing
            # so it can be processed in other branches of recursion
            self._visited_classes.discard(model_class)
