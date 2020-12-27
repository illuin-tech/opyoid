import threading

from opyoid.provider import Provider
from opyoid.utils import InjectedT


class ThreadScopedProvider(Provider[InjectedT]):
    """Always provides the same instance if called in the same thread, creates a new one if not."""

    def __init__(self, inner_provider: Provider[InjectedT]) -> None:
        self._inner_provider = inner_provider
        self._lock = threading.Lock()
        self._local = threading.local()

    def get(self) -> InjectedT:
        with self._lock:
            try:
                return self._local.cached_instance
            except AttributeError:
                self._local.cached_instance = self._inner_provider.get()
        return self._local.cached_instance
