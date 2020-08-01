from typing import Generic, Type, Union

import attr

from illuin_inject.provider import Provider
from illuin_inject.typings import EMPTY, InjectedT


@attr.s(auto_attribs=True, frozen=True)
class ItemBinding(Generic[InjectedT]):
    bound_type: Type[InjectedT] = EMPTY
    bound_instance: InjectedT = EMPTY
    bound_provider: Union[Provider, Type[Provider]] = EMPTY
