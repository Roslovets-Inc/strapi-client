from typing import Any
import os.path
import aiohttp


class StrapiClient:
    """REST API client for Strapi."""
    baseurl: str
    _token: str | None = None

    def __init__(self, baseurl: str) -> None:
        """Initialize client."""
        if not baseurl.endswith('/'):
            baseurl = baseurl + '/'
        self.baseurl = baseurl

    async def authorize(
            self,
            identifier: str | None = None,
            password: str | None = None,
            token: str | None = None
    ) -> None:
        """Set up or retrieve access token."""
        if token:
            self._token = token
        else:
            if not identifier or not password:
                raise ValueError('Either token or identifier and password must be provided')
            url: str = self.baseurl + 'api/auth/local'
            body: dict[str, str] = {
                'identifier': identifier,
                'password': password
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=body) as res:
                    if res.status != 200:
                        raise RuntimeError(f'Unable to authorize, error {res.status}: {res.reason}')
                    res_obj: dict[str, Any] = await res.json()
                    token: str = res_obj['jwt']
                self._token = token

    async def get_entry(
            self,
            plural_api_id: str,
            document_id: str,
            populate: list[str] | None = None,
            fields: list[str] | None = None
    ) -> dict[str, Any]:
        """Get entry by id."""
        populate_param: dict[str, Any] = _stringify_parameters('populate', populate)
        fields_param: dict[str, Any] = _stringify_parameters('fields', fields)
        params: dict[str, Any] = {
            **populate_param,
            **fields_param
        }
        url: str = f'{self.baseurl}api/{plural_api_id}/{document_id}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self._get_auth_header(), params=params) as res:
                if res.status != 200:
                    raise RuntimeError(f'Unable to get entry, error {res.status}: {res.reason}')
                return await res.json()

    async def get_entries(
            self,
            plural_api_id: str,
            sort: list[str] | None = None,
            filters: dict | None = None,
            populate: list[str] | None = None,
            fields: list[str] | None = None,
            pagination: dict | None = None,
            publication_state: str | None = None,
            get_all: bool = False,
            batch_size: int = 100
    ) -> dict[str, Any]:
        """Get list of entries. Optionally can operate in batch mode to get all entries automatically."""
        sort_param: dict[str, Any] = _stringify_parameters('sort', sort)
        filters_param: dict[str, Any] = _stringify_parameters('filters', filters)
        populate_param: dict[str, Any] = _stringify_parameters('populate', populate)
        fields_param: dict[str, Any] = _stringify_parameters('fields', fields)
        pagination_param: dict[str, Any] = _stringify_parameters('pagination', pagination)
        publication_state_param: dict[str, Any] = _stringify_parameters('publicationState', publication_state)
        url: str = f'{self.baseurl}api/{plural_api_id}'
        params: dict[str, Any] = {
            **sort_param,
            **filters_param,
            **pagination_param,
            **populate_param,
            **fields_param,
            **publication_state_param
        }
        async with aiohttp.ClientSession() as session:
            if not get_all:
                return await self._get_entries(session, url, params)
            else:
                page: int = 1
                get_more: bool = True
                while get_more:
                    pagination: dict[str, int] = {
                        'page': page,
                        'pageSize': batch_size
                    }
                    pagination_param: dict[str, Any] = _stringify_parameters('pagination', pagination)
                    key: str
                    for key in pagination_param:
                        params[key] = pagination_param[key]
                    res_page: dict[str, Any] = await self._get_entries(session, url, params)
                    if page == 1:
                        res: dict[str, Any] = res_page
                    else:
                        res['data'] += res_page['data']
                        res['meta'] = res_page['meta']
                    page += 1
                    pages_total: int = res['meta']['pagination']['pageCount']
                    get_more = page <= pages_total
                return res

    async def create_entry(
            self,
            plural_api_id: str,
            data: dict
    ) -> dict[str, Any]:
        """Create entry."""
        url: str = f'{self.baseurl}api/{plural_api_id}'
        body: dict[str, dict] = {
            'data': data
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=body, headers=self._get_auth_header()) as res:
                if res.status != 200:
                    raise RuntimeError(f'Unable to create entry, error {res.status}: {res.reason}')
                return await res.json()

    async def update_entry(
            self,
            plural_api_id: str,
            document_id: str,
            data: dict
    ) -> dict[str, Any]:
        """Update entry fields."""
        url: str = f'{self.baseurl}api/{plural_api_id}/{document_id}'
        body: dict[str, dict] = {
            'data': data
        }
        async with aiohttp.ClientSession() as session:
            async with session.put(url, json=body, headers=self._get_auth_header()) as res:
                if res.status != 200:
                    raise RuntimeError(f'Unable to update entry, error {res.status}: {res.reason}')
                return await res.json()

    async def delete_entry(
            self,
            plural_api_id: str,
            document_id: str
    ) -> dict[str, Any]:
        """Delete entry by id."""
        url: str = f'{self.baseurl}api/{plural_api_id}/{document_id}'
        async with aiohttp.ClientSession() as session:
            async with session.delete(url, headers=self._get_auth_header()) as res:
                if res.status != 200:
                    raise RuntimeError(f'Unable to delete entry, error {res.status}: {res.reason}')
                return await res.json()

    async def upsert_entry(
            self,
            plural_api_id: str,
            data: dict,
            keys: list[str],
            unique: bool = True
    ) -> dict[str, Any]:
        """Create entry or update fields."""
        filters: dict[str, dict[str, str]] = {}
        key: str
        for key in keys:
            if data[key] is not None:
                filters[key] = {'$eq': data[key]}
            else:
                filters[key] = {'$null': 'true'}
        current_rec: dict[str, Any] = await self.get_entries(
            plural_api_id=plural_api_id,
            fields=['id'],
            sort=['id:desc'],
            filters=filters,
            pagination={'page': 1, 'pageSize': 1}
        )
        rec_total: int = current_rec['meta']['pagination']['total']
        if unique and rec_total > 1:
            raise RuntimeError(f'Keys are ambiguous, found {rec_total} records')
        elif rec_total >= 1:
            return await self.update_entry(
                plural_api_id=plural_api_id,
                document_id=current_rec['data'][0]['id'],
                data=data
            )
        else:
            return await self.create_entry(
                plural_api_id=plural_api_id,
                data=data
            )

    async def send_post_request(
            self,
            route: str,
            body: dict | None = None
    ) -> dict[str, Any]:
        """Send POST request to custom endpoint."""
        route = route.lstrip('/')
        url: str = f'{self.baseurl}api/{route}'
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=body, headers=self._get_auth_header()) as res:
                if res.status != 200:
                    raise RuntimeError(f'Unable to send POST request, error {res.status}: {res.reason}')
                return await res.json()

    async def send_get_request(
            self,
            route: str
    ) -> dict[str, Any]:
        """Send GET request to custom endpoint."""
        route = route.lstrip('/')
        url: str = f'{self.baseurl}api/{route}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self._get_auth_header()) as res:
                if res.status != 200:
                    raise RuntimeError(f'Unable to send GET request, error {res.status}: {res.reason}')
                return await res.json()

    async def upload_files(
            self,
            files: list,
            ref: str | None = None,
            ref_id: int | None = None,
            field: str | None = None
    ) -> dict[str, Any]:
        """Upload files."""
        url: str = f'{self.baseurl}api/upload'
        data = aiohttp.FormData()
        for file in files:
            full_path: str = file
            filename: str = os.path.basename(full_path)
            data.add_field('files', open(full_path, 'rb'), filename=filename)
        if ref and ref_id and field:
            data.add_field('ref', ref)
            data.add_field('refId', str(ref_id))
            data.add_field('field', field)
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, headers=self._get_auth_header()) as res:
                if res.status != 200:
                    raise RuntimeError(f'Unable to send POST request, error {res.status}: {res.reason}')
                return await res.json()

    async def get_uploaded_files(
            self,
            filters: dict | None = None
    ) -> list[dict[str, Any]]:
        """Get uploaded files."""
        url: str = f'{self.baseurl}api/upload/files'
        filters_param: dict[str, Any] = _stringify_parameters('filters', filters)
        params: dict[str, Any] = {
            **filters_param
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=self._get_auth_header()) as res:
                if res.status != 200:
                    raise RuntimeError(f'Unable to get uploaded files, error {res.status}: {res.reason}')
                return await res.json()

    def _get_auth_header(self) -> dict | None:
        """Compose auth header from token."""
        if self._token:
            return {'Authorization': 'Bearer ' + self._token}

    async def _get_entries(
            self,
            session: aiohttp.ClientSession,
            url: str,
            params: dict[str, Any]
    ) -> dict[str, Any]:
        """Helper function to get entries."""
        async with session.get(
                url,
                headers=self._get_auth_header(),
                params=params
        ) as res:
            if res.status != 200:
                raise RuntimeError(f'Unable to get entries, error {res.status}: {res.reason}')
            return await res.json()


