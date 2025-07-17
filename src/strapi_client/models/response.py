from typing import Any
from pydantic import BaseModel, Field


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
