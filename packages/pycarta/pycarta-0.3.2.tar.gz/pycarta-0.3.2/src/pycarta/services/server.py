from __future__ import annotations

import os
import asyncio
import contextlib
import inspect
import json
import logging
import threading
import time
import uvicorn
from ..auth import CartaAgent
from ..admin import (
    get_current_user,
    get_resource,
    set_user_permission,
)
from ..admin.service import details as service_details
from ..admin.service import (
    reserve_namespace,
    remove_namespace,
    register_service,
    unregister_service,
)
from ..admin.permission import get_user_permission
from ..exceptions import PermissionDeniedException
from fastapi import APIRouter, FastAPI, Depends, Header, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.openapi.utils import get_openapi
from functools import cache
from pprint import pformat
from .proxy import CartaServiceManagerProxy
from pydantic import BaseModel, create_model
from typing import Annotated, Generator, Literal


logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("DEBUG_LEVEL", "INFO").upper())


__all__ = ["Service"]


RoleType = Literal["None", "Guest", "User", "Editor", "Owner"]

# region Helper Functions

def check_service_permission(agent: CartaAgent, namespace: str, service: str):
    """
    Verifies that the user (determined by the agent) has permission to
    write to (reserve) the service. Raises an HTTPException if not.
    """
    if not agent.is_authenticated():
        raise HTTPException(status_code=401, detail="Not authenticated")
    # user = get_current_user(agent=agent)
    # permissions = get_user_permission(svc.id, user.name, "User")
    svc = service_details(namespace, service, agent=agent)
    permissions = get_resource("Service", svc.id, agent=agent).permissions
    if not permissions.read:
        raise HTTPException(status_code=403, detail=f"Not authorized for /{namespace}/{service}")
    

# def check_namespace_permission(agent: CartaAgent, namespace: str):
#     """
#     Verifies that the user (determined by the agent) has permission to
#     execute the service. Raises an HTTPException if not.
#     """
#     if not agent.is_authenticated():
#         raise HTTPException(status_code=401, detail="Not authenticated")
#     user = get_current_user(agent=agent)
#     ns = service_details(namespace, agent=agent)
#     permissions = get_user_permission(ns.id, user.name)
#     if not permissions.write:
#         raise HTTPException(status_code=403,
#                             detail=f"Not authorized to edit namespace {namespace!r}")
    

def namespace_exists(namespace: str) -> bool:
    """
    Verifies that the namespace exists. Raises an HTTPException if not.
    """
    from pycarta import get_agent
    agent = get_agent()
    if not agent.is_authenticated():
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        _ = service_details(namespace, agent=agent)
        return True
    except:
        return False
    

def service_exists(namespace: str, service: str) -> bool:
    """
    Verifies that the service exists. Raises an HTTPException if not.
    """
    from pycarta import get_agent
    agent = get_agent()
    if not agent.is_authenticated():
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        _ = service_details(namespace, service, agent=agent)
        return True
    except:
        return False
    

def create_namespace(namespace: str):
    """
    Creates a namespace and sets the permissions for the current user to
    "Owner" for the namespace.
    """
    user = get_current_user()
    try:
        reserve_namespace(namespace)
        ns = service_details(namespace)
        set_user_permission(ns.id, user.id, "User", "Owner")
    except PermissionDeniedException:
        raise PermissionDeniedException(
            f"You do not have permission to create namespace {namespace}."
        )


def create_service(namespace: str, service: str, url: str):
    """
    Creates a service and sets the permissions for the current user to
    "Owner" for the service.
    """
    user = get_current_user()
    try:
        register_service(namespace, service, url)
        svc = service_details(namespace, service)
        set_user_permission(svc.id, user.id, "User", "Owner")
    except PermissionDeniedException:
        raise PermissionDeniedException(
            f"You do not have permission to create '/{namespace}/{service}': {url!r}."
        )
# end region


# region Helper Classes
class AuthorizationHeaders(BaseModel):
    """
    The headers that must be present in the request to the service.
    """
    authorization: str


