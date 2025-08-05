import asyncio
import datetime
import json
import pytest
import httpx
from src.strapi_client import StrapiClientAsync, SmartDocument
from src.strapi_client.models.base_document import BaseDocument


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
