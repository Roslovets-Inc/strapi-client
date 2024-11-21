from typing import Any
import os
import requests
from .strapi_client_base import StrapiClientBase
from .utils import stringify_parameters, compose_request_parameters


class StrapiClientSync(StrapiClientBase):
    """Synchronous REST API client for Strapi."""
    base_url: str
    _auth_header: dict[str, str] | None = None

    def authorize(
            self,
            identifier: str | None = None,
            password: str | None = None,
            token: str | None = None
    ) -> None:
        """Set up access token or retrieve it using identifier and password."""
        if token is None:
            if not identifier or not password:
                raise ValueError('Either token or identifier and password must be provided')
            url = self.base_url + 'api/auth/local'
            body = {
                'identifier': identifier,
                'password': password
            }
            res = requests.post(url, json=body)
            if res.status_code >= 400:
                raise RuntimeError(f'Unable to authorize, error {res.status_code}: {res.reason}')
            res_obj = res.json()
            token = str(res_obj['jwt'])
        self._auth_header = {'Authorization': 'Bearer ' + token}

    def get_entry(
            self,
            plural_api_id: str,
            document_id: str,
            populate: list[str] | None = None,
            fields: list[str] | None = None
    ) -> dict[str, Any]:
        """Get entry by ID."""
        params = compose_request_parameters(populate=populate, fields=fields)
        url = f'{self.base_url}api/{plural_api_id}/{document_id}'
        res = requests.get(url, headers=self._auth_header, params=params)
        if res.status_code >= 400:
            raise RuntimeError(f'Unable to get entry, error {res.status_code}: {res.reason}')
        return res.json()

    def get_entries(
            self,
            plural_api_id: str,
            sort: list[str] | None = None,
            filters: dict[str, Any] | None = None,
            populate: list[str] | None = None,
            fields: list[str] | None = None,
            pagination: dict | None = None,
            publication_state: str | None = None,
            get_all: bool = False,
            batch_size: int = 100
    ) -> dict[str, Any]:
        """Get list of entries. Supports batch mode to retrieve all entries."""
        url = f'{self.base_url}api/{plural_api_id}'
        params = compose_request_parameters(
            sort=sort,
            filters=filters,
            populate=populate,
            fields=fields,
            pagination=pagination,
            publication_state=publication_state,
        )
        if not get_all:
            res = requests.get(url, headers=self._auth_header, params=params)
            if res.status_code >= 400:
                raise RuntimeError(f'Unable to get entries, error {res.status_code}: {res.reason}')
            return res.json()

        # Batch mode
        page = 1
        all_data = []
        while True:
            params.update(stringify_parameters('pagination', {'page': page, 'pageSize': batch_size}))
            res = requests.get(url, headers=self._auth_header, params=params)
            if res.status_code >= 400:
                raise RuntimeError(f'Unable to get entries, error {res.status_code}: {res.reason}')
            data = res.json()
            all_data.extend(data['data'])
            if page >= data['meta']['pagination']['pageCount']:
                break
            page += 1
        return {'data': all_data}

    def create_entry(
            self,
            plural_api_id: str,
            data: dict[str, Any]
    ) -> dict[str, Any]:
        """Create entry."""
        url = f'{self.base_url}api/{plural_api_id}'
        res = requests.post(url, json={'data': data}, headers=self._auth_header)
        if res.status_code >= 400:
            raise RuntimeError(f'Unable to create entry, error {res.status_code}: {res.reason}')
        return res.json()

    def update_entry(
            self,
            plural_api_id: str,
            document_id: str,
            data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update entry fields."""
        url = f'{self.base_url}api/{plural_api_id}/{document_id}'
        res = requests.put(url, json={'data': data}, headers=self._auth_header)
        if res.status_code >= 400:
            raise RuntimeError(f'Unable to update entry, error {res.status_code}: {res.reason}')
        return res.json()

    def delete_entry(
            self,
            plural_api_id: str,
            document_id: str
    ) -> dict[str, Any]:
        """Delete entry by ID."""
        url = f'{self.base_url}api/{plural_api_id}/{document_id}'
        res = requests.delete(url, headers=self._auth_header)
        if res.status_code >= 400:
            raise RuntimeError(f'Unable to delete entry, error {res.status_code}: {res.reason}')
        return res.json()

    def upsert_entry(
            self,
            plural_api_id: str,
            data: dict[str, Any],
            keys: list[str],
            unique: bool = True
    ) -> dict[str, Any]:
        """Create entry or update fields."""
        filters: dict[str, dict[str, str]] = {}
        for key in keys:
            if data[key] is not None:
                filters[key] = {'$eq': data[key]}
            else:
                filters[key] = {'$null': 'true'}
        current_rec: dict[str, Any] = self.get_entries(
            plural_api_id=plural_api_id,
            fields=['documentId'],
            sort=['documentId:desc'],
            filters=filters,
            pagination={'page': 1, 'pageSize': 1}
        )
        rec_total: int = current_rec['meta']['pagination']['total']
        if unique and rec_total > 1:
            raise RuntimeError(f'Keys are ambiguous, found {rec_total} records')
        elif rec_total >= 1:
            return self.update_entry(
                plural_api_id=plural_api_id,
                document_id=current_rec['data'][0]['documentId'],
                data=data
            )
        else:
            return self.create_entry(
                plural_api_id=plural_api_id,
                data=data
            )

    def send_post_request(
            self,
            route: str,
            body: dict | None = None
    ) -> dict[str, Any]:
        """Send POST request to a custom endpoint."""
        route = route.lstrip('/')
        url = f'{self.base_url}api/{route}'
        res = requests.post(url, json=body, headers=self._auth_header)
        if res.status_code >= 400:
            raise RuntimeError(f'Unable to send POST request, error {res.status_code}: {res.reason}')
        return res.json()

    def send_get_request(
            self,
            route: str
    ) -> dict[str, Any]:
        """Send GET request to a custom endpoint."""
        route = route.lstrip('/')
        url = f'{self.base_url}api/{route}'
        res = requests.get(url, headers=self._auth_header)
        if res.status_code >= 400:
            raise RuntimeError(f'Unable to send GET request, error {res.status_code}: {res.reason}')
        return res.json()

    def upload_files(
            self,
            files: list,
            ref: str | None = None,
            ref_id: int | None = None,
            field: str | None = None
    ) -> dict[str, Any]:
        """Upload files."""
        url = f'{self.base_url}api/upload'
        with requests.Session() as session:
            files_data = [
                ('files', (os.path.basename(file), open(file, 'rb')))
                for file in files
            ]
            data = {}
            if ref and ref_id and field:
                data.update({'ref': ref, 'refId': str(ref_id), 'field': field})
            res = session.post(url, files=files_data, data=data, headers=self._auth_header)
            if res.status_code >= 400:
                raise RuntimeError(f'Unable to upload files, error {res.status_code}: {res.reason}')
            return res.json()
