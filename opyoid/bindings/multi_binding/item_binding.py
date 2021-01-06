from typing import Generic, Type, Union

import attr

from opyoid.provider import Provider
from opyoid.utils import EMPTY, InjectedT, get_class_full_name


@attr.s(auto_attribs=True, frozen=True, repr=False)
class ItemBinding(Generic[InjectedT]):
    bound_type: Type[InjectedT] = EMPTY
    bound_instance: InjectedT = EMPTY
    bound_provider: Union[Provider, Type[Provider]] = EMPTY

    def __repr__(self) -> str:
        if self.bound_type is not EMPTY:
            return get_class_full_name(self.bound_type)
        if self.bound_instance is not EMPTY:
            return repr(self.bound_instance)
        if isinstance(self.bound_provider, Provider):
            return repr(self.bound_provider)
        return get_class_full_name(self.bound_provider)
