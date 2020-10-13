from typing import Generic, Optional, Type

import attr

from opyoid.typings import InjectedT


@attr.s(auto_attribs=True, frozen=True)
class FrozenTarget(Generic[InjectedT]):
    """Identifies a class being injected, can be used as an index as it is read only."""

    type: Type[InjectedT]
    annotation: Optional[str] = None
