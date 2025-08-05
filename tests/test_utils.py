import datetime
import pytest
from pydantic import BaseModel
from src.strapi_client.utils import serialize_document_data, hash_model
from src.strapi_client.models.base_document import BaseDocument


class SimpleModel(BaseModel):
    name: str
    value: int


class NestedDocument(BaseDocument):
    title: str


class ParentDocument(BaseDocument):
    title: str
    nested: NestedDocument = None
    nested_list: list[NestedDocument] = None


def test_serialize_document_data_with_dict():
    """Test serialize_document_data with a dictionary."""
    data = {"name": "Test", "id": 1, "createdAt": "2024-01-01"}
    result = serialize_document_data(data)
    
    # Reserved fields should be removed
    assert "id" not in result
    assert "createdAt" not in result
    
    # Other fields should remain
    assert result["name"] == "Test"


def test_serialize_document_data_with_model():
    """Test serialize_document_data with a BaseModel."""
    model = SimpleModel(name="Test", value=42)
    result = serialize_document_data(model)
    
    assert result["name"] == "Test"
    assert result["value"] == 42


def test_hash_model_with_dict():
    """Test hash_model with a dictionary."""
    data = {"name": "Test", "value": 42}
    
    # Hash should be a non-empty string
    hash_value = hash_model(data)
    assert isinstance(hash_value, str)
    assert len(hash_value) > 0
    
    # Same data should produce same hash
    assert hash_model(data) == hash_model(data)
    
    # Different data should produce different hashes
    data2 = {"name": "Test2", "value": 42}
    assert hash_model(data) != hash_model(data2)


def test_hash_model_with_model():
    """Test hash_model with a BaseModel."""
    model = SimpleModel(name="Test", value=42)
    
    # Hash should be a non-empty string
    hash_value = hash_model(model)
    assert isinstance(hash_value, str)
    assert len(hash_value) > 0
    
    # Same model should produce same hash
    assert hash_model(model) == hash_model(model)
    
    # Different models should produce different hashes
    model2 = SimpleModel(name="Test2", value=42)
    assert hash_model(model) != hash_model(model2)


def test_hash_model_with_datetime():
    """Test hash_model with datetime objects."""
    data = {
        "name": "Test",
        "date": datetime.datetime(2024, 1, 1, 12, 0, 0)
    }
    
    # Should not raise an error
    hash_value = hash_model(data)
    assert isinstance(hash_value, str)
    assert len(hash_value) > 0


def test_hash_model_with_nested_documents():
    """Test hash_model with nested documents."""
    # Create nested documents
    nested1 = NestedDocument(
        id=2,
        documentId="2",
        createdAt=datetime.datetime(2024, 1, 1),
        updatedAt=datetime.datetime(2024, 1, 1),
        publishedAt=datetime.datetime(2024, 1, 1),
        title="Nested Document 1"
    )
    
    nested2 = NestedDocument(
        id=3,
        documentId="3",
        createdAt=datetime.datetime(2024, 1, 1),
        updatedAt=datetime.datetime(2024, 1, 1),
        publishedAt=datetime.datetime(2024, 1, 1),
        title="Nested Document 2"
    )
    
    # Create parent document with nested documents
    parent = ParentDocument(
        id=1,
        documentId="1",
        createdAt=datetime.datetime(2024, 1, 1),
        updatedAt=datetime.datetime(2024, 1, 1),
        publishedAt=datetime.datetime(2024, 1, 1),
        title="Parent Document",
        nested=nested1,
        nested_list=[nested1, nested2]
    )
    
    # Hash should be a non-empty string
    hash_value = hash_model(parent)
    assert isinstance(hash_value, str)
    assert len(hash_value) > 0
    
    # Same document should produce same hash
    assert hash_model(parent) == hash_model(parent)
    
    # Changing a nested document should change the hash
    parent2 = ParentDocument(
        id=1,
        documentId="1",
        createdAt=datetime.datetime(2024, 1, 1),
        updatedAt=datetime.datetime(2024, 1, 1),
        publishedAt=datetime.datetime(2024, 1, 1),
        title="Parent Document",
        nested=nested2,  # Different nested document
        nested_list=[nested1, nested2]
    )
    assert hash_model(parent) != hash_model(parent2)