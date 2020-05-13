from typing import Generic

from .typings import InjectedT


class Factory(Generic[InjectedT]):  # pragma: nocover
    def create(self) -> InjectedT:
        raise NotImplementedError
