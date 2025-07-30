import sys

if sys.version_info[:2] >= (3, 8):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
    from importlib.metadata import PackageNotFoundError, version  # pragma: no cover
else:
    from importlib_metadata import PackageNotFoundError, version  # pragma: no cover

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError


# ##### Import Submodules ##### #
from .services import service
from . import (
    admin,
    auth,
    mqtt,
    sbg,
)


# ##### Set pycarta context ##### #
import os
from .auth import (
    CartaAgent,
    CartaLoginUI,
    Profile,
)
from .admin.types import User, Group
from .exceptions import AuthenticationError
from .sbg.login import SbgLoginManager
from functools import wraps


class Singleton:
    _instance = None
    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance
    

class PycartaContext(Singleton):
    def __init__(self):
        self._sbg_login_manager: None | SbgLoginManager = None
        self._profile: None | Profile = Profile()
        self._agent: None | CartaAgent = None
        self._interactive: bool = False
        self.login()

    @property
    def agent(self):
        if self._agent is None:
            # attempt to log in
            if not self.login():
                return None
        return self._agent

    @agent.setter
    def agent(self, agent: None | CartaAgent):
        self._agent = agent

    @property
    def sbg_login_manager(self) -> SbgLoginManager:
        if self._sbg_login_manager is None:
            self._sbg_login_manager = SbgLoginManager()
        return self._sbg_login_manager

    def is_authenticated(self) -> bool:
        if self.agent is None:
            if not self.login():
                return False
        return self.agent.is_authenticated()

    def is_interactive(self) -> bool:
        return self._interactive
    
    def ion(self) -> None:
        """Allow interaction with the user."""
        self._interactive = True
    
    def ioff(self) -> None:
        """Disallow interaction with the user."""
        self._interactive = False

    def login(
        self,
        *,
        profile: str=None,
        username: str=None,
        password: str=None,
        environment: str=None,
        host: str=None,
        interactive: bool=False,
        reauthenticate_sbg: bool=False,
    ) -> bool:
        """
        Authenticate using a profile or username/password. Profile takes
        precedence over username/password. If neither are provided, then the
        CARTA_PROFILE environment variable is checked. If that is not set, then
        CARTA_USER and CARTA_PASS environment variables are checked for the
        username and password, respectively.

        If these options are exhausted, but either "interactive" is set to
        True or the context is interactive, then the CartaLoginUI is used to
        prompt the user for a username and password.

        Parameters
        ----------
        profile : str
            User profile to use for authentication. Default: None.
        username : str
            Carta username. Default: None
        password : str
            Carta password. Default: None
        token : str
            If provided, token supercedes username/password. Default: None.
        environment : str
            Resolves to either HOST_PROD, if "production", or HOST_DEV,
            otherwise. Defaults to None.
        host : str
            Host to use for authentication and subsequent API calls.
            Overrides environment. Recover default hosts by setting host
            to None. Defaults to None.
        interactive : bool
        reauthenticate_sbg : bool. Default: False

        Returns
        -------
        bool
            True if authentication is successful, False otherwise.
        """
        # Check environment variables
        profile_ = profile or os.environ.get("CARTA_PROFILE", None)
        username_ = username or os.environ.get("CARTA_USER", None)
        password_ = password or os.environ.get("CARTA_PASS", None)
        environment_ = environment or os.environ.get("CARTA_ENV", None)
        host_ = host or os.environ.get("CARTA_HOST", None)
        if profile:
            self.agent = CartaAgent(profile=profile)
        elif username and password:
            self.agent = CartaAgent(username=username,
                                    password=password,
                                    environment=environment_,
                                    host=host or host_,)
        elif profile_:
            self.agent = CartaAgent(profile=profile_)
        elif username_ and password_:
            self.agent = CartaAgent(username=username_,
                                    password=password_,
                                    environment=environment_,
                                    host=host or host_,)
        elif interactive or self.is_interactive():
            self.agent = CartaLoginUI().login(environment=environment_,
                                              host=host_,)
        # Log in to Seven Bridges
        if not self._sbg_login_manager:
            self._sbg_login_manager = SbgLoginManager()
        elif reauthenticate_sbg:
            self._sbg_login_manager.login(interactive=interactive)
        return False if self._agent is None else self.agent.is_authenticated()

    def authorize(self, *, users: None | list[str | User]=None, groups: None | list[str | Group]=None):
        """
        Defines what users and/or groups have permission to run the decorated
        function. If no users or groups are provided, then the function is
        available to anyone with a Carta account.

        .. note::
            Authentication is checked and, if necessary, attempted when this
            function is called. The list of authorized users is constructed
            at that point from the groups and users provided. A subsequent
            change in the membership of a group will not be reflected in this
            function until the next session. This will most likely be a problem
            only in long-running jobs.

        Parameters
        ----------
        users : list[str | User]
            List of users that are allowed to run the decorated function.
            Default: None If None, then all users are allowed.
        groups : list[str | Group]
            List of groups that are allowed to run the decorated function.
            Default: None If None, then all groups are allowed.

        Returns
        -------
        decorator : function
            Decorator function
        """
        def decorator(func):
            from pycarta.admin import get_current_user, list_members
            # Ensure the user is logged in.
            if not self.is_authenticated():  # pragma: no cover
                raise AuthenticationError("Authentication required.")
            # What users are allowed?
            if users or groups:
                allowed = [getattr(u, "name", u) for u in users] if users else []
                for g in (groups or []):
                    try:
                        members = list_members(g)
                    except Exception:  # pragma: no cover
                        members = []
                    allowed.extend([u.name for u in members])
            else:
                allowed = None
            @wraps(func)
            def wrapper(*args, **kwargs):
                # if user isn't authenticated, bail out.
                if not self.is_authenticated():  # pragma: no cover
                    raise AuthenticationError("Authentication required.")
                # check if current user is in allowed list
                user = get_current_user()
                if (allowed is not None) and (user.name not in allowed):
                    raise AuthenticationError(f"User {user.name} is not authorized.")
                return func(*args, **kwargs)
            return wrapper
        return decorator

# Expose context interface
__CONTEXT = PycartaContext()

@wraps(__CONTEXT.authorize)
def authorize(**kwds):
    return __CONTEXT.authorize(**kwds)

@wraps(__CONTEXT.is_authenticated)
def is_authenticated():
    return __CONTEXT.is_authenticated()

@wraps(__CONTEXT.agent)
def get_agent() -> CartaAgent:
    return __CONTEXT.agent

def set_agent(agent: None | CartaAgent) -> None:
    __CONTEXT.agent = agent

@wraps(__CONTEXT.login)
def login(**kwargs) -> bool:
    return __CONTEXT.login(**kwargs)

@wraps(__CONTEXT.is_interactive)
def is_interactive() -> bool:
    return __CONTEXT.is_interactive()

@wraps(__CONTEXT.ion)
def ion() -> None:
    """Turns on interactive mode (modeled after matplotlib)."""
    __CONTEXT.ion()

@wraps(__CONTEXT.ioff)
def ioff() -> None:
    """Turns off interactive mode (modeled after matplotlib)."""
    __CONTEXT.ioff()
