from .server import service
from ..auth.agent import CartaAgent


def get_websockets_uri(agent: None | CartaAgent=None) -> str:
    """
    Gets the web
    """
    if not agent:
        from .. import get_agent
        agent = get_agent()
    response = agent.get("service/carta/websocket")
    response.raise_for_status()
    return response.json()
