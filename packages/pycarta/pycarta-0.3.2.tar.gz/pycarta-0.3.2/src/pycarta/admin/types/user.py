from collections.abc import Hashable
from dataclasses import dataclass
from enum import Enum
from typing import List

from pydantic import BaseModel

from .group import SerializeGroup


class UserType(Enum):
    NAMESPACE = "NamespaceItem"
    PROJECT = "ProjectItem"
    USER = "User"
    GROUP = "UserGroup"
    WORKFLOW = "WorkflowItem"
    WORKSPACE = "WorkspaceItem"


class User(BaseModel, Hashable):
    name: str
    email: str=None
    organization: str=None
    id: str = None
    lastName: str = None
    firstName: str = None
    groups: List[SerializeGroup] = None

    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, value: "User") -> bool:
        return self.id == value.id


class UserAttribute(Enum):
    UserId = 0
    UserName = 1
    Email = 2
    FirstName = 3
    LastName = 4


class AttributeFilter(Enum):
    EQUALS = " = "
    STARTS_WITH = " ^= "


@dataclass
class UserFilter:
    attributeName: UserAttribute
    attributeValue: str
    attributeFilter: AttributeFilter

    def to_param(self):
        # return f"{self.attributeName}{self.attributeFilter.value}{self.attributeValue}"
        return {
            "attributeName": self.attributeName.value,
            "attributeValue": self.attributeValue,
            "attributeFilter": self.attributeFilter.value
        }
