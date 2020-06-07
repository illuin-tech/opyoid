from typing import Generic, TYPE_CHECKING, Tuple

import attr

from illuin_inject.target import Target
from illuin_inject.typings import InjectedT
from .binding import Binding

if TYPE_CHECKING:
    from .abstract_binding_spec import AbstractBindingSpec


@attr.s(auto_attribs=True, frozen=True)
class RegisteredBinding(Generic[InjectedT]):
    raw_binding: Binding[InjectedT]
    source_path: Tuple["AbstractBindingSpec", ...] = attr.Factory(tuple)
    target: Target[InjectedT] = attr.Factory(lambda self: self.raw_binding.target, takes_self=True)
