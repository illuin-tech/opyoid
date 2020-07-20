from typing import Generic

from illuin_inject.typings import InjectedT


class Provider(Generic[InjectedT]):
    """Base class for all providers, provides an instance of the injected class."""

    def get(self) -> InjectedT:
        raise NotImplementedError