class Server(uvicorn.Server):
    def __init__(self, app: FastAPI):
        config = uvicorn.Config(app=app, port=0)
        super().__init__(config=config)

    @contextlib.contextmanager
    def run_in_thread(self) -> Generator:
        thread = threading.Thread(target=self.run)
        thread.start()
        try:
            while not self.started:
                time.sleep(1e-3)
            yield
        finally:
            self.should_exit = True
            thread.join()

    def get_address_and_port(self):
        for server in self.servers:
            for sock in server.sockets:
                return sock.getsockname()


class Endpoint:
    def __init__(self, func: callable):
        """
        Gets information about the function using the inspect module to
        create a well-formed endpoint. This imposes several requirements
        on the function:
        
            1. The function must have type annotations for all parameters.
            2. The function must have a name that is a valid endpoint name.
            3. The function may not have *args or **kwargs.
        
        The resulting endpoint converts scalar positional parameters into
        endpoint path variables, e.g.:

            def foo(bar: int, baz: str) --> /foo/{bar}/{baz}
        
        Scalar keyword parameters are converted into query variables, e.g.:

            def foo(*, bar:int, baz:str) --> /foo?bar={bar}&baz={baz}

        And, finally, any complex variable (not a simple variable, such as an
        int, float, str, et.) must be a Pydantic BaseModel. These will be
        read from the body, e.g.

        .. code:: python

            class Foo(BaseModel):
                bar: int
                baz: str

            def func(foo: Foo):
                pass

        the resulting endpoint, "/func", should provide a JSON-formatted body::

            {
                "bar": 1,
                "baz": "hello"
            }

        If the function has multiple complex types, these are composed into a
        new BaseModel automatically, e.g.

        .. code:: python

            class Foo(BaseModel):
                bar: int
                baz: str

            class Bar(BaseModel):
                qux: int
                quux: str

            def func(foo: Foo, bar: Bar):
                pass

        the resulting endpoint, "/func", should provide a JSON-formatted body::

            {
                "foo": {
                    "bar": 1,
                    "baz": "hello"
                },
                "bar": {
                    "qux": 1,
                    "quux": "hello"
                }
            }       
        """
        self.name = func.__name__
        spec = inspect.getfullargspec(func)
        if spec.varargs or spec.varkw:
            raise ValueError("Endpoint cannot be created from a callable with "
                             "*args or **kwargs.")
        body = [(k,v) for k,v in spec.annotations.items()
                if issubclass(v, BaseModel)]
        scalars = [k for k,v in spec.annotations.items()
                   if not issubclass(v, BaseModel)]
        if len(body) > 1:
            type_ = self.name.title().strip("_") + "Body"
            body = [create_model(type_, **dict(body))]
        self.path = [s for s in scalars if s in spec.args]
        self.query = [s for s in scalars if s in spec.kwonlyargs]
        self.body = body[0] if body else None
    
    def __str__(self) -> str:
        return "/" + "/".join([self.name] + ["{" + p + "}" for p in self.path])
    
    @property
    def tags(self) -> list[str]:
        return [self.name]
# end region


