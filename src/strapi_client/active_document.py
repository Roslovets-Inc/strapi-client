from typing import Self, Any, ClassVar
import datetime
import hashlib
import json
import warnings
from pydantic import BaseModel, Field, PrivateAttr
from .strapi_client_async import StrapiClientAsync


def DocumentField(*args, unique: bool = False, relation: bool = False, **kwargs):
    field_info = Field(*args, **kwargs)
    field_info.metadata.append({'unique': unique, 'relation': relation})
    return field_info


class ActiveDocument(BaseModel):
    """Experimental ORM class for Strapi document."""
    __plural_api_id__: ClassVar[str]
    __managed_fields__: ClassVar[set[str]] = {
        'id', 'document_id', 'created_at', 'updated_at', 'published_at', '__plural_api_id__',
        '__managed_fields__'
    }
    _relations_populated: bool = PrivateAttr(default=False)
    id: int | None = DocumentField(default=None, unique=True)
    document_id: str | None = DocumentField(default=None, alias='documentId', unique=True)
    created_at: datetime.datetime | None = Field(default=None, alias='createdAt')
    updated_at: datetime.datetime | None = Field(default=None, alias='updatedAt')
    published_at: datetime.datetime | None = Field(default=None, alias='publishedAt')

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        super().__pydantic_init_subclass__(**kwargs)
        if '__plural_api_id__' not in cls.__dict__:
            cls.__plural_api_id__ = cls.__name__.lower() + 's'

    @classmethod
    async def get_document(
            cls,
            client: StrapiClientAsync,
            document_id: str,
            populate_all: bool = True,
    ) -> Self:
        """Get document by document id."""
        response = await client.get_document(
            plural_api_id=cls.__plural_api_id__,
            document_id=document_id,
            populate=list(cls._get_relation_fields()) if populate_all else None,
        )
        return cls.model_validate(response.data)

    @classmethod
    async def get_documents(
            cls,
            client: StrapiClientAsync,
            populate_all: bool = True,
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
        response = await client.get_documents(
            plural_api_id=cls.__plural_api_id__,
            sort=sort,
            filters=filters,
            populate=list(cls._get_relation_fields()) if populate_all else None,
            fields=list(cls._get_document_fields(with_relations=False)),
            publication_state=publication_state,
            locale=locale,
            page=page,
            start=start,
            batch_size=limit,
            with_count=with_count,
        )
        documents = [cls.model_validate(document) for document in response.data]
        if populate_all:
            for document in documents:
                document.set_relations_populated(populate_all)
        return documents

    async def create_document(self, client: StrapiClientAsync) -> Self:
        """Create new document from object."""
        response = await client.create_document(
            plural_api_id=self.__plural_api_id__,
            data=self.model_dump_variable()
        )
        return self.model_validate(response.data)

    async def update_document(self, client: StrapiClientAsync) -> Self:
        """Update document fields from object."""
        if not self.document_id:
            raise RuntimeError("Document ID cannot be empty to update document")
        if not self.relations_populated():
            warnings.warn(
                'Some relations are not populated, so all relations will not be updated. Use refresh() method to populate relations.'
            )
            # TODO: relations: set, connect, disconnect. Preserve hashing. Check warning
            data = self.model_dump_variable(exclude=self._get_relation_fields())
        else:
            data = self.model_dump_variable()
        response = await client.update_document(
            plural_api_id=self.__plural_api_id__,
            document_id=self.document_id,
            data=data
        )
        return self.model_validate(response.data)

    async def delete_document(self, client: StrapiClientAsync) -> None:
        """Delete document attached to object."""
        if not self.document_id:
            raise RuntimeError("Document ID cannot be empty to delete document")
        await client.delete_document(
            plural_api_id=self.__plural_api_id__,
            document_id=self.document_id
        )

    def relations_populated(self) -> bool:
        return self._relations_populated or not self._get_relation_fields()

    def set_relations_populated(self, value: bool) -> Self:
        self._relations_populated = value
        return self

    async def refresh(self, client: StrapiClientAsync, populate_all: bool = True) -> Self:
        """Refresh object with latest data from Strapi including relations."""
        if not self.document_id:
            raise RuntimeError("Document ID cannot be empty to refresh object")
        document = await self.__class__.get_document(client, self.document_id, populate_all=populate_all)
        for field in document.model_fields:
            setattr(self, field, getattr(document, field))

        self.set_relations_populated(populate_all)
        return self

    async def upsert_document(self, client: StrapiClientAsync) -> Self:
        """Create document or update fields."""
        keys: set[str] = self._unique_fields - self.__managed_fields__
        if not keys:
            raise RuntimeError("For upsert at least one model field should be declared as unique")
        model_dict = self.model_dump_variable()
        filters = {key: {"$eq": model_dict[key]} for key in keys}
        cur_response = await client.get_documents(
            plural_api_id=self.__plural_api_id__,
            filters=filters,
            fields=list(self._get_document_fields()),
            start=0,
            batch_size=1,
            with_count=True,
        )
        total_count: int = cur_response.meta.get_total_count()
        if total_count > 1:
            raise RuntimeError(f"Keys are ambiguous, found {total_count} records")
        elif total_count == 0:
            return await self.create_document(client)
        else:
            cur_document = self.model_validate(cur_response.data[0])
            if cur_document.model_hash() == self.model_hash():
                return cur_document
            else:
                self.id = cur_document.id
                self.document_id = cur_document.document_id
                return await self.update_document(client)

    def model_dump_variable(self, exclude: set[str] | None = None) -> dict[str, Any]:
        exclude = exclude or set()
        model_dict = self.model_dump(by_alias=True, exclude=self.__managed_fields__ | exclude)
        for rel in self._get_relation_fields():
            if model_dict.get(rel):
                model_dict[rel] = {'set': model_dict[rel]['documentId']}
        return model_dict

    def model_hash(self) -> str:
        dumped_str = json.dumps(self.model_dump_variable(), sort_keys=True, default=str)
        return hashlib.sha256(dumped_str.encode('utf-8')).hexdigest()

    @property
    def _unique_fields(self) -> set[str]:
        return {
            f for f, info in self.model_fields.items()
            if any(m.get('unique', False) for m in info.metadata)
        }

    @classmethod
    def _get_document_fields(cls, with_relations: bool = True) -> set[str]:
        return {
            info.alias or f
            for f, info in cls.__pydantic_fields__.items()
            if with_relations or not any(m.get('relation', False) for m in info.metadata)
        }

    @classmethod
    def _get_relation_fields(cls) -> set[str]:
        return {
            info.alias or f
            for f, info in cls.__pydantic_fields__.items()
            if any(m.get('relation', False) for m in info.metadata)
        }
