from typing import Any, Dict, Annotated, Optional

from pydantic import BaseModel, BeforeValidator, PlainSerializer


class Group(BaseModel):
    name: str
    organization: Optional[str] = None

    def __str__(self):
        return f"{self.organization}:{self.name}" if self.organization else self.name


def from_str(data: Any) -> Dict:
    if ':' in data:
        name = data.split(':')
        return {'name': name[1], 'organization': name[0]}
    else:
        return {'name': data}


def serialize_group(group: Group) -> str:
    return str(group)


SerializeGroup = Annotated[Group, BeforeValidator(from_str), PlainSerializer(serialize_group)]
