from typing import Generic, TYPE_CHECKING, Tuple, TypeVar

import attr

from opyoid.frozen_target import FrozenTarget
from opyoid.utils import InjectedT
from .binding import Binding

if TYPE_CHECKING:
    from .private_module import PrivateModule

BindingT = TypeVar("BindingT", bound=Binding)


@attr.s(auto_attribs=True, frozen=True)
class RegisteredBinding(Generic[BindingT]):
    raw_binding: BindingT
    source_path: Tuple["PrivateModule", ...] = attr.Factory(tuple)
    target: FrozenTarget[InjectedT] = attr.Factory(lambda self: self.raw_binding.target, takes_self=True)
