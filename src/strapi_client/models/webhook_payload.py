import datetime
from pydantic import BaseModel, Field
from strapi_client.types import WebhookEventName
from strapi_client.models.base_document import BaseDocument


class WebhookPayload(BaseModel):
    event: WebhookEventName
    created_at: datetime.datetime = Field(alias='createdAt')
    model: str | None = None
    entry: BaseDocument | None = None
