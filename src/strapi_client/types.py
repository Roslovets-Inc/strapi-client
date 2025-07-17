from typing import Literal

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
