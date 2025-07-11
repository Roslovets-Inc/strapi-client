from typing import Any, Self, Literal
import datetime
from pydantic import BaseModel, Field, SecretStr
from .utils import stringify_parameters


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


class BasePopulatable(BaseModel):
    """Strapi entry that can be populated in request."""


class DocumentResponse(BaseModel):
    data: dict[str, Any]


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


class BaseComponent(BasePopulatable):
    """Strapi component."""


class AuthPayload(BaseModel):
    identifier: str
    password: str


class AuthResponse(BaseModel):
    jwt: SecretStr


class ApiParameters(BaseModel):
    sort: list[str] | str | None = None
    filters: dict[str, Any] | None = None
    populate: list[str] | dict[str, Any] | str | None = None
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


class MediaImageFormatVariant(BaseModel):
    ext: str
    url: str
    hash: str
    mime: str
    name: str
    path: str | None = None
    size: float = Field(description='Size in kilobytes')
    width: int
    height: int
    size_in_bytes: int = Field(alias='sizeInBytes')


class MediaImageFormats(BaseModel):
    thumbnail: MediaImageFormatVariant | None = None
    small: MediaImageFormatVariant | None = None
    medium: MediaImageFormatVariant | None = None
    large: MediaImageFormatVariant | None = None

    @property
    def largest(self) -> MediaImageFormatVariant:
        if self.large: return self.large
        if self.medium: return self.medium
        if self.small: return self.small
        if self.thumbnail: return self.thumbnail
        raise ValueError('Image has no variants')


class MediaImageDocument(BaseDocument):
    name: str
    alternative_text: str | None = Field(default=None, alias='alternativeText')
    caption: str | None = None
    width: int
    height: int
    formats: MediaImageFormats
    hash: str
    ext: str
    mime: str
    size: float = Field(description='Size in kilobytes')
    url: str
    preview_url: str | None = Field(default=None, alias='previewUrl')
    provider: str
    provider_metadata: dict[str, Any] | None = None

    @property
    def largest_format(self) -> MediaImageFormatVariant:
        return self.formats.largest


WebhookEventName = Literal[
    "entry.create",
    "entry.update",
    "entry.delete",
    "entry.publish",
    "entry.unpublish",
    "media.create",
    "media.update",
    "media.delete",
    "releases.publish",
    "trigger-test",
]


class WebhookPayload(BaseModel):
    event: WebhookEventName
    created_at: datetime.datetime = Field(alias='createdAt')
    model: str | None = None
    entry: BaseDocument | None = None
