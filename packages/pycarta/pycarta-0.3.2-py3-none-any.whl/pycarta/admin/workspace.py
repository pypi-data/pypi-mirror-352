from ..auth.agent import CartaAgent
from .types import (
    PermissionEntity,
    PermissionsRole,
    UserType,
    Workspace,
)


def create_workspace(workspace: str, *, agent: None | CartaAgent=None) -> Workspace:
    if not agent:
        from pycarta import get_agent
    agent = agent or get_agent()
    response = agent.post(f"workspace/{workspace}")
    return Workspace(**response.json())

def get_workspace(workspace: str, *, agent: None | CartaAgent=None) -> Workspace:
    if not agent:
        from pycarta import get_agent
    agent = agent or get_agent()
    response = agent.get(f"workspace/{workspace}")
    return Workspace(**response.json())

def delete_workspace(workspace: str, *, agent: None | CartaAgent=None) -> None:
    if not agent:
        from pycarta import get_agent
    agent = agent or get_agent()
    response = agent.delete(f"workspace/{workspace}")

def current_user_workspaces(*, agent: None | CartaAgent=None) -> list[Workspace]:
    if not agent:
        from pycarta import get_agent
    agent = agent or get_agent()
    response = agent.get("workspace")
    return [Workspace(**workspace) for workspace in response.json()]

def get_workspace_permissions(
    workspace: str,
    user_type: UserType = UserType.USER,
    *,
    agent: None | CartaAgent=None
) -> list[PermissionEntity]:
    if not agent:
        from pycarta import get_agent
    agent = agent or get_agent()
    response = agent.get(f"workspace/{workspace}/permissions/users",
                           params={"userType": user_type.value})
    return [PermissionEntity(**user) for user in response.json()]

def get_workspace_permission(
    workspace_id: str,
    user_id: str,
    user_type: UserType,
    *,
    agent: None | CartaAgent=None
):
    if not agent:
        from pycarta import get_agent
    agent = agent or get_agent()
    response = agent.get(
        f"workspace/{workspace_id}/permissions/user/{user_id}",
        params={"userType": user_type.value})
    return response.json()

def set_workspace_permission(
    workspace_id: str,
    user_id: str,
    user_type: UserType,
    role: PermissionsRole,
    *,
    agent: None | CartaAgent=None
):
    if not agent:
        from pycarta import get_agent
    agent = agent or get_agent()
    response = agent.put(
        f"workspace/{workspace_id}/permissions/user/{user_id}",
        params={"role": role.value, "userType": user_type.value}
    )
    return response.json()

def remove_workspace_permission(
    workspace_id: str,
    user_id: str,
    user_type: UserType,
    *,
    agent: None | CartaAgent=None
):
    if not agent:
        from pycarta import get_agent
    agent = agent or get_agent()
    response = agent.delete(
        f"workspace/{workspace_id}/permissions/user/{user_id}",
        params={"userType": user_type.value}
    )
    return response.json()
