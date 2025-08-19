import asyncio
import datetime
import json
import pytest
import httpx
from pathlib import Path
from io import BytesIO
from unittest.mock import patch, AsyncMock, MagicMock
from src.strapi_client import StrapiClientAsync, SmartDocument
from src.strapi_client.models.base_document import BaseDocument
from src.strapi_client.utils import hash_model


# Simple SmartDocument subclass for testing
class TodoItem(SmartDocument):
    name: str
    
# Document with nested document for testing model_dump_data
class NestedDocument(BaseDocument):
    title: str
    
class ParentDocument(SmartDocument):
    title: str
    nested: NestedDocument
    nested_list: list[NestedDocument] = []


NOW = datetime.datetime(2024, 1, 1).isoformat()


async def mock_strapi_handler(request: httpx.Request) -> httpx.Response:
    if request.url.path == '/api/todo-items/1' and request.method == 'GET':
        return httpx.Response(200, json={
            'data': {
                'id': 1,
                'documentId': '1',
                'createdAt': NOW,
                'updatedAt': NOW,
                'publishedAt': NOW,
                'name': 'First'
            }
        })
    if request.url.path == '/api/todo-items/2' and request.method == 'GET':
        return httpx.Response(200, json={
            'data': {
                'id': 2,
                'documentId': '2',
                'createdAt': NOW,
                'updatedAt': NOW,
                'publishedAt': NOW,
                'name': 'Updated'
            }
        })
    if request.url.path == '/api/todo-items' and request.method == 'GET':
        return httpx.Response(200, json={
            'data': [{
                'id': 1,
                'documentId': '1',
                'createdAt': NOW,
                'updatedAt': NOW,
                'publishedAt': NOW,
                'name': 'First'
            }],
            'meta': {
                'pagination': {
                    'total': 1
                }
            }
        })
    if request.url.path == '/api/todo-items' and request.method == 'POST':
        body = json.loads(request.content.decode()) if request.content else {}
        return httpx.Response(200, json={
            'data': {
                'id': 2,
                'documentId': '2',
                'createdAt': NOW,
                'updatedAt': NOW,
                'publishedAt': NOW,
                **(body.get('data') or {})
            }
        })
    if request.url.path == '/api/todo-items/1' and request.method == 'PUT':
        body = json.loads(request.content.decode()) if request.content else {}
        return httpx.Response(200, json={
            'data': {
                'id': 1,
                'documentId': '1',
                'createdAt': NOW,
                'updatedAt': NOW,
                'publishedAt': NOW,
                **(body.get('data') or {})
            }
        })
    if request.url.path == '/api/todo-items/2' and request.method == 'PUT':
        body = json.loads(request.content.decode()) if request.content else {}
        return httpx.Response(200, json={
            'data': {
                'id': 2,
                'documentId': '2',
                'createdAt': NOW,
                'updatedAt': NOW,
                'publishedAt': NOW,
                **(body.get('data') or {})
            }
        })
    if request.url.path == '/api/todo-items/error' and request.method == 'PUT':
        return httpx.Response(500, json={'error': 'server error'})
    return httpx.Response(404, json={'error': 'not found'})


@pytest.fixture
def async_client():
    transport = httpx.MockTransport(mock_strapi_handler)
    client = StrapiClientAsync(base_url='http://test', token='token')
    client._client = httpx.AsyncClient(transport=transport)
    yield client
    asyncio.run(client.close())


def test_plural_api_id():
    assert TodoItem.__plural_api_id__ == 'todo-items'


def test_get_document(async_client):
    async def main():
        item = await TodoItem.get_document(async_client, '1')
        assert isinstance(item, TodoItem)
        assert item.name == 'First'
    asyncio.run(main())


def test_get_documents(async_client):
    async def main():
        docs = await TodoItem.get_documents(async_client)
        assert len(docs) == 1
        assert docs[0].document_id == '1'
    asyncio.run(main())


def test_get_documents_with_meta(async_client):
    async def main():
        docs, meta = await TodoItem.get_documents_with_meta(async_client)
        assert meta.get_total_count() == 1
        assert docs[0].name == 'First'
    asyncio.run(main())


def test_create_and_refresh(async_client):
    async def main():
        item = await TodoItem.create_document(async_client, {'name': 'New'})
        assert item.document_id == '2'
        item.name = 'Changed'
        await item.refresh_document(async_client)
        assert item.name == 'Updated'
    asyncio.run(main())


