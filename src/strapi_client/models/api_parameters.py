from typing import Any
from pydantic import BaseModel
from ..utils import stringify_parameters


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
