from pydantic import Field, field_serializer

from .user import UserType
from .item import Item
from .util import enum_to_str


class PermissionEntity(Item):
    user_id: str = Field(alias='userId')
    user_type: UserType = Field(alias='userType')

    user_type_serializer = field_serializer('user_type')(enum_to_str)
