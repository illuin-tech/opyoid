from opyoid.provider import Provider
from opyoid.utils import InjectedT
from .scope import Scope
from .singleton_scoped_provider import SingletonScopedProvider


class SingletonScope(Scope):
    """Always provides the same instance."""

    def get_scoped_provider(self, inner_provider: Provider[InjectedT]) -> Provider[InjectedT]:
        return SingletonScopedProvider(inner_provider)