def test_model_dump_data_basic():
    # Create a simple TodoItem
    todo = TodoItem(
        id=1,
        documentId="1",
        createdAt=datetime.datetime(2024, 1, 1),
        updatedAt=datetime.datetime(2024, 1, 1),
        publishedAt=datetime.datetime(2024, 1, 1),
        name="Test Todo"
    )
    
    # Test basic functionality
    data = todo.model_dump_data()
    assert data["id"] == 1
    assert data["documentId"] == "1"
    assert data["name"] == "Test Todo"
    
    # Test exclude_managed=True
    data_excluded = todo.model_dump_data(exclude_managed_fields=True)
    assert "id" not in data_excluded
    assert "documentId" not in data_excluded
    assert "createdAt" not in data_excluded
    assert "updatedAt" not in data_excluded
    assert "publishedAt" not in data_excluded
    assert data_excluded["name"] == "Test Todo"


def test_model_dump_data_nested():
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
    
    # Test with nested documents
    data = parent.model_dump_data()
    assert data["title"] == "Parent Document"
    assert data["nested"] == 2  # ID of nested1
    assert data["nested_list"] == [2, 3]  # IDs of nested1 and nested2
    
    # Test with exclude_managed=True
    data_excluded = parent.model_dump_data(exclude_managed_fields=True)
    assert "id" not in data_excluded
    assert data_excluded["title"] == "Parent Document"
    assert data_excluded["nested"] == 2
    assert data_excluded["nested_list"] == [2, 3]


def test_hash_basic():
    """Test the basic functionality of the hash_model function with SmartDocument."""
    # Create a simple TodoItem
    todo = TodoItem(
        id=1,
        documentId="1",
        createdAt=datetime.datetime(2024, 1, 1),
        updatedAt=datetime.datetime(2024, 1, 1),
        publishedAt=datetime.datetime(2024, 1, 1),
        name="Test Todo"
    )
    
    # Test that hash_model returns a non-empty string
    hash_value = hash_model(todo)
    assert isinstance(hash_value, str)
    assert len(hash_value) > 0
    
    # Test reproducibility - same document should produce same hash
    assert hash_model(todo) == hash_model(todo)
    
    # Test that different documents produce different hashes
    todo2 = TodoItem(
        id=2,
        documentId="2",
        createdAt=datetime.datetime(2024, 1, 1),
        updatedAt=datetime.datetime(2024, 1, 1),
        publishedAt=datetime.datetime(2024, 1, 1),
        name="Another Todo"
    )
    assert hash_model(todo) != hash_model(todo2)


def test_hash_nested():
    """Test the hash_model function with nested documents."""
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
    
    # Test that hash_model returns a non-empty string
    hash_value = hash_model(parent)
    assert isinstance(hash_value, str)
    assert len(hash_value) > 0
    
    # Test reproducibility - same document should produce same hash
    assert hash_model(parent) == hash_model(parent)
    
    # Test that changing a nested document changes the hash
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


def test_patch_document_default(async_client):
    """Test patch_document with default parameters."""
    async def main():
        # Create a document to patch
        item = TodoItem(
            id=2,
            documentId="2",
            createdAt=datetime.datetime(2024, 1, 1),
            updatedAt=datetime.datetime(2024, 1, 1),
            publishedAt=datetime.datetime(2024, 1, 1),
            name="Updated"
        )
        
        # Use update_document instead of lazy_update_document to get the response
        updated_item = await item.update_document(async_client, {"name": "New Name"})
        assert updated_item is not None
        assert updated_item.name == "New Name"
        
    asyncio.run(main())


def test_patch_document_with_model(async_client):
    """Test patch_document with a BaseModel as input."""
    async def main():
        # Create a document to patch
        item = TodoItem(
            id=1,
            documentId="1",
            createdAt=datetime.datetime(2024, 1, 1),
            updatedAt=datetime.datetime(2024, 1, 1),
            publishedAt=datetime.datetime(2024, 1, 1),
            name="First"
        )
        
        # Create a model to use as patch data
        update_data = TodoItem(
            id=1,
            documentId="1",
            createdAt=datetime.datetime(2024, 1, 1),
            updatedAt=datetime.datetime(2024, 1, 1),
            publishedAt=datetime.datetime(2024, 1, 1),
            name="Updated"
        )
        
        # Use update_document instead of lazy_update_document to get the response
        updated_item = await item.update_document(async_client, update_data)
        assert updated_item is not None
        assert updated_item.name == "Updated"
        
    asyncio.run(main())


