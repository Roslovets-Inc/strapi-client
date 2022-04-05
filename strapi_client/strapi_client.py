from typing import Union, Optional, List
import aiohttp


class StrapiClient:
    """RESP API client for Strapi."""

    baseurl: str = None
    _token: str = None

    def __init__(self, baseurl: str) -> None:
        """Initialize client."""
        if not baseurl.endswith('/'):
            baseurl = baseurl + '/'
        self.baseurl = baseurl

    async def authorize(self, identifier: str, password: str, token: str = None) -> None:
        """Set up or retrieve access token."""
        if not token:
            url = self.baseurl + 'api/auth/local'
            body = {
                'identifier': identifier,
                'password': password
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=body) as res:
                    if res.status != 200:
                        raise Exception(f'Unable to authorize, error {res.status}')
                    res_obj = await res.json()
                    token = res_obj['jwt']
                self._token = token

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
        """Get list of entries. Optionally can operate in batch mode to get all entities automatically."""
        sort_param = _stringify_parameters('sort', sort)
        filters_param = _stringify_parameters('filters', filters)
        populate_param = _stringify_parameters('populate', populate)
        fields_param = _stringify_parameters('fields', fields)
        pagination_param = _stringify_parameters('pagination', pagination)
        publication_state_param = _stringify_parameters('publicationState', publication_state)
        url = f'{self.baseurl}api/{plural_api_id}'
        params = {
            **sort_param,
            **filters_param,
            **pagination_param,
            **populate_param,
            **fields_param,
            **publication_state_param
        }
        async with aiohttp.ClientSession() as session:
            if not get_all:
                res_obj = await self._get_entities(session, url, params)
                return res_obj
            else:
                page = 1
                get_more = True
                while get_more:
                    pagination = {
                        'page': page,
                        'pageSize': batch_size
                    }
                    pagination_param = _stringify_parameters('pagination', pagination)
                    for key in pagination_param:
                        params[key] = pagination_param[key]
                    res_obj1 = await self._get_entities(session, url, params)
                    if page == 1:
                        res_obj = res_obj1
                    else:
                        res_obj['data'] += res_obj1['data']
                        res_obj['meta'] = res_obj1['meta']
                    page += 1
                    pages = res_obj['meta']['pagination']['pageCount']
                    get_more = page <= pages
                return res_obj

    async def update_entry(
            self,
            plural_api_id: str,
            document_id: int,
            data: dict
    ) -> None:
        """Update entry fields."""
        url = f'{self.baseurl}api/{plural_api_id}/{document_id}'
        body = {
            'data': data
        }
        async with aiohttp.ClientSession() as session:
            async with session.put(url, json=body, headers=self._get_auth_header()) as res:
                if res.status != 200:
                    raise Exception(f'Unable to update entry, error {res.status}')

    def _get_auth_header(self) -> Optional[dict]:
        """Compose auth header from token."""
        if self._token:
            header = {'Authorization': 'Bearer ' + self._token}
        else:
            header = None
        return header

    async def _get_entities(self, session, url, params) -> dict:
        """Helper function to get entities."""
        async with session.get(
                url,
                headers=self._get_auth_header(),
                params=params
        ) as res:
            if res.status != 200:
                raise Exception(f'Unable to get entries, error {res.status}: {res.reason}')
            res_obj = await res.json()
            return res_obj


def process_response(response: dict) -> (dict, dict):
    """Process response with entries."""
    data = response['data']
    entries = [{'id': entry['id'], **entry['attributes']} for entry in data]
    pagination = response['meta']['pagination']
    return entries, pagination


def _stringify_parameters(name: str, parameters: Union[dict, List[str], None]) -> dict:
    """Stringify dict for query parameters."""
    if type(parameters) is dict:
        return {name + k: v for k, v in _flatten_parameters(parameters)}
    elif type(parameters) is str:
        return {name: parameters}
    elif type(parameters) is list:
        return {name: ','.join(parameters)}
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
