from typing import Union, Optional, List
import asyncio
import platform
from strapi_client import StrapiClient

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
            identifier: Optional[str] = None,
            password: Optional[str] = None,
            token: Optional[str] = None
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
            populate: Optional[List[str]] = None,
            fields: Optional[List[str]] = None
    ) -> dict:
        """Get entry by id."""
        args = locals()
        del args['self']
        return asyncio.run(self._strapi_client.get_entry(**args))

    def get_entries(
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
        args = locals()
        del args['self']
        return asyncio.run(self._strapi_client.get_entries(**args))

    def create_entry(
            self,
            plural_api_id: str,
            data: dict
    ) -> dict:
        """Create entry."""
        args = locals()
        del args['self']
        return asyncio.run(self._strapi_client.create_entry(**args))

    def update_entry(
            self,
            plural_api_id: str,
            document_id: int,
            data: dict
    ) -> dict:
        """Update entry fields."""
        args = locals()
        del args['self']
        return asyncio.run(self._strapi_client.update_entry(**args))

    def delete_entry(
            self,
            plural_api_id: str,
            document_id: int
    ) -> dict:
        """Delete entry by id."""
        args = locals()
        del args['self']
        return asyncio.run(self._strapi_client.delete_entry(**args))

    def upsert_entry(
            self,
            plural_api_id: str,
            data: dict,
            keys: List[str],
            unique: bool = True
    ) -> dict:
        """Create entry or update fields."""
        args = locals()
        del args['self']
        return asyncio.run(self._strapi_client.upsert_entry(**args))

    def send_post_request(
            self,
            route: str,
            body: Optional[dict] = None
    ) -> dict:
        """Send POST request to custom endpoint."""
        return asyncio.run(self._strapi_client.send_post_request(route=route, body=body))

    def send_get_request(
            self,
            route: str
    ) -> dict:
        """Send GET request to custom endpoint."""
        return asyncio.run(self._strapi_client.send_get_request(route=route))

    def upload_files(
            self,
            files: list[str],
            ref: Optional[str] = None,
            ref_id: Optional[int] = None,
            field: Optional[str] = None
    ) -> dict:
        """Upload files."""
        return asyncio.run(self._strapi_client.upload_files(files=files, ref=ref, ref_id=ref_id, field=field))

    def get_uploaded_files(
            self,
            filters: Optional[dict] = None
    ) -> list[dict]:
        """Get uploaded files."""
        return asyncio.run(self._strapi_client.get_uploaded_files(filters=filters))