def test_patch_document_lazy_with_changes(async_client):
    """Test lazy_update_document with data that has changed."""
    async def main():
        # Create a document to patch
        item = TodoItem(
            id=1,
            documentId="1",
            createdAt=datetime.datetime(2024, 1, 1),
            updatedAt=datetime.datetime(2024, 1, 1),
            publishedAt=datetime.datetime(2024, 1, 1),
            name="First"
        )
        
        # Patch with dict data that is different from the current data
        result = await item.lazy_update_document(async_client, {"name": "Updated"})
        assert result is True  # Update should be performed
        
        # Note: In a real scenario, we would verify the update by getting the document again,
        # but in this test environment, the mock server doesn't reflect updates in subsequent GET requests.
        # The True return value indicates that an update was attempted, which is what we're testing.
        
    asyncio.run(main())


def test_patch_document_lazy_no_changes(async_client):
    """Test lazy_update_document with data that hasn't changed."""
    async def main():
        # Create a document to patch
        item = TodoItem(
            id=1,
            documentId="1",
            createdAt=datetime.datetime(2024, 1, 1),
            updatedAt=datetime.datetime(2024, 1, 1),
            publishedAt=datetime.datetime(2024, 1, 1),
            name="First"
        )
        
        # Patch with dict data that is the same as the current data
        result = await item.lazy_update_document(async_client, {"name": "First"})
        assert result is False  # No update should be performed
        
    asyncio.run(main())


def test_patch_document_with_mocked_client():
    """Test lazy_update_document with a mocked client to verify correct parameters."""
    async def main():
        # Create a mocked client
        mock_client = AsyncMock()
        mock_client.update_document = AsyncMock()
        mock_client.update_document.return_value = AsyncMock()
        
        # Create a document to patch
        item = TodoItem(
            id=1,
            documentId="1",
            createdAt=datetime.datetime(2024, 1, 1),
            updatedAt=datetime.datetime(2024, 1, 1),
            publishedAt=datetime.datetime(2024, 1, 1),
            name="First"
        )
        
        # Mock model_identical to return False to force an update
        with patch.object(SmartDocument, 'model_identical', return_value=False):
            # Patch with dict data
            result = await item.lazy_update_document(mock_client, {"name": "Updated"})
            
            # Verify the result is True (update performed)
            assert result is True
            
            # Verify that update_document was called with the correct parameters
            mock_client.update_document.assert_called_once()
            # Check that the method was called with the correct keyword arguments
            mock_client.update_document.assert_called_with(
                plural_api_id="todo-items",
                document_id="1",
                data={"name": "Updated"}
            )
        
    asyncio.run(main())


def test_patch_document_with_model_mocked_client():
    """Test lazy_update_document with a BaseModel as input and mocked client."""
    async def main():
        # Create a mocked client
        mock_client = AsyncMock()
        mock_client.update_document = AsyncMock()
        mock_client.update_document.return_value = AsyncMock()
        
        # Create a document to patch
        item = TodoItem(
            id=1,
            documentId="1",
            createdAt=datetime.datetime(2024, 1, 1),
            updatedAt=datetime.datetime(2024, 1, 1),
            publishedAt=datetime.datetime(2024, 1, 1),
            name="First"
        )
        
        # Create a model to use as patch data
        update_data = TodoItem(
            id=1,
            documentId="1",
            createdAt=datetime.datetime(2024, 1, 1),
            updatedAt=datetime.datetime(2024, 1, 1),
            publishedAt=datetime.datetime(2024, 1, 1),
            name="Updated"
        )
        
        # Mock model_identical to return False to force an update
        with patch.object(SmartDocument, 'model_identical', return_value=False):
            # Patch with model data
            result = await item.lazy_update_document(mock_client, update_data)
            
            # Verify the result is True (update performed)
            assert result is True
            
            # Verify that update_document was called with the correct parameters
            mock_client.update_document.assert_called_once()
            # We don't check the exact parameters here because serializing a model is more complex
        
    asyncio.run(main())


