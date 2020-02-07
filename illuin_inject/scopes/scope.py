from typing import Callable, Type

from illuin_inject.typings import InjectedT


class Scope:
    def get(self, bound_type: Type[InjectedT], provider: Callable[[], InjectedT]) -> InjectedT:
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
