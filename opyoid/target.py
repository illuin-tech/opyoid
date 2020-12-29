from typing import Any, Generic, Optional, Type, Union

import attr

from opyoid.utils import EMPTY, InjectedT, get_class_full_name


@attr.s(auto_attribs=True, repr=False)
class Target(Generic[InjectedT]):
    """Identifies a class being injected."""

    type: Union[Type[InjectedT], str]
    named: Optional[str] = None
    default: Any = attr.ib(default=EMPTY, eq=False)

    def __repr__(self) -> str:
        return f"{get_class_full_name(self.type)}" + (f"#{self.named}" if self.named else "")
