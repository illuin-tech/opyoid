import threading
from typing import Callable
from uuid import UUID

from illuin_inject.typings import InjectedT
from .scope import Scope


class ThreadScope(Scope):
    """Always provides the same instance if called in the same thread, creates a new one if not."""

    def __init__(self) -> None:
        Scope.__init__(self)
        self._lock = threading.RLock()
        self._local = threading.local()
        self._set_local_scope()

    def get(self, cache_key: UUID, provider: Callable[[], InjectedT]) -> InjectedT:
        with self._lock:
            self._set_local_scope()
            if cache_key not in self._local.thread_scope_cache:
                injected_instance = provider()
                self._local.thread_scope_cache[cache_key] = injected_instance
            return self._local.thread_scope_cache[cache_key]

    def _set_local_scope(self) -> None:
        with self._lock:
            try:
                self._local.thread_scope_cache
            except AttributeError:
                self._local.thread_scope_cache = {}
