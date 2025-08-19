from typing import Self, Any, ClassVar
from pydantic import BaseModel
import re
import warnings
from pathlib import Path
from io import BytesIO
from ..strapi_client_async import StrapiClientAsync
from ..utils import serialize_document_data, hash_model
from .response import ResponseMeta
from .smart_document_utils import get_model_fields_and_population, get_model_data
from .base_document import BaseDocument


class SmartDocument(BaseDocument):
    """Fully automated ORM class for Strapi documents."""
    __singular_api_id__: ClassVar[str]
    __plural_api_id__: ClassVar[str]
    __content_type_id__: ClassVar[str]
    __managed_fields__: ClassVar[set[str]] = {
        'id', 'document_id', 'created_at', 'updated_at', 'published_at',
        '__singular_api_id__', '__plural_api_id__', '__content_type_id__', '__managed_fields__'
    }

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        super().__pydantic_init_subclass__(**kwargs)
        if not hasattr(cls, '__singular_api_id__'):
            setattr(cls, '__singular_api_id__', re.sub(r'(?<!^)(?=[A-Z])', '-', cls.__name__).lower())
        if not hasattr(cls, '__plural_api_id__'):
            setattr(cls, '__plural_api_id__', f"{getattr(cls, '__singular_api_id__')}s")
        if not hasattr(cls, '__content_type_id__'):
            setattr(
                cls, '__content_type_id__',
                f"api::{getattr(cls, '__singular_api_id__')}.{getattr(cls, '__singular_api_id__')}"
            )

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
            limit: int = 100,
            with_count: bool = True,
    ) -> list[Self]:
        """Get list of documents."""
        fields, populate = get_model_fields_and_population(cls)
        response = await client.get_documents(
            plural_api_id=cls.__plural_api_id__,
            sort=sort or ['id'],
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
            start: int | None = None,
            page: int | None = None,
            limit: int = 100,
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
        response = await client.create_document(
            plural_api_id=cls.__plural_api_id__,
            data=serialize_document_data(data),
        )
        _, populate = get_model_fields_and_population(cls)
        if not populate:
            return cls.from_scalar_response(response)
        else:
            result_document = BaseDocument.from_scalar_response(response)
            return await cls.get_document(client, result_document.document_id)

    def model_dump_data(self, exclude_managed_fields: bool = False, json_mode: bool = False) -> dict[str, Any]:
        """
        Create a dictionary representation of the document.

        Args:
            exclude_managed_fields: If True, exclude fields listed in __managed_fields__
            json_mode: If True, serialize fields to JSON compatible types

        Returns:
            Dictionary representation of the document with nested BaseDocument instances
            replaced with their IDs
        """
        return get_model_data(self, exclude_managed_fields=exclude_managed_fields, json_mode=json_mode)

    def model_identical(
            self,
            data: dict[str, Any] | BaseModel,
            exclude_fields: list[str] | None = None
    ) -> bool:
        data_dict = data.model_dump(by_alias=True) if isinstance(data, BaseModel) else data
        data_dict_filtered = {
            k: v for k, v in data_dict.items() if k not in (exclude_fields or [])
        }
        record_dict = self.model_dump_data(exclude_managed_fields=True)
        record_dict_filtered = {
            k: v for k, v in record_dict.items() if k in data_dict_filtered
        }
        return hash_model(record_dict_filtered) == hash_model(data_dict_filtered)

    async def update_document(
            self,
            client: StrapiClientAsync,
            data: dict[str, Any] | BaseModel,
            lazy_mode: bool = False,
            do_not_compare_fields: list[str] | None = None,
    ) -> Self:
        """Update existing document."""
        _, populate = get_model_fields_and_population(self.__class__)
        if not lazy_mode and do_not_compare_fields:
            warnings.warn('do_not_compare_fields argument works only in lazy mode')
        elif lazy_mode and self.model_identical(data=data, exclude_fields=do_not_compare_fields):
            return self
        response = await client.update_document(
            plural_api_id=self.__plural_api_id__,
            document_id=self.document_id,
            data=serialize_document_data(data),
        )
        if not populate:
            result_document = self.__class__.from_scalar_response(response)
            self.__dict__.update(result_document.__dict__)
            return self
        else:
            return await self.refresh_document(client)

    async def lazy_update_document(
            self,
            client: StrapiClientAsync,
            data: dict[str, Any] | BaseModel,
            do_not_compare_fields: list[str] | None = None,
    ) -> bool:
        """Lazy update existing document fields without record synchronization."""
        if self.model_identical(data=data, exclude_fields=do_not_compare_fields):
            return False
        else:
            await client.update_document(
                plural_api_id=self.__plural_api_id__,
                document_id=self.document_id,
                data=serialize_document_data(data),
            )
            return True

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
            file: Path | str | dict[str, BytesIO | bytes | bytearray | memoryview],
            field: str
    ) -> Self:
        """Upload a file to the document's field."""
        if isinstance(file, dict):
            file_data: list[Path | str] | dict[str, BytesIO | bytes | bytearray | memoryview] = file
        else:
            file_data = [file]
        response = await client.upload_files(
            files=file_data,
            content_type_id=self.__content_type_id__,
            document_id=self.id,
            field=field,
        )
        return await self.refresh_document(client)
