import signal
from contextlib import contextmanager


class ProviderTimeout(Exception):
    pass


@contextmanager
def timeout(seconds: int):
    def handler(signum, frame):
        raise ProviderTimeout(f'Provider exceeded timeout of {seconds}s')

    previous = signal.signal(signal.SIGALRM, handler)
    signal.alarm(seconds)

    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous)
