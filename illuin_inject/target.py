from typing import Generic, Optional, Type, Union

import attr

from illuin_inject.typings import InjectedT


@attr.s(auto_attribs=True, frozen=True)
class Target(Generic[InjectedT]):
    type: Union[Type[InjectedT], str]
    annotation: Optional[str] = None
