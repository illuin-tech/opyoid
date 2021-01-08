from typing import Generic, Optional, Type

import attr

from opyoid.frozen_target import FrozenTarget
from opyoid.utils import InjectedT


@attr.s(auto_attribs=True, frozen=True)
class Binding(Generic[InjectedT]):
    """Abstract class representing a link between a Target and something used to create it."""

    @property
    def target_type(self) -> Type[InjectedT]:
        raise NotImplementedError

    @property
    def named(self) -> Optional[str]:
        raise NotImplementedError

    @property
    def target(self) -> FrozenTarget[InjectedT]:
        return FrozenTarget(self.target_type, self.named)
