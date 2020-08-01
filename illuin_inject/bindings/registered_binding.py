from typing import Generic, TYPE_CHECKING, Tuple

import attr

from illuin_inject.target import Target
from illuin_inject.typings import InjectedT
from .binding import Binding

if TYPE_CHECKING:
    from .private_module import PrivateModule


@attr.s(auto_attribs=True, frozen=True)
class RegisteredBinding(Generic[InjectedT]):
    raw_binding: Binding[InjectedT]
    source_path: Tuple["PrivateModule", ...] = attr.Factory(tuple)
    target: Target[InjectedT] = attr.Factory(lambda self: self.raw_binding.target, takes_self=True)
