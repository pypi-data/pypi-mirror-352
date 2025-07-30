from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .item import Item
from .user import User


class DocumentHistory(BaseModel):
    addedBy: User = Field(default=None)
    dateAdded: datetime = Field(default=None)
    dateModified: datetime = Field(default=None)
    modifiedBy: User = Field(default=None)


class TrackedItem(Item):
    document_history: DocumentHistory = Field(alias='documentHistory', default=None)
