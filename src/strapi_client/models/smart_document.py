from typing import Self, Any, ClassVar
from pydantic import BaseModel
import re
from ..strapi_client_async import StrapiClientAsync
from ..utils import serialize_document_data
from ..types import ResponseMeta
from .smart_document_utils import get_model_fields_and_population, extract_document_ids_from_document_fields
from .base_document import BaseDocument


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

    @classmethod
    async def create_document(
            cls,
            client: StrapiClientAsync,
            data: dict[str, Any] | BaseModel,
    ) -> Self:
        """Create a new document."""
        _, populate = get_model_fields_and_population(cls)
        response = await client.create_document(
            plural_api_id=cls.__plural_api_id__,
            data=serialize_document_data(data),
        )
        result_document = cls.from_scalar_response(response)
        if not populate:
            return result_document
        else:
            return await cls.get_document(client, result_document.document_id)

    async def refresh_document(self, client: StrapiClientAsync) -> Self:
        """Refresh the document with the latest data from Strapi."""
        fields, populate = get_model_fields_and_population(self.__class__)
        response = await client.get_document(
            plural_api_id=self.__plural_api_id__,
            document_id=self.document_id,
            fields=fields,
            populate=populate,
        )
        document = self.from_scalar_response(response)
        self.__dict__.update(document.__dict__)
        return self

    def model_dump_to_create(self) -> dict[str, Any]:
        """
        Serializes model to dict for creating a new Strapi record via API.

        Excludes documentId, createdAt, updatedAt, publishedAt fields.
        Handles nested BasePopulatable fields by replacing nested documents with their documentId.
        Supports nullable fields and lists of documents.

        Returns:
            dict[str, Any]: Dictionary suitable for creating a new Strapi record
        """
        # Get model data excluding the fields we don't want to send when creating
        exclude_fields = {'document_id', 'created_at', 'updated_at', 'published_at', 'id'}
        data = self.model_dump(exclude=exclude_fields, by_alias=True)
        fields_to_replace = extract_document_ids_from_document_fields(self)
        return data | fields_to_replace
