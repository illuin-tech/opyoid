from typing import Any, List, TypeVar

import attr

from .registered_binding import RegisteredBinding

InjectedItemT = TypeVar("InjectedItemT", bound=Any)


@attr.s(auto_attribs=True, frozen=True)
class RegisteredMultiBinding(RegisteredBinding[List[InjectedItemT]]):
    item_bindings: List[RegisteredBinding[InjectedItemT]] = attr.Factory(list)
