from typing import Generic, Optional, Type

import attr

from illuin_inject.typings import InjectedT


@attr.s(auto_attribs=True, frozen=True)
class Binding(Generic[InjectedT]):
    """Represents a link between a Target and something used to create it."""

    @property
    def target_type(self) -> Type[InjectedT]:
        raise NotImplementedError

    @property
    def annotation(self) -> Optional[str]:
        raise NotImplementedError