def test_patch_document_lazy_with_changes_mocked_client():
    """Test lazy_update_document with data that has changed and mocked client."""
    async def main():
        # Create a mocked client
        mock_client = AsyncMock()
        mock_client.update_document = AsyncMock()
        mock_client.update_document.return_value = AsyncMock()
        
        # Create a document to patch
        item = TodoItem(
            id=1,
            documentId="1",
            createdAt=datetime.datetime(2024, 1, 1),
            updatedAt=datetime.datetime(2024, 1, 1),
            publishedAt=datetime.datetime(2024, 1, 1),
            name="First"
        )
        
        # Mock model_identical to return False to force an update
        with patch.object(SmartDocument, 'model_identical', return_value=False):
            # Patch with dict data that is different from the current data
            result = await item.lazy_update_document(mock_client, {"name": "Updated"})
            
            # Verify the result is True (update performed)
            assert result is True
            
            # Verify that update_document was called with the correct parameters
            mock_client.update_document.assert_called_once()
            mock_client.update_document.assert_called_with(
                plural_api_id="todo-items",
                document_id="1",
                data={"name": "Updated"}
            )
        
    asyncio.run(main())


def test_patch_document_lazy_no_changes_mocked_client():
    """Test lazy_update_document with data that hasn't changed and mocked client."""
    async def main():
        # Create a mocked client
        mock_client = AsyncMock()
        mock_client.update_document = AsyncMock()
        mock_client.update_document.return_value = AsyncMock()
        
        # Create a document to patch
        item = TodoItem(
            id=1,
            documentId="1",
            createdAt=datetime.datetime(2024, 1, 1),
            updatedAt=datetime.datetime(2024, 1, 1),
            publishedAt=datetime.datetime(2024, 1, 1),
            name="First"
        )
        
        # Mock model_identical to return True to prevent an update
        with patch.object(SmartDocument, 'model_identical', return_value=True):
            # Patch with dict data that is the same as the current data
            result = await item.lazy_update_document(mock_client, {"name": "First"})
            
            # Verify the result is False (no update performed)
            assert result is False
            
            # Verify that update_document was not called
            mock_client.update_document.assert_not_called()
        
    asyncio.run(main())


def test_patch_document_error_handling():
    """Test patch_document error handling."""
    async def main():
        # Create a mocked client that raises an exception
        mock_client = AsyncMock()
        mock_client.update_document = AsyncMock(side_effect=RuntimeError("Server error"))
        
        # Create a document to patch
        item = TodoItem(
            id=999,
            documentId="999",
            createdAt=datetime.datetime(2024, 1, 1),
            updatedAt=datetime.datetime(2024, 1, 1),
            publishedAt=datetime.datetime(2024, 1, 1),
            name="Error"
        )
        
        # Patch should raise an exception
        with pytest.raises(RuntimeError):
            await item.lazy_update_document(mock_client, {"name": "Updated"})
        
    asyncio.run(main())


def test_get_first_document(async_client):
    """Test get_first_document method."""
    async def main():
        # Test getting the first document
        doc = await TodoItem.get_first_document(async_client)
        assert isinstance(doc, TodoItem)
        assert doc.document_id == '1'
        assert doc.name == 'First'
        
        # Test with filters
        doc = await TodoItem.get_first_document(
            async_client, 
            filters={"name": {"$eq": "First"}}
        )
        assert doc.name == 'First'
        
        # Test with sort
        doc = await TodoItem.get_first_document(
            async_client,
            sort=['name:desc']
        )
        assert doc.name == 'First'
        
        # Test with publication_state and locale
        doc = await TodoItem.get_first_document(
            async_client,
            publication_state='published',
            locale='en'
        )
        assert doc.name == 'First'
        
    asyncio.run(main())


def test_create_document_with_populate(async_client):
    """Test create_document with populate=True path."""
    async def main():
        # Mock the get_model_fields_and_population to return a non-empty populate
        with patch('src.strapi_client.models.smart_document.get_model_fields_and_population') as mock_get:
            # First call for create_document, second for get_document
            mock_get.side_effect = [
                (None, {"nested": True}),  # Return non-empty populate
                (None, {"nested": True})   # For the subsequent get_document call
            ]
            
            # Create a document
            item = await TodoItem.create_document(async_client, {"name": "New"})
            
            # Verify the document was created and fetched with populate
            assert item.document_id == '2'
            assert item.name == 'Updated'  # From the mock response for get_document
            
            # Verify that get_document was called
            mock_get.assert_called()
            
    asyncio.run(main())


