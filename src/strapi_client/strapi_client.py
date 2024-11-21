from typing import Any
import os.path
import aiohttp
from .strapi_client_base import StrapiClientBase
from .utils import stringify_parameters, compose_request_parameters


class StrapiClient(StrapiClientBase):
    """REST API client for Strapi."""
    base_url: str
    _auth_header: dict[str, str] | None = None

    async def authorize(
            self,
            identifier: str | None = None,
            password: str | None = None,
            token: str | None = None
    ) -> None:
        """Set up access token or retrieve it using identifier and password."""
        if token is None:
            if not identifier or not password:
                raise ValueError('Either token or identifier and password must be provided')
            url: str = self.base_url + 'api/auth/local'
            body: dict[str, str] = {
                'identifier': identifier,
                'password': password
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=body) as res:
                    if res.status != 200:
                        raise RuntimeError(f'Unable to authorize, error {res.status}: {res.reason}')
                    res_obj: dict[str, Any] = await res.json()
                    token = str(res_obj['jwt'])
        self._auth_header = {'Authorization': 'Bearer ' + token}

    async def get_entry(
            self,
            plural_api_id: str,
            document_id: str,
            populate: list[str] | None = None,
            fields: list[str] | None = None
    ) -> dict[str, Any]:
        """Get entry by id."""
        params: dict[str, Any] = compose_request_parameters(
            populate=populate,
            fields=fields
        )
        url: str = f'{self.base_url}api/{plural_api_id}/{document_id}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self._auth_header, params=params) as res:
                if res.status != 200:
                    raise RuntimeError(f'Unable to get entry, error {res.status}: {res.reason}')
                return await res.json()

    async def get_entries(
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
        """Get list of entries. Optionally can operate in batch mode to get all entries automatically."""
        url: str = f'{self.base_url}api/{plural_api_id}'
        params: dict[str, Any] = compose_request_parameters(
            sort=sort,
            filters=filters,
            populate=populate,
            fields=fields,
            pagination=pagination,
            publication_state=publication_state,
        )
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
                    pagination_param: dict[str, Any] = stringify_parameters('pagination', pagination)
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
            data: dict[str, Any]
    ) -> dict[str, Any]:
        """Create entry."""
        url: str = f'{self.base_url}api/{plural_api_id}'
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={'data': data}, headers=self._auth_header) as res:
                if res.status != 200:
                    raise RuntimeError(f'Unable to create entry, error {res.status}: {res.reason}')
                return await res.json()

    async def update_entry(
            self,
            plural_api_id: str,
            document_id: str,
            data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update entry fields."""
        url: str = f'{self.base_url}api/{plural_api_id}/{document_id}'
        async with aiohttp.ClientSession() as session:
            async with session.put(url, json={'data': data}, headers=self._auth_header) as res:
                if res.status != 200:
                    raise RuntimeError(f'Unable to update entry, error {res.status}: {res.reason}')
                return await res.json()

    async def delete_entry(
            self,
            plural_api_id: str,
            document_id: str
    ) -> dict[str, Any]:
        """Delete entry by id."""
        url: str = f'{self.base_url}api/{plural_api_id}/{document_id}'
        async with aiohttp.ClientSession() as session:
            async with session.delete(url, headers=self._auth_header) as res:
                if res.status != 200:
                    raise RuntimeError(f'Unable to delete entry, error {res.status}: {res.reason}')
                return await res.json()

    async def upsert_entry(
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
        current_rec: dict[str, Any] = await self.get_entries(
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
            return await self.update_entry(
                plural_api_id=plural_api_id,
                document_id=current_rec['data'][0]['documentId'],
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
        url: str = f'{self.base_url}api/{route}'
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=body, headers=self._auth_header) as res:
                if res.status != 200:
                    raise RuntimeError(f'Unable to send POST request, error {res.status}: {res.reason}')
                return await res.json()

    async def send_get_request(
            self,
            route: str
    ) -> dict[str, Any]:
        """Send GET request to custom endpoint."""
        route = route.lstrip('/')
        url: str = f'{self.base_url}api/{route}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self._auth_header) as res:
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
        url: str = f'{self.base_url}api/upload'
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
            async with session.post(url, data=data, headers=self._auth_header) as res:
                if res.status != 200:
                    raise RuntimeError(f'Unable to send POST request, error {res.status}: {res.reason}')
                return await res.json()

    async def get_uploaded_files(
            self,
            filters: dict | None = None
    ) -> list[dict[str, Any]]:
        """Get uploaded files."""
        url: str = f'{self.base_url}api/upload/files'
        params: dict[str, Any] = compose_request_parameters(filters=filters)
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=self._auth_header) as res:
                if res.status != 200:
                    raise RuntimeError(f'Unable to get uploaded files, error {res.status}: {res.reason}')
                return await res.json()

    async def _get_entries(
            self,
            session: aiohttp.ClientSession,
            url: str,
            params: dict[str, Any]
    ) -> dict[str, Any]:
        """Helper function to get entries."""
        async with session.get(url, headers=self._auth_header, params=params) as res:
            if res.status != 200:
                raise RuntimeError(f'Unable to get entries, error {res.status}: {res.reason}')
            return await res.json()
