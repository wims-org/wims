import pydantic
import requests

from dependencies import settings
from models.api import WebhookEvent
from models.category import Category
from models.item import File, Item
from models.reader import Reader
from models.user import User

settings = settings.get_settings()


class WebhookData(pydantic.BaseModel):
    event_type: WebhookEvent
    data: Item | Category | User | Reader | File


class WebhookHandler:
    def send_webhook(data: WebhookData):
        if not settings.webhook_url or data.event_type not in settings.webhook_events:
            return
        requests.post(url=settings.webhook_url, json=data.model_dump(mode="json"))