def test_update_document(async_client):
    """Test update_document method."""
    async def main():
        # Create a document to update
        item = TodoItem(
            id=1,
            documentId="1",
            createdAt=datetime.datetime(2024, 1, 1),
            updatedAt=datetime.datetime(2024, 1, 1),
            publishedAt=datetime.datetime(2024, 1, 1),
            name="First"
        )
        
        # Test update without populate
        with patch('src.strapi_client.models.smart_document.get_model_fields_and_population') as mock_get:
            mock_get.return_value = (None, None)  # Empty populate
            
            # Mock the response to include the updated name
            with patch.object(async_client, 'update_document') as mock_update:
                mock_response = MagicMock()
                mock_response.data = {
                    "id": 1,
                    "documentId": "1",
                    "createdAt": NOW,
                    "updatedAt": NOW,
                    "publishedAt": NOW,
                    "name": "Updated"
                }
                mock_update.return_value = mock_response
                
                updated = await item.update_document(async_client, {"name": "Updated"})
                
                # Verify the document was updated
                assert updated is item  # Should return self
                assert updated.name == "Updated"
        
        # Test update with populate
        with patch('src.strapi_client.models.smart_document.get_model_fields_and_population') as mock_get:
            mock_get.return_value = (None, {"nested": True})  # Non-empty populate
            
            # Mock refresh_document on the SmartDocument class
            with patch('src.strapi_client.models.smart_document.SmartDocument.refresh_document') as mock_refresh:
                # Create a copy of the item with updated name
                item_copy = TodoItem(
                    id=1,
                    documentId="1",
                    createdAt=datetime.datetime(2024, 1, 1),
                    updatedAt=datetime.datetime(2024, 1, 1),
                    publishedAt=datetime.datetime(2024, 1, 1),
                    name="Updated"
                )
                mock_refresh.return_value = item_copy
                
                updated = await item.update_document(async_client, {"name": "Updated Again"})
                
                # Verify refresh_document was called
                mock_refresh.assert_called_once()
                
                # Since we're mocking refresh_document to return item_copy
                assert updated.name == "Updated"
            
    asyncio.run(main())


def test_patch_document_with_basemodel_lazy(async_client):
    """Test lazy_update_document with BaseModel."""
    async def main():
        # Create a document to patch
        item = TodoItem(
            id=2,
            documentId="2",
            createdAt=datetime.datetime(2024, 1, 1),
            updatedAt=datetime.datetime(2024, 1, 1),
            publishedAt=datetime.datetime(2024, 1, 1),
            name="First"
        )
        
        # Create a model to use as patch data
        update_data = TodoItem(
            id=2,
            documentId="2",
            createdAt=datetime.datetime(2024, 1, 1),
            updatedAt=datetime.datetime(2024, 1, 1),
            publishedAt=datetime.datetime(2024, 1, 1),
            name="Updated"
        )
        
        # Patch with model data
        result = await item.lazy_update_document(async_client, update_data)
        assert result is True  # Update should be performed
        
        # Verify the update was performed by getting the document again
        updated_item = await TodoItem.get_document(async_client, "2")
        assert updated_item.name == "Updated"
        
    asyncio.run(main())


