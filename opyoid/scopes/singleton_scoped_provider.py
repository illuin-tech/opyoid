from threading import Lock
from typing import Union

from opyoid.provider import Provider
from opyoid.utils import EMPTY, InjectedT


class SingletonScopedProvider(Provider[InjectedT]):
    """Always provides the same instance."""

    def __init__(self, inner_provider: Provider[InjectedT]) -> None:
        self._inner_provider = inner_provider
        self._cached_instance: Union[InjectedT, object] = EMPTY
        self._lock = Lock()

    def get(self) -> InjectedT:
        with self._lock:
            if self._cached_instance is EMPTY:
                injected_instance = self._inner_provider.get()
                self._cached_instance = injected_instance
        return self._cached_instance
