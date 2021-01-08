from typing import Optional, Type

import attr

from opyoid.bindings.binding import Binding
from opyoid.exceptions import BindingError
from opyoid.scopes import Scope, SingletonScope
from opyoid.utils import InjectedT, get_class_full_name


@attr.s(auto_attribs=True, frozen=True, repr=False)
class ClassBinding(Binding[InjectedT]):
    _target_type: Type[InjectedT]
    bound_type: Type[InjectedT]
    scope: Type[Scope] = SingletonScope
    _named: Optional[str] = None

    def __attrs_post_init__(self) -> None:
        if not isinstance(self.bound_type, type):
            raise BindingError(f"Invalid {self!r}: bound type must be a class, got {self.bound_type!r}")
        if self.bound_type == self.target_type:
            raise BindingError(f"Invalid {self!r}: use a SelfBinding to bind a class to itself")

    @property
    def target_type(self) -> Type[InjectedT]:
        return self._target_type

    @property
    def named(self) -> Optional[str]:
        return self._named

    def __repr__(self) -> str:
        scope_string = f", scope={self.scope}" if self.scope != SingletonScope else ""
        return f"{self.__class__.__name__}({self.target!r} -> {get_class_full_name(self.bound_type)}{scope_string})"
