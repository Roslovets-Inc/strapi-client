import asyncio
import json
import pytest
import httpx2
from strapi_client import StrapiClient, StrapiClientAsync
from strapi_client.models.file_payload import FilePayload
from strapi_client.strapi_client_base import StrapiClientBase


# Mock Strapi REST API handler

def mock_strapi_handler(request: httpx2.Request) -> httpx2.Response:
    if request.url.path == '/api/auth/local' and request.method == 'POST':
        return httpx2.Response(200, json={'jwt': 'mock_jwt'})
    if request.url.path == '/api/items/1' and request.method == 'GET':
        return httpx2.Response(200, json={'data': {'id': 1}})
    if request.url.path == '/api/items' and request.method == 'POST':
        body = json.loads(request.content.decode()) if request.content else {}
        return httpx2.Response(200, json={'data': {'id': 2, 'attributes': body.get('data')}})
    if request.url.path == '/api/items/2' and request.method == 'PUT':
        body = json.loads(request.content.decode()) if request.content else {}
        return httpx2.Response(200, json={'data': {'id': 2, 'attributes': body.get('data')}})
    if request.url.path == '/api/items/2' and request.method == 'DELETE':
        return httpx2.Response(204)
    if request.url.path == '/api/upload' and request.method == 'POST':
        return httpx2.Response(200, json=[])
    if request.url.path == '/api/upload/files' and request.method == 'GET':
        return httpx2.Response(200, json=[{'id': 1}, {'id': 2}])
    if request.url.path == '/_health' and request.method == 'GET':
        return httpx2.Response(200)
    return httpx2.Response(404, json={'error': 'not found'})


@pytest.fixture
def mock_transport():
    return httpx2.MockTransport(mock_strapi_handler)


@pytest.fixture
def client(mock_transport):
    c = StrapiClient(base_url='http://test', token='token')
    c._client = httpx2.Client(transport=mock_transport)
    yield c
    c.close()




def test_auth_header_success(client):
    assert client._auth_header == {"Authorization": "Bearer token"}


def test_auth_header_missing(mock_transport):
    c = StrapiClient(base_url='http://test')
    c._client = httpx2.Client(transport=mock_transport)
    with pytest.raises(ValueError):
        _ = c._auth_header


def test_check_response_error():
    res = httpx2.Response(500, request=httpx2.Request('GET', 'http://x'))
    with pytest.raises(RuntimeError):
        StrapiClientBase._check_response(res, 'fail')


def test_authorize_sets_token(mock_transport):
    c = StrapiClient(base_url='http://test')
    c._client = httpx2.Client(transport=mock_transport)
    c.authorize('u', 'p')
    assert c._token.get_secret_value() == 'mock_jwt'


def test_get_document(client):
    res = client.get_document('items', '1')
    assert res.data['id'] == 1


def test_create_update_delete_document(client):
    res = client.create_document('items', {'title': 'a'})
    assert res.data['id'] == 2
    res = client.update_document('items', '2', {'title': 'b'})
    assert res.data['id'] == 2
    # Should not raise
    client.delete_document('items', '2')


def test_locale_is_forwarded_for_sync_crud():
    requests = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        if request.method == 'DELETE':
            return httpx2.Response(204)
        return httpx2.Response(200, json={'data': {'id': 1}})

    localized_client = StrapiClient(base_url='http://test', token='token')
    localized_client._client = httpx2.Client(transport=httpx2.MockTransport(handler))
    try:
        localized_client.get_document('items', '1', locale='fr')
        localized_client.get_single_document('homepage', locale='fr')
        localized_client.create_document('items', {'title': 'a'}, locale='fr')
        localized_client.update_document('items', '1', {'title': 'b'}, locale='fr')
        localized_client.delete_document('items', '1', locale='fr')
    finally:
        localized_client.close()

    assert len(requests) == 5
    assert all(request.url.params['locale'] == 'fr' for request in requests)


def test_locale_is_forwarded_for_async_crud():
    requests = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        if request.method == 'DELETE':
            return httpx2.Response(204)
        return httpx2.Response(200, json={'data': {'id': 1}})

    async def main():
        localized_client = StrapiClientAsync(base_url='http://test', token='token')
        localized_client._client = httpx2.AsyncClient(transport=httpx2.MockTransport(handler))
        try:
            await localized_client.get_document('items', '1', locale='fr')
            await localized_client.get_single_document('homepage', locale='fr')
            await localized_client.create_document('items', {'title': 'a'}, locale='fr')
            await localized_client.update_document('items', '1', {'title': 'b'}, locale='fr')
            await localized_client.delete_document('items', '1', locale='fr')
        finally:
            await localized_client.close()

    asyncio.run(main())

    assert len(requests) == 5
    assert all(request.url.params['locale'] == 'fr' for request in requests)


def test_upload_and_list_files(client, tmp_path):
    f = tmp_path / 'file.txt'
    f.write_text('content')
    assert isinstance(client.upload_files([f]), list)
    files = client.get_uploaded_files()
    assert isinstance(files, list) and files[0]['id'] == 1


def test_check_health(monkeypatch, mock_transport):
    original_client = httpx2.Client

    def create_client(*args, **kwargs):
        kwargs['transport'] = mock_transport
        return original_client(*args, **kwargs)

    monkeypatch.setattr(httpx2, 'Client', create_client)
    c = StrapiClient(base_url='http://test')
    assert c.check_health() is True


def test_file_payload_rejects_invalid_files_type():
    with pytest.raises(TypeError, match="Files must be a list of paths or a dict"):
        FilePayload.list_from_files(42)


def test_check_health_returns_false_on_http_error(monkeypatch):
    transport = httpx2.MockTransport(lambda request: httpx2.Response(503))
    original_client = httpx2.Client

    def create_client(*args, **kwargs):
        kwargs['transport'] = transport
        return original_client(*args, **kwargs)

    monkeypatch.setattr(httpx2, 'Client', create_client)

    assert StrapiClient(base_url='http://test').check_health() is False


def test_check_health_does_not_hide_unexpected_errors(monkeypatch):
    def create_client(*args, **kwargs):
        raise RuntimeError("unexpected client failure")

    monkeypatch.setattr(httpx2, 'Client', create_client)

    with pytest.raises(RuntimeError, match="unexpected client failure"):
        StrapiClient(base_url='http://test').check_health()


def test_async_check_health_returns_false_on_http_error(monkeypatch):
    transport = httpx2.MockTransport(lambda request: httpx2.Response(503))
    original_client = httpx2.AsyncClient

    def create_client(*args, **kwargs):
        kwargs['transport'] = transport
        return original_client(*args, **kwargs)

    monkeypatch.setattr(httpx2, 'AsyncClient', create_client)

    result = asyncio.run(StrapiClientAsync(base_url='http://test').check_health())

    assert result is False


def test_async_check_health_does_not_hide_unexpected_errors(monkeypatch):
    def create_client(*args, **kwargs):
        raise RuntimeError("unexpected async client failure")

    monkeypatch.setattr(httpx2, 'AsyncClient', create_client)

    with pytest.raises(RuntimeError, match="unexpected async client failure"):
        asyncio.run(StrapiClientAsync(base_url='http://test').check_health())



