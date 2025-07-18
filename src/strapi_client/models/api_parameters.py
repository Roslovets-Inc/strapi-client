from typing import Any
from pydantic import BaseModel
import qs_codec


class ApiParameters(BaseModel):
    """Parameters for Strapi API requests.
    
    This class represents the parameters that can be passed to Strapi API endpoints,
    such as sorting, filtering, pagination, etc. The stringify() method converts
    these parameters to a URL-encoded query string that can be directly passed to httpx.
    """
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

    def stringify(self) -> str:
        """Convert API parameters to a URL-encoded query string.
        
        Uses qs_codec to encode parameters in a format compatible with Strapi API.
        
        Returns:
            str: URL-encoded query string that can be directly passed to httpx.
        """
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
        params: dict[str, Any] = {}
        if self.sort:
            params['sort'] = self.sort
        if self.filters:
            params['filters'] = self.filters
        if self.populate:
            params['populate'] = self.populate
        if self.fields:
            params['fields'] = self.fields
        if pagination:
            params['pagination'] = pagination
        if self.publication_state:
            params['publicationState'] = self.publication_state
        if self.locale:
            params['locale'] = self.locale
        return qs_codec.encode(params)
