from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, field_serializer, Field, ConfigDict

from .document_history import TrackedItem
from .item import Item
from .util import enum_to_str


class FileSource(Enum):
    CARTA = 'Carta'
    HYPERTHOUGHT = 'HyperThought'


class StorageType(Enum):
    DYNAMODB = "DynamoDb"
    S3 = "S3"
    LOCAL = "Local"


class FileType(Enum):
    FILE = 'File'
    DIRECTORY = 'Directory'
    WORKSPACE = 'Workspace'


class StorageInfo(BaseModel):
    storage_type: StorageType = Field(alias='storageType')
    container: str = Field(default=None)
    path: str = Field(default=None)
    compressed: bool

    enumConverter = field_serializer('storage_type')(enum_to_str)


class File(TrackedItem):
    storage_info: StorageInfo = Field(alias="storageInfo")


class FileInformation(Item):
    path: str = Field(default=None)
    name: str
    source: FileSource
    type: FileType
    owner: str
    date_created: datetime = Field(alias="dateCreated", default=None)
    date_modified: datetime = Field(alias="dateModified", default=None)

    enumConverter = field_serializer('source', 'type')(enum_to_str)


class PresignedFile(BaseModel):
    file_path: str = Field(alias='filePath')
    upload_url: str = Field(alias='uploadUrl')
    download_url: str = Field(alias='downloadUrl')
    upload_id: str = Field(alias='uploadId')

    model_config = ConfigDict(
        populate_by_name=True,
    )


class ETag(BaseModel):
    checksum_crc32: str = Field(alias='checksumCRC32')
    checksum_crc32c: str = Field(alias='checksumCRC32C')
    checksum_sha1: str = Field(alias='checksumSHA1')
    checksum_sha256: str = Field(alias='checksumSHA256')
    part_number: int = Field(alias='partNumber', default=None)
    e_tag: str = Field(alias='eTag')

    model_config = ConfigDict(
        populate_by_name=True,
    )
