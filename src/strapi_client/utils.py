from typing import Any, Iterator
import warnings
from pydantic import BaseModel

RESERVED_FIELDS: set[str] = {
    "id", "documentId", "createdAt", "updatedAt", "publishedAt", "createdBy", "updatedBy", "publishedBy"
}


def serialize_document_data(data: dict[str, Any] | BaseModel) -> dict[str, Any]:
    """Serialize document data to dictionary for request body."""
    if isinstance(data, BaseModel):
        data_dict = data.model_dump(by_alias=True, mode='json')
    else:
        data_dict = data
    for key, value in data_dict.items():
        if key in RESERVED_FIELDS:
            warnings.warn(f"Field '{key}' is reserved by Strapi and will be ignored.")
            del data_dict[key]
    return data_dict
