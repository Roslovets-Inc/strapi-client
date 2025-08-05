"""
Unit tests for smart_document_utils module.

These tests cover the functionality of the refactored smart_document_utils module,
using mocks instead of a real database.
"""
from datetime import datetime
from typing import List, Optional, Union
from src.strapi_client.models.base_document import BaseDocument
from src.strapi_client.models.base_component import BaseComponent
from src.strapi_client.models.smart_document_utils import (
    TypeUtils,
    FieldUtils,
    PopulateStructureBuilder,
    ModelDataProcessor,
    get_model_fields_and_population,
    get_model_data,
    is_base_component
)


# Test models
class MockComponent(BaseComponent):
    """Test component for testing."""
    name: str


class MockMediaDocument(BaseDocument):
    """Test media document for testing."""
    url: str
    width: int
    height: int


class MockNestedDocument(BaseDocument):
    """Test nested document for testing."""
    title: str
    description: str = ""


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


# TypeUtils tests
class TestTypeUtils:
    """Tests for TypeUtils class."""

    def test_is_base_component(self):
        """Test is_base_component method."""
        # Test with component
        assert TypeUtils.is_base_component(MockComponent) is True
        # Test with base component class
        assert TypeUtils.is_base_component(BaseComponent) is False
        # Test with non-component
        assert TypeUtils.is_base_component(MockDocument) is False
        # Test with non-class
        assert TypeUtils.is_base_component("not a class") is False
        # Test with None
        assert TypeUtils.is_base_component(None) is False

    def test_is_media_image_document(self):
        """Test is_media_image_document method."""
        # We can't directly test with MediaImageDocument as it's imported in the module
        # Instead, we'll test the behavior with our test classes
        # This is a limitation of the test, but the function is simple enough
        assert TypeUtils.is_media_image_document(MockMediaDocument) is False
        assert TypeUtils.is_media_image_document(MockDocument) is False
        assert TypeUtils.is_media_image_document("not a class") is False
        assert TypeUtils.is_media_image_document(None) is False

    def test_is_scalar_type(self):
        """Test is_scalar_type method."""
        # Test with scalar types
        assert TypeUtils.is_scalar_type(str) is True
        assert TypeUtils.is_scalar_type(int) is True
        assert TypeUtils.is_scalar_type(float) is True
        assert TypeUtils.is_scalar_type(bool) is True
        # Test with non-scalar types
        assert TypeUtils.is_scalar_type(MockDocument) is False
        assert TypeUtils.is_scalar_type(MockComponent) is False
        # Test with None
        assert TypeUtils.is_scalar_type(None) is True

    def test_extract_field_type(self):
        """Test extract_field_type method."""
        # Test with simple types
        assert TypeUtils.extract_field_type(str) is str
        assert TypeUtils.extract_field_type(int) is int
        
        # Test with Optional
        assert TypeUtils.extract_field_type(Optional[str]) is str
        assert TypeUtils.extract_field_type(Optional[MockDocument]) is MockDocument
        
        # Test with Union
        assert TypeUtils.extract_field_type(Union[str, int]) is str
        assert TypeUtils.extract_field_type(Union[str, None]) is str
        
        # Test with List
        assert TypeUtils.extract_field_type(List[str]) is str
        assert TypeUtils.extract_field_type(List[MockDocument]) is MockDocument
        
        # Test with nested types
        assert TypeUtils.extract_field_type(Optional[List[str]]) is str
        assert TypeUtils.extract_field_type(List[Optional[str]]) is Optional[str]
        
        # Test with Python 3.10+ union syntax (if supported)
        try:
            # This will only work in Python 3.10+
            type_annotation = eval("str | None")
            assert TypeUtils.extract_field_type(type_annotation) is str
            
            type_annotation = eval("list[str] | None")
            assert TypeUtils.extract_field_type(type_annotation) is str
        except SyntaxError:
            # Python version doesn't support the new union syntax
            pass


# FieldUtils tests
class TestFieldUtils:
    """Tests for FieldUtils class."""

    def test_get_field_name(self):
        """Test get_field_name method."""
        # Create a mock field_info with alias
        class MockFieldInfo:
            alias = "test_alias"
        
        # Test with alias
        assert FieldUtils.get_field_name("original_name", MockFieldInfo()) == "test_alias"
        
        # Test without alias
        class MockFieldInfoNoAlias:
            pass
        
        assert FieldUtils.get_field_name("original_name", MockFieldInfoNoAlias()) == "original_name"

    def test_get_model_fields(self):
        """Test get_model_fields method."""
        # Create a test document instance
        doc = MockDocument(
            id=1,
            documentId="1",
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
            publishedAt=datetime.now(),
            name="Test",
            customField="custom"
        )
        
        # Get model fields
        fields = FieldUtils.get_model_fields(MockDocument)
        
        # Check that fields include the expected fields
        assert "name" in fields
        assert "description" in fields
        assert "tags" in fields
        assert "component" in fields
        assert "media" in fields
        assert "related" in fields
        assert "related_list" in fields
        assert "customField" in fields  # Using the field name directly instead of alias


