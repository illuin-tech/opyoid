from typing import Optional, TYPE_CHECKING, Type, Union

import attr

from opyoid.bindings.binding import Binding
from opyoid.exceptions import BindingError
from opyoid.scopes import Scope, SingletonScope
from opyoid.utils import InjectedT, get_class_full_name

if TYPE_CHECKING:
    from typing import TypeVar


@attr.s(auto_attribs=True, frozen=True, repr=False)
class ClassBinding(Binding[InjectedT]):
    _target_type: Union[Type[InjectedT], "TypeVar"]
    bound_class: Type[InjectedT]
    scope: Type[Scope] = attr.ib(default=SingletonScope, kw_only=True)
    _named: Optional[str] = attr.ib(default=None, kw_only=True)

    def __attrs_post_init__(self) -> None:
        if not isinstance(self.bound_class, type):
            raise BindingError(f"Invalid {self!r}: bound type must be a class, got {self.bound_class!r}")
        if self.bound_class == self.target_type:
            raise BindingError(f"Invalid {self!r}: use a SelfBinding to bind a class to itself")

    @property
    def target_type(self) -> Union[Type[InjectedT], "TypeVar"]:
        return self._target_type

    @property
    def named(self) -> Optional[str]:
        return self._named

    def __repr__(self) -> str:
        scope_string = f", scope={self.scope}" if self.scope != SingletonScope else ""
        return f"{self.__class__.__name__}({self.target!r} -> {get_class_full_name(self.bound_class)}{scope_string})"
