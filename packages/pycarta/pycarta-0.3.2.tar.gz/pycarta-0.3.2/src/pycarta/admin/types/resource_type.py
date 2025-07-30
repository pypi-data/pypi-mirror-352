from enum import Enum

from .file import File
from .namespace import Namespace
from .project import Project
from .service import Service
from .workspace import Workspace
from .connection import Connection


class ResourceType(Enum):
    WORKSPACE = "Workspace"
    CONNECTION = "Connection"
    FILE = "File"
    NAMESPACE = "Namespace"
    SERVICE = "Service"
    PROJECT = "Project"


def get_resource_class(resource: str | ResourceType):
    if isinstance(resource, str):
        try:
            resource = ResourceType[resource]
        except KeyError:
            resource = ResourceType(resource)
    return {
        ResourceType.WORKSPACE: Workspace,
        ResourceType.CONNECTION: Connection,
        ResourceType.FILE: File,
        ResourceType.NAMESPACE: Namespace,
        ResourceType.SERVICE: Service,
        ResourceType.PROJECT: Project,
    }[resource]
