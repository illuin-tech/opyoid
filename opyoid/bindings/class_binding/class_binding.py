from typing import Optional, Type

import attr

from opyoid.bindings.binding import Binding
from opyoid.exceptions import BindingError
from opyoid.scopes import Scope, SingletonScope
from opyoid.typings import InjectedT


@attr.s(auto_attribs=True, frozen=True)
class ClassBinding(Binding[InjectedT]):
    _target_type: Type[InjectedT]
    bound_type: Type[InjectedT] = attr.Factory(lambda self: self.target_type, takes_self=True)
    scope: Type[Scope] = SingletonScope
    _annotation: Optional[str] = None

    def __attrs_post_init__(self) -> None:
        if not isinstance(self.bound_type, type):
            raise BindingError(f"Invalid {self!r}: bound type must be a class, got {self.bound_type!r}")

    @property
    def target_type(self) -> Type[InjectedT]:
        return self._target_type

    @property
    def annotation(self) -> Optional[str]:
        return self._annotation
