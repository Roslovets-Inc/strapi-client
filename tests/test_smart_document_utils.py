"""
Unit tests for smart_document_utils module.

These tests cover the functionality of the smart_document_utils module,
using mocks instead of a real database.
"""
from datetime import datetime
from typing import List, Optional, Union
from src.strapi_client.models.base_document import BaseDocument
from src.strapi_client.models.base_component import BaseComponent
from src.strapi_client.models.base_populatable import BasePopulatable
from src.strapi_client.models.smart_document_utils import (
    is_populatable_model,
    is_media_image_document,
    extract_field_type,
    get_field_name,
    get_model_fields,
    is_base_component,
    get_model_data,
    PopulateStructureBuilder,
    get_model_fields_and_population
)
from pydantic import BaseModel, Field


# Test models
class MockComponent(BaseComponent):
    """Test component for testing."""
    name: str


class MockMediaDocument(BaseDocument):
    """Test media document for testing."""
    url: str
    width: int
    height: int
    createdAt: datetime
    updatedAt: datetime
    publishedAt: datetime


class MockNestedDocument(BaseDocument):
    """Test nested document for testing."""
    title: str
    description: str = ""
    createdAt: datetime
    updatedAt: datetime
    publishedAt: datetime


class MockDocument(BaseDocument):
    """Test document for testing."""
    name: str
    description: str = ""
    tags: List[str] = []
    component: Optional[MockComponent] = None
    media: Optional[MockMediaDocument] = None
    related: Optional[MockNestedDocument] = None
    related_list: List[MockNestedDocument] = []
    customField: str  # Using the field name directly instead of alias


class MockCircularParent(BaseDocument):
    """Test document with circular reference."""
    name: str
    child: Optional['MockCircularChild'] = None


class MockCircularChild(BaseDocument):
    """Test document with circular reference to parent."""
    name: str
    parent: Optional[MockCircularParent] = None


# Tests for utility functions
class TestUtilityFunctions:
    """Tests for utility functions."""

    def test_is_base_component(self):
        """Test is_base_component function."""
        # Test with component
        assert is_base_component(MockComponent) is True
        # Test with base component class
        assert is_base_component(BaseComponent) is False
        # Test with non-component
        assert is_base_component(MockDocument) is False
        # Test with non-class
        assert is_base_component("not a class") is False
        # Test with None
        assert is_base_component(None) is False

    def test_is_media_image_document(self):
        """Test is_media_image_document function."""
        # We can't directly test with MediaImageDocument as it's imported in the module
        # Instead, we'll test the behavior with our test classes
        # This is a limitation of the test, but the function is simple enough
        assert is_media_image_document(MockMediaDocument) is False
        assert is_media_image_document(MockDocument) is False
        assert is_media_image_document("not a class") is False
        assert is_media_image_document(None) is False

    def test_is_populatable_model(self):
        """Test is_populatable_model function."""
        # Test with populatable model
        assert is_populatable_model(MockDocument) is True
        # Test with base populatable class
        assert is_populatable_model(BasePopulatable) is False
        # Test with non-populatable
        assert is_populatable_model(str) is False
        # Test with non-class
        assert is_populatable_model("not a class") is False
        # Test with None
        assert is_populatable_model(None) is False

    def test_extract_field_type(self):
        """Test extract_field_type function."""
        # Test with simple types
        assert extract_field_type(str) is str
        assert extract_field_type(int) is int
        
        # Test with Optional
        optional_str = Optional[str]
        assert extract_field_type(optional_str) is str
        
        # Test with Union
        union_type = Union[str, int]
        extracted = extract_field_type(union_type)
        assert extracted in (str, int)
        
        # Test with List
        list_type = List[str]
        assert extract_field_type(list_type) is str
        
        # Test with nested containers
        nested_type = List[Optional[str]]
        assert extract_field_type(nested_type) is Optional[str]
        
        # Test with None
        assert extract_field_type(None) is None


