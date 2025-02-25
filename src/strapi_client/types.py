from typing import Any, Self
import datetime
from pydantic import BaseModel, Field, SecretStr
from httpx import Response
from .utils import stringify_parameters


class BaseDocument(BaseModel):
    """Strapi document with standard fields."""
    id: int
    document_id: str = Field(alias='documentId')
    created_at: datetime.datetime = Field(alias='createdAt')
    updated_at: datetime.datetime = Field(alias='updatedAt')
    published_at: datetime.datetime = Field(alias='publishedAt')
    locale: str | None = None

    @classmethod
    def from_response(cls, response: Response) -> Self:
        return cls.model_validate(response.json())


class AuthPayload(BaseModel):
    identifier: str
    password: str


class AuthResponse(BaseModel):
    jwt: SecretStr


class ApiParameters(BaseModel):
    sort: list[str] | str | None = None
    filters: dict[str, Any] | None = None
    populate: list[str] | str | None = None
    fields: list[str] | str | None = None
    page: int | None = None
    page_size: int | None = None
    with_count: bool = True
    start: int | None = None
    limit: int | None = None
    publication_state: str | None = None
    locale: str | None = None

    def stringify(self) -> dict[str, Any]:
        if self.page is not None and self.page_size is not None:
            pagination = {
                'page': self.page,
                'pageSize': self.page_size,
                'withCount': self.with_count,
            }
        elif self.start is not None and self.limit is not None:
            pagination = {
                'start': self.start,
                'limit': self.limit,
                'withCount': self.with_count,
            }
        else:
            pagination = {}
        return {
            **(stringify_parameters('sort', self.sort) if self.sort else {}),
            **(stringify_parameters('filters', self.filters) if self.filters else {}),
            **(stringify_parameters('populate', self.populate) if self.populate else {}),
            **(stringify_parameters('fields', self.fields) if self.fields else {}),
            **(stringify_parameters('pagination', pagination)),
            **(stringify_parameters('publicationState', self.publication_state) if self.publication_state else {}),
            **(stringify_parameters('locale', self.locale) if self.locale else {}),
        }


class ResponsePagination(BaseModel):
    page: int | None = None
    page_size: int | None = Field(default=None, alias='pageSize')
    page_count: int | None = Field(default=None, alias='pageCount')
    start: int | None = None
    limit: int | None = None
    total: int | None = None


class ResponseMeta(BaseModel):
    pagination: ResponsePagination

    def get_total_count(self) -> int:
        if self.pagination.total is None:
            raise ValueError('Total count is not available in response')
        return self.pagination.total


class DocumentsResponse(BaseModel):
    data: list[dict[str, Any]]
    meta: ResponseMeta


class DocumentResponse(BaseModel):
    data: dict[str, Any]
