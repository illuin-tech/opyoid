from typing import Generic

from .typings import InjectedT


class Factory(Generic[InjectedT]):
    def create(self) -> InjectedT:
        raise NotImplementedError
