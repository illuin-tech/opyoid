from typing import Generic, Optional, Type

import attr

from opyoid.utils import InjectedT, get_class_full_name


@attr.s(auto_attribs=True, frozen=True, repr=False)
class FrozenTarget(Generic[InjectedT]):
    """Identifies a class being injected, can be used as an index as it is read only."""

    type: Type[InjectedT]
    named: Optional[str] = None

    def __repr__(self) -> str:
        return f"{get_class_full_name(self.type)}" + (f"#{self.named}" if self.named else "")
