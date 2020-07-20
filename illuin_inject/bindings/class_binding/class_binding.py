from typing import Optional, Type

import attr

from illuin_inject.bindings.binding import Binding
from illuin_inject.scopes import Scope, SingletonScope
from illuin_inject.typings import InjectedT


@attr.s(auto_attribs=True, frozen=True)
class ClassBinding(Binding[InjectedT]):
    _target_type: Type[InjectedT]
    bound_type: Type[InjectedT] = attr.Factory(lambda self: self.target_type, takes_self=True)
    scope: Type[Scope] = SingletonScope
    _annotation: Optional[str] = None

    @property
    def target_type(self) -> Type[InjectedT]:
        return self._target_type

    @property
    def annotation(self) -> Optional[str]:
        return self._annotation
