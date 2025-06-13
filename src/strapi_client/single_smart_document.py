from typing import Self, Any, ClassVar
import re
from .strapi_client_async import StrapiClientAsync
from .types import BaseDocument
from .model_utils import get_model_fields_and_population


class SingleSmartDocument(BaseDocument):
    """Fully automated ORM class for single Strapi document."""
    __single_api_id__: ClassVar[str]

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        super().__pydantic_init_subclass__(**kwargs)
        if '__single_api_id__' not in cls.__dict__:
            name = re.sub(r'(?<!^)(?=[A-Z])', '-', cls.__name__).lower()
            cls.__single_api_id__ = name

    @classmethod
    async def get_document(
            cls,
            client: StrapiClientAsync,
    ) -> Self:
        """Get single document by single api id."""
        response = await client.get_single_document(
            single_api_id=cls.__single_api_id__
        )
        return cls.from_scalar_response(response)
