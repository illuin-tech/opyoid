from typing import Set

from .abstract_binding_spec import AbstractBindingSpec
from .registered_binding import RegisteredBinding


class PrivateBindingSpec(AbstractBindingSpec):
    def __init__(self):
        AbstractBindingSpec.__init__(self)
        self._exposed_bindings: Set[RegisteredBinding] = set()

    def configure(self) -> None:
        raise NotImplementedError

    def is_exposed(self, binding: RegisteredBinding) -> bool:
        return binding in self._exposed_bindings

    def expose(self, *bindings: RegisteredBinding) -> None:
        for binding in bindings:
            self._exposed_bindings.add(binding)
