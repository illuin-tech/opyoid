from typing import cast

from opyoid.provider import Provider
from opyoid.utils import EMPTY, InjectedT


class ContextScopedProvider(Provider[InjectedT]):
    """Always provides the same instance in the same context, a new instance in each context."""

    def __init__(self, unscoped_provider: Provider[InjectedT]):
        self._unscoped_provider = unscoped_provider
        self._cached_instance = EMPTY
        self._is_scope_activated = False

    def get(self) -> InjectedT:
        if not self._is_scope_activated:
            return self._unscoped_provider.get()

        if self._cached_instance is EMPTY:
            self._cached_instance = self._unscoped_provider.get()

        return cast(InjectedT, self._cached_instance)

    def enter(self) -> None:
        self._is_scope_activated = True

    def exit(self) -> None:
        self._is_scope_activated = False
        self._cached_instance = EMPTY
