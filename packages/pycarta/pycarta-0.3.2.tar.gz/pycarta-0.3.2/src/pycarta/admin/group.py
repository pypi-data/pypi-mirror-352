from ..auth.agent import CartaAgent
from ..exceptions import InvalidParameterException
from .types import Group, User


def create_group(group: Group, *, exists_ok: bool=False, agent: None | CartaAgent=None) -> None:
    if not agent:
        from pycarta import get_agent
    try:
        agent = agent or get_agent()
        agent.post(f"user/group/{str(group)}")
    except InvalidParameterException as error:
        if exists_ok:
            return
        raise error

def add_user_to_group(
    add_user: User,
    group: Group,
    create_if_not_exists=False,
    *,
    agent: None | CartaAgent=None
) -> None:
    if not agent:
        from pycarta import get_agent
    agent = agent or get_agent()
    try:
        response = agent.post(f"user/group/{str(group)}/{add_user.name}")
    except InvalidParameterException as error:  # pragma: no cover
        if create_if_not_exists:
            create_group(group)
            # If this fails, something else was wrong with the request
            add_user_to_group(add_user, group, create_if_not_exists=False)
            return
        raise error

def list_members(group: str | Group, *, agent: None | CartaAgent=None) -> list[User]:
    if not agent:
        from pycarta import get_agent
    agent = agent or get_agent()
    response = agent.get(f"user/group/{str(group)}")
    users = response.json()
    return [User(**user) for user in users]
