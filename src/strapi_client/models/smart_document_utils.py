"""
Utilities for working with Pydantic models in the context of Strapi API.

This module provides functions for:
1. Type checking and extraction
2. Field name and type extraction from Pydantic models
3. Building populate structures for Strapi API requests
4. Processing model data for API requests
"""
from typing import Any, Union, get_origin, get_args, TypeVar, List, Set, Tuple, Dict
from types import UnionType
from pydantic import BaseModel
from .base_populatable import BasePopulatable
from .media_image_document import MediaImageDocument
from .base_document import BaseDocument
from .base_component import BaseComponent

# Type variables for better type hints
T = TypeVar('T')
ModelType = TypeVar('ModelType', bound=BaseModel)


def is_populatable_model(field_type: Any) -> bool:
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


def is_media_image_document(field_type: Any) -> bool:
    """
    Check if the type is a MediaImageDocument.

    Media files in Strapi have special handling - they only need populate: true.

    Args:
        field_type: The type to check

    Returns:
        bool: True if the type is a subclass of MediaImageDocument
    """
    try:
        return (isinstance(field_type, type) and
                issubclass(field_type, MediaImageDocument))
    except (TypeError, AttributeError):
        return False


def extract_field_type(field_type: Any) -> Any:
    """
    Extract the actual field type, handling Union, Optional and container types.

    This function handles:
    - Optional types: Optional[T] -> T
    - Union types: Union[T, None] -> T
    - New union syntax: T | None -> T
    - Container types: List[T], list[T], Set[T], etc. -> T
    - Nested combinations: Optional[List[T]] -> T, List[T] | None -> T

    Examples:
        - Optional[str] -> str
        - List[Category] -> Category
        - Union[str, None] -> str
        - list[Category] | None -> Category

    Args:
        field_type: The type to extract from

    Returns:
        The extracted type
    """

    # Helper function to extract type from container
    def extract_from_container(type_obj: Any) -> Any:
        origin = get_origin(type_obj)
        args = get_args(type_obj)

        # Handle containers: List[T], Tuple[T], Set[T] -> T
        if origin in (list, List, tuple, Tuple, set, Set) and args:
            return args[0]
        return type_obj

    # Helper function to get first non-None type from union args
    def get_non_none_type(args: tuple) -> Any:
        non_none_types = [arg for arg in args if arg is not type(None)]
        if non_none_types:
            first_non_none = non_none_types[0]
            # After getting non-None type, check if it's a container
            return extract_from_container(first_non_none)
        return None

    # Handle new Union syntax (Python 3.10+): str | None
    if isinstance(field_type, UnionType):
        args = get_args(field_type)
        result = get_non_none_type(args)
        if result:
            return result

    # Handle older syntax
    origin = get_origin(field_type)
    args = get_args(field_type)

    # If not a generic type, return as is
    if origin is None:
        return field_type

    # Handle containers directly: List[T], Tuple[T], Set[T] -> T
    if origin in (list, List, tuple, Tuple, set, Set) and args:
        return args[0]

    # For Union types (including Optional) - choose the first non-None type
    if origin is Union and args:
        result = get_non_none_type(args)
        if result:
            return result

    # Fallback to original type
    return field_type


def get_field_name(field_name: str, field_info: Any) -> str:
    """
    Return field name for Strapi API.

    Priority: pydantic alias -> original field name.

    Args:
        field_name: The original field name
        field_info: The field info from Pydantic model

    Returns:
        str: The field name to use for Strapi API
    """
    return getattr(field_info, 'alias', None) or field_name


def get_model_fields(model_class: type[BaseModel]) -> dict:
    """
    Get fields from a Pydantic model.

    Args:
        model_class: The Pydantic model class

    Returns:
        dict: The model fields
    """
    return getattr(model_class, 'model_fields', {})


def is_base_component(field_type: Any) -> bool:
    """
    Check if the type is a subclass of BaseComponent.

    Components in Strapi need simple populate: true like media files.

    Args:
        field_type: The type to check

    Returns:
        bool: True if the type is a subclass of BaseComponent (but not BaseComponent itself)
    """
    try:
        return (isinstance(field_type, type) and
                issubclass(field_type, BaseComponent) and
                field_type is not BaseComponent)
    except (TypeError, AttributeError):
        return False


