from ..auth.agent import CartaAgent
from .types import (
    ResourceType,
    PermissionsRole,
    UserType,
    Item,
    PermissionEntity,
    get_resource_class,
)
from .types.permissions import convert_permissions_from_str


def resource_types(*, agent: None | CartaAgent=None) -> list[ResourceType]:
    if not agent:
        from pycarta import get_agent
    agent = agent or get_agent()
    response = agent.get('permissions/resources')
    return [ResourceType(resource) for resource in response.json()]

def get_user_resources(
    resource_type: str | ResourceType,
    from_user: str | None = None,
    *,
    agent: None | CartaAgent=None
) -> list[Item]:
    if not agent:
        from pycarta import get_agent
    agent = agent or get_agent()
    if isinstance(resource_type, str):
        resource_type = ResourceType(resource_type)
    response = agent.get(f'permissions/resources/{resource_type.value}',
                         params={"userId": from_user})
    resource_class = get_resource_class(resource_type)
    try:
        return [resource_class(**resource) for resource in response.json()]
    except Exception as e:  # pragma: no cover
        raise ValueError(response.content)

def get_resource(
        resource_type: str | ResourceType,
        resource_id: str,
        *,
        agent: None | CartaAgent=None
) -> Item:
    if not agent:
        from pycarta import get_agent
    agent = agent or get_agent()
    if isinstance(resource_type, str):
        resource_type = ResourceType(resource_type)
    response = agent.get(f'permissions/resources/{resource_type.value}/{resource_id}')
    return get_resource_class(resource_type)(**response.json())

def get_user_permission(
    resource_id: str,
    user_id: str,
    user_type: None | str | UserType=None,
    *,
    agent: CartaAgent | None = None
):
    if not agent:
        from pycarta import get_agent
    agent = agent or get_agent()
    if user_type is None:
        response = agent.get(f'permissions/{resource_id}/{user_id}')
    else:
        if isinstance(user_type, str):
            user_type = UserType(user_type)
        response = agent.get(f'permissions/{resource_id}/{user_id}',
                            params={"userType": user_type.value})
    return convert_permissions_from_str(response.text)

def set_user_permission(
    resource_id: str,
    user_id: str,  # username or group name, not UUID.
    user_type: str | UserType,
    role: str | PermissionsRole,
    *,
    agent: None | CartaAgent=None
):
    """
    Sets user permissions for a resource

    Parameters
    ----------
    resource_id : UUID (str)
    
    user_id : name (str)
        The username or group name to whom permissions are to be granted.
    
    user_type : Literal["User", "UserGroup"]
        Whether the user_id refers to a user or to a group.

    role : Literal["None", "Guest", "User", "Admin", "Owner"]
        The role to assign to the user_id.

    agent : pycarta.CartaAgent (optional)
        The agent to use when making Carta calls. Defaults to the user
        currently logged in.
    """
    if not agent:
        from pycarta import get_agent
    agent = agent or get_agent()
    if isinstance(user_type, str):
        user_type = UserType(user_type)
    if isinstance(role, str):
        role = PermissionsRole(role)
    response = agent.put(f'permissions/{resource_id}/{user_id}',
                         params={
                             "userType": user_type.value,
                             "role": role.value, })
    return response.json()

def remove_user_permission(
    resource_id: str,
    user_id: str,
    user_type: str | UserType,
    *,
    agent: None | CartaAgent=None
):
    if not agent:
        from pycarta import get_agent
    agent = agent or get_agent()
    if isinstance(user_type, str):
        user_type = UserType(user_type)
    response = agent.delete(f'permissions/{resource_id}/{user_id}',
                            params={"userType": user_type.value})
    return response.json()

def list_resource_permissions(
    resource_id: str,
    user_type: str | UserType,
    *,
    agent: None | CartaAgent=None
) -> list[PermissionEntity]:
    if not agent:
        from pycarta import get_agent
    agent = agent or get_agent()
    if isinstance(user_type, str):
        user_type = UserType(user_type)
    response = agent.get(f'permissions/{resource_id}/users',
                         params={"userType": user_type.value})
    return [PermissionEntity(**user) for user in response.json()]
