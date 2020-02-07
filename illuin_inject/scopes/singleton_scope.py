from threading import RLock
from typing import Any, Callable, Dict, Type

from illuin_inject.typings import InjectedT
from .scope import Scope


class SingletonScope(Scope):
    """Always provides the same instance."""

    def __init__(self) -> None:
        self._cache: Dict[Type, Any] = {}
        self._lock = RLock()

    def get(self, bound_type: Type[InjectedT], provider: Callable[[], InjectedT]) -> InjectedT:
        with self._lock:
            if bound_type not in self._cache:
                injected_instance = provider()
                self._cache[bound_type] = injected_instance
            return self._cache[bound_type]
