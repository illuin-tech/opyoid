from typing import List, Optional, TYPE_CHECKING, Type, Union

import attr

from opyoid.bindings.binding import Binding
from opyoid.bindings.multi_binding.item_binding import ItemBinding
from opyoid.scopes import Scope, SingletonScope
from opyoid.utils import InjectedT

if TYPE_CHECKING:
    from typing import TypeVar


@attr.s(auto_attribs=True, frozen=True, repr=False)
class MultiBinding(Binding[List[InjectedT]]):
    item_target_type: Union[Type[InjectedT], "TypeVar"]
    item_bindings: List[ItemBinding[InjectedT]]
    scope: Type[Scope] = attr.ib(default=SingletonScope, kw_only=True)
    _named: Optional[str] = attr.ib(default=None, kw_only=True)
    override_bindings: bool = attr.ib(default=True, kw_only=True)

    @property
    def target_type(self) -> Union[Type[List[InjectedT]], "TypeVar"]:
        return List[self.item_target_type]

    @property
    def named(self) -> Optional[str]:
        return self._named

    def __repr__(self) -> str:
        items_string = ", ".join(f"{item!r}" for item in self.item_bindings)
        scope_string = f", scope={self.scope}" if self.scope != SingletonScope else ""
        return f"{self.__class__.__name__}({self.target!r} -> [{items_string}]{scope_string})"
