from typing import Generic, Type

import attr

from illuin_inject.typings import InjectedT


@attr.s(auto_attribs=True)
class Binding(Generic[InjectedT]):
    target_type: Type[InjectedT]