def process_data(entry: dict[str, Any]) -> dict[str, Any] | list[dict[str, Any]]:
    """Process response with entries."""
    data: dict[str, Any] | list[dict[str, Any]] | None = entry['data']
    if data is None:
        return {}
    elif type(data) is list:
        return [{'id': d['id'], **d['attributes']} for d in data]
    else:
        return {'id': data['id'], **data['attributes']}


def process_response(response: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Process response with entries."""
    entries: list[dict[str, Any]] = process_data(response)
    pagination: dict[str, Any] = response['meta']['pagination']
    return entries, pagination


def _stringify_parameters(name: str, parameters: dict | list[str] | None) -> dict[str, Any]:
    """Stringify dict for query parameters."""
    if type(parameters) is dict:
        return {name + k: v for k, v in _flatten_parameters(parameters)}
    elif type(parameters) is str:
        return {name: parameters}
    elif type(parameters) is list:
        return {f'{name}[{i}]': p for i, p in enumerate(parameters)}
    else:
        return {}


def _flatten_parameters(parameters: dict[str, Any]) -> tuple[str, Any]:
    """Flatten parameters dict for query."""
    for key, value in parameters.items():
        if isinstance(value, dict):
            for key1, value1 in _flatten_parameters(value):
                yield f'[{key}]{key1}', value1
        else:
            yield f'[{key}]', value