def get_model_data(
        document: BaseModel,
        exclude_managed_fields: bool = False,
        json_mode: bool = False
) -> dict[str, Any]:
    """
        Process a document to create a dictionary representation with nested BaseDocument instances
        replaced with their IDs.

        Args:
            document: The document to process
            exclude_managed_fields: If True, exclude fields listed in managed_fields
            json_mode: If True, serialize fields to JSON compatible types

        Returns:
            Dictionary representation of the document with nested BaseDocument instances
            replaced with their IDs
        """
    # Get the model data as a dictionary with aliases
    data = document.model_dump(by_alias=True, mode='json' if json_mode else 'python')

    # Get managed fields if provided or available on the document
    if exclude_managed_fields and hasattr(document, '__managed_fields__'):
        fields_to_exclude: set[str] = document.__managed_fields__
    else:
        fields_to_exclude = set()

    # Get model fields information for finding original field names
    model_fields = get_model_fields(type(document))

    # Process the data to replace nested BaseDocument instances with their IDs
    result: dict[str, Any] = {}
    for key, value in data.items():
        # Find the original field name and info
        original_field_name = None
        field_info = None
        for orig_name, info in model_fields.items():
            if get_field_name(orig_name, info) == key:
                original_field_name = orig_name
                field_info = info
                break

        # Skip managed fields if exclude_managed_fields is True
        if exclude_managed_fields and original_field_name and original_field_name in fields_to_exclude:
            continue

        # Get the actual field value from the original document
        if original_field_name and hasattr(document, original_field_name):
            original_value = getattr(document, original_field_name)
        else:
            # Fallback to serialized value if we can't find the original field
            original_value = value

        # Replace nested BaseDocument instances with their IDs based on actual value type
        if isinstance(original_value, BaseDocument):
            result[key] = original_value.id
        elif isinstance(original_value, list) and original_value:
            if all(isinstance(item, BaseDocument) for item in original_value):
                result[key] = [item.id for item in original_value]
            else:
                result[key] = value
        else:
            # Scalar field or other type - use serialized value
            result[key] = value

    return result


class PopulateStructureBuilder:
    """Builder for Strapi API populate structures."""
    visited_classes: set[type]

    def __init__(self):
        """Initialize the builder with an empty set of visited classes."""
        self.visited_classes = set()

    def get_model_fields_and_population(self, model_class: type[ModelType]) -> tuple[list[str], dict[str, Any]]:
        """
        Recursively scan class fields and return fields and populate structure for Strapi API.

        Uses pydantic aliases when available, otherwise field names.

        Args:
            model_class: The Pydantic model class to scan

        Returns:
            tuple[list[str], Dict[str, Any]]: (fields_list, populate_dict)
        """
        self.visited_classes = set()  # Reset visited classes
        return self._process_model(model_class)

    def _process_model(self, model_class: type[ModelType]) -> tuple[list[str], dict[str, Any]]:
        """
        Process a model and return its fields and populate structure.

        Args:
            model_class: The Pydantic model class to process

        Returns:
            tuple[list[str], dict[str, Any]]: (fields_list, populate_dict)
        """
        root_fields: list[str] = []
        populate_dict: dict[str, Any] = {}

        # Get field metadata from pydantic model
        model_fields = get_model_fields(model_class)

        for field_name, field_info in model_fields.items():
            field_type = extract_field_type(field_info.annotation)
            actual_field_name = get_field_name(field_name, field_info)

            # Related documents go to the populate structure
            if is_populatable_model(field_type):
                populate_dict[actual_field_name] = self._get_populate_structure(field_type)
            # All other fields (scalar types) go to the main fields list
            else:
                root_fields.append(actual_field_name)

        return root_fields, populate_dict

    def _get_populate_structure(self, field_type: type) -> dict[str, Any] | bool:
        """
        Generate populate structure for a relation field.

        For media files and components returns True (simple populate).
        For other documents - nested structure with fields and their relations.

        Args:
            field_type: The field type to generate populate structure for

        Returns:
            dict[str, Any] | bool: The populate structure or True for simple populate
        """
        # Media files are handled simply: populate: true
        if is_media_image_document(field_type):
            return True

        # Components are handled simply: populate: true (like media)
        if is_base_component(field_type):
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

        Args:
            model_class: The model class to scan

        Returns:
            dict[str, Any]: The populate structure for the nested model
        """
        # Prevent infinite recursion with circular references
        if model_class in self.visited_classes:
            return {}

        self.visited_classes.add(model_class)

        try:
            nested_fields: list[str] = []  # Scalar fields of the nested model
            nested_populate: dict[str, Any] = {}  # Relations of the nested model

            model_fields = get_model_fields(model_class)

            for field_name, field_info in model_fields.items():
                field_type = extract_field_type(field_info.annotation)
                actual_field_name = get_field_name(field_name, field_info)

                if is_populatable_model(field_type):
                    nested_populate[actual_field_name] = self._get_populate_structure(field_type)
                else:
                    nested_fields.append(actual_field_name)

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
            self.visited_classes.discard(model_class)


def get_model_fields_and_population(model_class: type[BaseModel]) -> tuple[list[str], dict[str, Any]]:
    """
    Recursively scans class fields and returns fields and populate structure for Strapi API.
    Uses pydantic aliases when available, otherwise field names.

    Returns:
        tuple[list[str], Dict[str, Any]]: (fields_list, populate_dict)
    """
    builder = PopulateStructureBuilder()
    return builder.get_model_fields_and_population(model_class)
