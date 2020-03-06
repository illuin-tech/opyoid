from typing import Generic, Optional, Type

import attr

from illuin_inject.typings import InjectedT


@attr.s(auto_attribs=True)
class Binding(Generic[InjectedT]):
    target_type: Type[InjectedT]
    annotation: Optional[str] = None
