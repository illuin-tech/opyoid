from typing import Any, Generic, Optional, Type, TypeVar, Union

import attr

from opyoid.utils import EMPTY, get_class_full_name, InjectedT


@attr.s(auto_attribs=True, repr=False)
class Target(Generic[InjectedT]):
    """Identifies a class being injected."""

    type: Union[Type[InjectedT], TypeVar, str, Any]
    named: Optional[str] = None
    default: Union[InjectedT, object] = attr.ib(default=EMPTY, eq=False)
    provider_cache_key: Optional[Any] = None

    def __repr__(self) -> str:
        return f"{get_class_full_name(self.type)}" + (f"#{self.named}" if self.named else "")
