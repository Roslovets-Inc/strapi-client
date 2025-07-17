import asyncio
import datetime
import json
import pytest
import httpx
from src.strapi_client import StrapiClientAsync, SmartDocument


# Simple SmartDocument subclass for testing
class TodoItem(SmartDocument):
    name: str


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