#region Service
# This class, Service, is a capitalized version to disambiguate the object
# (Service) with the service name (service). However, this disambiguation
# is not necessary when @pycarta.service(namespace, service) is used because
# of the unambiguous context. Further, "service" should be lowercase since it
# is part of the pycarta API. That assignment follows the class definition.
class Service:
    """
    Decorator to register a function as a Carta service, making that function
    available to others through a REST API call to
    
        {Carta Base URL}/service/{namespace}/{service}/{function name}

    Parameters
    ----------
    namespace : str
        The namespace into which the service should be placed.

    service : str
        The name of the service.

    users : Optional[dict[str | tuple[str, str], RoleType]]
        Additional users to authorize to use this service. This should be
        provided as a mapping of user information and role::

            {
                ("first name", "last name") : RoleType,
                "username" : RoleType,
                "name@email.com" : RoleType
            }
        
        where `RoleType = Literal["None", "Guest", "User", "Editor", "Owner"]`.
        Email addresses are recognized by the presence of "@", names as
        a tuple, and usernames otherwise.
        
    groups : Optional[dict[str, RoleType]]
        Groups (by name) to authorize to use this service.
        
    cleanup : Optional[bool]
        Whether to cleanup the the service(s) and/or namespace(s) that were
        constructed implicitly based on decorated functions. Default: True.

    Examples
    --------

    .. code:: python

        import pycarta as pc
        pc.login(profile="my-profile")

        @pc.service(namespace="alice", service="test").get()
        def foo():
            # This makes "foo" available as ".../alice/test/foo"
            return "Hello from 'foo'"
        
        @pc.service(namespace="alice", service="test").get()
        def bar():
            # This makes "bar" available as ".../alice/test/bar"
            return "Hello from 'bar'"
        
        @pc.service(namespace="alice", service="test2").get("foo")
        def another_foo():
            # This makes "another_foo" available as ".../alice/test2/foo".
            return "Hello from 'another_foo'"
        
        # This can be repeated as often as needed to construct all endpoints.


        if __name__ == "__main__":
            # The function is unchanged and still usable locally.
            print(foo())  # prints "Hello from 'foo'".

            # Connect to Carta and wait for events. Ctrl-c to stop.
            try:
                asyncio.run(pc.service.connect())
            finally:
                # Clean up any services/namespaces that were created.
                pc.service.cleanup()
    """
    HOST: str="http://localhost"
    WEBSERVER: None | FastAPI=None
    SERVICES: dict[tuple[str, str], Service] = dict()
    NEW_NAMESPACES: set[str] = set()

    def __new__(cls, namespace: str, service: str, *,
                users: dict[str | tuple[str, str], RoleType]=dict(),
                groups: dict[str, RoleType]=dict(),
                cleanup: bool=True):
        if cls.WEBSERVER is None:
            cls.WEBSERVER = FastAPI()
        # Singleton construct (per namespace/service combination)
        key = (namespace, service)
        if cls.SERVICES.get(key, None) is None:
            obj = super().__new__(cls)
            obj.namespace = namespace
            obj.service = service
            obj.new_service = not service_exists(namespace, service)
            if not namespace_exists(namespace):
                create_namespace(namespace)
                Service.NEW_NAMESPACES.add(namespace)
            if obj.new_service:
                # Create the service here and then update it with the URL and
                # other connection information when the service is run. Websockets
                # will eventually overwrite this URL on @connect call.
                # create_service(namespace, service, cls.HOST)
                create_service(namespace, service, None)
                obj.cleanup_service = cleanup
            else:
                obj.cleanup_service = False
            # Authorize users and groups
            for name, role in users.items():
                obj.authorize(user=name, role=role)
            for name, role in groups.items():
                obj.authorize(group=name, role=role)
            # Set up local API server
            obj.__thread = None
            obj.prefix = f"/{namespace}/{service}"
            obj.router = APIRouter(
                prefix=obj.prefix,
                tags=[service],
                dependencies=[Depends(obj.authenticate)])
            # Docs require a connection to the server, which is not possible here.
            # Static documentation is created whenever this is called.
            obj.get("docs", include_in_schema=False)(obj.get_redoc)
            obj.get("redoc", include_in_schema=False)(obj.get_redoc)
            cls.WEBSERVER.include_router(obj.router)
            cls.SERVICES[key] = obj 
        return cls.SERVICES[key]
    
    def __del__(self):
        self._cleanup(force=False)
        if (self.namespace, self.service) in Service.SERVICES:
            del Service.SERVICES[(self.namespace, self.service)]

    # @classmethod
    # def get_docs(cls):
    #     logger.info(f"Requesting Swagger docs from {cls.HOST}/docs")
    #     # return requests.get(f"{cls.HOST}/docs").text
    #     with sync_playwright() as p:
    #         browser = p.chromium.launch()
    #         page = browser.new_page()
    #         page.goto(f"{cls.HOST}/docs")
    #         return page.content()
    
    # @classmethod
    def get_redoc(self):
        logger.info(f"Requesting ReDoc docs from {self.HOST}/redoc")
        # return requests.get(f"{cls.HOST}/redoc").text
        def package_openapi():
            # routes = list()
            # for svc in cls.SERVICES.values():
            #     routes.extend(svc.router.routes or list())
            routes = self.router.routes
            logger.info(f"Routes: {routes}")
            return get_openapi(
                title=f"{self.prefix} Service API",
                version="1.0.0",
                description=f"{self.prefix} service documentation.",
                routes=routes,
            )
        
        # Get the OpenAPI spec and dump it as JSON text.
        spec = package_openapi()
        spec_json = json.dumps(spec)
        # Write this to static HTML using a custom template.
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>ReDoc</title>
            <script src="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"></script>
        </head>
        <body>
            <div id="redoc-container"></div>
            <script>
            // Inline the OpenAPI spec into the page
            const spec = {spec_json};
            Redoc.init(spec, {{}}, document.getElementById('redoc-container'));
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    
    @classmethod
    def cleanup(cls, *, force: bool=False):
        for key in list(cls.SERVICES.keys()):
            svc = cls.SERVICES[key]
            svc._cleanup(force=force)
            del cls.SERVICES[key]
    
    def _cleanup(self, *, force: bool=False):
        """
        Cleans up the service. This is called automatically when the service is
        deleted. If force is True, the service is deleted even if it is not
        owned by the current user.

        **Note** Namespaces that were created to support an ad hoc service and
        are no longer needed are deleted. Do not depend on ad hoc services to
        create namespaces you want to persist. Reserve those using the
        `pycarta.admin.reserve_namespace` function.
        """
        logger.info(f"Cleaning up service '/{self.namespace}/{self.service}'")
        # cleanup the service
        if force or (self.new_service and self.cleanup_service):
            try:
                unregister_service(self.namespace, self.service)
            except:
                pass
        # cleanup any namespaces that were created and no longer needed
        remaining_namespaces = {ns for (ns, _), svc in Service.SERVICES.items()
                                if svc is not None}
        for ns in Service.NEW_NAMESPACES - remaining_namespaces:
            try:
                remove_namespace(ns)
            except:
                pass
    
    async def authenticate(self, authorization: Annotated[str, Header()]) -> CartaAgent:
        """
        Returns an authenticated CartaAgent requesting this service. This is lazy and
        is only evaluated when the service is called.
        """
        if not authorization:
            raise HTTPException(status_code=401, detail="No authorization header")
        token = authorization
        try:
            token = token.split(" ")[-1]
        except IndexError:
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        agent = CartaAgent(token=token)
        check_service_permission(agent, self.namespace, self.service)
        return agent
    
    def authorize(self, *, user: tuple[str, str] | str | None=None, group: str | None=None, role: str="User"):
        """
        Authorizes others to access the service with the given role.
        """
        from ..admin import get_user, set_user_permission, details
        
        def get_user_id(**kwargs):
            user = get_user(**kwargs)
            if isinstance(user, list):
                raise ValueError(f"{kwargs} is not a unique user. Found "
                                f"{len(user)} users with the same info.")
            return getattr(user, "name", None)
        
        if user:
            if isinstance(user, tuple):
                # Looks like a first and last name
                first, last = user
                user_id = get_user_id(first_name=first, last_name=last)
            elif user.find("@") == -1:
                # Looks like a username
                user_id = get_user_id(username=user)
            else:
                # Looks like an email
                user_id = get_user_id(email=user)
            if user_id is None:
                raise ValueError(f"{user} is not a recognized username or email.")
            user_type = "User"
        elif group:
            user_id = group
            user_type = "UserGroup"
        else:
            raise ValueError("Either a user (username or email) or group must be given.")
        service = details(self.namespace, self.service)
        try:
            set_user_permission(service.id, user_id, user_type, role)
        except:
            msg = f"Failed to set {role} role for {user or group}."
            logger.error(msg)
            raise RuntimeError(msg)

    @cache
    @staticmethod
    def _register_service(namespace: str, service: str, url: str):
        # Updates the service URL on Carta. This is cached so repeated calls to
        # the same service do not incur the overhead of registering the service.
        register_service(namespace, service, url)
        return

    async def listen(self, proxy: CartaServiceManagerProxy) -> None:
        """
        Listens for incoming events from the proxy and handles them.
        """
        for response in await proxy:
            logger.info(f"Response: {pformat(response)!r}")
        
    @classmethod
    async def connect(cls, url: str | None=None,
                      *,
                      agent: None | CartaAgent=None
    ) -> None:
        """
        This starts a webserver to host user-defined services and listens to a
        websockets connection for client events.

        Parameters
        ----------
        url : str (optional)
            The websockets API URL. If not specified, this is pulled from Carta.
        agent : CartaAgent (optional)
            The agent that will be used to make the connection to the
            websockets API.

        Returns
        -------
        None
            This function does not return anything. It runs indefinitely until
            an exception occurs. Exit cleanly using ctrl-c (keyboard interrupt).
        """
        if not agent:
            from pycarta import get_agent

        agent = agent or get_agent()
        if not url:
            from . import get_websockets_uri
            url = get_websockets_uri()
            logger.info(f"Websockets URL: {url}")
        # Start the webserver
        app = FastAPI()
        for route in cls.SERVICES.values():
            app.include_router(route.router)
        server = Server(app)
        with server.run_in_thread():
            # Run the webserver in a thread until the websockets events are
            # halted.
            address, port = server.get_address_and_port()
            try:
                cls.HOST = f"http://{address}:{port}"
                logger.info(f"HTTP server is running on {cls.HOST}")
                async with asyncio.TaskGroup() as tg:
                    for svc in cls.SERVICES.values():
                        # Start listening for websocket events for each service.
                        logger.info(f"Listening to websocket for {svc.prefix}")
                        proxy = CartaServiceManagerProxy(
                            url, svc.namespace, svc.service,
                            redirect=cls.HOST,
                            agent=agent,
                        )
                        tg.create_task(proxy.listen())
                    logger.info("Listening to all proxies.")
            except (KeyboardInterrupt, asyncio.exceptions.CancelledError):
                logger.info(f"Stopped handling proxy events.")
            except ExceptionGroup as eg:
                for exc in eg.exceptions:
                    logger.error(f"Proxy error: {exc}")
                raise eg
            except Exception as e:
                logger.error(f"Caught exception: {e}")
                raise e
            finally:
                logger.info("Closing webserver.")
                cls.HOST = None

