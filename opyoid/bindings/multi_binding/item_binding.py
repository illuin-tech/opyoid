from typing import Generic, Optional, Type, Union

import attr

from opyoid.provider import Provider
from opyoid.scopes import Scope
from opyoid.utils import EMPTY, InjectedT, get_class_full_name


@attr.s(auto_attribs=True, frozen=True, repr=False, kw_only=True)
class ItemBinding(Generic[InjectedT]):
    bound_class: Type[InjectedT] = EMPTY
    bound_instance: InjectedT = EMPTY
    bound_provider: Union[Provider, Type[Provider]] = EMPTY
    named: Optional[str] = attr.ib(default=EMPTY, kw_only=True)
    scope: Type[Scope] = attr.ib(default=EMPTY, kw_only=True)

    def __repr__(self) -> str:
        if self.bound_class is not EMPTY:
            return get_class_full_name(self.bound_class)
        if self.bound_instance is not EMPTY:
            return repr(self.bound_instance)
        if isinstance(self.bound_provider, Provider):
            return repr(self.bound_provider)
        return get_class_full_name(self.bound_provider)
