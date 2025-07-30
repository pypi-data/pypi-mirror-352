from pydantic import BaseModel, Field, ConfigDict

from .item import Item


class NativeId(BaseModel):
    file_id: str = Field(alias='fileId', default=None)
    bucket_name: str = Field(alias='bucketName', default=None)
    prefix: str = Field(default=None)

    model_config = ConfigDict(
        populate_by_name=True,
    )


class Connection(Item):
    name: str
    backend: str
    key_path: str = Field(alias='keyPath', default=None)
    native_id: NativeId = Field(alias='nativeId', default=None)
