from typing import List

import attr

from opyoid.utils import InjectedT
from .multi_binding import MultiBinding
from .registered_binding import RegisteredBinding


@attr.s(auto_attribs=True, frozen=True)
class RegisteredMultiBinding(RegisteredBinding[MultiBinding[InjectedT]]):
    item_bindings: List[RegisteredBinding[InjectedT]] = attr.Factory(list)
