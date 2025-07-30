from pydantic import Field

from .item import Item


class Project(Item):
    name: str
    bucket_name: str = Field(alias='bucketName')
