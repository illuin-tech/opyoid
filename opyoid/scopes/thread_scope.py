from opyoid.provider import Provider
from opyoid.utils import InjectedT
from .scope import Scope
from .thread_scoped_provider import ThreadScopedProvider


class ThreadScope(Scope):
    """Always provides the same instance if called in the same thread, creates a new one if not."""

    def get_scoped_provider(self, inner_provider: Provider[InjectedT]) -> Provider[InjectedT]:
        return ThreadScopedProvider(inner_provider)
