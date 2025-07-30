from .agent import CartaAgent
from .config import CartaConfig
from .profile import Profile
try:
    from .ui import (
        CartaLogin as CartaLoginUI,
        CartaProfile as CartaProfileUI,
    )
except ImportError:
    from warnings import warn
    msg = "You appear to be running in a headless environment, e.g. Lambda, so " \
          "UI components could not be imported. Any attempt to create a GUI " \
          "will raise an ImportError."
    warn(msg)
    class CartaLoginUI:
        def __new__(cls, *args, **kwargs):
            raise ImportError(msg)
    
    class CartaProfileUI:
        def __new__(cls, *args, **kwargs):
            raise ImportError(msg)
