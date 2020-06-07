from illuin_inject.provider import Provider
from illuin_inject.typings import InjectedT
from .scope import Scope
from .singleton_scoped_provider import SingletonScopedProvider

EMPTY = object()


class SingletonScope(Scope):
    """Always provides the same instance."""

    def get_scoped_provider(self, inner_provider: Provider[InjectedT]) -> Provider[InjectedT]:
        return SingletonScopedProvider(inner_provider)
