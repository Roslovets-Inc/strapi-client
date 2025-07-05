from typing import Any
from pathlib import Path
from io import BytesIO
from urllib.parse import urljoin
import httpx
from .strapi_client_base import StrapiClientBase
from .types import (
    DocumentsResponse, DocumentResponse, ApiParameters, AuthPayload, AuthResponse
)


class StrapiClientAsync(StrapiClientBase):
    """Async REST API client for Strapi."""
    _client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        self.open()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    def open(self) -> httpx.AsyncClient:
        # Fallback to creating a client if not used in a context manager.
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def close(self):
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        if not self._client:
            raise RuntimeError("Client is not initialized.")
        return self._client

    async def authorize(
            self,
            identifier: str,
            password: str,
    ) -> None:
        """Get auth token using identifier and password."""
        res = await self.send_post_request(
            "auth/local",
            json=AuthPayload(identifier=identifier, password=password).model_dump(),
            use_auth=False
        )
        self._token = AuthResponse.model_validate(res.json()).jwt

    async def get_single_document(self, single_api_id: str) -> DocumentResponse:
        """Get document of single type."""
        res = await self.send_get_request(single_api_id)
        return DocumentResponse.model_validate(res.json())

    async def get_document(
            self,
            plural_api_id: str,
            document_id: str,
            populate: list[str] | dict[str, Any] | str | None = None,
            fields: list[str] | None = None,
    ) -> DocumentResponse:
        """Get document by document id."""
        params = ApiParameters(populate=populate, fields=fields)
        res = await self.send_get_request(
            f"{plural_api_id}/{document_id}",
            params=params.stringify()
        )
        return DocumentResponse.model_validate(res.json())

    async def get_documents(
            self,
            plural_api_id: str,
            sort: list[str] | None = None,
            filters: dict[str, Any] | None = None,
            populate: list[str] | dict[str, Any] | str | None = None,
            fields: list[str] | None = None,
            publication_state: str | None = None,
            locale: str | None = None,
            start: int | None = 0,
            page: int | None = None,
            batch_size: int = 25,
            with_count: bool = True,
    ) -> DocumentsResponse:
        """Get list of documents. By default, operates in batch mode to get all documents automatically."""
        params = ApiParameters(
            sort=sort,
            filters=filters,
            populate=populate,
            fields=fields,
            page=page,
            page_size=batch_size,
            start=start,
            limit=batch_size,
            publication_state=publication_state,
            locale=locale,
        )
        if params.page is not None or params.start is not None:  # Get specific page/batch
            res = await self.send_get_request(plural_api_id, params=params.stringify())
            return DocumentsResponse.model_validate(res.json())
        else:  # Get all records
            params.start = 0
            params.with_count = True
            res = await self.send_get_request(plural_api_id, params=params.stringify())
            res_page = DocumentsResponse.model_validate(res.json())
            start_list = [i for i in range(batch_size, res_page.meta.get_total_count(), batch_size)]
            all_data = res_page
            for cur_start in start_list:
                params.start = cur_start
                params.with_count = with_count
                res = await self.send_get_request(plural_api_id, params=params.stringify())
                res_page = DocumentsResponse.model_validate(res.json())
                all_data.data += res_page.data
                all_data.meta = res_page.meta
            return all_data

    async def create_or_update_single_document(self, single_api_id: str, data: dict[str, Any]) -> DocumentResponse:
        """Create or update single type document."""
        res = await self.send_put_request(single_api_id, body={"data": data})
        return DocumentResponse.model_validate(res.json())

    async def create_document(
            self, plural_api_id: str, data: dict[str, Any]
    ) -> DocumentResponse:
        """Create new document."""
        res = await self.send_post_request(
            plural_api_id,
            json={"data": data},
        )
        return DocumentResponse.model_validate(res.json())

    async def update_document(
            self, plural_api_id: str, document_id: str, data: dict[str, Any]
    ) -> DocumentResponse:
        """Update document fields."""
        res = await self.send_put_request(
            f"{plural_api_id}/{document_id}",
            body={"data": data},
        )
        return DocumentResponse.model_validate(res.json())

    async def delete_single_document(self, single_api_id: str) -> None:
        """Delete single type document."""
        await self.send_delete_request(single_api_id)

    async def delete_document(
            self, plural_api_id: str, document_id: str
    ) -> None:
        """Delete document by document id."""
        await self.send_delete_request(f"{plural_api_id}/{document_id}")

    async def send_get_request(
            self,
            route: str,
            params: dict[str, Any] | None = None,
            use_auth: bool = True,
    ) -> httpx.Response:
        """Send GET request to custom endpoint."""
        res = await self.client.get(
            url=urljoin(self.api_url, route),
            params=params,
            headers=self._auth_header if use_auth else None
        )
        self._check_response(res, "Unable to send GET request")
        return res

    async def send_put_request(
            self,
            route: str,
            body: dict[str, Any] | None = None,
            params: dict[str, Any] | None = None,
            use_auth: bool = True,
    ) -> httpx.Response:
        """Send PUT request to custom endpoint."""
        res = await self.client.put(
            url=urljoin(self.api_url, route),
            json=body,
            params=params,
            headers=self._auth_header if use_auth else None
        )
        self._check_response(res, "Unable to send PUT request")
        return res

    async def send_post_request(
            self,
            route: str,
            json: dict[str, Any] | None = None,
            params: dict[str, Any] | None = None,
            data: dict[str, Any] | None = None,
            files: list | None = None,
            use_auth: bool = True,
    ) -> httpx.Response:
        """Send POST request to custom endpoint."""
        res = await self.client.post(
            url=urljoin(self.api_url, route),
            json=json,
            params=params,
            data=data,
            files=files,
            headers=self._auth_header if use_auth else None
        )
        self._check_response(res, "Unable to send POST request")
        return res

    async def send_delete_request(self, route: str, use_auth: bool = True) -> httpx.Response:
        """Send DELETE request to custom endpoint."""
        res = await self.client.delete(
            url=urljoin(self.api_url, route),
            headers=self._auth_header if use_auth else None
        )
        self._check_response(res, "Unable to send DELETE request")
        return res

    async def upload_files(
            self,
            files: list[Path | str],
            ref: str | None = None,
            ref_id: int | None = None,
            field: str | None = None,
    ) -> dict[str, Any]:
        """Upload list of files."""
        files_payload = []
        for path in files:
            path = Path(path)
            # Read file into memory.
            with path.open("rb") as f:
                bio = BytesIO(f.read())
            bio.name = path.name
            files_payload.append(("files", (path.name, bio, "application/octet-stream")))
        data: dict[str, Any] = {}
        if ref and ref_id and field:
            data = {"ref": ref, "refId": str(ref_id), "field": field}
        res = await self.send_post_request("upload", data=data, files=files_payload)
        self._check_response(res, "Unable to send POST request")
        return res.json() or {}

    async def get_uploaded_files(self, filters: dict | None = None) -> list[dict[str, Any]]:
        """Get uploaded files."""
        params = ApiParameters(filters=filters)
        res = await self.send_get_request("upload/files", params=params.stringify())
        return res.json()

    async def check_health(self) -> bool:
        """Check if Strapi API is available."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(urljoin(self.base_url, "_health"))
                res.raise_for_status()
                return True
        except Exception:
            return False
