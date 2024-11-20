from abc import ABC, abstractmethod
from typing import Any


class StrapiClientBase(ABC):
    """Abstract base class for Strapi clients."""

    def __init__(self, base_url: str) -> None:
        """Initialize client."""
        self.base_url = base_url.rstrip('/') + '/'

    @abstractmethod
    def authorize(
            self,
            identifier: str | None = None,
            password: str | None = None,
            token: str | None = None
    ) -> Any:
        pass

    @abstractmethod
    def get_entry(
            self,
            plural_api_id: str,
            document_id: str,
            populate: list[str] | None = None,
            fields: list[str] | None = None
    ) -> Any:
        pass

    @abstractmethod
    def get_entries(
            self,
            plural_api_id: str,
            sort: list[str] | None = None,
            filters: dict | None = None,
            populate: list[str] | None = None,
            fields: list[str] | None = None,
            pagination: dict | None = None
    ) -> Any:
        pass

    @abstractmethod
    def create_entry(self, plural_api_id: str, data: dict) -> Any:
        pass

    @abstractmethod
    def update_entry(self, plural_api_id: str, document_id: str, data: dict) -> Any:
        pass

    @abstractmethod
    def delete_entry(self, plural_api_id: str, document_id: str) -> Any:
        pass
