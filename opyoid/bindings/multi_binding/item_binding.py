from typing import Generic, Type, Union

import attr

from opyoid.provider import Provider
from opyoid.typings import EMPTY, InjectedT


@attr.s(auto_attribs=True, frozen=True)
class ItemBinding(Generic[InjectedT]):
    bound_type: Type[InjectedT] = EMPTY
    bound_instance: InjectedT = EMPTY
    bound_provider: Union[Provider, Type[Provider]] = EMPTY
