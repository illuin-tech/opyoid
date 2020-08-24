from typing import Generic, Optional, Type, Union

import attr

from opyoid.typings import InjectedT


@attr.s(auto_attribs=True, frozen=True)
class Target(Generic[InjectedT]):
    """Identifies a class being injected."""

    type: Union[Type[InjectedT], str]
    annotation: Optional[str] = None
