from typing import Callable, Type

from illuin_inject.typings import InjectedT
from .scope import Scope


class PerLookupScope(Scope):
    """Provides a new instance every time."""

    def get(self, bound_type: Type[InjectedT], provider: Callable[[], InjectedT]) -> InjectedT:
        return provider()
