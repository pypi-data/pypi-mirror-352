import logging
from functools import partial
from .types.group import Group
from .types.user import User, UserFilter, AttributeFilter, UserAttribute
from ..exceptions import InvalidParameterException
from ..auth.agent import CartaAgent

logger = logging.getLogger(__name__)


def get_current_user(*, agent: None | CartaAgent=None) -> User:
    if not agent:
        from pycarta import get_agent
    agent = agent or get_agent()
    response = agent.get('user')
    user_dict = response.json()
    return User(**user_dict)

def create_user(
        add_user: User,
        exists_ok: bool=False,
        *,
        agent: None | CartaAgent=None
) -> User:
    from .group import add_user_to_group
    if not agent:
        from pycarta import get_agent
    agent = agent or get_agent()
    try:
        # Workaround for mistakenly requiring organization
        add_user.organization = getattr(add_user, "organization", "None")
        response = agent.post("user",
            json=add_user.model_dump(exclude_defaults=True, by_alias=True))
    except InvalidParameterException:
        logger.debug(f"User {add_user.name!r} already exists")
        if exists_ok:
            user = get_user(
                username=add_user.name,
                email=add_user.email,
            )
            logger.debug("Found matching user.")
            return user
        else:
            raise
    add_user_to_group(
        add_user,
        Group(name="AllUsers"),
        create_if_not_exists=True
    )
    add_user_to_group(
        add_user,
        Group(name="All", organization=add_user.organization),
        create_if_not_exists=True
    )
    return User(**response.json())

def reset_user_password(
        username: str,
        *,
        agent: None | CartaAgent=None
) -> None:
    if not agent:
        from pycarta import get_agent
    agent = agent or get_agent()
    agent.reset_user_password(username)

def _find_users(
        user_filter: UserFilter = None,
        *,
        agent: None | CartaAgent=None
) -> list[User]:
    if not agent:
        from pycarta import get_agent
    agent = agent or get_agent()
    if user_filter:
        user_filter = user_filter.to_param()
    response = agent.get("user/users", params=user_filter)
    users = response.json()
    return [User(**user) for user in users]

list_users = partial(_find_users, None)
list_users.__doc__ = "Lists all users in the system."

def get_user(
    *,
    username: None | str=None,
    email: None | str=None,
    first_name: None | str=None,
    last_name: None | str=None,
    partial_match: bool=False,
    agent: None | CartaAgent=None
) -> None | User | list[User]:
    matches = None
    filters = []
    comparison = AttributeFilter.STARTS_WITH if partial_match else AttributeFilter.EQUALS
    if username is not None:
        logger.debug(f"Searching for user: {username!r}")
        filters.append(UserFilter(
            attributeName=UserAttribute.UserName,
            attributeValue=username,
            attributeFilter=comparison))
    if email is not None:
        logger.debug(f"Searching for user: {email!r}")
        filters.append(UserFilter(
            attributeName=UserAttribute.Email,
            attributeValue=email,
            attributeFilter=comparison))
    if first_name is not None:
        logger.debug(f"Searching for user: {first_name!r}")
        filters.append(UserFilter(
            attributeName=UserAttribute.FirstName,
            attributeValue=first_name,
            attributeFilter=comparison))
    if last_name is not None:
        logger.debug(f"Searching for user: {last_name!r}")
        filters.append(UserFilter(
            attributeName=UserAttribute.LastName,
            attributeValue=last_name,
            attributeFilter=comparison))
    for filter in filters:
        users = _find_users(filter, agent=agent)
        if matches is None:
            matches = set(users)
        else:
            # Only keep users that have matched all criteria.
            matches &= set(users)
        if len(matches) == 0:
            # Abort if no users match all criteria.
            break
    else:
        return list(matches) if len(matches) > 1 else matches.pop()
    return None
        
