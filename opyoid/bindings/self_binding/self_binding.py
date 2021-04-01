from typing import Optional, Type

import attr

from opyoid.bindings.binding import Binding
from opyoid.scopes import Scope, SingletonScope
from opyoid.utils import InjectedT


@attr.s(auto_attribs=True, frozen=True, repr=False)
class SelfBinding(Binding[InjectedT]):
    _target_type: Type[InjectedT]
    scope: Type[Scope] = attr.ib(default=SingletonScope, kw_only=True)
    _named: Optional[str] = attr.ib(default=None, kw_only=True)

    @property
    def target_type(self) -> Type[InjectedT]:
        return self._target_type

    @property
    def named(self) -> Optional[str]:
        return self._named

    def __repr__(self) -> str:
        scope_string = f", scope={self.scope}" if self.scope != SingletonScope else ""
        return f"{self.__class__.__name__}({self.target!r}{scope_string})"