#region Service::Requests API
    def _update_endpoint(self, func, endpoint: str | None, kwargs):
        if not endpoint:
            e = Endpoint(func)
            endpoint = str(e)
            kwargs.setdefault("tags", e.tags)
        endpoint = "/" + endpoint.strip("/")
        return endpoint
    
    def request(self, endpoint: str | None=None, *args, methods: list[str], **kwargs):
        """
        Adds the endpoint, which by default is constructed from the decorated
        function's name and type annotations. Any parameter without an
        annotation is assumed to be a scalar parameter. The endpoint can be
        overridden by passing a string to the endpoint parameter.
        
        Any additional arguments are passed to the fastapi.FastAPI.add_api_route()
        call.

        Parameters
        ----------
        endpoint : str, optional
            The endpoint path. By default this is constructed from the
            function. Note that if this is specified manually, several rules
            must be followed:
            - The endpoint must be a valid path (e.g. /foo/bar)
            - The endpoint must contain a path parameter for each scalar
              positional parameter of the decorated function
            - The endpoint must contain a query parameter for each scalar
              keyword parameter of the decorated function
            - Only one non-scalar parameter, which must subclass
              pydantic.BaseModel, is allowed. This object will be constructed
              and validated from the request body.
        """
        def decorator(func):
            ep = self._update_endpoint(func, endpoint, kwargs)
            self.router.add_api_route(ep, func, *args, methods=methods, **kwargs)
            return func
        return decorator

    def get(self, endpoint: str | None=None, *args, **kwargs):
        """
        See the documentation for "request".
        """
        return self.request(endpoint, *args, methods=["GET"], **kwargs)
    
    def post(self, endpoint: str | None=None, *args, **kwargs):
        """
        See the documentation for "request".
        """
        return self.request(endpoint, *args, methods=["POST"], **kwargs)
    
    def put(self, endpoint: str | None=None, *args, **kwargs):
        """
        See the documentation for "request".
        """
        return self.request(endpoint, *args, methods=["PUT"], **kwargs)
    
    def patch(self, endpoint: str | None=None, *args, **kwargs):
        """
        See the documentation for "request".
        """
        return self.request(endpoint, *args, methods=["PATCH"], **kwargs)
    
    def delete(self, endpoint: str | None=None, *args, **kwargs):
        """
        See the documentation for "request".
        """
        return self.request(endpoint, *args, methods=["DELETE"], **kwargs)
    
service = Service
#endregion
