from typing import Any
import asyncio
import platform
from .strapi_client import StrapiClient

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class StrapiClientSync:
    """RESP API client for Strapi."""

    _strapi_client: StrapiClient

    def __init__(self, baseurl: str) -> None:
        """Initialize client."""
        self._strapi_client = StrapiClient(baseurl=baseurl)

    def authorize(
            self,
            identifier: str | None = None,
            password: str | None = None,
            token: str | None = None
    ) -> None:
        """Set up or retrieve access token."""
        args = locals()
        del args['self']
        asyncio.run(self._strapi_client.authorize(
            **args
        ))

    def get_entry(
            self,
            plural_api_id: str,
            document_id: int,
            populate: list[str] | None = None,
            fields: list[str] | None = None
    ) -> dict[str, Any]:
        """Get entry by id."""
        args = locals()
        del args['self']
        return asyncio.run(self._strapi_client.get_entry(**args))

    def get_entries(
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
        """Get list of entries. Optionally can operate in batch mode to get all entities automatically."""
        args = locals()
        del args['self']
        return asyncio.run(self._strapi_client.get_entries(**args))

    def create_entry(
            self,
            plural_api_id: str,
            data: dict
    ) -> dict[str, Any]:
        """Create entry."""
        args = locals()
        del args['self']
        return asyncio.run(self._strapi_client.create_entry(**args))

    def update_entry(
            self,
            plural_api_id: str,
            document_id: int,
            data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update entry fields."""
        args = locals()
        del args['self']
        return asyncio.run(self._strapi_client.update_entry(**args))

    def delete_entry(
            self,
            plural_api_id: str,
            document_id: int
    ) -> dict[str, Any]:
        """Delete entry by id."""
        args = locals()
        del args['self']
        return asyncio.run(self._strapi_client.delete_entry(**args))

    def upsert_entry(
            self,
            plural_api_id: str,
            data: dict,
            keys: list[str],
            unique: bool = True
    ) -> dict[str, Any]:
        """Create entry or update fields."""
        args = locals()
        del args['self']
        return asyncio.run(self._strapi_client.upsert_entry(**args))

    def send_post_request(
            self,
            route: str,
            body: dict | None = None
    ) -> dict[str, Any]:
        """Send POST request to custom endpoint."""
        return asyncio.run(self._strapi_client.send_post_request(route=route, body=body))

    def send_get_request(
            self,
            route: str
    ) -> dict[str, Any]:
        """Send GET request to custom endpoint."""
        return asyncio.run(self._strapi_client.send_get_request(route=route))

    def upload_files(
            self,
            files: list,
            ref: str | None = None,
            ref_id: int | None = None,
            field: str | None = None
    ) -> dict[str, Any]:
        """Upload files."""
        return asyncio.run(self._strapi_client.upload_files(files=files, ref=ref, ref_id=ref_id, field=field))

    def get_uploaded_files(
            self,
            filters: dict | None = None
    ) -> list[dict[str, Any]]:
        """Get uploaded files."""
        return asyncio.run(self._strapi_client.get_uploaded_files(filters=filters))
