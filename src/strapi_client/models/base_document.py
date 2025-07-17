from typing import Any, Self
import datetime
from pydantic import Field
from .base_populatable import BasePopulatable
from ..models.response import DocumentResponse, DocumentsResponse


class BaseDocument(BasePopulatable):
    """Strapi document with standard fields."""
    id: int
    document_id: str = Field(alias='documentId')
    created_at: datetime.datetime = Field(alias='createdAt')
    updated_at: datetime.datetime = Field(alias='updatedAt')
    published_at: datetime.datetime = Field(alias='publishedAt')

    @classmethod
    def from_scalar_response(cls, response: DocumentResponse) -> Self:
        return cls.model_validate(response.data)

    @classmethod
    def from_list_response(cls, response: DocumentsResponse) -> list[Self]:
        return [cls.model_validate(d) for d in response.data]

    @classmethod
    def first_from_list_response(cls, response: DocumentsResponse) -> Self | None:
        return cls.model_validate(response.data[0]) if len(response.data) > 0 else None


class BaseDocumentWithLocale(BaseDocument):
    """Strapi document with standard fields and locale."""
    locale: str | None = None