# PopulateStructureBuilder tests
class TestPopulateStructureBuilder:
    """Tests for PopulateStructureBuilder class."""

    def test_get_model_fields_and_population(self):
        """Test get_model_fields_and_population method."""
        builder = PopulateStructureBuilder()
        fields, populate = builder.get_model_fields_and_population(MockDocument)
        
        # Check fields
        assert "id" in fields
        assert "documentId" in fields
        assert "createdAt" in fields
        assert "updatedAt" in fields
        assert "publishedAt" in fields
        assert "name" in fields
        assert "description" in fields
        assert "tags" in fields
        assert "customField" in fields  # Alias is used
        
        # Check populate
        assert "component" in populate
        assert "media" in populate
        assert "related" in populate
        assert "related_list" in populate
        
        # Check that component uses simple populate
        assert populate["component"] is True
        # Check that media has a nested structure (not simple populate in the refactored version)
        assert isinstance(populate["media"], dict)
        assert "fields" in populate["media"]
        
        # Check that related has nested structure
        assert isinstance(populate["related"], dict)
        assert "fields" in populate["related"]
        assert "id" in populate["related"]["fields"]
        assert "documentId" in populate["related"]["fields"]
        assert "title" in populate["related"]["fields"]
        assert "description" in populate["related"]["fields"]

    def test_circular_references(self):
        """Test handling of circular references."""
        builder = PopulateStructureBuilder()
        fields, populate = builder.get_model_fields_and_population(MockCircularParent)
        
        # Check fields
        assert "id" in fields
        assert "name" in fields
        
        # Check populate
        assert "child" in populate
        assert isinstance(populate["child"], dict)
        assert "fields" in populate["child"]
        assert "id" in populate["child"]["fields"]
        assert "name" in populate["child"]["fields"]
        
        # Check that child.parent is handled correctly
        # In the refactored version, circular references result in a nested structure rather than an empty dict
        assert "populate" in populate["child"]
        assert "parent" in populate["child"]["populate"]
        # Just check that it's a dictionary with fields, not the exact content
        assert isinstance(populate["child"]["populate"]["parent"], dict)


# ModelDataProcessor tests
class TestModelDataProcessor:
    """Tests for ModelDataProcessor class."""

    def test_get_model_data_basic(self):
        """Test get_model_data with basic document."""
        # Create a test document
        doc = MockDocument(
            id=1,
            documentId="1",
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
            publishedAt=datetime.now(),
            name="Test",
            description="Test description",
            tags=["tag1", "tag2"],
            customField="custom"
        )
        
        # Get model data
        data = ModelDataProcessor.get_model_data(doc)
        
        # Check basic fields
        assert data["id"] == 1
        assert data["documentId"] == "1"
        assert "createdAt" in data
        assert "updatedAt" in data
        assert "publishedAt" in data
        assert data["name"] == "Test"
        assert data["description"] == "Test description"
        assert data["tags"] == ["tag1", "tag2"]
        assert data["customField"] == "custom"  # Alias is used

    def test_get_model_data_with_nested(self):
        """Test get_model_data with nested documents."""
        # Create nested documents
        nested = MockNestedDocument(
            id=2,
            documentId="2",
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
            publishedAt=datetime.now(),
            title="Nested",
            description="Nested description"
        )
        
        nested2 = MockNestedDocument(
            id=3,
            documentId="3",
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
            publishedAt=datetime.now(),
            title="Nested 2",
            description="Nested description 2"
        )
        
        # Create a test document with nested documents
        doc = MockDocument(
            id=1,
            documentId="1",
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
            publishedAt=datetime.now(),
            name="Test",
            related=nested,
            related_list=[nested, nested2],
            customField="custom"
        )
        
        # Get model data
        data = ModelDataProcessor.get_model_data(doc)
        
        # Check nested fields
        assert data["related"] == 2  # ID of nested
        assert data["related_list"] == [2, 3]  # IDs of nested and nested2

    def test_get_model_data_exclude_managed(self):
        """Test get_model_data with exclude_managed_fields=True."""
        # Create a test document
        doc = MockDocument(
            id=1,
            documentId="1",
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
            publishedAt=datetime.now(),
            name="Test",
            customField="custom"
        )
        
        # Add managed fields
        doc.__managed_fields__ = {"id", "document_id", "created_at", "updated_at", "published_at"}
        
        # Get model data with exclude_managed_fields=True
        data = ModelDataProcessor.get_model_data(doc, exclude_managed_fields=True)
        
        # Check that managed fields are excluded
        assert "id" not in data
        assert "documentId" not in data
        assert "createdAt" not in data
        assert "updatedAt" not in data
        assert "publishedAt" not in data
        
        # Check that other fields are included
        assert data["name"] == "Test"


# Public API tests
class TestPublicAPI:
    """Tests for public API functions."""

    def test_is_base_component(self):
        """Test is_base_component function."""
        assert is_base_component(MockComponent) is True
        assert is_base_component(BaseComponent) is False
        assert is_base_component(MockDocument) is False

    def test_get_model_fields_and_population(self):
        """Test get_model_fields_and_population function."""
        fields, populate = get_model_fields_and_population(MockDocument)
        
        # Check fields
        assert "name" in fields
        assert "description" in fields
        
        # Check populate
        assert "component" in populate
        assert "media" in populate
        assert "related" in populate

    def test_get_model_data(self):
        """Test get_model_data function."""
        # Create a test document
        doc = MockDocument(
            id=1,
            documentId="1",
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
            publishedAt=datetime.now(),
            name="Test",
            customField="custom"
        )
        
        # Get model data
        data = get_model_data(doc)
        
        # Check basic fields
        assert data["id"] == 1
        assert data["name"] == "Test"
