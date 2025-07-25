from typing import Self, Any, ClassVar
from pydantic import BaseModel
import re
from pathlib import Path
from io import BytesIO
from ..strapi_client_async import StrapiClientAsync
from ..utils import serialize_document_data
from .response import ResponseMeta
from .smart_document_utils import get_model_fields_and_population
from .base_document import BaseDocument


class SmartDocument(BaseDocument):
    """Fully automated ORM class for Strapi documents."""
    __singular_api_id__: ClassVar[str]
    __plural_api_id__: ClassVar[str]
    __content_type_id__: ClassVar[str]

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        super().__pydantic_init_subclass__(**kwargs)
        if '__singular_api_id__' not in cls.__dict__:
            name = re.sub(r'(?<!^)(?=[A-Z])', '-', cls.__name__).lower()
            cls.__singular_api_id__ = name
        if '__plural_api_id__' not in cls.__dict__:
            cls.__plural_api_id__ = cls.__singular_api_id__ + 's'
        if '__content_type_id__' not in cls.__dict__:
            cls.__content_type_id__ = f'api::{cls.__singular_api_id__}.{cls.__singular_api_id__}'
        if not cls.__content_type_id__.startswith('api::'):
            raise ValueError(f'__content_type_id__ should start with "api::" for {cls.__name__}')

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
            start: int | None = None,
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
        result_document = BaseDocument.from_scalar_response(response)
        if not populate:
            return cls.from_scalar_response(response)
        else:
            return await cls.get_document(client, result_document.document_id)

    async def update_document(
            self,
            client: StrapiClientAsync,
            data: dict[str, Any] | BaseModel,
    ) -> Self:
        """Update existing document."""
        response = await client.update_document(
            plural_api_id=self.__plural_api_id__,
            document_id=self.document_id,
            data=serialize_document_data(data),
        )
        return await self.refresh_document(client)

    async def update_relations(
            self,
            client: StrapiClientAsync,
            field: str,
            relations: list[BaseDocument] | None = None,
            connect: list[BaseDocument] | None = None,
            disconnect: list[BaseDocument] | None = None,
    ) -> Self:
        """Update field relations."""
        if not relations and not connect and not disconnect:
            raise ValueError("At least one of relations, connect or disconnect should be provided")
        if relations and (connect or disconnect):
            raise ValueError("relations argument does not work with connect or disconnect arguments")
        if relations:
            data = {
                field: {
                    'set': [d.document_id for d in relations]
                }
            }
        else:
            data = {
                field: {
                    'connect': [d.document_id for d in connect or {}],
                    'disconnect': [d.document_id for d in disconnect or {}]
                }
            }
        response = await client.update_document(
            plural_api_id=self.__plural_api_id__,
            document_id=self.document_id,
            data=data,
        )
        return await self.refresh_document(client)

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

    async def delete_document(self, client: StrapiClientAsync) -> None:
        """Delete the document."""
        await client.delete_document(
            plural_api_id=self.__plural_api_id__,
            document_id=self.document_id,
        )

    async def upload_file(
            self,
            client: StrapiClientAsync,
            file: Path | str | dict[str, BytesIO],
            field: str
    ) -> Self:
        """Upload a file to the document's field."""
        if isinstance(file, dict):
            file_data: list[Path | str] | dict[str, BytesIO] = file
        else:
            file_data = [file]
        response = await client.upload_files(
            files=file_data,
            content_type_id=self.__content_type_id__,
            document_id=self.id,
            field=field,
        )
        return await self.refresh_document(client)
