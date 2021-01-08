from typing import List, Optional, Type

import attr

from opyoid.bindings.binding import Binding
from opyoid.bindings.multi_binding.item_binding import ItemBinding
from opyoid.scopes import Scope, SingletonScope
from opyoid.utils import InjectedT


@attr.s(auto_attribs=True, frozen=True, repr=False)
class MultiBinding(Binding[List[InjectedT]]):
    item_target_type: Type[InjectedT]
    item_bindings: List[ItemBinding[InjectedT]]
    scope: Type[Scope] = SingletonScope
    _named: Optional[str] = None
    override_bindings: bool = True

    @property
    def target_type(self) -> Type[List[InjectedT]]:
        return List[self.item_target_type]

    @property
    def named(self) -> Optional[str]:
        return self._named

    def __repr__(self) -> str:
        items_string = ", ".join(f"{item!r}" for item in self.item_bindings)
        scope_string = f", scope={self.scope}" if self.scope != SingletonScope else ""
        return f"{self.__class__.__name__}({self.target!r} -> [{items_string}]{scope_string})"
