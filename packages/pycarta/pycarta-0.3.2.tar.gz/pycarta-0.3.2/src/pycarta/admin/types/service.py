from pydantic import Field
from .document_history import TrackedItem
from .item import Item


class Service(TrackedItem):
    name: str
    base_url: str = Field(alias='baseUrl', default=None)
