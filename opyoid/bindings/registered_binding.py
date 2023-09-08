from typing import Generic, Tuple, TYPE_CHECKING

import attr

from opyoid.frozen_target import FrozenTarget
from opyoid.utils import InjectedT
from .binding import Binding

if TYPE_CHECKING:
    from .private_module import PrivateModule


@attr.s(auto_attribs=True, frozen=True)
class RegisteredBinding(Generic[InjectedT]):
    raw_binding: Binding[InjectedT]
    source_path: Tuple["PrivateModule", ...] = attr.Factory(tuple)
    target: FrozenTarget[InjectedT] = attr.Factory(lambda self: self.raw_binding.target, takes_self=True)
