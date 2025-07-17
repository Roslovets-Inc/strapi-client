from typing import Any, Iterator, Self
import warnings
from pathlib import Path
from io import BytesIO
from pydantic import BaseModel

RESERVED_FIELDS: set[str] = {
    "id", "documentId", "createdAt", "updatedAt", "publishedAt", "createdBy", "updatedBy", "publishedBy"
}


def flatten_parameters(parameters: dict[str, Any]) -> Iterator[tuple[str, Any]]:
    """Flatten nested dict with parameters to flat structure for query."""
    for key, value in parameters.items():
        if isinstance(value, dict):
            for key1, value1 in flatten_parameters(value):
                yield f'[{key}]{key1}', value1
        else:
            yield f'[{key}]', value


def stringify_parameters(
        name: str,
        parameters: dict[str, Any] | list[str] | str | None
) -> dict[str, Any]:
    """Stringify nested dict with parameters to strings for query."""
    if type(parameters) is dict:
        return {name + k: v for k, v in flatten_parameters(parameters)}
    elif type(parameters) is str:
        return {name: parameters}
    elif type(parameters) is list:
        return {f'{name}[{i}]': p for i, p in enumerate(parameters)}
    else:
        return {}


def serialize_document_data(data: dict[str, Any] | BaseModel) -> dict[str, Any]:
    """Serialize document data to dictionary for request body."""
    if isinstance(data, BaseModel):
        data_dict = data.model_dump(by_alias=True)
    else:
        data_dict = data
    for key, value in data_dict.items():
        if key in RESERVED_FIELDS:
            warnings.warn(f"Field '{key}' is reserved by Strapi and will be ignored.")
            del data_dict[key]
    return data_dict
