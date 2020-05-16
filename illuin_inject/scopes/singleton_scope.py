from threading import RLock
from typing import Any, Callable, Dict
from uuid import UUID

from illuin_inject.typings import InjectedT
from .scope import Scope


class SingletonScope(Scope):
    """Always provides the same instance."""

    def __init__(self) -> None:
        self._cache: Dict[UUID, Any] = {}
        self._lock = RLock()

    def get(self, cache_key: UUID, provider: Callable[[], InjectedT]) -> InjectedT:
        with self._lock:
            if cache_key not in self._cache:
                injected_instance = provider()
                self._cache[cache_key] = injected_instance
            return self._cache[cache_key]
