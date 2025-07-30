from contextlib import contextmanager
from .publisher import publish
from .subscriber import subscribe


@contextmanager
def timeout(seconds: float):
    import signal
    def _raise_timeout(*args):
        raise TimeoutError()

    signal.signal(signal.SIGALRM, _raise_timeout)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, signal.SIG_DFL)
