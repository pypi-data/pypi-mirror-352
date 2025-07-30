
from pydantic import BaseModel, Field, BeforeValidator, PlainSerializer
from enum import Enum
from typing import Annotated


class Permissions(BaseModel):
    execute: bool = Field(default=False)
    write: bool = Field(default=False)
    read: bool = Field(default=False)
    clone: bool = Field(default=False)
    admin: bool = Field(default=False)


class PermissionsRole(Enum):
    NONE = 'None'
    GUEST = 'Guest'
    USER = 'User'
    EDITOR = 'Editor'
    OWNER = 'Owner'


def convert_permissions_from_str(value: str):
    # perms = list(map(lambda s: s.lower().strip(), value.split(',')))  # Fails on empty string
    perms = [s.lower().strip() for s in value.split(',') if s]
    return Permissions(**dict(zip(perms, [True, ] * len(perms))))


def convert_permissions_to_str(value: Permissions | None, _info) -> str:
    return ", ".join([key.capitalize() for key, v in dict(value or dict()).items() if v])


PermissionsField = Annotated[
    Permissions, BeforeValidator(convert_permissions_from_str), PlainSerializer(convert_permissions_to_str)
]
