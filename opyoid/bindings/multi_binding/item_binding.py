from typing import cast, Generic, Optional, Type, Union

import attr

from opyoid.provider import Provider
from opyoid.scopes import Scope
from opyoid.utils import EMPTY, get_class_full_name, InjectedT


@attr.s(auto_attribs=True, frozen=True, repr=False, kw_only=True)
class ItemBinding(Generic[InjectedT]):
    bound_class: Union[Type[InjectedT], object] = EMPTY
    bound_instance: Union[InjectedT, object] = EMPTY
    bound_provider: Union[Provider[InjectedT], Type[Provider[InjectedT]], object] = EMPTY
    named: Union[Optional[str], object] = attr.ib(default=EMPTY, kw_only=True)
    scope: Union[Type[Scope], object] = attr.ib(default=EMPTY, kw_only=True)

    def __repr__(self) -> str:
        if self.bound_class is not EMPTY:
            return get_class_full_name(cast(Type[InjectedT], self.bound_class))
        if self.bound_instance is not EMPTY:
            return repr(self.bound_instance)
        if isinstance(self.bound_provider, Provider):
            return repr(self.bound_provider)
        return get_class_full_name(cast(Type[InjectedT], self.bound_provider))
