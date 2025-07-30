from enum import Enum

from pydantic import BaseModel, Field, ConfigDict

from .permissions import PermissionsField


class Item(BaseModel):
    id: str = Field(default=None)
    permissions: PermissionsField = Field(alias='permission', default=None)

    model_config = ConfigDict(
        populate_by_name=True,
    )
