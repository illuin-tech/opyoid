from illuin_inject.provider import Provider
from illuin_inject.typings import InjectedT
from .scope import Scope


class PerLookupScope(Scope):
    """Provides a new instance every time."""

    def get_scoped_provider(self, inner_provider: Provider[InjectedT]) -> Provider[InjectedT]:
        return inner_provider
