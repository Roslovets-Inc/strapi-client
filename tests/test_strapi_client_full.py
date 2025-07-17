import json
import pytest
import httpx
from src.strapi_client import StrapiClient
from src.strapi_client.strapi_client_base import StrapiClientBase


# Mock Strapi REST API handler

def mock_strapi_handler(request: httpx.Request) -> httpx.Response:
    if request.url.path == '/api/auth/local' and request.method == 'POST':
        return httpx.Response(200, json={'jwt': 'mock_jwt'})
    if request.url.path == '/api/items/1' and request.method == 'GET':
        return httpx.Response(200, json={'data': {'id': 1}})
    if request.url.path == '/api/items' and request.method == 'POST':
        body = json.loads(request.content.decode()) if request.content else {}
        return httpx.Response(200, json={'data': {'id': 2, 'attributes': body.get('data')}})
    if request.url.path == '/api/items/2' and request.method == 'PUT':
        body = json.loads(request.content.decode()) if request.content else {}
        return httpx.Response(200, json={'data': {'id': 2, 'attributes': body.get('data')}})
    if request.url.path == '/api/items/2' and request.method == 'DELETE':
        return httpx.Response(204)
    if request.url.path == '/api/upload' and request.method == 'POST':
        return httpx.Response(200, json={'result': 'ok'})
    if request.url.path == '/api/upload/files' and request.method == 'GET':
        return httpx.Response(200, json=[{'id': 1}, {'id': 2}])
    if request.url.path == '/_health' and request.method == 'GET':
        return httpx.Response(200)
    return httpx.Response(404, json={'error': 'not found'})


@pytest.fixture
def mock_transport():
    return httpx.MockTransport(mock_strapi_handler)


@pytest.fixture
def client(mock_transport):
    c = StrapiClient(base_url='http://test', token='token')
    c._client = httpx.Client(transport=mock_transport)
    yield c
    c.close()




def test_auth_header_success(client):
    assert client._auth_header == {"Authorization": "Bearer token"}


def test_auth_header_missing(mock_transport):
    c = StrapiClient(base_url='http://test')
    c._client = httpx.Client(transport=mock_transport)
    with pytest.raises(ValueError):
        _ = c._auth_header


def test_check_response_error():
    res = httpx.Response(500, request=httpx.Request('GET', 'http://x'))
    with pytest.raises(RuntimeError):
        StrapiClientBase._check_response(res, 'fail')


def test_authorize_sets_token(mock_transport):
    c = StrapiClient(base_url='http://test')
    c._client = httpx.Client(transport=mock_transport)
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


def test_upload_and_list_files(client, tmp_path):
    f = tmp_path / 'file.txt'
    f.write_text('content')
    assert client.upload_files([f]) == {'result': 'ok'}
    files = client.get_uploaded_files()
    assert isinstance(files, list) and files[0]['id'] == 1


def test_check_health(monkeypatch, mock_transport):
    original_client = httpx.Client

    def create_client(*args, **kwargs):
        kwargs['transport'] = mock_transport
        return original_client(*args, **kwargs)

    monkeypatch.setattr(httpx, 'Client', create_client)
    c = StrapiClient(base_url='http://test')
    assert c.check_health() is True



