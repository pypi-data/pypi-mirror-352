from .types import Service, Namespace
from ..auth.agent import CartaAgent


def details(namespace: str, service: str | None=None, *, agent: CartaAgent | None=None) -> Service | Namespace:
    if not agent:
        from pycarta import get_agent
    agent = agent or get_agent()
    if service is None:
        response = agent.get(f'service/details/{namespace}')
        return Namespace(**response.json())
    else:
        response = agent.get(f'service/details/{namespace}/{service}')
        return Service(**response.json())


def register_service(
        namespace: str,
        service: str,
        url: str | None=None,
        *,
        agent: None | CartaAgent=None
) -> Service:
    if not agent:
        from pycarta import get_agent
    agent = agent or get_agent()
    # NOTE: The server doesn't currently allow a non-existent service to be
    #       registered. As a workaround, register the service first, then
    #       update the service with the URL, i.e.
    #       register_service(ns, svc, None)
    #       register_service(ns, svc, url)
    response = agent.post(f'service/register/{namespace}/{service}',
                          params={
                              "baseUrl": url,
                          } if url else None)
    return Service(**response.json())


def unregister_service(
        namespace: str,
        service: str,
        *,
        agent: None | CartaAgent=None
) -> bool:
    if not agent:
        from pycarta import get_agent
    agent = agent or get_agent()
    agent.delete(f'service/remove/{namespace}/{service}')
    return True


def rename_service(
        namespace: str,
        current_service: str,
        new_service: str,
        *,
        agent: None | CartaAgent=None
) -> bool:
    if not agent:
        from pycarta import get_agent
    agent = agent or get_agent()
    agent.patch(f'service/rename/{namespace}/{current_service}/{new_service}')
    return True


def reserve_namespace(namespace: str, *, agent: None | CartaAgent=None):
    if not agent:
        from pycarta import get_agent
    agent = agent or get_agent()
    agent.post(f'service/reserve/{namespace}')
    return True


def remove_namespace(namespace: str, *, agent: None | CartaAgent=None):
    if not agent:
        from pycarta import get_agent
    agent = agent or get_agent()
    agent.delete(f'service/remove/{namespace}')
    return True


class ServiceUtility:

    def __init__(self, agent: CartaAgent, namespace: str, service: str):
        self.agent = agent
        self.service_path = f"service/{namespace}/{service}"

    @staticmethod
    def join_path(*args):
        return "/".join([a.strip("/") for a in args]).strip("/")

    def get(self, endpoint: str="", **kwargs):
        return self.agent.get(ServiceUtility.join_path(self.service_path, endpoint), **kwargs)

    def post(self, endpoint: str="", **kwargs):
        return self.agent.post(ServiceUtility.join_path(self.service_path, endpoint), **kwargs)

    def put(self, endpoint: str="", **kwargs):
        return self.agent.put(ServiceUtility.join_path(self.service_path, endpoint), **kwargs)

    def patch(self, endpoint: str="", **kwargs):
        return self.agent.patch(ServiceUtility.join_path(self.service_path, endpoint), **kwargs)

    def delete(self, endpoint: str="", **kwargs):
        return self.agent.delete(ServiceUtility.join_path(self.service_path, endpoint), **kwargs)


def utilize_service(
        namespace: str,
        service: str,
        *,
        agent: None | CartaAgent=None
) -> ServiceUtility:
    if not agent:
        from pycarta import get_agent
    agent = agent or get_agent()
    return ServiceUtility(agent, namespace, service)