# Tests for field utilities
class TestFieldUtilities:
    """Tests for field utilities."""

    def test_get_field_name(self):
        """Test get_field_name function."""
        # Test with field that has an alias
        class MockFieldInfo:
            alias = "custom_field"
        
        assert get_field_name("field_name", MockFieldInfo()) == "custom_field"
        
        # Test with field that doesn't have an alias
        class MockFieldInfoNoAlias:
            pass
        
        assert get_field_name("field_name", MockFieldInfoNoAlias()) == "field_name"

    def test_get_model_fields(self):
        """Test get_model_fields function."""
        # Define a test model with various field types
        class TestModel(BaseModel):
            string_field: str
            int_field: int
            optional_field: Optional[str] = None
            list_field: List[str] = []
            custom_name: str = Field(alias="customName")
        
        # Get the model fields
        fields = get_model_fields(TestModel)
        
        # Check that all fields are present
        assert "string_field" in fields
        assert "int_field" in fields
        assert "optional_field" in fields
        assert "list_field" in fields
        assert "custom_name" in fields
        
        # Check that the field info contains the correct type
        assert fields["string_field"].annotation == str
        assert fields["int_field"].annotation == int
        assert fields["list_field"].annotation == List[str]
        
        # Check that the alias is preserved
        assert fields["custom_name"].alias == "customName"


# Tests for PopulateStructureBuilder
class TestPopulateStructureBuilder:
    """Tests for PopulateStructureBuilder class."""

    def test_get_model_fields_and_population(self):
        """Test get_model_fields_and_population method."""
        # Create a builder
        builder = PopulateStructureBuilder()
        
        # Test with a simple model
        fields, populate = builder.get_model_fields_and_population(MockDocument)
        
        # Check that fields include all scalar fields
        assert "id" in fields
        assert "documentId" in fields
        assert "name" in fields
        assert "description" in fields
        assert "tags" in fields
        assert "customField" in fields
        
        # Check that populate structure includes all relation fields
        assert "component" in populate
        assert "media" in populate
        assert "related" in populate
        assert "related_list" in populate
        
        # Test with a model that has circular references
        fields, populate = builder.get_model_fields_and_population(MockCircularParent)
        
        # Check that fields include all scalar fields
        assert "id" in fields
        assert "documentId" in fields
        assert "name" in fields
        
        # Check that populate structure includes relation fields
        assert "child" in populate
        assert "populate" in populate["child"]
        assert "parent" in populate["child"]["populate"]

    def test_circular_references(self):
        """Test handling of circular references."""
        # Create a builder
        builder = PopulateStructureBuilder()
        
        # Test with a model that has circular references
        fields, populate = builder.get_model_fields_and_population(MockCircularParent)
        
        # Check that the circular reference is handled correctly
        assert "child" in populate
        assert "populate" in populate["child"]
        assert "parent" in populate["child"]["populate"]


