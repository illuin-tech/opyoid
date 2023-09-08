from typing import Generic, Optional, Type, TypeVar, Union

import attr

from opyoid.utils import get_class_full_name, InjectedT


@attr.s(auto_attribs=True, frozen=True, repr=False)
class FrozenTarget(Generic[InjectedT]):
    """Identifies a class being injected, can be used as an index as it is read only."""

    type: Union[Type[InjectedT], TypeVar]
    named: Optional[str] = None

    def __repr__(self) -> str:
        return f"{get_class_full_name(self.type)}" + (f"#{self.named}" if self.named else "")
