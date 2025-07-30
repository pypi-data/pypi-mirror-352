import warnings
from ..auth.agent import CartaAgent


def put_secret(name: str, value: str, *, agent: None | CartaAgent=None):
    if not agent:
        from pycarta import get_agent
    if "_" in name:
        warnings.warn("Secret names should not contain underscores. Replacing with hyphens.")
        name = name.replace("_", "-")
    if len(value) > 1024:
        raise ValueError("Secret values should be less than 1024 characters.")
    agent = agent or get_agent()
    agent.put('secrets', headers={f"secret-{name}": value})

def get_secret(name: str, *, agent: None | CartaAgent=None):
    if not agent:
        from pycarta import get_agent
    if "_" in name:
        warnings.warn("Secret names should not contain underscores. Replacing with hyphens.")
        name = name.replace("_", "-")
    agent = agent or get_agent()
    response = agent.get('secrets', params={"name": name})
    return response.text
