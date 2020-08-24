from typing import Generic, Optional, Type

import attr

from opyoid.target import Target
from opyoid.typings import InjectedT


@attr.s(auto_attribs=True, frozen=True)
class Binding(Generic[InjectedT]):
    """Abstract class representing a link between a Target and something used to create it."""

    @property
    def target_type(self) -> Type[InjectedT]:
        raise NotImplementedError

    @property
    def annotation(self) -> Optional[str]:
        raise NotImplementedError

    @property
    def target(self) -> Target[InjectedT]:
        return Target(self.target_type, self.annotation)
