from .document_history import TrackedItem


class Workspace(TrackedItem):
    name: str = None
    archived: bool = None
