from typing import Optional, Type

import attr

from opyoid.bindings.binding import Binding
from opyoid.utils import InjectedT


@attr.s(auto_attribs=True, frozen=True, repr=False)
class InstanceBinding(Binding[InjectedT]):
    _target_type: Type[InjectedT]
    bound_instance: InjectedT
    _named: Optional[str] = None

    @property
    def target_type(self) -> Type[InjectedT]:
        return self._target_type

    @property
    def named(self) -> Optional[str]:
        return self._named

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.target!r} -> {self.bound_instance!r})"
