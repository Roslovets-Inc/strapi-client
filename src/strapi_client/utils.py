from typing import Any
import warnings
import json
import hashlib
import datetime
from pydantic import BaseModel

RESERVED_FIELDS: set[str] = {
    "id", "documentId", "createdAt", "updatedAt", "publishedAt", "createdBy", "updatedBy", "publishedBy"
}


def serialize_document_data(data: dict[str, Any] | BaseModel) -> dict[str, Any]:
    """Serialize document data to dictionary for request body."""
    if isinstance(data, BaseModel):
        data_dict = data.model_dump(by_alias=True, mode='json')
    else:
        # Create a copy of the dictionary to avoid modifying the original
        data_dict = data.copy()
    # Collect keys to remove
    keys_to_remove = []
    for key in data_dict:
        if key in RESERVED_FIELDS:
            warnings.warn(f"Field '{key}' is reserved by Strapi and will be ignored.")
            keys_to_remove.append(key)
    # Remove the keys
    for key in keys_to_remove:
        del data_dict[key]
    return data_dict


def hash_model(data: BaseModel | dict[str, Any]) -> str:
    """
    Calculate a deterministic hash of a dictionary or BaseModel.
    
    The hash is calculated by:
    1. If input is a BaseModel, converting it to a dictionary
    2. Converting the dictionary to a JSON string with sorted keys
    3. Computing a SHA-256 hash of the JSON string
    
    Args:
        data: A dictionary or BaseModel to hash
        
    Returns:
        A hexadecimal string representation of the hash
    """
    # If data is a BaseModel, convert it to a dictionary
    if isinstance(data, BaseModel):
        data_dict = data.model_dump(by_alias=True, mode='json')
    else:
        data_dict = data

    # Define a custom JSON encoder to handle datetime objects
    class DateTimeEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime.datetime):
                return obj.isoformat()
            return super().default(obj)

    # Convert the dictionary to a JSON string with sorted keys for deterministic output
    json_str = json.dumps(data_dict, sort_keys=True, cls=DateTimeEncoder)
    # Compute the SHA-256 hash of the JSON string
    hash_obj = hashlib.sha256(json_str.encode('utf-8'))
    # Return the hash as a hexadecimal string
    return hash_obj.hexdigest()