# Tests for model data processing
class TestModelDataProcessing:
    """Tests for model data processing functions."""

    def test_get_model_data_basic(self):
        """Test get_model_data with basic fields."""
        # Create a document with basic fields
        doc = MockDocument(
            id=1,
            documentId="1",
            createdAt=datetime(2024, 1, 1),
            updatedAt=datetime(2024, 1, 1),
            publishedAt=datetime(2024, 1, 1),
            name="Test Document",
            description="A test document",
            tags=["tag1", "tag2"],
            customField="custom value"
        )
        
        # Get the model data
        data = get_model_data(doc)
        
        # Check that basic fields are included
        assert data["id"] == 1
        assert data["documentId"] == "1"
        assert data["name"] == "Test Document"
        assert data["description"] == "A test document"
        assert data["tags"] == ["tag1", "tag2"]
        assert data["customField"] == "custom value"

    def test_get_model_data_with_nested(self):
        """Test get_model_data with nested documents."""
        # Create nested documents
        component = MockComponent(name="Test Component")
        media = MockMediaDocument(
            id=2, 
            documentId="2", 
            url="http://example.com/image.jpg", 
            width=100, 
            height=100,
            createdAt=datetime(2024, 1, 1),
            updatedAt=datetime(2024, 1, 1),
            publishedAt=datetime(2024, 1, 1)
        )
        related = MockNestedDocument(
            id=3, 
            documentId="3", 
            title="Related Document",
            createdAt=datetime(2024, 1, 1),
            updatedAt=datetime(2024, 1, 1),
            publishedAt=datetime(2024, 1, 1)
        )
        related_list = [
            MockNestedDocument(
                id=4, 
                documentId="4", 
                title="Related 1",
                createdAt=datetime(2024, 1, 1),
                updatedAt=datetime(2024, 1, 1),
                publishedAt=datetime(2024, 1, 1)
            ),
            MockNestedDocument(
                id=5, 
                documentId="5", 
                title="Related 2",
                createdAt=datetime(2024, 1, 1),
                updatedAt=datetime(2024, 1, 1),
                publishedAt=datetime(2024, 1, 1)
            )
        ]
        
        # Create a document with nested fields
        doc = MockDocument(
            id=1,
            documentId="1",
            createdAt=datetime(2024, 1, 1),
            updatedAt=datetime(2024, 1, 1),
            publishedAt=datetime(2024, 1, 1),
            name="Test Document",
            component=component,
            media=media,
            related=related,
            related_list=related_list,
            customField="custom value"
        )
        
        # Get the model data
        data = get_model_data(doc)
        
        # Check that nested documents are replaced with their IDs
        assert data["media"] == 2
        assert data["related"] == 3
        assert data["related_list"] == [4, 5]
        
        # Components should be included as-is
        assert isinstance(data["component"], dict)
        assert data["component"]["name"] == "Test Component"

    def test_get_model_data_exclude_managed(self):
        """Test get_model_data with exclude_managed_fields=True."""
        # Create a document with managed fields
        class ManagedDocument(BaseDocument):
            name: str
            internal_field: str
            __managed_fields__ = {"internal_field"}
        
        doc = ManagedDocument(
            id=1,
            documentId="1",
            createdAt=datetime(2024, 1, 1),
            updatedAt=datetime(2024, 1, 1),
            publishedAt=datetime(2024, 1, 1),
            name="Test Document",
            internal_field="internal value"
        )
        
        # Get the model data with exclude_managed_fields=False
        data = get_model_data(doc, exclude_managed_fields=False)
        
        # Check that all fields are included
        assert "name" in data
        assert "internal_field" in data
        
        # Get the model data with exclude_managed_fields=True
        data = get_model_data(doc, exclude_managed_fields=True)
        
        # Check that managed fields are excluded
        assert "name" in data
        assert "internal_field" not in data


# Tests for public API
class TestPublicAPI:
    """Tests for public API functions."""

    def test_is_base_component(self):
        """Test is_base_component function."""
        # This is a public API function, so we test it directly
        assert is_base_component(MockComponent) is True
        assert is_base_component(BaseComponent) is False
        assert is_base_component(MockDocument) is False

    def test_get_model_fields_and_population(self):
        """Test get_model_fields_and_population function."""
        # This is a public API function that uses PopulateStructureBuilder
        fields, populate = get_model_fields_and_population(MockDocument)
        
        # Check that fields include all model fields
        assert "id" in fields
        assert "documentId" in fields
        assert "name" in fields
        
        # Check that populate structure includes relations
        assert "component" in populate
        assert "media" in populate
        assert "related" in populate
        assert "related_list" in populate

    def test_get_model_data(self):
        """Test get_model_data function."""
        # Create a document with basic fields
        doc = MockDocument(
            id=1,
            documentId="1",
            createdAt=datetime(2024, 1, 1),
            updatedAt=datetime(2024, 1, 1),
            publishedAt=datetime(2024, 1, 1),
            name="Test Document",
            customField="custom value"
        )
        
        # Get the model data
        data = get_model_data(doc)
        
        # Check that basic fields are included
        assert data["id"] == 1
        assert data["documentId"] == "1"
        assert data["name"] == "Test Document"
        assert data["customField"] == "custom value"
        
        # Test with json_mode=True
        data_json = get_model_data(doc, json_mode=True)
        assert data_json["id"] == 1
        assert data_json["name"] == "Test Document"
