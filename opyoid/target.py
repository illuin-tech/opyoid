from typing import Any, Generic, Optional, Type, Union

import attr

from opyoid.typings import EMPTY, InjectedT


@attr.s(auto_attribs=True)
class Target(Generic[InjectedT]):
    """Identifies a class being injected."""

    type: Union[Type[InjectedT], str]
    annotation: Optional[str] = None
    default: Any = attr.ib(default=EMPTY, eq=False)
