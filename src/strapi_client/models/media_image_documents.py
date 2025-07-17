from typing import Any
from pydantic import Field
from ..types import MediaImageFormatVariant, MediaImageFormats
from .base_document import BaseDocument


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


def is_media_image_document(field_type: Any) -> bool:
    """
    Check if the type is MediaImageDocument.
    Media files in Strapi have special handling - they only need populate: true.
    """
    try:
        return (isinstance(field_type, type) and
                issubclass(field_type, MediaImageDocument))
    except (TypeError, AttributeError):
        return False
