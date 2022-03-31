from typing import Union
import requests


class StrapiClient:
    """RESP API client for Strapi."""

    baseurl: str = None
    _token: str = None

    def __init__(self, baseurl: str) -> None:
        """Initialize client."""
        if not baseurl.endswith('/'):
            baseurl = baseurl + '/'
        self.baseurl = baseurl

    def authorize(self, identifier: str, password: str, token: str = None) -> None:
        """Set up or retrieve access token."""
        if not token:
            url = self.baseurl + 'api/auth/local'
            body = {
                'identifier': identifier,
                'password': password
            }
            res = requests.post(url, json=body)
            if res.status_code != 200:
                raise Exception(f'Unable to authorize, error {res.status_code}')
            res_obj = res.json()
            token = res_obj['jwt']
        self._token = token

    def get_entries(
            self,
            plural_api_id: str,
            filters: Union[dict, None] = None,
            pagination: Union[dict, None] = None,
            publication_state: Union[str, None] = None
    ) -> dict:
        """Get list of entries."""
        filters_param = _stringify_parameters('filters', filters)
        pagination_param = _stringify_parameters('pagination', pagination)
        publication_state_param = _stringify_parameters('publicationState', publication_state)
        url = f'{self.baseurl}api/{plural_api_id}'
        resp = requests.get(
            url,
            headers=self._get_auth_header(),
            params={**filters_param, **pagination_param, **publication_state_param}
        )
        if resp.status_code != 200:
            raise Exception(f'Unable to get entries, error {resp.status_code}')
        resp_obj = resp.json()
        return resp_obj

    def update_entry(
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
        resp = requests.put(url, json=body, headers=self._get_auth_header())
        if resp.status_code != 200:
            raise Exception(f'Unable to update entry, error {resp.status_code}')

    def _get_auth_header(self) -> Union[dict, None]:
        """Compose auth header from token."""
        if self._token:
            header = {'Authorization': 'Bearer ' + self._token}
        else:
            header = None
        return header


def process_response(response: dict) -> (dict, dict):
    """Process response with entries."""
    data = response['data']
    entries = [{'id': entry['id'], **entry['attributes']} for entry in data]
    pagination = response['meta']['pagination']
    return entries, pagination


def _stringify_parameters(name: str, parameters: Union[dict, None]) -> dict:
    """Stringify dict for query parameters."""
    if type(parameters) is dict:
        return {name + k: v for k, v in _flatten_parameters(parameters)}
    elif type(parameters) is str:
        return {name: parameters}
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
