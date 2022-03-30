import requests


class StrapiClient:
    """RESP API client for Strapi."""

    baseurl: str = None
    _token: str = None

    def __init__(self, baseurl: str):
        if not baseurl.endswith('/'):
            baseurl = baseurl + '/'
        self.baseurl = baseurl

    def authorize(self, identifier: str, password: str, token: str = None):
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

    def get_entries(self, plural_api_id: str, filters: dict = None) -> dict:
        """Get list of entries."""
        if filters:
            filters_param = self._stringify_params('filters', filters)
        else:
            filters_param = {}
        url = f'{self.baseurl}api/{plural_api_id}'
        resp = requests.get(url, headers=self._get_auth_header(), params={**filters_param})
        if resp.status_code != 200:
            raise Exception(f'Unable to get entries, error {resp.status_code}')
        resp_obj = resp.json()
        return resp_obj

    def update_entry(self, plural_api_id: str, document_id: int, data: dict):
        """Update entry fields."""
        url = f'{self.baseurl}api/{plural_api_id}/{document_id}'
        body = {
            'data': data
        }
        resp = requests.put(url, json=body, headers=self._get_auth_header())
        if resp.status_code != 200:
            raise Exception(f'Unable to update entry, error {resp.status_code}')

    def _get_auth_header(self) -> dict:
        """Compose auth header from token."""
        if self._token:
            header = {'Authorization': 'Bearer ' + self._token}
        else:
            header = None
        return header

    @staticmethod
    def _stringify_params(name, parameters):
        """Stringify dict ro query parameters."""
        def flatten(d):
            for k, v in d.items():
                if isinstance(v, dict):
                    for s, i in flatten(v):
                        yield '[%s]%s' % (k, s), i
                else:
                    yield '[%s]' % k, v
        return {name + k: v for k, v in flatten(parameters)}
