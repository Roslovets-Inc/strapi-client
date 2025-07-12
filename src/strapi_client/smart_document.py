from typing import Self, Any, ClassVar
import re
from .strapi_client_async import StrapiClientAsync
from .types import BaseDocument, ResponseMeta
from .model_utils import get_model_fields_and_population


class SmartDocument(BaseDocument):
    """Fully automated ORM class for Strapi documents."""
    __plural_api_id__: ClassVar[str]

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        super().__pydantic_init_subclass__(**kwargs)
        if '__plural_api_id__' not in cls.__dict__:
            name = re.sub(r'(?<!^)(?=[A-Z])', '-', cls.__name__).lower()
            cls.__plural_api_id__ = name + 's'

    @classmethod
    async def get_document(
            cls,
            client: StrapiClientAsync,
            document_id: str,
    ) -> Self:
        """Get document by document id."""
        fields, populate = get_model_fields_and_population(cls)
        response = await client.get_document(
            plural_api_id=cls.__plural_api_id__,
            document_id=document_id,
            fields=fields,
            populate=populate,
        )
        return cls.from_scalar_response(response)

    @classmethod
    async def get_documents(
            cls,
            client: StrapiClientAsync,
            sort: list[str] | None = None,
            filters: dict[str, Any] | None = None,
            publication_state: str | None = None,
            locale: str | None = None,
            start: int | None = 0,
            page: int | None = None,
            limit: int = 25,
            with_count: bool = True,
    ) -> list[Self]:
        """Get list of documents."""
        fields, populate = get_model_fields_and_population(cls)
        response = await client.get_documents(
            plural_api_id=cls.__plural_api_id__,
            sort=sort,
            filters=filters,
            populate=populate,
            fields=fields,
            publication_state=publication_state,
            locale=locale,
            page=page,
            start=start,
            batch_size=limit,
            with_count=with_count,
        )
        return cls.from_list_response(response)

    @classmethod
    async def get_documents_with_meta(
            cls,
            client: StrapiClientAsync,
            sort: list[str] | None = None,
            filters: dict[str, Any] | None = None,
            publication_state: str | None = None,
            locale: str | None = None,
            start: int | None = 0,
            page: int | None = None,
            limit: int = 25,
            with_count: bool = True,
    ) -> tuple[list[Self], ResponseMeta]:
        """Get list of documents."""
        fields, populate = get_model_fields_and_population(cls)
        response = await client.get_documents(
            plural_api_id=cls.__plural_api_id__,
            sort=sort,
            filters=filters,
            populate=populate,
            fields=fields,
            publication_state=publication_state,
            locale=locale,
            page=page,
            start=start,
            batch_size=limit,
            with_count=with_count,
        )
        return cls.from_list_response(response), response.meta

    @classmethod
    async def get_first_document(
            cls,
            client: StrapiClientAsync,
            sort: list[str] | None = None,
            filters: dict[str, Any] | None = None,
            publication_state: str | None = None,
            locale: str | None = None,
    ) -> Self | None:
        """First documents if available."""
        fields, populate = get_model_fields_and_population(cls)
        response = await client.get_documents(
            plural_api_id=cls.__plural_api_id__,
            sort=sort,
            filters=filters,
            populate=populate,
            fields=fields,
            publication_state=publication_state,
            locale=locale,
            start=0,
            batch_size=1,
            with_count=False,
        )
        return cls.first_from_list_response(response)
