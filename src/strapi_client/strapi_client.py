from typing import Any
from pathlib import Path
from io import BytesIO
from urllib.parse import urljoin
import httpx
from .strapi_client_base import StrapiClientBase
from .types import (
    DocumentsResponse, DocumentResponse, ApiParameters, AuthPayload, AuthResponse
)


class StrapiClient(StrapiClientBase):
    """REST API client for Strapi."""
    _client: httpx.Client | None = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def open(self) -> httpx.Client:
        # Fallback to creating a client if not used in a context manager.
        if self._client is None:
            self._client = httpx.Client(timeout=self.timeout)
        return self._client

    def close(self):
        if self._client is not None:
            self._client.close()
            self._client = None

    @property
    def client(self) -> httpx.Client:
        if not self._client:
            raise RuntimeError("Client is not initialized.")
        return self._client

    def authorize(
            self,
            identifier: str,
            password: str,
    ) -> None:
        """Get auth token using identifier and password."""
        res = self.send_post_request(
            "auth/local",
            json=AuthPayload(identifier=identifier, password=password).model_dump(),
            use_auth=False
        )
        self._token = AuthResponse.model_validate(res.json()).jwt

    def get_single_document(self, single_api_id: str) -> DocumentResponse:
        """Get document of single type."""
        res = self.send_get_request(single_api_id)
        return DocumentResponse.model_validate(res.json())

    def get_document(
            self,
            plural_api_id: str,
            document_id: str,
            populate: list[str] | dict[str, Any] | str | None = None,
            fields: list[str] | None = None,
    ) -> DocumentResponse:
        """Get document by document id."""
        params = ApiParameters(populate=populate, fields=fields)
        res = self.send_get_request(
            f"{plural_api_id}/{document_id}",
            params=params.stringify()
        )
        return DocumentResponse.model_validate(res.json())

    def get_documents(
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
            res = self.send_get_request(plural_api_id, params=params.stringify())
            return DocumentsResponse.model_validate(res.json())
        else:  # Get all records
            params.start = 0
            params.with_count = True
            res = self.send_get_request(plural_api_id, params=params.stringify())
            res_page = DocumentsResponse.model_validate(res.json())
            start_list = [i for i in range(batch_size, res_page.meta.get_total_count(), batch_size)]
            all_data = res_page
            for cur_start in start_list:
                params.start = cur_start
                params.with_count = with_count
                res = self.send_get_request(plural_api_id, params=params.stringify())
                res_page = DocumentsResponse.model_validate(res.json())
                all_data.data += res_page.data
                all_data.meta = res_page.meta
            return all_data

    def create_or_update_single_document(self, single_api_id: str, data: dict[str, Any]) -> DocumentResponse:
        """Create or update single type document."""
        res = self.send_put_request(single_api_id, body={"data": data})
        return DocumentResponse.model_validate(res.json())

    def create_document(
            self, plural_api_id: str, data: dict[str, Any]
    ) -> DocumentResponse:
        """Create new document."""
        res = self.send_post_request(
            plural_api_id,
            json={"data": data},
        )
        return DocumentResponse.model_validate(res.json())

    def update_document(
            self, plural_api_id: str, document_id: str, data: dict[str, Any]
    ) -> DocumentResponse:
        """Update document fields."""
        res = self.send_put_request(
            f"{plural_api_id}/{document_id}",
            body={"data": data},
        )
        return DocumentResponse.model_validate(res.json())

    def delete_single_document(self, single_api_id: str) -> None:
        """Delete single type document."""
        self.send_delete_request(single_api_id)

    def delete_document(
            self, plural_api_id: str, document_id: str
    ) -> None:
        """Delete document by document id."""
        self.send_delete_request(f"{plural_api_id}/{document_id}")

    def send_get_request(
            self,
            route: str,
            params: dict[str, Any] | None = None,
            use_auth: bool = True,
    ) -> httpx.Response:
        """Send GET request to custom endpoint."""
        res = self.client.get(
            url=urljoin(self.api_url, route),
            params=params,
            headers=self._auth_header if use_auth else None
        )
        self._check_response(res, "Unable to send GET request")
        return res

    def send_put_request(
            self,
            route: str,
            body: dict[str, Any] | None = None,
            params: dict[str, Any] | None = None,
            use_auth: bool = True,
    ) -> httpx.Response:
        """Send PUT request to custom endpoint."""
        res = self.client.put(
            url=urljoin(self.api_url, route),
            json=body,
            params=params,
            headers=self._auth_header if use_auth else None
        )
        self._check_response(res, "Unable to send PUT request")
        return res

    def send_post_request(
            self,
            route: str,
            json: dict[str, Any] | None = None,
            params: dict[str, Any] | None = None,
            data: dict[str, Any] | None = None,
            files: list | None = None,
            use_auth: bool = True,
    ) -> httpx.Response:
        """Send POST request to custom endpoint."""
        res = self.client.post(
            url=urljoin(self.api_url, route),
            json=json,
            params=params,
            data=data,
            files=files,
            headers=self._auth_header if use_auth else None
        )
        self._check_response(res, "Unable to send POST request")
        return res

    def send_delete_request(self, route: str, use_auth: bool = True) -> httpx.Response:
        """Send DELETE request to custom endpoint."""
        res = self.client.delete(
            url=urljoin(self.api_url, route),
            headers=self._auth_header if use_auth else None
        )
        self._check_response(res, "Unable to send DELETE request")
        return res

    def upload_files(
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
        res = self.send_post_request("upload", data=data, files=files_payload)
        self._check_response(res, "Unable to send POST request")
        return res.json() or {}

    def get_uploaded_files(self, filters: dict | None = None) -> list[dict[str, Any]]:
        """Get uploaded files."""
        params = ApiParameters(filters=filters)
        res = self.send_get_request("upload/files", params=params.stringify())
        return res.json()

    def check_health(self) -> bool:
        """Check if Strapi API is available."""
        try:
            with httpx.Client(timeout=5.0) as client:
                res = client.get(urljoin(self.base_url, "_health"))
                res.raise_for_status()
                return True
        except Exception:
            return False
