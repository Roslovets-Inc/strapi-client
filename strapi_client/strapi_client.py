from typing import Union, Optional, List, Tuple
import os.path
import aiohttp


class StrapiClient:
    """REST API client for Strapi."""

    baseurl: str
    _token: Optional[str] = None

    def __init__(self, baseurl: str) -> None:
        """Initialize client."""
        if not baseurl.endswith('/'):
            baseurl = baseurl + '/'
        self.baseurl = baseurl

    async def authorize(
            self,
            identifier: Optional[str] = None,
            password: Optional[str] = None,
            token: Optional[str] = None
    ) -> None:
        """Set up or retrieve access token."""
        if token:
            self._token = token
        else:
            if not identifier or not password:
                raise ValueError('Either token or identifier and password must be provided')
            url: str = self.baseurl + 'api/auth/local'
            body: dict = {
                'identifier': identifier,
                'password': password
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=body) as res:
                    if res.status != 200:
                        raise Exception(f'Unable to authorize, error {res.status}: {res.reason}')
                    res_obj = await res.json()
                    token = res_obj['jwt']
                self._token = token

    async def get_entry(
            self,
            plural_api_id: str,
            document_id: int,
            populate: Optional[List[str]] = None,
            fields: Optional[List[str]] = None
    ) -> dict:
        """Get entry by id."""
        populate_param: dict = _stringify_parameters('populate', populate)
        fields_param: dict = _stringify_parameters('fields', fields)
        params: dict = {
            **populate_param,
            **fields_param
        }
        url: str = f'{self.baseurl}api/{plural_api_id}/{document_id}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self._get_auth_header(), params=params) as res:
                if res.status != 200:
                    raise Exception(f'Unable to get entry, error {res.status}: {res.reason}')
                return await res.json()

    async def get_entries(
            self,
            plural_api_id: str,
            sort: Optional[List[str]] = None,
            filters: Optional[dict] = None,
            populate: Optional[List[str]] = None,
            fields: Optional[List[str]] = None,
            pagination: Optional[dict] = None,
            publication_state: Optional[str] = None,
            get_all: bool = False,
            batch_size: int = 100
    ) -> dict:
        """Get list of entries. Optionally can operate in batch mode to get all entries automatically."""
        sort_param: dict = _stringify_parameters('sort', sort)
        filters_param: dict = _stringify_parameters('filters', filters)
        populate_param: dict = _stringify_parameters('populate', populate)
        fields_param: dict = _stringify_parameters('fields', fields)
        pagination_param: dict = _stringify_parameters('pagination', pagination)
        publication_state_param: dict = _stringify_parameters('publicationState', publication_state)
        url: str = f'{self.baseurl}api/{plural_api_id}'
        params: dict = {
            **sort_param,
            **filters_param,
            **pagination_param,
            **populate_param,
            **fields_param,
            **publication_state_param
        }
        async with aiohttp.ClientSession() as session:
            if not get_all:
                res: dict = await self._get_entries(session, url, params)
                return res
            else:
                page: int = 1
                get_more: bool = True
                while get_more:
                    pagination: dict = {
                        'page': page,
                        'pageSize': batch_size
                    }
                    pagination_param: dict = _stringify_parameters('pagination', pagination)
                    key: str
                    for key in pagination_param:
                        params[key] = pagination_param[key]
                    res_page = await self._get_entries(session, url, params)
                    if page == 1:
                        res = res_page
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
    ) -> dict:
        """Create entry."""
        url: str = f'{self.baseurl}api/{plural_api_id}'
        body: dict = {
            'data': data
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=body, headers=self._get_auth_header()) as res:
                if res.status != 200:
                    raise Exception(f'Unable to create entry, error {res.status}: {res.reason}')
                return await res.json()

    async def update_entry(
            self,
            plural_api_id: str,
            document_id: int,
            data: dict
    ) -> dict:
        """Update entry fields."""
        url: str = f'{self.baseurl}api/{plural_api_id}/{document_id}'
        body: dict = {
            'data': data
        }
        async with aiohttp.ClientSession() as session:
            async with session.put(url, json=body, headers=self._get_auth_header()) as res:
                if res.status != 200:
                    raise Exception(f'Unable to update entry, error {res.status}: {res.reason}')
                return await res.json()

    async def delete_entry(
            self,
            plural_api_id: str,
            document_id: int
    ) -> dict:
        """Delete entry by id."""
        url: str = f'{self.baseurl}api/{plural_api_id}/{document_id}'
        async with aiohttp.ClientSession() as session:
            async with session.delete(url, headers=self._get_auth_header()) as res:
                if res.status != 200:
                    raise Exception(f'Unable to delete entry, error {res.status}: {res.reason}')
                return await res.json()

    async def upsert_entry(
            self,
            plural_api_id: str,
            data: dict,
            keys: List[str],
            unique: bool = True
    ) -> dict:
        """Create entry or update fields."""
        filters: dict = {}
        key: str
        for key in keys:
            if data[key] is not None:
                filters[key] = {'$eq': data[key]}
            else:
                filters[key] = {'$null': 'true'}
        current_rec: dict = await self.get_entries(
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
            body: Optional[dict] = None
    ) -> dict:
        """Send POST request to custom endpoint."""
        route = route.lstrip('/')
        url: str = f'{self.baseurl}api/{route}'
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=body, headers=self._get_auth_header()) as res:
                if res.status != 200:
                    raise Exception(f'Unable to send POST request, error {res.status}: {res.reason}')
                return await res.json()

    async def send_get_request(
            self,
            route: str
    ) -> dict:
        """Send GET request to custom endpoint."""
        route = route.lstrip('/')
        url: str = f'{self.baseurl}api/{route}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self._get_auth_header()) as res:
                if res.status != 200:
                    raise Exception(f'Unable to send GET request, error {res.status}: {res.reason}')
                return await res.json()

    async def upload_files(
            self,
            files: list,
            ref: Optional[str] = None,
            ref_id: Optional[int] = None,
            field: Optional[str] = None
    ) -> dict:
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
                    raise Exception(f'Unable to send POST request, error {res.status}: {res.reason}')
                return await res.json()

    async def get_uploaded_files(
            self,
            filters: Optional[dict] = None
    ) -> list[dict]:
        """Get uploaded files."""
        url: str = f'{self.baseurl}api/upload/files'
        filters_param: dict = _stringify_parameters('filters', filters)
        params: dict = {
            **filters_param
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=self._get_auth_header()) as res:
                if res.status != 200:
                    raise Exception(f'Unable to get uploaded files, error {res.status}: {res.reason}')
                return await res.json()

    def _get_auth_header(self) -> Optional[dict]:
        """Compose auth header from token."""
        if self._token:
            header: Optional[dict] = {'Authorization': 'Bearer ' + self._token}
        else:
            header = None
        return header

    async def _get_entries(self, session, url, params) -> dict:
        """Helper function to get entries."""
        async with session.get(
                url,
                headers=self._get_auth_header(),
                params=params
        ) as res:
            if res.status != 200:
                raise Exception(f'Unable to get entries, error {res.status}: {res.reason}')
            res_dict: dict = await res.json()
            return res_dict


def process_data(entry: dict) -> Union[dict, List[dict]]:
    """Process response with entries."""
    data: Optional[Union[dict, List[dict]]] = entry['data']
    if data is None:
        return {}
    elif type(data) is list:
        return [{'id': d['id'], **d['attributes']} for d in data]
    else:
        return {'id': data['id'], **data['attributes']}


def process_response(response: dict) -> Tuple[List[dict], dict]:
    """Process response with entries."""
    entries: List[dict] = process_data(response)
    pagination: dict = response['meta']['pagination']
    return entries, pagination


def _stringify_parameters(name: str, parameters: Union[dict, List[str], None]) -> dict:
    """Stringify dict for query parameters."""
    if type(parameters) is dict:
        return {name + k: v for k, v in _flatten_parameters(parameters)}
    elif type(parameters) is str:
        return {name: parameters}
    elif type(parameters) is list:
        return {f'{name}[{i}]': p for i, p in enumerate(parameters)}
    else:
        return {}


def _flatten_parameters(parameters: dict):
    """Flatten parameters dict for query."""
    for key, value in parameters.items():
        if isinstance(value, dict):
            for key1, value1 in _flatten_parameters(value):
                yield f'[{key}]{key1}', value1
        else:
            yield f'[{key}]', value
