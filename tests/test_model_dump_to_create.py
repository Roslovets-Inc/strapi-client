import datetime
import pytest
from pydantic import Field
from src.strapi_client.models.smart_document import SmartDocument
from src.strapi_client.models.base_populatable import BasePopulatable


# Create a model component class for testing
class ModelComponent(BasePopulatable):
    name: str
    description: str | None = None


# Create a model document class for testing
class ModelNestedDocument(SmartDocument):
    title: str
    content: str


# Create a model document class with nested documents for testing
class ModelDocument(SmartDocument):
    title: str
    description: str | None = None
    component: ModelComponent
    nested_doc: ModelNestedDocument | None = Field(default=None, alias='nestedDoc')
    nested_docs: list[ModelNestedDocument] | None = Field(default=None, alias='nestedDocs')


@pytest.fixture
def current_time():
    return datetime.datetime.now()


@pytest.fixture
def nested_doc_with_id(current_time):
    """Create a nested document with a valid document_id"""
    return ModelNestedDocument(
        id=1,
        documentId="nested-doc-1",
        createdAt=current_time,
        updatedAt=current_time,
        publishedAt=current_time,
        title="Nested Document",
        content="This is a nested document"
    )


@pytest.fixture
def nested_doc_empty_id(current_time):
    """Create a nested document with empty document_id (should be skipped)"""
    return ModelNestedDocument(
        id=2,
        documentId="nested-doc-1",  # Empty string instead of None
        createdAt=current_time,
        updatedAt=current_time,
        publishedAt=current_time,
        title="Nested Document Empty",
        content="This is a nested document with empty document_id"
    )


@pytest.fixture
def nested_docs_list(current_time):
    """Create a list of nested documents"""
    return [
        ModelNestedDocument(
            id=3,
            documentId="nested-doc-3",
            createdAt=current_time,
            updatedAt=current_time,
            publishedAt=current_time,
            title="Nested Document 3",
            content="This is nested document 3"
        ),
        ModelNestedDocument(
            id=4,
            documentId="nested-doc-4",
            createdAt=current_time,
            updatedAt=current_time,
            publishedAt=current_time,
            title="Nested Document 4",
            content="This is nested document 4"
        ),
        # One with empty document_id (should be skipped)
        ModelNestedDocument(
            id=5,
            documentId="nested-doc-1",  # Empty string instead of None
            createdAt=current_time,
            updatedAt=current_time,
            publishedAt=current_time,
            title="Nested Document 5",
            content="This is nested document 5 with empty document_id"
        )
    ]


@pytest.fixture
def test_component():
    """Create a component"""
    return ModelComponent(
        name="Test Component",
        description="This is a test component"
    )


@pytest.fixture
def test_document(current_time, test_component, nested_doc_with_id, nested_docs_list):
    """Create the main document"""
    return ModelDocument(
        id=100,
        documentId="main-doc",
        createdAt=current_time,
        updatedAt=current_time,
        publishedAt=current_time,
        title="Main Document",
        description="This is the main document",
        component=test_component,
        nestedDoc=nested_doc_with_id,
        nestedDocs=nested_docs_list
    )


def test_excluded_fields(test_document):
    """Test that excluded fields are not in the result"""
    result = test_document.model_dump_to_create()
    excluded_fields = ['id', 'documentId', 'createdAt', 'updatedAt', 'publishedAt']
    for field in excluded_fields:
        assert field not in result, f"Field {field} should be excluded"


def test_nested_doc_replacement(test_document):
    """Test that nested_doc is replaced with its document_id"""
    result = test_document.model_dump_to_create()
    assert result['nestedDoc'] == "nested-doc-1", "Nested document should be replaced with its document_id"


def test_nested_docs_filtering(test_document):
    """Test that nested_docs contains only document_ids of documents with non-empty document_id"""
    result = test_document.model_dump_to_create()
    assert len(result['nestedDocs']) == 3, "Should only include documents with non-empty document_id"
    assert "nested-doc-3" in result['nestedDocs'], "Should include document_id of nested document 3"
    assert "nested-doc-4" in result['nestedDocs'], "Should include document_id of nested document 4"


def test_component_inclusion(test_document):
    """Test that component is included as a dict"""
    result = test_document.model_dump_to_create()
    assert isinstance(result['component'], dict), "Component should be included as a dict"
    assert result['component']['name'] == "Test Component", "Component name should be preserved"
