from opyoid.provider import Provider
from opyoid.utils import InjectedT
from .singleton_scope import SingletonScope


class ImmediateScope(SingletonScope):
    """Always provides the same instance, objects are instantiated immediately."""

    def get_scoped_provider(self, inner_provider: Provider[InjectedT]) -> Provider[InjectedT]:
        provider = SingletonScope.get_scoped_provider(self, inner_provider)
        provider.get()
        return provider
