from typing import Callable
from uuid import UUID

from illuin_inject.typings import InjectedT
from .scope import Scope


class PerLookupScope(Scope):
    """Provides a new instance every time."""

    def get(self, cache_key: UUID, provider: Callable[[], InjectedT]) -> InjectedT:
        return provider()
