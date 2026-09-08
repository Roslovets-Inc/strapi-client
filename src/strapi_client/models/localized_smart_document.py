from typing import ClassVar

from strapi_client.models.smart_document import SmartDocument


class LocalizedSmartDocument(SmartDocument):
    """SmartDocument for Strapi content types with internationalization enabled."""

    __abstract_smart_document__: ClassVar[bool] = True
    locale: str

    __managed_fields__: ClassVar[set[str]] = SmartDocument.__managed_fields__ | {"locale"}
