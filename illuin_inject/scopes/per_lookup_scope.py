from illuin_inject.provider import Provider
from illuin_inject.typings import InjectedT
from .scope import Scope


class PerLookupScope(Scope):
    """Provides a new instance every time."""

    @classmethod
    def get_scoped_provider(cls, inner_provider: Provider[InjectedT]) -> Provider[InjectedT]:
        return inner_provider
