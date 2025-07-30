# from typing import BinaryIO
# from pathlib import Path
# from pycarta import get_agent
from ..auth.agent import CartaAgent
from .types import (
    # ETag,
    FileSource,
    FileInformation,
    # PresignedFile,
)


def list_file_sources(*, agent: None | CartaAgent=None) -> list[str]:
    "Lists the file sources available to the authenticated user."
    if not agent:
        from pycarta import get_agent
    agent = agent or get_agent()
    response = agent.get('files')
    return response.json()

def file_source_support(source: str | FileSource, *, agent: None | CartaAgent=None) -> list[str]:
    "Lists the functions that a source supports."
    if not agent:
        from pycarta import get_agent
    agent = agent or get_agent()
    source = FileSource(source) if isinstance(source, str) else source
    response = agent.get(f"files/{source.value}/support")
    support: list[str] = response.json().split(',')
    support = list(map(lambda s: s.strip(), support))
    return support

def list_files(source: str | FileSource, path: str = None, *, agent: None | CartaAgent=None) -> list[FileInformation]:
    "Lists the files in a given path."
    if not agent:
        from pycarta import get_agent
    agent = agent or get_agent()
    source = FileSource(source) if isinstance(source, str) else source
    response = agent.get(f"files/{source.value}/list",
                         params={
                             "path": path,
                             "partial": source == FileSource.HYPERTHOUGHT
                        })

    return [FileInformation(**_file) for _file in response.json()]

def get_file(
    source: str | FileSource,
    file_id: str,
    container_id: None | str=None,
    *,
    agent: None | CartaAgent=None
) -> bytes:
    """
    Retrieves a file from a named file source, a list of which can be retrieved
    using `list_file_sources()`.

    *Note* This returns a byte stream of the file's contents, not a unicode
    stream.

    Parameters
    ----------
    source : str | FileSource
        The name of the file source.
    file_id : str
        The ID of the file to retrieve.
    container_id : str, (null effect)
        The ID of the container from which to retrieve the file. This
        is reserved for future use and currently has no effect.

    Returns
    -------
    bytes
        The contents of the file.
    """
    if not agent:
        from pycarta import get_agent
    agent = agent or get_agent()
    source = FileSource(source) if isinstance(source, str) else source
    response = agent.get(f"files/{source.value}/file/{file_id}",
                         params={"containerId": container_id})
    return response.content
