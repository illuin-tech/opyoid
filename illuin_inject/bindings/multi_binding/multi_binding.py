from typing import List, Optional, Type

import attr

from illuin_inject.bindings.binding import Binding
from illuin_inject.bindings.multi_binding.item_binding import ItemBinding
from illuin_inject.scopes import Scope, SingletonScope
from illuin_inject.typings import InjectedT


@attr.s(auto_attribs=True, frozen=True)
class MultiBinding(Binding[List[InjectedT]]):
    item_target_type: Type[InjectedT]
    item_bindings: List[ItemBinding[InjectedT]]
    scope: Type[Scope] = SingletonScope
    _annotation: Optional[str] = None
    override_bindings: bool = True

    @property
    def target_type(self) -> Type[List[InjectedT]]:
        return List[self.item_target_type]

    @property
    def annotation(self) -> Optional[str]:
        return self._annotation
