# from .. import __CONTEXT
from .base import SbgFile, SbgDirectory
from .login import SbgLoginManager
from .project import ExecutableApp, ExecutableProject

def get_login_manager() -> SbgLoginManager:
    from .. import __CONTEXT
    return __CONTEXT.sbg_login_manager
