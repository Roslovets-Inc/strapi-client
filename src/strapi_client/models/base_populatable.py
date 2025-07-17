from typing import Any
from pydantic import BaseModel


class BasePopulatable(BaseModel):
    """Strapi entry that can be populated in request."""


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
