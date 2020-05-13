from typing import Callable
from uuid import UUID

from illuin_inject.typings import InjectedT


class Scope:
    def get(self, cache_key: UUID, provider: Callable[[], InjectedT]) -> InjectedT:
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
