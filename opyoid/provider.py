from typing import Generic

from opyoid.utils import InjectedT


class Provider(Generic[InjectedT]):
    """Base class for all providers, provides an instance of the injected class."""

    def get(self) -> InjectedT:
        raise NotImplementedError
