from ..auth.agent import CartaAgent
from .types import (
    Connection,
    Project,
)


def create_project(
        name: str,
        bucket: str,
        *,
        agent: None | CartaAgent=None
) -> Project:
    if not agent:
        from pycarta import get_agent
    agent = agent or get_agent()
    response = agent.post('project',
                          json={
                              "name": name,
                              "bucketName": bucket
                          })
    return Project(**response.json())

def delete_project(
        project_id: str,
        *,
        agent: None | CartaAgent=None
) -> bool:
    if not agent:
        from pycarta import get_agent
    agent = agent or get_agent()
    agent.delete(f'project/{project_id}')
    return True

def create_connection(
        project_id: str,
        connection: Connection,
        *,
        agent: None | CartaAgent=None
) -> Connection:
    if not agent:
        from pycarta import get_agent
    agent = agent or get_agent()
    response = agent.post(f'project/connection/{project_id}',
                          json=connection.model_dump(
                              exclude_defaults=True,
                              by_alias=True))
    return Connection(**response.json())

def delete_connection(connection_id: str, *, agent: None | CartaAgent=None) -> bool:
    if not agent:
        from pycarta import get_agent
    agent = agent or get_agent()
    agent.delete(f'project/connection/{connection_id}')
    return True