def test_update_relations():
    """Test update_relations method."""
    async def main():
        # Create a document to update relations
        item = TodoItem(
            id=1,
            documentId="1",
            createdAt=datetime.datetime(2024, 1, 1),
            updatedAt=datetime.datetime(2024, 1, 1),
            publishedAt=datetime.datetime(2024, 1, 1),
            name="First"
        )
        
        # Create related documents
        related1 = TodoItem(
            id=2,
            documentId="2",
            createdAt=datetime.datetime(2024, 1, 1),
            updatedAt=datetime.datetime(2024, 1, 1),
            publishedAt=datetime.datetime(2024, 1, 1),
            name="Related 1"
        )
        
        related2 = TodoItem(
            id=3,
            documentId="3",
            createdAt=datetime.datetime(2024, 1, 1),
            updatedAt=datetime.datetime(2024, 1, 1),
            publishedAt=datetime.datetime(2024, 1, 1),
            name="Related 2"
        )
        
        # Test with no arguments - should raise ValueError
        mock_client = AsyncMock()
        with pytest.raises(ValueError):
            await item.update_relations(mock_client, "related")
        
        # Test with relations and connect/disconnect - should raise ValueError
        with pytest.raises(ValueError):
            await item.update_relations(
                mock_client, 
                "related", 
                relations=[related1], 
                connect=[related2]
            )
        
        # Create a mock for the update_document method
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_client.update_document.return_value = mock_response
        
        # Create a mock for the refresh_document method
        # We need to patch the actual method on the SmartDocument class
        with patch('src.strapi_client.models.smart_document.SmartDocument.refresh_document') as mock_refresh:
            mock_refresh.return_value = item
            
            # Test with relations
            result = await item.update_relations(
                mock_client,
                "related",
                relations=[related1, related2]
            )
            
            # Verify update_document was called with correct parameters
            mock_client.update_document.assert_called_with(
                plural_api_id="todo-items",
                document_id="1",
                data={"related": {"set": ["2", "3"]}}
            )
            
            # Verify refresh_document was called
            mock_refresh.assert_called_once()
            
            assert result is item
            
            # Reset mocks
            mock_client.update_document.reset_mock()
            mock_refresh.reset_mock()
            
            # Test with connect and disconnect
            result = await item.update_relations(
                mock_client,
                "related",
                connect=[related1],
                disconnect=[related2]
            )
            
            # Verify update_document was called with correct parameters
            mock_client.update_document.assert_called_with(
                plural_api_id="todo-items",
                document_id="1",
                data={"related": {"connect": ["2"], "disconnect": ["3"]}}
            )
            
            # Verify refresh_document was called
            mock_refresh.assert_called_once()
            
            assert result is item
            
    asyncio.run(main())


def test_delete_document(async_client):
    """Test delete_document method."""
    async def main():
        # Create a document to delete
        item = TodoItem(
            id=1,
            documentId="1",
            createdAt=datetime.datetime(2024, 1, 1),
            updatedAt=datetime.datetime(2024, 1, 1),
            publishedAt=datetime.datetime(2024, 1, 1),
            name="First"
        )
        
        # Mock client.delete_document to avoid actual API calls
        mock_client = AsyncMock()
        mock_client.delete_document = AsyncMock()
        
        # Delete the document
        await item.delete_document(mock_client)
        
        # Verify delete_document was called with correct parameters
        mock_client.delete_document.assert_called_with(
            plural_api_id="todo-items",
            document_id="1"
        )
        
    asyncio.run(main())


def test_upload_file():
    """Test upload_file method."""
    async def main():
        # Create a document to upload file to
        item = TodoItem(
            id=1,
            documentId="1",
            createdAt=datetime.datetime(2024, 1, 1),
            updatedAt=datetime.datetime(2024, 1, 1),
            publishedAt=datetime.datetime(2024, 1, 1),
            name="First"
        )
        
        # Mock client.upload_files to avoid actual API calls
        mock_client = AsyncMock()
        mock_client.upload_files = AsyncMock(return_value=MagicMock())
        
        # Mock refresh_document to return self
        with patch('src.strapi_client.models.smart_document.SmartDocument.refresh_document') as mock_refresh:
            mock_refresh.return_value = item
            
            # Test with Path
            test_path = Path("test_file.txt")
            result = await item.upload_file(mock_client, test_path, "attachment")
            
            # Verify upload_files was called with correct parameters
            mock_client.upload_files.assert_called_with(
                files=[test_path],
                content_type_id=item.__content_type_id__,
                document_id=1,
                field="attachment"
            )
            
            # Verify refresh_document was called
            mock_refresh.assert_called_once()
            
            assert result is item
            
            # Reset mocks
            mock_client.upload_files.reset_mock()
            mock_refresh.reset_mock()
            
            # Test with string
            result = await item.upload_file(mock_client, "test_file.txt", "attachment")
            
            # Verify upload_files was called with correct parameters
            mock_client.upload_files.assert_called_with(
                files=["test_file.txt"],
                content_type_id=item.__content_type_id__,
                document_id=1,
                field="attachment"
            )
            
            # Verify refresh_document was called
            mock_refresh.assert_called_once()
            
            # Reset mocks
            mock_client.upload_files.reset_mock()
            mock_refresh.reset_mock()
            
            # Test with dict
            file_dict = {"file1": BytesIO(b"test content")}
            result = await item.upload_file(mock_client, file_dict, "attachment")

            # Verify upload_files was called with correct parameters
            mock_client.upload_files.assert_called_with(
                files=file_dict,
                content_type_id=item.__content_type_id__,
                document_id=1,
                field="attachment"
            )
            
            # Verify refresh_document was called
            mock_refresh.assert_called_once()
            
    asyncio.run(main())
